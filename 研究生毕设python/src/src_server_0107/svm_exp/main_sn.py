'''
Created on 2015-6-19

@author: may
'''
from snet import getfeature
from snet import getsnet
from sklearn import datasets, linear_model
from sklearn.svm import SVC
from sklearn.metrics import roc_curve,auc
import os
import pickle
import logging
import numpy as np
from snet import getgeneratorlen
import networkx as nx
import math
from WGraph import *
from sklearn.preprocessing import StandardScaler
from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.grid_search import GridSearchCV

u,v,cn,cn_node,cn_edge,aa,aa_node,aa_edge,path,rwr,wrwr,ttarget=range(12)
uclos = [cn,aa,path,rwr]

    
if __name__ == '__main__':
    if not os.path.exists(r'log'): 
            os.mkdir('log')

    logging.basicConfig(filename='log/sn_78_nogrid0.9.log', filemode='w',
                        format='[%(asctime)s] - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s',
                        level=logging.INFO)
    train_test='../data/78train_test_sn0.93.pkl'
    if not os.path.exists (train_test):
        
        
        pklfile='../data/jul3nets.pkl0.9310sanrwr'
        
        pkl_file = open(pklfile, 'rb')
        rwr_sn,rwr_wsn= pickle.load(pkl_file)
        pkl_file.close()
        
        pntestfile='../data/pntest78.pkl'
        
        pklfile='../data/jul3nets.pkl'  
    #     net,anet,snet=getsnet(datafile)
        pkl_file = open(pklfile, 'rb')
        _,_,net = pickle.load(pkl_file)
        pkl_file.close()
        
        wsn = WGraph(net)
        pntestfile='../data/pntest78.pkl'
        pkl_file = open(pntestfile, 'rb')
        p,n,test = pickle.load(pkl_file)
        pkl_file.close()  
        
        trainvector=[]
        testvector=[]
  
        path_len = nx.all_pairs_shortest_path_length(net)
        
        for [u,v,target] in p:
#             cn,cn_node_weight,cn_edge_weight= get(wg,i,j)
            sncn,_,sncn_node,sncn_edge = wsn.get_cn_weight(u, v)
            snaa,_,snaa_node,snaa_edge = wsn.get_aa_weight(u, v)
        
            net.remove_edge(u,v)
            
            try:
                path_len[u][v]=len(nx.shortest_path(net,u,v))-1
            except nx.exception.NetworkXNoPath:
                path_len[u][v]=28
            rwr = 0
            wrwr =0
            try:
                rwr = rwr_sn[u][v]
                wrwr = rwr_wsn[u][v]
            except KeyError:
                rwr = rwr_sn[v][u]
                wrwr = rwr_wsn[v][u]
     
            net.add_edge(u,v)
            trainvector.append([u,v,sncn,sncn_node,sncn_edge,snaa,snaa_node,snaa_edge,path_len[u][v],rwr,wrwr,target])
            
        for [u,v,target] in n:
            sncn,_,sncn_node,sncn_edge = wsn.get_cn_weight(u, v)
            snaa,_,snaa_node,snaa_edge = wsn.get_aa_weight(u, v)
            
            path =0
            try:
                path = path_len[u][v]
            except KeyError:
                path =28
            rwr = 0
            wrwr =0
            try:
                rwr = rwr_sn[u][v]
                wrwr = rwr_wsn[u][v]
            except KeyError:
                rwr = rwr_sn[v][u]
                wrwr = rwr_wsn[v][u]
     
         
            trainvector.append([u,v,sncn,sncn_node,sncn_edge,snaa,snaa_node,snaa_edge,path_len[u][v],rwr,wrwr,target])
        
        for [u,v,target] in test:
            sncn,_,sncn_node,sncn_edge = wsn.get_cn_weight(u, v)
            snaa,_,snaa_node,snaa_edge = wsn.get_aa_weight(u, v)
            
            path =0
            try:
                path = path_len[u][v]
            except KeyError:
                path =28
            rwr = 0
            wrwr =0
            try:
                rwr = rwr_sn[u][v]
                wrwr = rwr_wsn[u][v]
            except KeyError:
                rwr = rwr_sn[v][u]
                wrwr = rwr_wsn[v][u]
     
         
            testvector.append([u,v,sncn,sncn_node,sncn_edge,snaa,snaa_node,snaa_edge,path_len[u][v],rwr,wrwr,target])
        
        
        trainvector = np.array(trainvector)
        testvector = np.array(testvector)
#         trainvector=trainvector[trainvector[:,path]<10]
        output = open(train_test, 'wb')
        pickle.dump([trainvector,testvector], output)
        output.close()
    else:
        
        pkl_file = open(train_test, 'rb')
        trainvector,testvector= pickle.load(pkl_file)
        pkl_file.close()
    trainvector = np.array(trainvector)
    testvector = np.array(testvector)

    plen = len(trainvector[trainvector[:,-1]==1])
    nlen = len(trainvector[trainvector[:,-1]==0])
    print 'sn_p,n,t',plen,nlen,len(testvector)    
    logging.info([trainvector.shape,testvector.shape])
    print trainvector[0],testvector[0]
    
#     u,v,cn,scn_node,cn_edge,aa,aa_node,aa_edge,path,rwr,wrwr,target=range(12)
#*************************************************************************

 
    logging.info('****************\n\nuclos = [cn,aa,path,rwr]')
    uclos = [cn,aa,path,rwr]
    gammas  = [e/100. for e in range(25,39)]
    for gamma in gammas:

        clf = SVC(kernel='rbf',gamma = gamma,probability=True)
        clf.fit(trainvector[:,uclos], trainvector[:,-1]) 
        labelclass=clf.classes_  
        logging.info('SVM.SVC* training over****************')
        predicted = clf.predict_proba(testvector[:,uclos])
        
        fpr, tpr, thresholds = roc_curve(testvector[:,-1], predicted[:,1], pos_label=1)
        roc_auc = auc(fpr,tpr)
        logging.info('gamma = %0.2f ,' % gamma)
        logging.info('ROC curve (area = %0.8f)' % roc_auc)
    
#     u,v,cn,scn_node,cn_edge,aa,aa_node,aa_edge,path,rwr,wrwr,target=range(12)
#*************************************************************************
    logging.info('uclos =  [cn_node,aa_node,path,wrwr]')
    uclos = [cn_node,aa_node,path,wrwr]
    gammas  = [e/100. for e in range(55,66)]
    for gamma in gammas:

        clf = SVC(kernel='rbf',gamma = gamma,probability=True)
        clf.fit(trainvector[:,uclos], trainvector[:,-1]) 
        labelclass=clf.classes_  
        logging.info('SVM.SVC* training over****************')
        predicted = clf.predict_proba(testvector[:,uclos])
        
        fpr, tpr, thresholds = roc_curve(testvector[:,-1], predicted[:,1], pos_label=1)
        roc_auc = auc(fpr,tpr)
        logging.info('gamma = %0.2f ,' % gamma)
        logging.info('ROC curve (area = %0.8f)' % roc_auc)
    
  #     u,v,cn,scn_node,cn_edge,aa,aa_node,aa_edge,path,rwr,wrwr,target=range(12)
#*************************************************************************
    logging.info('uclos =  [cn_edge,aa_edge,path,wrwr]')
    uclos =  [cn_edge,aa_edge,path,wrwr]
    gammas  = [e/100. for e in range(5,16)]
    for gamma in gammas:

        clf = SVC(kernel='rbf',gamma = gamma,probability=True)
        clf.fit(trainvector[:,uclos], trainvector[:,-1]) 
        labelclass=clf.classes_  
        logging.info('SVM.SVC* training over****************')
        predicted = clf.predict_proba(testvector[:,uclos])
        
        fpr, tpr, thresholds = roc_curve(testvector[:,-1], predicted[:,1], pos_label=1)
        roc_auc = auc(fpr,tpr)
        logging.info('gamma = %0.2f ,' % gamma)
        logging.info('ROC curve (area = %0.8f)' % roc_auc)
        
      
#     u,v,cn,scn_node,cn_edge,aa,aa_node,aa_edge,path,rwr,wrwr,target=range(12)
#*************************************************************************
    logging.info('uclos =  [cn,cn_node,cn_edge,aa,aa_node,aa_edge,path,wrwr]')
    uclos = [cn,cn_node,cn_edge,aa,aa_node,aa_edge,path,wrwr]
    
    gammas  = [e/10. for e in range(11)]
    for gamma in gammas:

        clf = SVC(kernel='rbf',gamma =gamma,probability=True)
        clf.fit(trainvector[:,uclos], trainvector[:,-1]) 
        labelclass=clf.classes_  
        logging.info('SVM.SVC* training over****************')
        predicted = clf.predict_proba(testvector[:,uclos])
        
        fpr, tpr, thresholds = roc_curve(testvector[:,-1], predicted[:,1], pos_label=1)
        roc_auc = auc(fpr,tpr)
        logging.info('gamma = %0.2f ,' % gamma)
        logging.info('ROC curve (area = %0.8f)' % roc_auc)
    
    #     u,v,cn,scn_node,cn_edge,aa,aa_node,aa_edge,path,rwr,wrwr,target=range(12)
    fpr, tpr, thresholds = roc_curve(testvector[:,-1],testvector[:,2],  pos_label=1)
    roc_auc = auc(fpr,tpr)
    logging.info('cn ROC curve (area = %0.8f)' % roc_auc)
    
    fpr, tpr, thresholds = roc_curve(testvector[:,-1],testvector[:,3],  pos_label=1)
    roc_auc = auc(fpr,tpr)
    logging.info('cn_node,ROC curve (area = %0.8f)' % roc_auc)
    
    fpr, tpr, thresholds = roc_curve(testvector[:,-1],testvector[:,4],  pos_label=1)
    roc_auc = auc(fpr,tpr)
    logging.info('cn_edge,ROC curve (area = %0.8f)' % roc_auc)
    
    fpr, tpr, thresholds = roc_curve(testvector[:,-1],testvector[:,5], pos_label=1)
    roc_auc = auc(fpr,tpr)
    logging.info('aa,ROC curve (area = %0.8f)' % roc_auc)
    
    fpr, tpr, thresholds = roc_curve(testvector[:,-1],testvector[:,6],  pos_label=1)
    roc_auc = auc(fpr,tpr)
    logging.info('aa_node,ROC curve (area = %0.8f)' % roc_auc)
    
    fpr, tpr, thresholds = roc_curve(testvector[:,-1],testvector[:,7],  pos_label=1)
    roc_auc = auc(fpr,tpr)
    logging.info('aa_edge ROC curve (area = %0.8f)' % roc_auc)
    
    fpr, tpr, thresholds = roc_curve(testvector[:,-1],testvector[:,8],  pos_label=1)
    roc_auc = auc(fpr,tpr)
    logging.info('path ROC curve (area = %0.8f)' % roc_auc)
    
    fpr, tpr, thresholds = roc_curve(testvector[:,-1],testvector[:,9], pos_label=1)
    roc_auc = auc(fpr,tpr)
    logging.info('rwr ROC curve (area = %0.8f)' % roc_auc)
    
    fpr, tpr, thresholds = roc_curve(testvector[:,-1],testvector[:,10], pos_label=1)
    roc_auc = auc(fpr,tpr)
    logging.info('wrwr ROC curve (area = %0.8f)' % roc_auc)
   
   
    
    
