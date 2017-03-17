'''
Created on 2015-6-19

@author: may
'''


import os
import pickle
from net_mcc import getbestthreshold
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

def linktest78file():
    p_ufile='../data/ja78P_U_Utarget.pkl'
    pkl_file = open(p_ufile, 'rb')
    _,u= pickle.load(pkl_file)
    pkl_file.close()
    alphas = [0.93]
    nows=[]
    edges=[]
    for a in alphas:
#         'jul3nets.pkl0.110sanrwrbk'
        logging.debug("\n\n***************************\n\n")
        logging.debug('step=10 alphas=%0.1f'%a)
        pklfile='../data/jul3nets.pkl'+str(a)+'10sanrwr'
        pkl_file = open(pklfile, 'rb')
        rwr,rwr_wsn= pickle.load(pkl_file)
        pkl_file.close()
           
           
        
        
        data = []
        
        for (i,j,target) in u:
            data.append([i,j,rwr[i][j],rwr_wsn[i][j],target])
            
        
        data = np.array(data)     
        fpr, tpr, thresholds = roc_curve(data[:,4], data[:,2], pos_label=1)
    #     logging.info('rw best threshold %0.8f'%getbestthreshold(fpr, tpr, thresholds))
    #     logging.info('rw thresholds len=%d'%len(thresholds))
        rwroc_auc = auc(fpr,tpr)
        plt.figure()
    
        plt.plot(fpr, tpr, label='rwroc_auc ROC curve (area = %0.8f)' % rwroc_auc)
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC')
        plt.legend(loc="lower right")
        plt.show()
        
        logging.debug('rwr auc = %0.8f'%rwroc_auc)
        nows.append(rwroc_auc)
        fpr, tpr, thresholds = roc_curve(data[:,4], data[:,3], pos_label=1)
        rwroc_auc = auc(fpr,tpr)
        logging.debug('rwr wsn auc = %0.8f'%rwroc_auc)
        edges.append(rwroc_auc)
        
        plt.figure()
    
        plt.plot(fpr, tpr, label='rwroc_auc ROC curve (area = %0.8f)' % rwroc_auc)
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC')
        plt.legend(loc="lower right")
        plt.show()
    logging.debug([alphas,nows,edges])
    
  
    print alphas,nows,edges

if __name__ == '__main__':
    logging.basicConfig(filename='log/sanrwr_alpha_20.txt', filemode='w',
                    format='[%(asctime)s] - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
#     get_sn_wsn_rwr()
    linktest78file()

#     