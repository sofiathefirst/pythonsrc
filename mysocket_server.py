#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import socket
import subprocess #导入执行命令模块
ip_port=('192.168.106.24',9999) #定义元祖
#买手机
s=socket.socket()  #绑定协议，生成套接字
s.bind(ip_port)    #绑定ip+协议+端口：用来唯一标识一个进程，ip_port必须是元组格式
s.listen(5)        #定义最大可以挂起链接数
#等待电话
while True:  #用来重复接收新的链接
    conn,addr=s.accept()   #接收客户端胡的接请求，返回conn（相当于一个特定胡链接），addr是客户端ip+port
    conn.sendall('abc是啊de')
    #收消息
    while True: #用来基于一个链接重复收发消息
            try: #捕捉客户端异常关闭（ctrl+c）
                recv_data=conn.recv(1024).decode() #收消息，阻塞
                print recv_data
                if len(recv_data) == 0:break #客户端如果退出，服务端将收到空消息，退出
                conn.send('啊啊阿斯蒂芬杀到了疯狂')
            except Exception:
                break
    #挂电话
    conn.close()