'''
Created on 2015-7-9

@author: may
'''
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.datasets.base import Bunch
import logging
import networkx as nx

i,j,acnlen,ajc,cnlen,shortest,jc,clusteri,clusterj,betwi,betwj,label=range(12)

def getbestthreshold(fpr,tpr,thresholds):
    logging.info('tpr,fpr,a*************')
    logging.info(str(tpr))
    logging.info(str(fpr))
    
    a=tpr/10-fpr*10
    logging.info(str(a))
    logging.info('tpr,fpr,a*************')
    acopy=a.copy()
    acopy.sort()
    ths_inds=np.where(a>acopy[-5])
    thresholds=np.take(thresholds, ths_inds) 
    return thresholds[0]

def getsnet(datafile):
    snet = nx.Graph()
    anet = nx.Graph()
    sanet = nx.Graph()
    filesns = open(datafile)
    for line in filesns:
        ids = line.split()
        snode = int(ids[0])
        snum = int(ids[1])
        anum = int(ids[2])
        
        for i in xrange(3,3+snum):
            snet.add_edge(snode,int(ids[i]))   
            sanet.add_edge(snode,int(ids[i]))           
        for i in xrange(3+snum,3+snum+anum):
            a = int(ids[i])
            anet.add_edge(snode,a)   
            sanet.add_edge(snode,a)   
    filesns.close()   
    return snet,anet,sanet

def load_net_train(featurefile,usecols=None):
    data= np.loadtxt(featurefile,usecols=usecols)
    logging.info(data.shape)
    
    target = np.array([bool(e) for e in data[:,-1]])
    data = np.delete(data,-1,1)
    logging.info(data.shape)
    return Bunch(data=data, target=target)

def load_net2hop_test(featurefile,usecols=None):
    data= np.loadtxt(featurefile,usecols=usecols)
    a_bool = data[:,shortest]==2
    b_bool = data[:,-1]==0
    logging.info( data.shape)
    data = data[a_bool&b_bool]
    logging.info(data.shape)

    data = np.delete(data,-1,1)
    logging.info(data.shape)
    return data

def load_netallhop_test(featurefile,usecols=None):
    snet=load_net_train(featurefile,usecols)
    return snet.data[~snet.target]

def load_net_train2(datafiel1,featurefile1,datafiel2,usecols=None):
    
    net1,anet,sanet=getsnet(datafiel1)
    del anet,sanet
    net2,anet,sanet=getsnet(datafiel2)
    del anet,sanet
    
    dela = list(set(net2.edges()).difference(set(net1.edges())))
    logging.info( len(dela))
    
    snet=load_net_train(featurefile1,usecols)
    train1class = snet.data[snet.target]
    test = snet.data[~snet.target]
    target = np.array([False]*test.shape[0])
    for i in range(test.shape[0]):
        if (test[i,0],test[i,1]) in dela:
            target[i]=True
    logging.info( target[target].shape)
    return train1class,test,target

def load_net2hop_test2(filename,filename2):
    data= np.loadtxt(filename)
    a_bool = data[:,shortest]==2
    b_bool = data[:,-1]==0
    logging.info( data.shape)
    data = data[a_bool&b_bool]
    logging.info(data.shape)

    data = np.delete(data,-1,1)
    logging.info(data.shape)
    return data
    
if __name__ == '__main__':
    logging.basicConfig(filename='log/weibo.log', filemode='w',
                        format='[%(asctime)s] - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s',
                        level=logging.INFO)
    load_net_train2('../data/AUG4.txt','../data/aug4.csv','../data/SEP4.txt')
    