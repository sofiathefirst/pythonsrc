#!/usr/bin/env python

from controlprotocol import *
import rospy
import redis
import time

global cnt
cnt = 0

class fifo(object):
    def __init__(self):
        self.buf = []
    def write(self, data):
        self.buf += data
        return len(data)
    def read(self):
        return self.buf.pop(0)

f = fifo()

def my_handler(message):

	#f = MAVLink_message()

	# create a mavlink instance, which will do IO on file object 'f'
	mav = MAVLink(f)

	#mav.param_set_send(7, 1, "WP_RADIUS", 101)

	# alternatively, produce a MAVLink_param_set object 
	# this can be sent via your own transport if you like
	#m = mav.param_set_encode(7, 1, "WP_RADIUS", 101)

	# get the encoded message as a buffer
	#b = m.get_msgbuf()
	print    message
	inv =message['data']
	#inv = inv.reverse();
	m2 = mav.decode(inv)
	# show what fields it has
	print("Got a message with id %u and fields %s" % (m2.get_msgId(), m2.get_fieldnames()))

	# print out the fields
	print m2,type(m2)


r = redis.StrictRedis(host='192.168.115.36', port=6379, db=0)
p = r.pubsub()

p.subscribe(**{'test': my_handler})

thread = p.run_in_thread(sleep_time=0.001)

while True:
	#r.publish('test', 'kjsadkjldfs')
	time.sleep(1)
	#cnt += 1
	#global cnt
	#if cnt>300000:
		#thread.stop()
		#break
