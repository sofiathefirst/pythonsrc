from sklearn import cross_validation
c = []

out_train = open(r'smalldata/small_user_sns.txt','r')
'''
Created on 2015-4-14

@author: may
'''
# -*- coding: cp936 -*-
import math
import threading
import numpy as np
import random
from fileinput import filename
from scipy.constants.codata import precision
logfile = open('logfile_all.txt','w+')
def heldout(datafile,M,k,seed):
    test = []
    train = []
    random.seed(seed)
    filesns = open(datafile)
    for line in filesns:
        ids = line.split('\t')
        u = int(ids[0])
        v = int(ids[1])
        if random.randint(0,M)==k:
            test.append((u,v))
        else:
            train.append((u,v,1))
            
    test=list(set(test))
    train=list(set(train))
    return train,test

def getGGT(subtrain,G,lock):
#     //train,test=heldout(filename,10,3,339)
    for ids in subtrain:      
        u = ids[0]
        v = ids[1]
        lock.acquire()
        if not G.has_key(u):
            G[u]=set()
        G[u].add(v)
        lock.release()
      
    for u, followees in G.items():
        G[u]=list(G[u]) 
    return G 

def randomnegativesample(followees,G,ratio=1,mul=2,N=3):
    ret = dict()
    for i in followees:
        ret[i]=1
    n=0
    negsnum = ratio * len(followees)
    negs=set() 
    while N>0:
        for ukey in followees:
            if G.has_key(ukey):
                neg_pool=G[ukey]
                for i in range(mul):
                    neg = neg_pool[random.randint(0,len(neg_pool)-1)]
                    if neg not in followees:
                        ret[neg]=0
                        n +=1
                        if n>negsnum:
                            return ret
        N=N-1
    return ret
def initmodel(G,F):
    p = dict()
    for u, followees in G.items():
        if not p.has_key(u):
            p[u]=[random.random()/math.sqrt(F) for x in range(F)]
        for followee in followees:
            if not p.has_key(followee):    
                p[followee]=[random.random()/math.sqrt(F) for x in range(F)]
    return p

def predict(u,followee,P,F):
    return sum(P[u][f]*P[followee][f] for f in range(0,F))
 
def recommend(u,P,F,followees,N):
    rank = dict()
     
    
    for followee, plist in P.items():
        if followee in followees:
            continue
        if followee not in rank:
            rank[followee] = sum(P[u][f]*P[followee][f] for f in range(0,F))
    logfile.write('\n***********u,*************\n'+str(u)) 
    logfile.write('\n***********followees*************\n'+str(followees))  
   
    
    topn=sorted(rank.items(),key = lambda e:e[1],reverse = True)[0:N]
    logfile.write('\n***********rank*************\n'+str(topn))
    return topn
  
def lfm(G,F,N,alpha,lam,ratio,mul,negn):
    P = initmodel(G,F)
    for step in range(N):
        print step
        for u, followees in G.items():
            samples = randomnegativesample(followees,G, ratio, mul,negn)
            print len(samples),len(followees)
            for followee, rui in samples.items():
                eui = rui-predict(u,followee,P,F)
                for f in range(F):
                    P[u][f] += alpha * (eui *P[followee][f] - lam * P[u][f])
                    P[followee][f] += alpha * (eui *P[u][f] - lam * P[followee][f])
        alpha *= 0.9
    return P   

def evaluation(predic,lable,preall):
    hit = 0
    
    recallall = 0
    for u,followees in lable.items():
        recallall+=len(followees)
        if predic.has_key(u):
            prefollowees=predic[u]
            for e in prefollowees:
                if e in followees:
                    hit+=1
    
    return hit/(preall*1.0),hit/(recallall*1.0)     
 
def test(ratio, mul,negn,N):
    filename = 'smalldata/small_user_sns.txt'
    train,test=heldout(filename,10,3,339)
    G,GT=getGGT(train)
    del train
    testG,GT = getGGT(test)
    del GT   
    del test
    P=lfm(G,100,N,0.02,0.01,ratio, mul,negn)
    predic=dict()
    preall=0
    for u in P.keys():
        predic[u]=set()
        rank=[]
        
        if G.has_key(u):
            rank=recommend(u, P,100,G[u],10)
        else:
            rank=recommend(u, P,100,[],10)
        preall+=len(rank)    
        for e in rank:
            predic[u].add(e[0])
    
    precision,recall = evaluation(predic,testG,preall)
    logfile.write( '\nration,N,pre,recall\n')
    
    logfile.write( str(ratio)+','+str(N)+','+str(precision)+','+str(recall))
    logfile.close()
    
if __name__ == '__main__':
    test(2,5,5,10)
