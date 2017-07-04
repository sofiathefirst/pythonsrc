#!/usr/bin/env python
# -*- encoding: utf-8 -*- 
'''
最长递增子序列，Longest Increasing Subsequence 
d(i) = max{1, d(j)+1},其中j<i,A[j]<=A[i]

用大白话解释就是，想要求d(i)，就把i前面的各个子序列中，最后一个数不大于A[i]的序列长度加1，然后取出最大的长度即为d(i)。
'''
data = [5,3,4,8,6,7]
d = [1]*len(data)
for i in range(1,len(d)):
	for j in range(i):
		if data[j] <= data[i]:
			d[i]=max(1, d[j]+1)

print d
	
