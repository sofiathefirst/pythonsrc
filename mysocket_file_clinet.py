#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang
import sys
reload(sys)
sys.setdefaultencoding('utf8')
ip_port=('192.168.106.24',9999)
#买手机
import socket,os,struct
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(ip_port)
while True:
    
    filepath = raw_input('Please Enter chars:\r\n')
    if os.path.isfile(filepath):
        fileinfo_size=struct.calcsize('128sl') #定义打包规则
        #定义文件头信息，包含文件名和文件大小
        fhead = struct.pack('128sl',os.path.basename(filepath),os.stat(filepath).st_size)
        s.send(fhead) 
        print 'client filepath: ',filepath
        # with open(filepath,'rb') as fo: 这样发送文件有问题，发送完成后还会发一些东西过去
        fo = open(filepath,'rb')
        while True:
            filedata = fo.read(1024)
            if not filedata:
                break
            s.send(filedata)
        fo.close()
        print 'send over...'
        #s.close()