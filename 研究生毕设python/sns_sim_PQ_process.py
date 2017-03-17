'''
Created on 2015-5-14

@author: may
'''
# -*- coding: cp936 -*-
import math
import random
import threading
import multiprocessing
import time
import pickle
logfile = open('logfile_all-process.txt','w+')
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
    filesns.close()
    return train,test

def getGGT(train):
#     //train,test=heldout(filename,10,3,339)
    G={} #out 
    GT={}#in
    for ids in train:      
        u = ids[0]
        v = ids[1]
        if not G.has_key(u):
            G[u]=set()
            
#         if not GT.has_key(v):
#             GT[v]=set()
        G[u].add(v)
#         GT[v].add(u)
        
    for u, followees in G.items():
        G[u]=list(G[u])
#     trainoldlen=len(train)
#     negativsample(100)
#     trainnewlen=len(train)
#     print trainoldlen,trainnewlen,len(test)     
    return G,GT  

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
    q = dict()
    for u, followees in G.items():
        if not p.has_key(u):
            p[u]=[random.random()/math.sqrt(F) for x in range(F)]
            q[u]=[random.random()/math.sqrt(F) for x in range(F)]
        for followee in followees:
            if not p.has_key(followee):    
                p[followee]=[random.random()/math.sqrt(F) for x in range(F)]
                q[followee]=[random.random()/math.sqrt(F) for x in range(F)]
    return p,q

def predict(u,followee,P,Q,F):
    return sum(P[u][f]*Q[followee][f] for f in range(0,F))
 
def recommend(u,P,Q,F,followees,N):
    rank = dict()
    followees.append(u) 
    
    for followee in P.keys():
        if followee in followees:
            continue 
        rank[followee] = sum(P[u][f]*Q[followee][f] for f in range(0,F))
    
    topn=sorted(rank.items(),key = lambda e:e[1],reverse = True)[0:N]
#     global logfile
#    
#     logfile.write('\n***********u,*************\n'+str(u)) 
#     logfile.write('\n***********followees*************\n'+str(followees))  
#    
#     logfile.write('\n***********rank*************\n'+str(topn))

    return topn
  
def lfm(G,F,N,alpha,lam,ratio,mul,negn):
    P,Q = initmodel(G,F)
    for step in range(N):
        print step
        for u, followees in G.items():
            samples = randomnegativesample(followees,G, ratio, mul,negn)
#             print len(samples),len(followees)
            for followee, rui in samples.items():
                eui = rui-predict(u,followee,P,Q,F)
                for f in range(F):
                    P[u][f] += alpha * (eui *Q[followee][f] - lam * P[u][f])
                    Q[followee][f] += alpha * (eui *P[u][f] - lam * Q[followee][f])
        alpha *= 0.9
    output = open('PQdata_thread.pkl', 'wb')

    # Pickle dictionary using protocol 0.
    pickle.dump([P,Q], output)
    output.close()
    return P,Q   

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
   
    print preall,recallall
    return hit/(preall*1.0),hit/(recallall*1.0)   
  
def multithread(users,numthread,G,P,Q,testG,ratio,N):
    pool = multiprocessing.Pool(processes=numthread)
    result = []
    subusers=[]
    threadpool=[]
    global preall
    
    for i in range(numthread):
        subusers.append([])
    i=0    
    for u in users:
        if P.has_key(u):
            preall+=1
            subusers[i].append(u)
            i+=1
            if i==numthread:
                i=0
     
    for i in range(numthread):
        result.append(pool.apply_async(run, (subusers[i],G,P,Q,testG)))
#         threadpool.append(threading.Thread(target=run,args=(subusers[i],predic,G,P,Q)))
#         threadpool[i].start()
    pool.close()
    pool.join()
    predic=dict()
    preall=0
    for dic in result:
        getdic=dic.get()
        preall+=len(getdic)
        for k,v in getdic.items():
            
            logfile.write('\n***********u,*************\n'+str(k))     
            logfile.write('\n***********rank*************\n'+str(v))
            predic[k]=v
    
    logfile.write("######################predic\n")
    logfile.write(str(predic))
    return predic,preall      
    
def run(subusers,G,P,Q,testG):
    predic = dict()
    for u in subusers:
        predic[u]=set()
        rank=[]
        
        if G.has_key(u):
            rank=recommend(u, P,Q,100,G[u],len(testG[u]))
        else:
            rank=recommend(u, P,Q,100,[],len(testG[u]))
#         global preall
#         con.acquire()    
#         preall+=len(rank)  
#         print preall
#         con.release()  
       
        for e in rank:
            predic[u].add(e[0])
    return predic
                 
def test(ratio, mul,negn,N):
    filename = 'smalldata/user_sns.txt'
    train,test=heldout(filename,10,3,339)
    G,GT=getGGT(train)
    del train
    testG,GT = getGGT(test)
    del GT   
    del test
#     P,Q=lfm(G,100,N,0.02,0.01,ratio, mul,negn)
    PQ=open('PQdata_thread.pkl','rb')
    [P,Q]=pickle.load(PQ)
    PQ.close()
    global preall 
    preall=0
    start = time.time()
    
    reslut,preall=multithread(testG.keys(),10,G,P,Q,testG,ratio,N)
    del P 
    del Q
    del G
    precision,recall = evaluation(reslut,testG,preall)
    logfile.write( '\nration,N,pre,recall\n')
     
    logfile.write( str(ratio)+','+str(N)+','+str(precision)+','+str(recall))
    logfile.write( '\ncost time:\n'+str(time.time()-start))
    logfile.write('\nration,N,pre,recall\n')
     
    logfile.write( str(ratio)+','+str(N)+','+str(precision)+','+str(recall))
    logfile.write( '\ncost time:\n'+str(time.time()-start))
    logfile.close()
 
start =0 

if __name__ == '__main__':
    test(2,5,5,2)#last number is iterater num
    

        