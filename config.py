import os

# 使用 os.getenv 读取环境变量
# 第二个参数是默认值，如果环境变量未设置，将使用默认值兜底
BOT_TOKEN = os.getenv('BOT_TOKEN', '在此处填入你的后备Token，或者留空')

# 容器内的默认下载挂载路径
ROOT_DIR = os.getenv('ROOT_DIR', '/downloads')

# 指向 Docker Compose 网络中的 Aria2 服务
RPC_SERVER = os.getenv('RPC_SERVER', 'http://aria2:6801/jsonrpc')

# Aria2 的 RPC Token
RPC_TOKEN = os.getenv('RPC_TOKEN', 'token:')

# 容器内的数据库存放路径
DB_PATH = os.getenv('DB_PATH', '/app/data/media.db')