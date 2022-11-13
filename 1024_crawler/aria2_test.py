import requests
import json
# TOKEN = 'Aria21281066939'

def add_download_rpc(link):
    jsonreq = json.dumps({'jsonrpc':'2.0', 'id':'qwer', 'method':'aria2.addUri',
                         'params':['token:Aria21281066939', [link]]})
    # jsonreq = {'jsonrpc':'2.0', 'id':'qwer', 'method':'aria2.addUri','params':['token:Aria21281066939', [link]]}
    c = requests.post('http://127.0.0.1:6800/jsonrpc', jsonreq)
    print(c.text)
if __name__ == '__main__':
    url = input()
    add_download_rpc(url)