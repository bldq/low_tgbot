import sqlite3
import os
import config
import random
# import imghdr

# def list(dirpath):
#     # dirpath = r'/root/docker_aria2-pro/downloads_local' 
#     img_list = []
#     from_item = []
#     size_list = []
#     for root, dirs, files in os.walk(dirpath):
#         for file in files:
#             full_name = os.path.join(root, file)
#             # print(full_name)
#             img_list.append(full_name)
#             from_item.append(os.path.basename(os.path.dirname(full_name)))
#             size_list.append(os.path.getsize(full_name))
#             imgType = imghdr.what(full_name)
#             # print(from_item)
#             # exit()
#             # print(len(img_list))
#     return (img_list, from_item, size_list)
    # result = sample(img_list,9)
    # pic_list = []
    # for pic in result:
        # pic_list.append(InputMediaPhoto(open(pic, 'rb'), caption = 'enjoy'))
        # from_item.
    # await context.bot.send_media_group(chat_id=update.effective_chat.id, media=pic_list)
        # await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(pic, 'rb'))

def create_db():
    
    conn = sqlite3.connect(config.DB_PATH)
    try:
        create_tb_cmd = '''
            CREATE TABLE IF NOT EXISTS media
            (
            MEDIA_ID INT,
            MEDIA_FULL_PATH TEXT,
            MEDIA_ITEM TEXT,
            MEDIA_SIZE INT);
            '''
        conn.execute(create_tb_cmd)
    except:
        pass
    conn.commit()
    conn.close()


def reset_media_db():
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor() 
    c.execute("DROP TABLE IF EXISTS media")
    create_tb_cmd = '''
            CREATE TABLE media
            (
            MEDIA_ID primary key,
            MEDIA_FULL_PATH TEXT,
            MEDIA_ITEM TEXT,
            MEDIA_SIZE INT);
            '''
    c.execute(create_tb_cmd)
    # c.execute('''CREATE TABLE book(BOOK_ID INT, BOOK_NAME TEXT,  BOOK_DIR TEXT)''')
    # dirpath = r'/root/docker_aria2-pro/downloads_local' 
    # img_list = []
    # from_item = []
    # size_list = []
    n = 0
    for root, dirs, files in os.walk(config.ROOT_DIR):
        for file in files:
            full_name = os.path.join(root, file)
            item = os.path.basename(os.path.dirname(full_name))
            size = os.path.getsize(full_name)
            if int(size) < 10000000:
                n += 1
            # print(n)
                c.execute("insert into media values (?, ?, ?, ?)", (n, full_name, item, size))
    conn.commit()
    create_tb_cmd = '''
            CREATE TABLE IF NOT EXISTS nub
            (
            MEDIA_NUB int);
            '''
    c.execute(create_tb_cmd)
    c.execute("insert into nub values (?)", (n,))
    conn.commit()
    conn.close()
    # print('共获得%d条图书信息' % i)
    return '共获得%d条有效图片信息' % n


def rows_nub():
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    # c.execute("SELECT count(*) FROM nub")
    # hangshu = c.fetchall()
    c.execute("SELECT * FROM media")
    # hangshu = c.fetchall()
    # rdm_nub = random.randint(1, int(hangshu[0][0]))
    # c.execute("SELECT * FROM media where MEDIA_SIZE<?", (10000000,))
    values = c.fetchall()
    result = random.sample(values,9)
    conn.commit()
    conn.close()
    return result

if __name__ == '__main__':
    # create_db()
    # reset_media_db()
    print(reset_media_db())