import config
import re
import os
import xmlrpc.client
import requests
from bs4 import BeautifulSoup

def add_download_rpc(url_list,path):
    s = xmlrpc.client.ServerProxy(config.RPC_SERVER)
    for url in url_list: 
        s.aria2.addUri(config.RPC_TOKEN,[url],dict(dir=os.path.join(r"/downloads",path)))

def get_1024_url(url):
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}
    response = requests.get(url,headers=headers)
    # response = requests.get(url,headers=headers,proxies=proxies)
    # 获取响应的 html 内容
    html = response.content.decode('utf-8')
    url_list = re.findall('ess-data=\'([a-zA-z]+://[^\s]*)\'', html)
    # print('共获得%d个链接'%len(url_list))
    soup = BeautifulSoup(html,'html.parser')
    path = soup.h4.string
    # print('开始导入链接')
    down_path = str(path)
    add_download_rpc(url_list, down_path)
    return "从该网址获得{many}张图片地址， 题名为:{title}".format(many=str(len(url_list)), title=path)