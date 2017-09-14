#!/usr/bin/env python
import numpy as np 
from math import cos,sin
import matplotlib.pyplot as plt 
import matplotlib.animation as animation 
from geometry_msgs.msg import *

import sys
import rospy
from std_msgs.msg import String
NAME = 'talker_callback'
# First set up the figure, the axis, and the plot element we want to animate 
time_template = 'angle = %.1fdegree'
fig = plt.figure() 
ax = plt.axes(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5)) 
line, = ax.plot([], [], lw=2) 
time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)

myang=0.7
# initialization function: plot the background of each frame 
def init(): 
  line.set_data([], []) 
  return line, 
# animation function. This is called sequentially 
# note: i is framenumber 
def animate(ii): 
	global myang
	x = [0,1.2*cos(myang*3.1415926/180)]#np.linspace(0,1.2*cos(myang*3.1415926/180), 1000) 
	y = [0,1.2*sin(myang*3.1415926/180)]
	line.set_data(x, y) 
	time_text.set_text('angle = %.1f degree'%myang)
	#plt.title('Easy as %f'%myang) 
	return line, time_text
	# call the animator. blit=True means only re-draw the parts that have changed. 

def callback(data):
	global myang
	myang = data.z
	rospy.loginfo( 'angle_min:%f,', myang) 
   
if __name__ == '__main__':
	rospy.init_node(NAME, anonymous=True)
	rospy.Subscriber('/euler', Point, callback)
	thetas=np.linspace(0, 2*3.1416, 1000)
	x=np.zeros(1000)
	y=np.zeros(1000)
	i=0
	for theta in thetas:
		x[i]=cos(theta)
		y[i]=sin(theta)
		i+=1

	plt.plot(x,y)

	anim = animation.FuncAnimation(fig, animate, init_func=init, 
			        frames=200, interval=20, blit=True) 
	#anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264']) 
	plt.show() 
