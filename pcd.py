import numpy as np
from math import atan
#fil1 = open('/home/a/Desktop/vsMovedq.txt.cpp')
fil1 = open('4.pcd')
w=1280
h=720
dd=57.295780490442965

def top(line):
#27.798019
	return 0
	toks = line.split();
	x=float(toks[0])
	y=float(toks[1])
	z=float(toks[2])
	print '1top',ind,ind/w,ind%w,line
	print '2top',atan(y/x)*dd,atan(z/x)*dd,

def left(line):
	return 0	
	toks = line.split();
	x=float(toks[0])
	y=float(toks[1])
	z=float(toks[2])
	print '1left',ind,ind/w,ind%w,line
	print '2left',atan(y/x)*dd,atan(z/x)*dd,
def right(line):
#-41.84041
	return 0
	toks = line.split();
	x=float(toks[0])
	y=float(toks[1])
	z=float(toks[2])
	print '1right',ind,ind/w,ind%w,line
	print '2right',atan(y/x)*dd,atan(z/x)*dd,

def down(line):
#-28.35467
	toks = line.split();
	x=float(toks[0])
	y=float(toks[1])
	z=float(toks[2])
	print '1down',ind,ind/w,ind%w,line
	print '2down',atan(y/x)*dd,atan(z/x)*dd,

ind=-1
for line in fil1 :
	ind+=1

	if line.find('nan')>=0:
		continue
	if ind<1280:
		top(line)
	if ind%1280==0:
		left(line)
	if ind%1280==1279:
		right(line)
	if ind>w*(h-1):
		down(line)

		
		




