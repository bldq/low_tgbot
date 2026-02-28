import sqlite3
import os
import random
import config

def init_db():
    """
    初始化数据库结构。
    如果数据库和表不存在则创建，不会清空已有数据，保障数据安全。
    """
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    # 创建 media 表。
    # MEDIA_ID: 自增主键，后续通过最大ID取随机数实现 O(1) 极速抽图
    # MEDIA_FULL_PATH: 图片完整路径，设置 UNIQUE 约束防止同一图片重复录入
    # FILE_ID: 用于缓存 Telegram 上传成功后返回的专属 file_id，避免后续重复消耗流量上传
    create_tb_cmd = '''
        CREATE TABLE IF NOT EXISTS media
        (
        MEDIA_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        MEDIA_FULL_PATH TEXT UNIQUE,
        MEDIA_ITEM TEXT,
        MEDIA_NAME TEXT,
        MEDIA_SIZE INT,
        FILE_ID TEXT DEFAULT NULL
        );
    '''
    c.execute(create_tb_cmd)
    conn.commit()
    conn.close()


def reset_media_db():
    """
    增量同步本地图片到数据库（替代旧版的删表重建）。
    自动录入新图片，清理已被移出硬盘的图片记录，并完美保留已有的 FILE_ID。
    """
    init_db() # 确保表已建立
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor() 
    
    # 1. 提取数据库中现有的所有图片路径，存入集合(set)用于极速比对
    c.execute("SELECT MEDIA_FULL_PATH FROM media")
    db_paths = set([row[0] for row in c.fetchall()])
    
    # 2. 遍历本地文件系统，收集当前实际存在的有效文件路径
    local_paths = set()
    local_file_info = {} # 暂存文件元数据，减少磁盘 I/O
    
    for root, dirs, files in os.walk(config.ROOT_DIR):
        for file in files:
            full_name = os.path.join(root, file)
            size = os.path.getsize(full_name)
            
            # 过滤掉大于 10MB 的文件，确保录入的都是正常图片
            if size < 10000000: 
                local_paths.add(full_name)
                local_file_info[full_name] = {
                    'item': os.path.basename(os.path.dirname(full_name)),
                    'name': os.path.basename(full_name),
                    'size': size
                }
                
    # 3. 集合运算寻找差异（增量判断的核心）
    to_add = local_paths - db_paths      # 硬盘新增的图片 -> 需要入库
    to_remove = db_paths - local_paths   # 硬盘已删的图片 -> 需要清理出库
    
    # 4. 从数据库清理失效图片记录
    for path in to_remove:
        c.execute("DELETE FROM media WHERE MEDIA_FULL_PATH = ?", (path,))
        
    # 5. 将新图片写入数据库 (新入库记录的 FILE_ID 默认保持为 NULL)
    for path in to_add:
        info = local_file_info[path]
        c.execute('''
            INSERT OR IGNORE INTO media (MEDIA_FULL_PATH, MEDIA_ITEM, MEDIA_NAME, MEDIA_SIZE) 
            VALUES (?, ?, ?, ?)
        ''', (path, info['item'], info['name'], info['size']))

    # 获取当前库内的有效图片总数，用于向管理员汇报
    c.execute("SELECT COUNT(*) FROM media")
    total_valid = c.fetchone()[0]

    conn.commit()
    conn.close()
    
    return f"同步完毕！新增 {len(to_add)} 张，清理失效 {len(to_remove)} 张，当前有效图片共 {total_valid} 张。"


def get_random_pics(limit=9):
    """
    极速随机抽图。
    摒弃 fetchall() 全量内存读取，通过主键直接精准命中，提升数十倍性能。
    """
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    
    # 1. 查询当前最大的自增 ID (耗时极短)
    c.execute("SELECT MAX(MEDIA_ID) FROM media")
    max_id_row = c.fetchone()
    
    # 如果查不到数据，说明库是空的
    if not max_id_row or not max_id_row[0]:
        conn.close()
        return []
    
    max_id = max_id_row[0]
    
    # 2. 生成随机抽取的 ID
    # 注意：如果触发过删除操作，部分 ID 可能会产生“空洞”。
    # 为了防止因为抽到空洞导致实际返回数量不够 9 张，抽取基数乘以 3 以提供冗余缓冲。
    pool_size = min(max_id, limit * 3) 
    random_ids = random.sample(range(1, max_id + 1), pool_size)
    
    # 3. 利用 SQL 的 IN 语法，通过主键直接一次性拉取命中数据
    # 将 random_ids 转换为占位符: (?, ?, ?, ...)
    placeholders = ','.join('?' for _ in random_ids)
    query = f"""
        SELECT MEDIA_ID, MEDIA_FULL_PATH, FILE_ID 
        FROM media 
        WHERE MEDIA_ID IN ({placeholders}) 
        LIMIT ?
    """
    
    # 拼装查询参数，末尾加上 limit 参数限制最终返回数量
    params = tuple(random_ids) + (limit,)
    c.execute(query, params)
    
    result = c.fetchall()
    conn.close()
    
    return result


def update_file_id(media_id, file_id):
    """
    保存/缓存 Telegram File ID。
    当机器人通过本地读取上传了一张新图片后，主程序会调用此函数将其 ID 写入库中。
    下一次再抽到相同图片时，机器人直接发送该缓存 ID 实现“秒传”。
    """
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE media SET FILE_ID = ? WHERE MEDIA_ID = ?", (file_id, media_id))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # 方便单独执行此脚本测试目录扫描和数据库同步
    print(reset_media_db())