# 使用官方轻量级 Python 3.9 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制剩余所有 Python 代码
COPY . .

# 启动 Bot
CMD ["python", "pxx.py"]