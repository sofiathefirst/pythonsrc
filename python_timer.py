#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

import time
def fun_timer():
    print('Hello Timer!')
    print '%.19f'%time.time()

    global timer
    timer = threading.Timer(1, fun_timer)
    timer.start()
    time.sleep(0.5)

timer = threading.Timer(1, fun_timer)
timer.start()

time.sleep(15) # 15秒后停止定时器
timer.cancel()
