from math import fabs
x=100
'''
y=x*x*x+9.2*x*x+16.7*x+4

dy=3*x*x+2*9.2*x+16.7

while fabs(y)>10e-6 :
	x=x-y/dy
	y=x*x*x+9.2*x*x+16.7*x+4

	dy=3*x*x+2*9.2*x+16.7

print x,y,dy


x_n+1=x_n-f(x_n)/df(x_n)
'''

y=x*x-4*x+3

dy=2*x-4

while fabs(y)>10e-6 :
	x=x-y*1./dy
	y=x*x-4*x+3

	dy=2*x-4

print x,y,dy
