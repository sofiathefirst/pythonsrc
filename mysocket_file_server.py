#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import socket,time,SocketServer,struct,os,thread
import subprocess #导入执行命令模块
ip_port=('192.168.106.24',9999) #定义元祖
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM) #定义socket类型
s.bind(ip_port) #绑定需要监听的Ip和端口号，tuple格式
s.listen(1)
#address='192.168.106.24'
 
def conn_thread(connection,address):  
    while True:
        try:
            connection.settimeout(600)
            fileinfo_size=struct.calcsize('128sl') 
            buf = connection.recv(fileinfo_size)
            if buf: #如果不加这个if，第一个文件传输完成后会自动走到下一句
                filename,filesize =struct.unpack('128sl',buf) 
                filename_f = filename.strip('\00')
                filenewname = os.path.join('/home/a/',('new_'+ filename_f))
                print 'file new name is %s, filesize is %s' %(filenewname,filesize)
                recvd_size = 0 #定义接收了的文件大小
                file = open(filenewname,'wb')
                print 'stat receiving...'
                while not recvd_size == filesize:
                    if filesize - recvd_size > 1024:
                        rdata = connection.recv(1024)
                        recvd_size += len(rdata)
                    else:
                        rdata = connection.recv(filesize - recvd_size) 
                        recvd_size = filesize
                    file.write(rdata)
                file.close()
                print 'receive done'
                #connection.close()
        except socket.timeout:
            connection.close()


while True:
    connection,address=s.accept()
    print('Connected by ',address)
    #thread = threading.Thread(target=conn_thread,args=(connection,address)) #使用threading也可以
    #thread.start()
    thread.start_new_thread(conn_thread,(connection,address)) 

s.close()