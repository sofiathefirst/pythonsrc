#!/usr/bin/env python
# -*- encoding: utf-8 -*- 
'''
如果我们有面值为1元、3元和5元的硬币若干枚，如何用最少的硬币凑够11元
d(3)=min{d(3-1)+1, d(3-3)+1}。d[i]=min(d[i-1]+1, d[i-3]+1,d[i-5]+1)

'''
d = [0]*12
d[1]=1
d[2]=2
d[3]=1
d[4]=2
d[5]=1
for i in range(6,len(d)):
	d[i]=min(d[i-1]+1, d[i-3]+1,d[i-5]+1)

print d
	
