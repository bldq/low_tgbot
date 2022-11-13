import sqlite3
import os
import config
from random import sample

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
            MEDIA_ID INT,
            MEDIA_FULL_PATH TEXT,
            MEDIA_ITEM TEXT,
            MEDIA_SIZE INT);
            '''
    c.execute(create_tb_cmd)
    n = 0
    for root, dirs, files in os.walk(config.ROOT_DIR):
        for file in files:
            full_name = os.path.join(root, file)
            item = os.path.basename(os.path.dirname(full_name))
            size = os.path.getsize(full_name)
            n += 1
            c.execute("insert into media values (?, ?, ?, ?)", (n, full_name, item, size))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # create_db()
    reset_media_db()