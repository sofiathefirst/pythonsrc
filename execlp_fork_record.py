#!/usr/bin/python
# coding: UTF-8

import os
import time


cid = 0

def child():
    print('hello from child', os.getpid())
    os._exit(0)
def parent():
    pid = os.fork()
    if pid == 0:
        os.execlp('/opt/ros/kinetic/lib/rosbag/record','record', '-a', '-o','/home/q/a.bag')
    else:
        time.sleep(5)
        os.system("kill -2 "+str(cid))
        print('hello from parent', os.getpid(), pid)
parent()