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
import gc
from WGraph import *

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

def PersonalRank(G,alpha,root,max_step):
    rank = dict()
    Gnodes = G.nodes()
    rank = {x:0 for x in Gnodes}
    rank[root]=1
    for k in range(max_step):
        tmp = {x:0 for x in Gnodes}
        for i in G.nodes():
            ri=nx.neighbors(G,i)
            for j in ri:
                if j not in tmp:
                    tmp[j]=0
                
                tmp[j]+=alpha*rank[i]/(1.0*len(ri))
                if j==root:
                    tmp[j]+=1-alpha
        rank = tmp
    
    return rank

def PersonalRankw(G,alpha,root,max_step):
    rank = dict()
    rank = {x:0 for x in G.g.nodes()}
    rank[root]=1
    for k in range(max_step):
        tmp = {x:0 for x in G.g.nodes()}
        for i in G.g.nodes():
            ri=nx.neighbors(G.g,i)
            mu=[G.get_edge_weight(i,e) for e in ri ]
            mu=1.*sum(mu)
            for j in ri:
                if j not in tmp:
                    tmp[j]=0

                tmp[j]+=alpha*rank[i]*G.get_edge_weight(i,j)/mu
                
                if j==root:
                    
                    tmp[j]+=1-alpha
        rank = tmp
    
    return rank


def get_sn_wsn_rwr(pkloldf = '../data/jul3nets.pkl',alpha=0.5,max_step=20):
    pkl_old = open(pkloldf, 'rb')
    net,_,_ = pickle.load(pkl_old)
    pkl_old.close()
    
    wg = WGraph(net)
    rwr_sn=dict()
    
    rwr_wsn=dict()
    
    
    for x in net.nodes():
        rwr_sn[x]=PersonalRank(net,alpha,x,max_step)
        rwr_wsn[x]=PersonalRankw(wg,alpha,x,max_step)
    lenn = len(net)
    del net
    for i in range(lenn):
        gc.collect()
        for j in range(i+1,lenn):
            rwr_sn[i][j]=(rwr_sn[i][j]+rwr_sn[j][i])/2.0
            rwr_wsn[i][j]=(rwr_wsn[i][j]+rwr_wsn[j][i])/2.0
            del rwr_sn[j][i],rwr_wsn[j][i]
    
    output = open(pkloldf+str(alpha)+str(max_step)+'snrwr', 'wb')
    pickle.dump([rwr_sn,rwr_wsn], output)
    output.close()

def get_san_wsan_rwr(pkloldf = '../data/jul3nets.pkl',alpha=0.5,max_step=20):
    pkl_old = open(pkloldf, 'rb')
    onet,_,net = pickle.load(pkl_old)
    pkl_old.close()
    
    wg = WGraph(net)
    rwr_sn=dict()
    
    rwr_wsn=dict()
    
    
    for x in net.nodes():
        rwr_sn[x]=PersonalRank(net,alpha,x,max_step)
        rwr_wsn[x]=PersonalRankw(wg,alpha,x,max_step)
    lenn = len(onet)
    del onet
    del net
    for i in range(lenn):
        gc.collect()
        for j in range(i+1,lenn):
            rwr_sn[i][j]=(rwr_sn[i][j]+rwr_sn[j][i])/2.0
            rwr_wsn[i][j]=(rwr_wsn[i][j]+rwr_wsn[j][i])/2.0
            del rwr_sn[j][i],rwr_wsn[j][i]
    
    output = open(pkloldf+str(alpha)+str(max_step)+'sanrwr', 'wb')
    pickle.dump([rwr_sn,rwr_wsn], output)
    output.close()
    
def getwa(wg):
    
    wgnodes  = wg.g.nodes()
    wgnodesindex  = {}
    j=0
    for i in wgnodes:
        wgnodesindex[i]=j
        j+=1

    print wgnodesindex
    lenwg = len(wgnodes)
    a=np.reshape(np.zeros(lenwg*lenwg),(lenwg,lenwg))  
     
    print a
    
    for node in wgnodes:
        nodeneighbors = wg.g.neighbors(node)
        mu=0
        for nn in nodeneighbors:
            mu += wg.get_edge_weight(node,nn)
        for nn in nodeneighbors:
            print a[wgnodesindex[node]][wgnodesindex[nn]],wgnodesindex[node],wgnodesindex[nn]
            a[wgnodesindex[node]][wgnodesindex[nn]]= wg.get_edge_weight(node,nn)*1./mu
    return a
    
def geta(wg):
    
    wgnodes  = wg.nodes()
    wgnodesindex  = {}
    j=0
    for i in wgnodes:
        wgnodesindex[i]=j
        j+=1

    print wgnodesindex
    lenwg = len(wgnodes)
    a=np.reshape(np.zeros(lenwg*lenwg),(lenwg,lenwg))  
     
    print a
    
    for node in wgnodes:
        nodeneighbors = wg.g.neighbors(node)
        
        for nn in nodeneighbors:
            print a[wgnodesindex[node]][wgnodesindex[nn]],wgnodesindex[node],wgnodesindex[nn]
            a[wgnodesindex[node]][wgnodesindex[nn]]= 1./nx.degree(wg, node)
    return a 
   
def get_san_wsan_rwr_matrix(pkloldf = '../data/jul3nets.pkl',alpha=0.5,max_step=10):
    pkl_old = open(pkloldf, 'rb')
    _,_,sanet = pickle.load(pkl_old)
    pkl_old.close()
    
    wg = WGraph(sanet)
   
   
    rwr_san=dict()
    
    rwr_wsan=dict()
    
    a=getwa(wg)
    
    a=np.matrix(a)
    
    p0=np.eye(len(sanet))
    p0 = np.matrix(p0)
    a_reverse = (p0-alpha*a.T).I
    a_reverse=np.matrix(a_reverse)
    
    wrestul =np.matrix( np.eye(len(sanet)))
    for i in range(max_step):
        wrestul=wrestul*a_reverse
        
    
    wrestul=math.pow((1-alpha),max_step)*(wrestul)
    
    
    a=geta(sanet)
    
    a=np.matrix(a)
    
    p0=np.eye(len(sanet))
    p0 = np.matrix(p0)
    a_reverse = (p0-alpha*a.T).I
    a_reverse=np.matrix(a_reverse)
    
    restul =np.matrix( np.eye(len(sanet)))
    for i in range(max_step):
        restul=restul*a_reverse
        
    
    restul=math.pow((1-alpha),max_step)*(restul)
    
    
    output = open(pkloldf+str(alpha)+str(max_step)+'sanrwr', 'wb')
    pickle.dump([restul,wrestul], output)
    output.close()

def linktest2file(pkloldf = '../data/jul3nets.pkl',pklnewf='../data/aug3nets.pkl',alpha=0.5,max_step=20):
    pkl_old = open(pkloldf, 'rb')
    net,_,sanet = pickle.load(pkl_old)
    pkl_old.close()
    pkl_new = open(pklnewf, 'rb')
    newnet,_,newsanet = pickle.load(pkl_new)
    pkl_new.close()
    logging.debug('snets read finished....shot 0 cn roc ')
    
    logging.debug('rw started....')
    rw=dict()
    
    wg = WGraph(net)
    wg.set_edges_weight()
    
    for x in net.nodes():
        rw[x]=PersonalRank(net,alpha,x,max_step)
    rwsan=dict()
    nrwsan=dict()
    netnodes = net.nodes()
    netedges = net.edges()
    newnetedges = newnet.edges()
    lenn = len(netnodes)
    logging.debug('rwsan started....')
    for x in sanet.nodes():
        rwsan[x]=PersonalRank(sanet,alpha,x,max_step)
    logging.debug('rwsan over....') 
    del newnet  
    del sanet
    del newsanet
    for i in range(lenn):
        gc.collect()
        for j in range(i+1,lenn):
            rwsan[i][j]=(rwsan[i][j]+rwsan[j][i])/2.0
            rw[i][j]=(rw[i][j]+rw[j][i])/2.0
            del rw[j][i],rwsan[j][i]
                          
    for x in net.nodes():
        nrwsan[x]=PersonalRankw(wg,alpha,x,max_step)
    logging.debug('nrwsan over....')
    for i in range(lenn):
        gc.collect()
        for j in range(i+1,lenn):
            nrwsan[i][j]=(nrwsan[i][j]+nrwsan[j][i])/2.0
            
            del nrwsan[j][i]
            
    data=[]
    target=[]
    newtarget=[]
      
    for i in range(lenn):
        gc.collect()
        for j in range(i+1,lenn):
            
            label =False
            newlabel = False
            if (i,j) in netedges:
                label =True
            if (i,j) in newnetedges:
                newlabel =True
            
            target.append(label)
            newtarget.append(newlabel) 
            data.append([i,j,rw[i][j],rwsan[i][j],nrwsan[i][j]])
            del rw[i][j],rwsan[i][j],nrwsan[i][j]

    del rw
    del rwsan 
    del nrwsan   
    gc.collect()    
    data=np.array(data)
    target=np.array(target)  
    newtarget=np.array(newtarget) 
    
    data=data[~target]
    target=newtarget[~target]   
         
    fpr, tpr, thresholds = roc_curve(target, data[:,2], pos_label=True)
    logging.info('rw best threshold %0.8f'%getbestthreshold(fpr, tpr, thresholds))
    logging.info('rw thresholds len=%d'%len(thresholds))
    rwroc_auc = auc(fpr,tpr)
    logging.debug(rwroc_auc)
    plt.figure()
    
    plt.plot(fpr, tpr, label='ROC curve (area = %0.8f)' % rwroc_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.savefig('rwroc_auc.jpg')
    
    fpr, tpr, thresholds = roc_curve(target, data[:,3], pos_label=True)
    logging.info('rwsan best threshold %0.8f'%getbestthreshold(fpr, tpr, thresholds))
    logging.info('rwsan thresholds len=%d'%len(thresholds))
    rwsanroc_auc = auc(fpr,tpr)
    
    plt.figure()
    
    plt.plot(fpr, tpr, label='ROC curve (area = %0.8f)' % rwsanroc_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.savefig('rwsanroc_auc.jpg')
    
    fpr, tpr, thresholds = roc_curve(target, data[:,4], pos_label=True)
    logging.info('rwsan best threshold %0.8f'%getbestthreshold(fpr, tpr, thresholds))
    logging.info('rwsan thresholds len=%d'%len(thresholds))
    rwsanroc_auc = auc(fpr,tpr)
    
    plt.figure()
    
    plt.plot(fpr, tpr, label='ROC curve (area = %0.8f)' % rwsanroc_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.savefig('nrwsanroc_auc.jpg')
    logging.debug(pkloldf+'****'+pklnewf+'************')
    logging.debug('rwroc_auc=%0.8f,rwsanroc_auc=%0.8f'%(rwroc_auc,rwsanroc_auc))
    

if __name__ == '__main__':
#     get_sn_wsn_rwr()
    a=float(sys.argv[1])
    m=int(sys.argv[2])
    get_san_wsan_rwr(alpha=a,max_step=m)
    get_sn_wsn_rwr(alpha=a,max_step=m)

#     one2=sys.argv[1]
#     if one2=='1':
#         pklfile='../data/'+sys.argv[2]+'3nets.pkl'
#         cenkey=sys.argv[3]
# 
#         if not os.path.exists(r'log'): 
#             os.mkdir('log')
#         logging.basicConfig(filename='log/'+sys.argv[2]+sys.argv[3], filemode='w',
#                         format='[%(asctime)s] - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s',
#                         level=logging.DEBUG)
#         print pklfile,cenkey
# #         linktest2file(pklfile,cenkey)
#     elif one2=='2':
#         pkloldf='../data/'+sys.argv[2]+'3nets.pkl'
#         pklnewf='../data/'+sys.argv[3]+'3nets.pkl'
#         
#         if not os.path.exists(r'log'): 
#             os.mkdir('log')
#         logging.basicConfig(filename='log/weight'+sys.argv[2]+sys.argv[3],filemode='w',
#                         format='[%(asctime)s] - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s',
#                         level=logging.DEBUG)
#         linktest2file(pkloldf,pklnewf)
#     