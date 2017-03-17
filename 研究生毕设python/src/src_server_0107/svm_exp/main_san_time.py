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
def getind(i,j):
    return j-i+i*(5199+5200-i)/2-1
u,v,cn,cn_node,cn_edge,aa,aa_node,aa_edge,path,rwr,wrwr,time,ttarget=range(13)


    
if __name__ == '__main__':
    if not os.path.exists(r'log'): 
            os.mkdir('log')
    st=int(sys.argv[1])
    en=int(sys.argv[2])
    num = int(sys.argv[3])
    logging.basicConfig(filename='log/san_789_nogrid_tiny_gamma%d-%d_%d_time.log'%(st,en,num), filemode='w',
                        format='[%(asctime)s] - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s',
                        level=logging.INFO)
    train_test='../data/789train_test_san.pkl'
    timefile = '../data/aug3nets.pkltimef'
    if not os.path.exists (train_test):
        timefileopen = open(timefile)
        timef= pickle.load(timefileopen)
        timefileopen.close()
        
        timef=timef.data
        pklfile='../data/jul3nets.pkl0.9310sanrwr'
        
        pkl_file = open(pklfile, 'rb')
        rwr_sn,rwr_wsn= pickle.load(pkl_file)
        pkl_file.close()
        
    
        
        pklfile='../data/aug3nets.pkl'  
    #     net,anet,sanet=getsnet(datafile)
        pkl_file = open(pklfile, 'rb')
        _,_,net = pickle.load(pkl_file)
        pkl_file.close()
        
        wsan = WGraph(net)
        pntestfile='../data/pntest89.pkl'
        pkl_file = open(pntestfile, 'rb')
        p,n,test = pickle.load(pkl_file)
        pkl_file.close()  
        
        trainvector=[]
        testvector=[]
  
        path_len = nx.all_pairs_shortest_path_length(net)
         
        for [u,v,target] in p:
#             cn,cn_node_weight,cn_edge_weight= get(wg,i,j)
            sancn,_,sancn_node,sancn_edge = wsan.get_cn_weight(u, v)
            sanaa,_,sanaa_node,sanaa_edge = wsan.get_aa_weight(u, v)
        
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
             
            trainvector.append([u,v,sancn,sancn_node,sancn_edge,sanaa,sanaa_node,sanaa_edge,path_len[u][v],rwr,wrwr,timef[getind(u,v)][2],target])
            
        for [u,v,target] in n:
            sancn,_,sancn_node,sancn_edge = wsan.get_cn_weight(u, v)
            sanaa,_,sanaa_node,sanaa_edge = wsan.get_aa_weight(u, v)
            
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
     
         
            trainvector.append([u,v,sancn,sancn_node,sancn_edge,sanaa,sanaa_node,sanaa_edge,path_len[u][v],rwr,wrwr,timef[getind(u,v)][2],target])
        
        for [u,v,target] in test:
            sancn,_,sancn_node,sancn_edge = wsan.get_cn_weight(u, v)
            sanaa,_,sanaa_node,sanaa_edge = wsan.get_aa_weight(u, v)
            
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
     
         
            testvector.append([u,v,sancn,sancn_node,sancn_edge,sanaa,sanaa_node,sanaa_edge,path_len[u][v],rwr,wrwr,timef[getind(u,v)][2],target])
        
        
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
    
    logging.info('****************\n\nuclos = [cn_node,aa_node,path,wrwr,time]')
    uclos = [cn_node,aa_node,path,wrwr,time]
    gammas  = np.linspace(start=st, stop=en, num=num, endpoint=False)
    results={}
    for gamma in gammas:

        clf = SVC(kernel='rbf',gamma = gamma,probability=True)
        clf.fit(trainvector[:,uclos], trainvector[:,-1]) 
        labelclass=clf.classes_  
        logging.info('SVM.SVC* training over****************')
        predicted = clf.predict_proba(testvector[:,uclos])
        
        fpr, tpr, thresholds = roc_curve(testvector[:,-1], predicted[:,1], pos_label=1)
        roc_auc = auc(fpr,tpr)
        logging.info('gamma = %0.8f ,' % gamma)
        logging.info('ROC curve (area = %0.8f)' % roc_auc)
        results[gamma]=roc_auc
    
    
    logging.info("******************\n****************\n")
    logging.info('uclos =  [cn_node,aa_node,path,wrwr,time]')
    logging.info(max(results.values()))
    results.clear()
    logging.info("******************\n****************\n\n")
    
#     u,v,cn,scn_node,cn_edge,aa,aa_node,aa_edge,path,rwr,wrwr,target=range(12)
#*************************************************************************

 
    logging.info('****************\n\nuclos = [cn_node,aa_node,path,wrwr]')
    uclos = [cn_node,aa_node,path,wrwr]
    
    results={}
    for gamma in gammas:

        clf = SVC(kernel='rbf',gamma = gamma,probability=True)
        clf.fit(trainvector[:,uclos], trainvector[:,-1]) 
        labelclass=clf.classes_  
        logging.info('SVM.SVC* training over****************')
        predicted = clf.predict_proba(testvector[:,uclos])
        
        fpr, tpr, thresholds = roc_curve(testvector[:,-1], predicted[:,1], pos_label=1)
        roc_auc = auc(fpr,tpr)
        logging.info('gamma = %0.8f ,' % gamma)
        logging.info('ROC curve (area = %0.8f)' % roc_auc)
        results[gamma]=roc_auc
    
    
    logging.info("******************\n****************\n")
    logging.info('uclos =   [cn_node,aa_node,path,wrwr]')
    logging.info(max(results.values()))
    results.clear()
    logging.info("******************\n****************\n\n")
    
#     u,v,cn,scn_node,cn_edge,aa,aa_node,aa_edge,path,rwr,wrwr,target=range(12)
#*************************************************************************
    logging.info('uclos = [cn_edge,aa_edge,path,wrwr]')
    uclos = [cn_edge,aa_edge,path,wrwr]
   
    for gamma in gammas:

        clf = SVC(kernel='rbf',gamma = gamma,probability=True)
        clf.fit(trainvector[:,uclos], trainvector[:,-1]) 
        labelclass=clf.classes_  
        logging.info('SVM.SVC* training over****************')
        predicted = clf.predict_proba(testvector[:,uclos])
        
        fpr, tpr, thresholds = roc_curve(testvector[:,-1], predicted[:,1], pos_label=1)
        roc_auc = auc(fpr,tpr)
        logging.info('gamma = %0.8f ,' % gamma)
        logging.info('ROC curve (area = %0.8f)' % roc_auc)
        results[gamma]=roc_auc
    
    
    logging.info("******************\n****************\n")
    logging.info('uclos =  [cn_edge,aa_edge,path,wrwr]')
    logging.info(max(results.values()))
    results.clear()
    logging.info("******************\n****************\n\n")
    
    
    
#*************************************************************************

 
    
    
#     u,v,cn,scn_node,cn_edge,aa,aa_node,aa_edge,path,rwr,wrwr,target=range(12)
#*************************************************************************
    logging.info('uclos =  [cn_edge,aa_edge,path,wrwr,time]')
    uclos = [cn_edge,aa_edge,path,wrwr,time]
    
    results ={}
    for gamma in gammas:

        clf = SVC(kernel='rbf',gamma = gamma,probability=True)
        clf.fit(trainvector[:,uclos], trainvector[:,-1]) 
        labelclass=clf.classes_  
        logging.info('SVM.SVC* training over****************')
        predicted = clf.predict_proba(testvector[:,uclos])
        
        fpr, tpr, thresholds = roc_curve(testvector[:,-1], predicted[:,1], pos_label=1)
        roc_auc = auc(fpr,tpr)
        logging.info('gamma = %0.8f ,' % gamma)
        logging.info('ROC curve (area = %0.8f)' % roc_auc)
        results[gamma]= roc_auc
    
    logging.info("******************\n****************\n")
    logging.info('uclos =  [cn_edge,aa_edge,path,wrwr,time]')
    logging.info(max(results.values()))
    results.clear()
    logging.info("******************\n****************\n\n")
    
    
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
    
    fpr, tpr, thresholds = roc_curve(testvector[:,-1],testvector[:,11], pos_label=1)
    roc_auc = auc(fpr,tpr)
    logging.info('time ROC curve (area = %0.8f)' % roc_auc)
   
   
    
    
