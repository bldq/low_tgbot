import sqlite3
import os
import config
from random import sample
def list():
    dirpath = r'/root/docker_aria2-pro/downloads_local' 
    img_list = from_item = []
    for root, dirs, files in os.walk(dirpath):
        for file in files:
            full_name = os.path.join(root, file)
            img_list.append(full_name)
            from_item.append(os.path.basename(full_name))
    
    result = sample(img_list,9)
    pic_list = []
    # for pic in result:
        # pic_list.append(InputMediaPhoto(open(pic, 'rb'), caption = 'enjoy'))
        # from_item.
    # await context.bot.send_media_group(chat_id=update.effective_chat.id, media=pic_list)
        # await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(pic, 'rb'))

def create_db(db_path):
    conn = sqlite3.connect(db_path)
    try:
        create_tb_cmd = '''
            CREATE TABLE IF NOT EXISTS media
            (
            MEDIA_ID INT,
            MEDIA_NAME TEXT,
            MEDIA_DIR TEXT,
            MEDIA_SIZE INT);
            '''
        conn.execute(create_tb_cmd)
    except:
        pass
    conn.commit()
    conn.close()


def reset_media_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DROP TABLE media")
    create_tb_cmd = '''
            CREATE TABLE media
            (
            MEDIA_ID INT,
            MEDIA_NAME TEXT,
            MEDIA_DIR TEXT,
            MEDIA_SIZE INT);
            '''
    c.execute(create_tb_cmd)
    # c.execute('''CREATE TABLE book(BOOK_ID INT, BOOK_NAME TEXT,  BOOK_DIR TEXT)''')
    i = 0
    # print(Config.book_root_dir)
    for (dirname, dirs, files) in os.walk(config.ROOT_DIR):
        for filename in files:
            if filename.endswith(('.txt', '.epub', '.mobi', '.pdf')):
            # if filename.endswith(('.txt', '.epub', '.mobi')):
                i = i+1
                full_path = os.path.join(dirname, filename)
                # print(type(i))
                book_c = (i, filename, full_path)
                # print (os.path.getsize(thefile), thefile)
                # print(str(i), thefile)
                c.execute("insert into book values (?, ?, ?)", book_c)
    conn.commit()
    conn.close()
    # print('共获得%d条图书信息' % i)
    return i


def rows_nub():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT count(*) FROM book")
    hangshu = c.fetchall()
    rdm_nub = random.randint(1, int(hangshu[0][0]))
    c.execute("SELECT * FROM book where BOOK_ID=?", (rdm_nub,))
    values = c.fetchall()
    conn.commit()
    conn.close()
    return values