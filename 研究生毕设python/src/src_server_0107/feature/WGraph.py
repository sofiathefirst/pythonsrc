# -*- coding: gb18030 -*-
'''
Created on 2015-10-12

@author: may
'''
import networkx as nx
import math
import numpy as np
import logging
import sys
import pickle

import matplotlib.pyplot as plt
class WGraph:
    
    def __init__(self,g):
        self.g=g
        self.set_edges_weight()
        self.set_nodes_weight()
        
    def get_cn_len(self,u,v):
        cn=nx.common_neighbors(self.g,u,v)
        cnt = 0
        for e in cn:
            cnt+=1
        return cnt+1
    
    def set_nodes_weight(self):
        ds=self.g.degree()
        dsv=np.array(ds.values ())
        stat=[len(self.g.edges()),np.max(dsv),np.min(dsv),np.average(dsv),np.median(dsv)]
        print stat
        ma=max(ds.values ())
        
        for i in ds.keys():
            ds[i]=ds[i]*1./ma
        self.wnodes= ds
        return ds
    def set_weight_time(self):
        pkl_file='../data/jul3nets.pkl'
        pkl_file = open(pkl_file, 'rb')
        jsnet,_,_ = pickle.load(pkl_file)
        pkl_file.close()
        
        pkl_file='../data/aug3nets.pkl'
        pkl_file = open(pkl_file, 'rb')
        asnet,_,_ = pickle.load(pkl_file)
        pkl_file.close()
        
        
        
        jdegrees = nx.degree(jsnet)
        adegrees = nx.degree(asnet)
   
        self.wnodes_time={}
        for i in range(5200):
            self.wnodes_time[i]=adegrees[i]-jdegrees[i]
        self.wedges_time={}
        gedges = self.g.edges()
        self.wedges = {}
        for (x,y) in gedges:
            self.wedges[(x,y)]=self.wnodes_time[x]+self.wnodes_time[y]
        
    def set_edges_weight(self):
        gedges = self.g.edges()
        self.wedges = {}
        for (x,y) in gedges:
            self.wedges[(x,y)]=self.get_cn_len(x,y)
        return self.wedges
 
    def get_node_weight(self,u):
        return self.wnodes[u]
    def get_edge_weight(self,u,v):
        if u==v:
            return 1.0
        try:
            return self.wedges[(u,v)]
        except KeyError:
            try:
                return self.wedges[(v,u)]
            except KeyError:
                return 0
        return 0
    
    def get_node_weight_time(self,u):
        return self.wnodes_time[u]
    def get_edge_weight_time(self,u,v):
        if u==v:
            return 1.0
        try:
            return self.wedges_time[(u,v)]
        except KeyError:
            try:
                return self.wedges_time[(v,u)]
            except KeyError:
                return 0
        return 0
    
    def get_cn_weight(self,u,v):
        cn=nx.common_neighbors(self.g,u,v)
        cntw = 0
        cntw2=0
        cnt=0
        cnte=0
        for e in cn:
            cntw+=self.wnodes[e]
            cntw2+=1./self.wnodes[e]
            cnt+=1
            cnte+=self.get_edge_weight(u,e)+self.get_edge_weight(v,e)
        return cnt,cntw,cntw2,cnte

    def get_aa_weight(self,u,v):
        cn=nx.common_neighbors(self.g,u,v)
        cntw = 0
        cntw2=0
        cnt=0
        cnte=0
        for e in cn:
            t=math.log(self.g.degree(e))
            cntw+=self.wnodes[e]/t
            cntw2+=1./(self.wnodes[e]*t)
            cnt+=1./t
            cnte+=(self.get_edge_weight(u,e)+self.get_edge_weight(v,e))/t
        return cnt,cntw,cntw2,cnte
   
    def get_jc_weight(self,u,v):
        cn=nx.common_neighbors(self.g,u,v)
        merg=set(self.g.neighbors(u)+self.g.neighbors(v));
        
        cntw = 0
        mergcntw=0
        cntwr = 0
        
        cntw2=0
        mergcntw2=0
        cntw2r=0
        
        cnt=0
        mergcnt=0
        cntr=0
        
        cntedge = 0
        mergedgecnt=0
        cntedger=0
        
        for e in cn:
            cntw+=self.wnodes[e]
            cntw2+=1./(self.wnodes[e])
            cnt+=1
            cntedge+=(self.get_edge_weight(u,e)+self.get_edge_weight(v,e))
            
        if cnt<0.0000000000000000000000001:
            cnt=0
        if cntw<0.0000000000000000000000001:
            cntw=0
        if cntw2<0.0000000000000000000000001:
            cntw2=0
        if cntedge<0.0000000000000000000000001:
            cntedge=0
        
        for e in merg:
            if cntw>0:
                mergcntw+=self.wnodes[e]
            if cntw2>0:
                mergcntw2+=1./(self.wnodes[e])
            if cnt>0:
                mergcnt+=1  
            if cntedge>0:
                mergedgecnt+=(self.get_edge_weight(u,e)+self.get_edge_weight(v,e))
        
        if cnt==0:
            cntr=0  
        else:
            cntr=cnt*1./mergcnt
        
        if cntw==0:
            cntwr=0  
        else:
            cntwr=cntw*1./mergcntw     
         
        if cntw2==0:
            cntw2r=0  
        else:
            cntw2r=cntw2*1./mergcntw2
        
        if cntedge==0:
            cntedger=0  
        else:
            cntedger=cntedge*1./mergedgecnt     
        
        return cntr,cntwr,cntw2r,cntedger
      
    def get_cos_weight(self,u,v):
        cn=nx.common_neighbors(self.g,u,v)
        cntw = 0
        cntw2=0
        cnt=0
        cntedge=0
        t=math.sqrt(self.g.degree(u)*self.g.degree(v))
        for e in cn:
            
            cntw+=self.wnodes[e]
            cntw2+=1./(self.wnodes[e])
            cnt+=1
            cntedge+=(self.get_edge_weight(u,e)+self.get_edge_weight(v,e))
        return cnt*1./t,cntw*1./t,cntw2*1./t,cntedge*1./t
    
class WAGraph:
    
    def __init__(self,g):
        self.g=g
        
    def get_cn_len(self,u,v):
        cn=nx.common_neighbors(self.g,u,v)
        cnt = 0
        for e in cn:
            cnt+=1
        return cnt+1
    
    def set_nodes_weight(self):
        ds=self.g.degree()
        ma=max(ds.values ())
        for i in ds.keys():
            ds[i]=ds[i]*1./ma
        self.wnodes= ds
        return ds
    
    def set_edges_weight(self):
        gedges = self.g.edges()
        self.wedges = {}
        for (x,y) in gedges:
            self.wedges[(x,y)]=self.get_cn_len(x,y)
        return self.wedges
 
    def get_node_weight(self,u):
        return self.wnodes[u]
    def get_edge_weight(self,u,v):
        try:
            return self.wedges[(u,v)]
        except KeyError:
            try:
                return self.wedges[(v,u)]
            except KeyError:
                return 0
        return 0
    
  
    
class WSAGraph:
    
    def __init__(self,san):
        self.g = san
        self.set_node_weight()
        self.set_edge_weight()
        
    def set_node_weight(self):
        nx.degree_centrality(self.g)
        
    def set_edge_weight(self):
        self.wedges={}
        for (u,v) in self.g.edges():
            self.wedges[(u,v)]= self.get_cn_len(u,v)
            
        
    def get_cn_len(self,u,v):
        cn=nx.common_neighbors(self.g,u,v)
        cnt = 0
        for e in cn:
            cnt+=1
        return cnt+0.5
 
   
    def get_edge_weight(self,u,v):
        
        try:
            return self.wedges[(u,v)]
        except KeyError:
            try:
                return self.wedges[(v,u)]
            except KeyError:
                return 0
       
                                         
        return 0
    def get_aa_weight(self,u,v):
        cn=nx.common_neighbors(self.g,u,v)
        cntw = 0
        cntw2=0
        cnt=0
        cnte=0
        for e in cn:
            t=math.log(self.g.degree(e))
            cntw+=self.wnodes[e]/t
            cntw2+=1./(self.wnodes[e]*t)
            cnt+=1/t
            cnte+=(self.get_edge_weight(u,e)+self.get_edge_weight(v,e))/t
        return cnt,cntw,cntw2,cnte
   
    def get_jc_weight(self,u,v):
        cn=nx.common_neighbors(self.g,u,v)
        merg=set(self.g.neighbors(u)+self.g.neighbors(v));
        cntw = 0
        mergcntw=0
        cntw2=0
        mergcntw2=0
        cnt=0
        mergcnt=0
        cntr=0
        cntwr=0
        cntw2r=0
        
        cnte = 0
        mergcnte=0
        
        for e in cn:
            cntw+=self.wnodes[e]
            cntw2+=1./(self.wnodes[e])
            cnt+=1
            cnte+=(self.get_edge_weight(u,e)+self.get_edge_weight(v,e))
        if cnt<0.0000000000000000000000001:
            cntr=0
        if cnt<0.0000000000000000000000001:
            cntwr=0
        if cnt<0.0000000000000000000000001:
            cntw2r=0
        
        for e in merg:
            mergcntw+=self.wnodes[e]
            mergcntw2+=1./(self.wnodes[e])
            mergcnt+=1  
            mergcnte+=(self.get_edge_weight(u,e)+self.get_edge_weight(v,e))
         
        return cnt*1./mergcnt,cntw*1./mergcntw,cntw2*1./mergcntw2,cnte*1./mergcnte
        
    def get_cos_weight(self,u,v):
        cn=nx.common_neighbors(self.g,u,v)
        cntw = 0
        cntw2=0
        cnt=0
        cntedge=0
        t=math.sqrt(self.g.degree(u)*self.g.degree(v))
        for e in cn:
            
            cntw+=self.wnodes[e]
            cntw2+=1./(self.wnodes[e])
            cnt+=1
            cntedge+=(self.get_edge_weight(u,e)+self.get_edge_weight(v,e))
        return cnt*1./t,cntw*1./t,cntw2*1./t,cntedge*1./t
    def get_cn_weight(self,u,v):
        cn=nx.common_neighbors(self.g,u,v)
        cntw = 0
        cntw2=0
        cnt=0
        cnte=0
        for e in cn:
            cntw+=self.wnodes[e]
            cntw2+=1./self.wnodes[e]
            cnt+=1
            cnte+=self.get_edge_weight(u,e)+self.get_edge_weight(v,e)
        return cnt,cntw,cntw2,cnte
 
if __name__ == '__main__':
    pklfile='../data/'+sys.argv[1]+'3nets.pkl';
    pkl_file = open(pklfile, 'rb')
    net,anet,sanet = pickle.load(pkl_file)
    pkl_file.close()
    wg = WGraph(net)
    dsv=np.array(net.degree().values())
    dsvdic={}
    stat=[len(net.edges()),np.max(dsv),np.min(dsv),np.average(dsv),np.median(dsv)]
    print stat
    
    for e in dsv:
        if dsvdic.has_key(e):
            dsvdic[e]+=1
        else:
            dsvdic[e]=1
    x=dsvdic.keys()
    y=dsvdic.values()
    
    plt.bar(x,y)
    plt.title('degree distribution')
    plt.xlabel('degree')
    plt.ylabel('frequency')
    plt.show()
#     wg.set_edges_weight()
    
    
