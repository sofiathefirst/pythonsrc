#!/usr/bin/env python
import rospy

from std_msgs.msg import Char

import sys, select, termios, tty

 
def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

 
if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)
    
    rospy.init_node('ctibot_key')
    pub = rospy.Publisher('/cmd_vel_key', Char, queue_size=5)

    try:
        while(1):
            key = getKey()
            if key :
                print key ;  
                twist = Char()
                twist.data = ord(key); pub.publish(twist); #twist.linear.z = 0
                if key == 'q':
                    exit()
    except Exception, e:
        print e

    finally:
        pass#twist = Twist()
        #twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        #twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        #pub.publish(twist)

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

