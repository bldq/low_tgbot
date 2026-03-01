import config
import re
import os
import requests
from bs4 import BeautifulSoup

# def add_download_rpc(url_list,path):
#     s = xmlrpc.client.ServerProxy(config.RPC_SERVER)
#     for url in url_list: 
#         s.aria2.addUri(config.RPC_TOKEN,[url],dict(dir=os.path.join(r"/downloads",path)))

def add_download_rpc(url_list, path):
    """
    使用 requests 向 Aria2 的 JSON-RPC 接口发送下载请求
    """
    rpc_url = config.RPC_SERVER
    
    for url in url_list: 
        # 构建符合 JSON-RPC 2.0 规范的请求体
        payload = {
            "jsonrpc": "2.0",
            "id": "tgbot",
            "method": "aria2.addUri",
            "params": [
                config.RPC_TOKEN,          # 参数1: RPC Token
                [url],                     # 参数2: 下载链接列表
                {"dir": os.path.join(r"/downloads", path)} # 参数3: 下载目录配置
            ]
        }
        
        try:
            # 发送 POST 请求，自动将 payload 转换为 JSON 格式
            response = requests.post(rpc_url, json=payload)
            # 检查响应状态（如果需要可以取消下方注释查看详细日志）
            # print(f"添加任务响应: {response.json()}")
        except Exception as e:
            print(f"请求 Aria2 JSON-RPC 失败: {e}")

def get_1024_url(url):
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}
    response = requests.get(url,headers=headers)
    # response = requests.get(url,headers=headers,proxies=proxies)
    # 获取响应的 html 内容
    html = response.content.decode('utf-8')
    url_list = re.findall(r'ess-data=\'([a-zA-z]+://[^\s]*)\'', html)
    # print('共获得%d个链接'%len(url_list))
    soup = BeautifulSoup(html,'html.parser')
    path = soup.h4.string
    # print('开始导入链接')
    down_path = str(path)
    add_download_rpc(url_list, down_path)
    return "从该网址获得{many}张图片地址， 题名为:{title}".format(many=str(len(url_list)), title=path)