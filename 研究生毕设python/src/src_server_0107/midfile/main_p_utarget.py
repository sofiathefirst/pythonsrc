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
#2acn,4cn,5shortest path_len,6jc

def saveP_U_Utarget():
    pkl_file='../data/jul3nets.pkl'
    
    pkl_file = open(pkl_file, 'rb')
    jsnet,janet,_ = pickle.load(pkl_file)
    pkl_file.close()
    
    pkl_file='../data/aug3nets.pkl'
    pkl_file = open(pkl_file, 'rb')
    asnet,_,_ = pickle.load(pkl_file)
    pkl_file.close()
    
    pkl_file='../data/sep3nets.pkl'
    pkl_file = open(pkl_file, 'rb')
    ssnet,_,_ = pickle.load(pkl_file)
    pkl_file.close()
    
    p=[]
    u=[]
    
    
    a7edges = jsnet.edges()
    a8edges = asnet.edges()
    a9edges = ssnet.edges()
    ja78='../data/ja78P_U_Utarget.pkl'
    jas78_9='../data/ja78_9P_U_Utarget.pkl'
    for i in range(5200):
        for j in range(i+1,5200):
            if (i,j) in a7edges:
                p.append([i,j,1])
            else:
                if (i,j) in a8edges:
                    u.append([i,j,1])
                else:
                    u.append([i,j,0])
    output = open(ja78, 'wb')
    pickle.dump([p,u], output)
    output.close()
    
    del p
    del u 
    p=[]
    u=[]
    for i in range(5200):
        for j in range(i+1,5200):
            if (i,j) in a8edges:
                p.append([i,j,1])
            else:
                if (i,j) in a9edges:
                    u.append([i,j,1])
                else:
                    u.append([i,j,0])
    
    output = open(jas78_9, 'wb')
    pickle.dump([p,u], output)
    output.close()

    
    
if __name__ == '__main__':
    file='../data/ja78P_U_Utarget.pkl'
    if not os.path.exists (file):
        saveP_U_Utarget()
    
    

   