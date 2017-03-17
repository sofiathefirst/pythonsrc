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
from WGraph import *

import networkx as nx
import matplotlib.pyplot as plt
import gc

from sklearn.metrics import f1_score
from sklearn.metrics import precision_recall_fscore_support

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
def linktest1file(pklfile='../data/jul3nets.pkl',fff=WGraph.get_cn_weight):
    
    pkl_file = open(pklfile, 'rb')
    net,_,sanet = pickle.load(pkl_file)
    pkl_file.close()
    logging.debug('snets read finished....shot 0 cn roc ')
    


    gc.collect()
    
    wg = WGraph(net)
    
    wsang = WGraph(sanet)

      
    data=[]
    target=[]
    
    netnodes = net.nodes()
    netedges = net.edges()
    lenn = len(net)
     
    for i in range(lenn):
        for j in range(i+1,lenn):
                
#             cn,cn_node_weight= wg.fff(i,j)
#             cn_edge_weight= wg.ffg(i,j)
            cn,cn_node_weight,cn_node_weight2,cn_edge_weight= fff(wg,i,j)
            sancn,sancn_node,sancn_node2,sancn_edge = fff(wsang,i,j)
#             cn_edge_weight= wg.ffg(i,j)           
            label =False
            if (i,j) in netedges:
                label =True
            target.append(label)
            data.append([i,j,cn,sancn,cn_node_weight,sancn_node,cn_node_weight2,sancn_node2,cn_edge_weight,sancn_edge])
    
    del net
    del sanet
    gc.collect()        
    data=np.array(data)  
         
    fpr, tpr, thresholds = roc_curve(target, data[:,2], pos_label=True)
    cnroc_auc = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        f1 = f1_score(target, data[:,2]>=myth, pos_label=True)
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,2]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        logging.info('cn myth%0.8f'%myth)
        logging.info('cn f1%0.8f'%f1)
        logging.info('******************\n\n')
    
    fpr, tpr, thresholds = roc_curve(target, data[:,4], pos_label=True)
    cn_node_weight = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        f1 = f1_score(target, data[:,4]>=myth, pos_label=True)
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,4]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        logging.info('cn_node_weight myth%0.8f'%myth)
        logging.info('cn_node_weight f1%0.8f'%f1)
        logging.info('******************\n\n')
        
    fpr, tpr, thresholds = roc_curve(target, data[:,6], pos_label=True)
    cn_node_weight2 = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        f1 = f1_score(target, data[:,6]>=myth, pos_label=True)
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,6]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        logging.info('cn_node_weight2 myth%0.8f'%myth)
        logging.info('cn_node_weight2 f1%0.8f'%f1)
        logging.info('******************\n\n')
        
    fpr, tpr, thresholds = roc_curve(target, data[:,8], pos_label=True)
    cn_edge_weight = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        f1 = f1_score(target, data[:,8]>=myth, pos_label=True)
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,8]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        logging.info('cn_edge_weight myth%0.8f'%myth)
        logging.info('cn_edge_weight f1%0.8f'%f1)
        logging.info('******************\n\n')
        
    fpr, tpr, thresholds = roc_curve(target, data[:,3], pos_label=True)
    sancnroc_auc = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,3]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        f1 = f1_score(target, data[:,3]>=myth, pos_label=True)
        logging.info('sancn myth%0.8f'%myth)
        logging.info('sancn f1%0.8f'%f1)
        logging.info('******************\n\n')
   
    
    fpr, tpr, thresholds = roc_curve(target, data[:,5], pos_label=True)
    sancn_node_weight = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,5]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        f1 = f1_score(target, data[:,5]>=myth, pos_label=True)
        logging.info('sancn_node_weight myth%0.8f'%myth)
        logging.info('sancn_node_weight f1%0.8f'%f1)
        logging.info('******************\n\n')
    
   
    
    fpr, tpr, thresholds = roc_curve(target, data[:,7], pos_label=True)
    sancn_node_weight2 = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,7]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        f1 = f1_score(target, data[:,7]>=myth, pos_label=True)
        logging.info('sancn_node_weight2 myth%0.8f'%myth)
        logging.info('cn_node_weight2 f1%0.8f'%f1)
        logging.info('******************\n\n')
    
   
    
    fpr, tpr, thresholds = roc_curve(target, data[:,9], pos_label=True)
    sancn_edge_weight = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        f1 = f1_score(target, data[:,9]>=myth, pos_label=True)
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,9]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        logging.info('sancn_edge_weight myth%0.8f'%myth)
        logging.info('sancn_edge_weight f1%0.8f'%f1)
        logging.info('******************\n\n')
   
    logging.debug('cnroc_auc=%0.8f,cn_node_weight=%0.8f,cn_node_weight2=%0.8f,cn_edge_weight=%0.8f,'%(cnroc_auc,cn_node_weight,cn_node_weight2,cn_edge_weight))
    logging.debug('cnroc_auc=%0.8f,cn_node_weight=%0.8f,cn_node_weight2=%0.8f,cn_edge_weight=%0.8f,'%(sancnroc_auc,sancn_node_weight,sancn_node_weight2,sancn_edge_weight))

   
   
     
   
        
        
    
     
def linktest2file(pkloldf = '../data/jul3nets.pkl',pklnewf='../data/aug3nets.pkl',fff=WGraph.get_cn_weight):
    pkl_old = open(pkloldf, 'rb')
    net,_,sanet = pickle.load(pkl_old)
    pkl_old.close()
    pkl_new = open(pklnewf, 'rb')
    newnet,_,_ = pickle.load(pkl_new)
    pkl_new.close()
    logging.debug('snets read finished....shot 0 cn roc ')
 
    gc.collect()
    wg = WGraph(net)
    
    wsang = WGraph(sanet)

     
    data=[]
    target=[]
    newtarget=[]
    netnodes = net.nodes()
    netedges = net.edges()
    newnetedges = newnet.edges()
    lenn = len(netnodes)
      
    for i in range(lenn):
        for j in range(i+1,lenn):
            cn,cn_node_weight,cn_node_weight2,cn_edge_weight= fff(wg,i,j)
            sancn,sancn_node,sancn_node2,sancn_edge = fff(wsang,i,j)
#             cn_edge_weight= wg.ffg(i,j)
            label =False
            newlabel = False
            if (i,j) in netedges:
                label =True
            if (i,j) in newnetedges:
                newlabel =True
             
            target.append(label)
            newtarget.append(newlabel)
            data.append([i,j,cn,sancn,cn_node_weight,sancn_node,cn_node_weight2,sancn_node2,cn_edge_weight,sancn_edge])
#             data.append([i,j,cn,cn_node_weight,cn_node_weight2,cn_edge_weight])

     
    del net
    del newnet
    gc.collect()        
    data=np.array(data)
    target=np.array(target)         
    newtarget=np.array(newtarget) 
    data=data[~target]
    target=newtarget[~target]  
    
    fpr, tpr, thresholds = roc_curve(target, data[:,2], pos_label=True)
    cnroc_auc = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        f1 = f1_score(target, data[:,2]>=myth, pos_label=True)
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,2]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        logging.info('cn myth%0.8f'%myth)
        logging.info('cn f1%0.8f'%f1)
        logging.info('******************\n\n')
    
    fpr, tpr, thresholds = roc_curve(target, data[:,4], pos_label=True)
    cn_node_weight = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        f1 = f1_score(target, data[:,4]>=myth, pos_label=True)
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,4]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        logging.info('cn_node_weight myth%0.8f'%myth)
        logging.info('cn_node_weight f1%0.8f'%f1)
        logging.info('******************\n\n')
        
    fpr, tpr, thresholds = roc_curve(target, data[:,6], pos_label=True)
    cn_node_weight2 = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        f1 = f1_score(target, data[:,6]>=myth, pos_label=True)
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,6]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        logging.info('cn_node_weight2 myth%0.8f'%myth)
        logging.info('cn_node_weight2 f1%0.8f'%f1)
        logging.info('******************\n\n')
        
    fpr, tpr, thresholds = roc_curve(target, data[:,8], pos_label=True)
    cn_edge_weight = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        f1 = f1_score(target, data[:,8]>=myth, pos_label=True)
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,8]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        logging.info('cn_edge_weight myth%0.8f'%myth)
        logging.info('cn_edge_weight f1%0.8f'%f1)
        logging.info('******************\n\n')
        
    fpr, tpr, thresholds = roc_curve(target, data[:,3], pos_label=True)
    sancnroc_auc = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,3]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        f1 = f1_score(target, data[:,3]>=myth, pos_label=True)
        logging.info('sancn myth%0.8f'%myth)
        logging.info('sancn f1%0.8f'%f1)
        logging.info('******************\n\n')
   
    
    fpr, tpr, thresholds = roc_curve(target, data[:,5], pos_label=True)
    sancn_node_weight = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,5]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        f1 = f1_score(target, data[:,5]>=myth, pos_label=True)
        logging.info('sancn_node_weight myth%0.8f'%myth)
        logging.info('sancn_node_weight f1%0.8f'%f1)
        logging.info('******************\n\n')
    
   
    
    fpr, tpr, thresholds = roc_curve(target, data[:,7], pos_label=True)
    sancn_node_weight2 = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,7]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        f1 = f1_score(target, data[:,7]>=myth, pos_label=True)
        logging.info('sancn_node_weight2 myth%0.8f'%myth)
        logging.info('cn_node_weight2 f1%0.8f'%f1)
        logging.info('******************\n\n')
    
   
    
    fpr, tpr, thresholds = roc_curve(target, data[:,9], pos_label=True)
    sancn_edge_weight = auc(fpr,tpr)
    myths=getbestthreshold(fpr, tpr, thresholds)
    for myth in myths:
        f1 = f1_score(target, data[:,9]>=myth, pos_label=True)
        pre_recall_f1 = precision_recall_fscore_support(target, data[:,9]>=myth, pos_label=True)
        logging.info(str(pre_recall_f1))
        logging.info('sancn_edge_weight myth%0.8f'%myth)
        logging.info('sancn_edge_weight f1%0.8f'%f1)
        logging.info('******************\n\n')
   
    logging.debug('cnroc_auc=%0.8f,cn_node_weight=%0.8f,cn_node_weight2=%0.8f,cn_edge_weight=%0.8f,'%(cnroc_auc,cn_node_weight,cn_node_weight2,cn_edge_weight))
    logging.debug('cnroc_auc=%0.8f,cn_node_weight=%0.8f,cn_node_weight2=%0.8f,cn_edge_weight=%0.8f,'%(sancnroc_auc,sancn_node_weight,sancn_node_weight2,sancn_edge_weight))

   
     
   

if __name__ == '__main__':
    
    centralitys={'cn':WGraph.get_cn_weight,'jc':WGraph.get_jc_weight,'aa':WGraph.get_aa_weight,
                 'cos':WGraph.get_cos_weight}
    
    
    one2=sys.argv[1]
    if one2=='1':
        pklfile='../data/'+sys.argv[2]+'3nets.pkl'
       
        fff= centralitys[sys.argv[3]]
        if not os.path.exists(r'log'): 
            os.mkdir('log')
        logging.basicConfig(filename='log/'+sys.argv[3]+sys.argv[2], filemode='w',
                        format='[%(asctime)s] - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
        print pklfile,
        linktest1file(pklfile,fff)
    elif one2=='2':
        pkloldf='../data/'+sys.argv[2]+'3nets.pkl'
        pklnewf='../data/'+sys.argv[3]+'3nets.pkl'
        
        fff= centralitys[sys.argv[4]]
        if not os.path.exists(r'log'): 
            os.mkdir('log')
        logging.basicConfig(filename='log/'+sys.argv[4]+sys.argv[2]+sys.argv[3],filemode='w',
                        format='[%(asctime)s] - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
        linktest2file(pkloldf,pklnewf,fff)
    