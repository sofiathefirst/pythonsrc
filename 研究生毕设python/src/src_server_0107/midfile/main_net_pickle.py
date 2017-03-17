'''
Created on 2015-7-19

@author: may
'''

import pickle
import os
import re
import logging
import networkx as nx
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


if __name__ == '__main__':
    
    if not os.path.exists(r'log'): 
        os.mkdir('log')
    logging.basicConfig(filename='log/netpickle.log', filemode='w',
                        format='[%(asctime)s] - %(module)s.%(funcName)s.%(lineno)d - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
#     kneibors_prob_semi_randneg(2,7,1,2,300000)
    if not os.path.exists(r'../data/jul3nets.pkl'): 
        datafile='../data/JUL4.txt'
        snet,anet,sanet=getsnet(datafile)  
        logging.debug('writting jul3nets.pkl....') 
        output = open('../data/jul3nets.pkl', 'wb')
        pickle.dump([snet,anet,sanet], output)
        output.close()
        os.remove(datafile)
        
        datafile='../data/AUG4.txt'  
        snet,anet,sanet=getsnet(datafile)
        logging.debug('writting aug3nets.pkl....')
        output = open('../data/aug3nets.pkl', 'wb')
        pickle.dump([snet,anet,sanet], output)
        output.close()
        os.remove(datafile)
        
        datafile='../data/SEP4.txt'
        snet,anet,sanet=getsnet(datafile)
        logging.debug('writting sep3nets.pkl....')
        output = open('../data/sep3nets.pkl', 'wb')
        pickle.dump([snet,anet,sanet], output)
        output.close()
        os.remove(datafile)
    