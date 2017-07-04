#!/usr/bin/env python
# -*- encoding: utf-8 -*- 
'''
平面上有N＊M个格子(n<=m)，每个格子中放着一定数量的苹果。你从左上角的格子开始，每一步只能向下走或是向右走，每次走到一个格子上就把格子里的苹果收集起来，这样下去，你最多能收集到多少个苹果
S[i][j]=A[i][j] + max(S[i-1][j], if i>0 ; S[i][j-1], if j>0)
'''
import numpy as np
data=[[1,2,3],[4,2,1],[4,2,1]]
data = np.array(data)
cost = np.zeros(data.shape)
cost[0][0]=data[0][0]
for i in range(data.shape[0]):
	for j in range(i,data.shape[1]):
		print data[i][j]	
		if i>0:
			cost[i][j]= cost[i-1][j] + data[i][j]
		if j>0:
			if cost[i][j-1] + data[i][j] > cost[i][j]:
				cost[i][j]= cost[i][j-1] + data[i][j]
	for k in range(i+1,data.shape[0]):
		print data[k][i]	
		if i>0:
			cost[k][i]= cost[k][i-1] + data[k][i]
		if k>0:
			if cost[k-1][i] + data[k][i] > cost[k][i]:
				cost[k][i]= cost[k-1][i] + data[k][i]


print cost
	
