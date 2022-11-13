import xmlrpc
import xmlrpc.client
s = xmlrpc.client.ServerProxy('http://127.0.0.1:6800/rpc')

s.aria2.addUri('token:Aria21281066939',['http://example.org/file'],dict(dir="/tmp"))