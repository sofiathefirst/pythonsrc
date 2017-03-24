#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import socket
ip_port=('192.168.106.24',9999)
#买手机
s=socket.socket()
#拨号
s.connect(ip_port)  #链接服务端，如果服务已经存在一个好的连接，那么挂起

welcom_msg = s.recv(200).decode()#获取服务端欢迎消息
print(welcom_msg)
while True:        #基于connect建立的连接来循环发送消息
    
    send_data = 'e啊啊安抚xit'
    
    s.send(bytes(send_data))
    welcom_msg = s.recv(200).decode()#获取服务端欢迎消息
    print(welcom_msg)
    #挂电话
s.close()