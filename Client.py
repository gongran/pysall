import socket
import time
print("开始创建socket")
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("结束！")

s.connect(("www.baidu.com",80))
print(s.getsockname())
print(s.getpeername())

time.sleep(10)

#s.send()