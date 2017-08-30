#!/usr/bin/env python
# coding: UTF-8

import time
import sys
import os
import rospy
from geometry_msgs.msg import  Twist
from sensor_msgs.msg import Joy

import copy

process_flag_goal = False
process_flag_cur = False
pid = None
def joycallback( joydata):
    global process_flag_goal
    if (joydata.axes[0] > 0.5 ):
        process_flag_goal = True

    elif(joydata.axes[0] < -0.5 ):
        process_flag_goal = False

def ros_init(self):

    rospy.Subscriber('/joy', Joy, self.joycallback, queue_size=1)

if __name__ == '__main__':
   
    rospy.init_node("control_process", anonymous=True)
    rospy.Subscriber('/joy', Joy, joycallback, queue_size=1)

    while True:

        if process_flag_goal!=process_flag_cur:
            if process_flag_goal==True:
                process_flag_cur = True
                pid = os.fork()
                if pid == 0:
                    print 'in child exec 1111----'
                    
                    #time.sleep(5)
                    os.execlp('/opt/ros/kinetic/lib/rosbag/record','record', '-a', '-o','/home/a/a.bag')
            else:
                print 'in kill 22222----pid=',pid
                #time.sleep(5)
                process_flag_cur = False
                os.system("kill -9 "+str(pid))
                
        
