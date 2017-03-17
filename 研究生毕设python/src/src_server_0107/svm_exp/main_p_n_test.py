'''
Created on 2015-11-4

@author: may
'''
import matplotlib.pyplot as plt
import numpy as np
import sys
import logging
import pickle
from snet import *
import os
import random
import networkx as nx
#2acn,4cn,5shortest path_len,6jc


   

def get_cn_acn(snet,anet,u,v,swicth='sn'):
    cn=nx.common_neighbors(snet, u, v)
    cnlen=0
    for e in cn:
        cnlen+=1
    acn = nx.common_neighbors(anet,u,v)
    acnlen =0
    for e in acn:
        acnlen+=1
    if swicth == 'sn':    
        return cnlen,0
    else:
        return cnlen,acnlen
    

   
def save78train_test(): 
    file='../data/ja78P_U_Utarget.pkl'
    
    pkl_file='../data/jul3nets.pkl'
    
    pkl_file = open(pkl_file, 'rb')
    jsnet,janet,_ = pickle.load(pkl_file)
    pkl_file.close()
    
    
    p_ufile=file
    mth = 9
    swicth='sn'
    pkl_file = open(p_ufile, 'rb')
    p,u = pickle.load(pkl_file)
    pkl_file.close()
    
    
    u_filter_vector=[]
    u_filter=[]
    path_len = nx.all_pairs_shortest_path_length(jsnet)
    for [u,v,target] in u:
        cn,acn = get_cn_acn(jsnet, janet, u, v,swicth)
        
        filterscore  = path_len[u][v]-cn-acn
        u_filter.append(filterscore)
        u_filter_vector.append([u,v,filterscore,target])
  
    th = np.median(u_filter)   
    print th 
    th = mth
    cnt = 0
    for e in u_filter:
        if e<th:
            cnt+=1
    print cnt#u' len
    
    mi = min(u_filter)
    ma = max(u_filter)+1
    
    data = np.array(u_filter_vector)
    x=[e for e in range(mi,ma)]    
    data1 = data[data[:,3]==1]
    y=[data1[data1[:,2]==i].shape[0] for i in x]
    
    z=[data[data[:,2]==i].shape[0] for i in x]
    
    print x
    print y
    print z
    
    
    test = data[data[:,2]<2]
    
    filterdata = data[data[:,2]>=2]
    plen = len(p)
    
    filterdatamin = filterdata[:,2]>2
    filterdatamax = filterdata[:,2]<11
    filterdata = filterdata[filterdatamin]
    filterdata = filterdata[filterdatamax]
    
    
    n = random.sample(filterdata.tolist(),plen)
    
    test = test[:,[0,1,3]]
    n = np.array(n)
    n= n[:,[0,1,3]]
    print test.shape
 
    
    jas78='../data/pntest78.pkl'
    output = open(jas78, 'wb')
    pickle.dump([p,n,test], output)
    output.close()

def save789train_test():
    file='../data/ja78_9P_U_Utarget.pkl'
   
      
    pkl_file='../data/jul3nets.pkl'  
    pkl_file = open(pkl_file, 'rb')
    jsnet,janet,_ = pickle.load(pkl_file)
    pkl_file.close()
    
    pkl_file='../data/aug3nets.pkl'
    pkl_file = open(pkl_file, 'rb')
    asnet,aanet,_ = pickle.load(pkl_file)
    pkl_file.close()
    
  
 
    p_ufile=file
    mth=3
    swicth='san'
    pkl_file = open(p_ufile, 'rb')
    p,u = pickle.load(pkl_file)
    pkl_file.close()
    
    
    u_filter_vector=[]
    u_filter=[]
    path_len = nx.all_pairs_shortest_path_length(asnet)
    for [u,v,target] in u:
        cn,acn = get_cn_acn(asnet, aanet, u, v,swicth)
        
        filterscore  = path_len[u][v]-cn-acn
        u_filter.append(filterscore)
        u_filter_vector.append([u,v,filterscore,target])
  
    th = np.median(u_filter)   
    print th 
    th = mth
    cnt = 0
    for e in u_filter:
        if e<th:
            cnt+=1
    print cnt#u' len
    
    mi = min(u_filter)
    ma = max(u_filter)+1
    
    data = np.array(u_filter_vector)
    x=[e for e in range(mi,ma)]    
    data1 = data[data[:,3]==1]
    y=[data1[data1[:,2]==i].shape[0] for i in x]
    
    z=[data[data[:,2]==i].shape[0] for i in x]
    
    print x
    print y
    print z
    
    
    test = data[data[:,2]<=mth]
    
    filterdata = data[data[:,2]>mth]
    plen = len(p)
    
    filterdatamin = filterdata[:,2]>mth
    filterdatamax = filterdata[:,2]<11
    filterdata = filterdata[filterdatamin]
    filterdata = filterdata[filterdatamax]
    
    
    n = random.sample(filterdata.tolist(),plen)
    
    test = test[:,[0,1,3]]
    n = np.array(n)
    n= n[:,[0,1,3]]
    
    print test.shape,len(p),n.shape
 
    
    jas78='../data/pntest89.pkl'
    output = open(jas78, 'wb')
    pickle.dump([p,n,test], output)
    output.close()
       
if __name__ == '__main__':
    
    file='../data/pntest78.pkl'
    if not os.path.exists (file):
        save78train_test()
    file='../data/pntest89.pkl'
    if not os.path.exists (file):
        save789train_test()
    
    

   