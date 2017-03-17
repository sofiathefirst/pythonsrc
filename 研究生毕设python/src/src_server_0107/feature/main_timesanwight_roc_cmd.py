'''
Created on 2015-6-19

@author: may
'''


import os
import pickle
from sklearn import cross_validation
from sklearn import svm
import networkx as nx
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_curve,auc
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets.base import Bunch
import logging
import sys

def gettimegeneratorlen(u,v,net,sanet,newnet,newsanet):
    return nx.degree(newnet, u)-nx.degree(net,u)+nx.degree(newnet, v)-nx.degree(net,v),\
        nx.degree(newsanet, u)-nx.degree(sanet,u)+nx.degree(newsanet, v)-nx.degree(sanet,v)

        
#     timeuf=0
#     timevf=0
#     timeufsan=0
#     timevfsan=0
#     
#     timeuf=nx.degree(net, u)
#     timeuf=(nx.degree(newnet, u)-timeuf)*1.0/timeuf
#     
#     timevf=nx.degree(net, v)
#     timevf=(nx.degree(newnet, u)-timevf)*1.0/timevf
#     
#     timeufsan=nx.degree(sanet, u)
#     timeufsan=(nx.degree(newsanet, u)-timeufsan)*1.0/timeufsan
#     timevfsan=nx.degree(sanet,v)
#     timevfsan =(nx.degree(newsanet,v)-timevfsan)*1.0/timevfsan
#     
#     return timeuf+timevf,timeufsan+timevfsan

 
  
def getind(i,j):
    return j-i+i*(5199+5200-i)/2-1

def linktest3file(pkloldf = '../data/jul3nets.pkl',pklnewf='../data/aug3nets.pkl',pkltest='../data/sep3nets.pkl'):
    pkl_old = open(pkloldf, 'rb')
    net,_,sanet = pickle.load(pkl_old)
    pkl_old.close()
    pkl_new = open(pklnewf, 'rb')
    newnet,_,newsanet = pickle.load(pkl_new)
    pkl_new.close()
    pkl_test = open(pkltest, 'rb')
    testnet,_,_ = pickle.load(pkl_test)
    pkl_new.close()
    logging.debug('snets read finished....shot 0 timef roc ')
    
    data=[]
    target=[]
    newtarget=[]
    
#     up triangular
    if not os.path.exists(pklnewf+'timef'):
        
    #     timef,timefweight,timefsan,timefsanweight
        netnodes = net.nodes()
        netedges = newnet.edges()
        newnetedges = testnet.edges()
        lenn = len(netnodes)
        for i in range(lenn):
            for j in range(i+1,lenn):

                timef,timefsan = gettimegeneratorlen(i,j,net,sanet,newnet,newsanet)
                
                label =False
                newlabel = False
                if (i,j) in netedges:
                    label =True
                if (i,j) in newnetedges:
                    newlabel =True
                
                target.append(label)
                newtarget.append(newlabel)
                          
                data.append([i,j,timef,timefsan])
        data=np.array(data)
        target=np.array(target)
        
        output = open(pklnewf+'timef', 'wb')
        pickle.dump(Bunch(data=data,target=target), output)
        output.close()
    else:
        output = open(pklnewf+'timef', 'rb')
        dtarget=pickle.load( output)
        output.close()
        data=np.array(dtarget.data)
        target=np.array(dtarget.target)

        newnetedges = testnet.edges()
        lenn = len(net)
         
        for i in range(lenn):
            for j in range(i+1,lenn):
                newlabel = False
                
                if (i,j) in newnetedges:
                    newlabel =True
                newtarget.append(newlabel)
            
    newtarget=np.array(newtarget) 
    
    data=data[~target]
    target=newtarget[~target]   
         
    fpr, tpr, thresholds = roc_curve(target, data[:,2], pos_label=True)
    timefroc_auc = auc(fpr,tpr)
    
    fpr, tpr, thresholds = roc_curve(target, data[:,3], pos_label=True)
    timefsanroc_auc = auc(fpr,tpr)
       
    logging.debug(pkloldf+'****'+pklnewf+'************')
    logging.debug('timefroc_auc=%0.8f,timefsanroc_auc=%0.8f'%(timefroc_auc,timefsanroc_auc))
    

if __name__ == '__main__':
       
    if not os.path.exists(r'log'): 
        os.mkdir('log')
    logging.basicConfig(filename='log/timef.log',filemode='w',
                    format='[%(asctime)s] - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
    linktest3file()
    