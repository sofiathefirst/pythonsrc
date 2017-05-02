#!/usr/bin/env python
# -*- coding:utf-8 -*-
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
迭代的策略主要体现在如何选择下降方向，以及如何选择步长两个方面。主要有 Gauss-Newton （GN）法和 Levenberg-Marquardt （LM）法两种，它们的细节可以在维基上找到，我们不细说。请理解它们主要在迭代策略上有所不同，但是寻找梯度并迭代则是一样的。
'''

y=x*x-4*x+3

dy=2*x-4

while fabs(y)>10e-6 :
	x=x-y*1./dy
	y=x*x-4*x+3

	dy=2*x-4

print x,y,dy
