'''
Created on 2015-4-9

@author: may
'''
import time
from userdata import *

starttime = time.time()

userpairs = {}
users={}

def readprofile(filename):
    profile = open(filename)
    for line in profile:
        ids=line.split('\t')
        #100044    1899    1    5    831;55;198;8;450;7;39;5;111
        #100054    1987    2    6    0
        u = user(int(ids[0]))
        try:
            bathy = int(ids[1])
            sex = int(ids[2])
            tweetnum = int(ids[3])
            tags = ids[4]
            u.setprofile(bathy,sex,tweetnum,tags)
            users[u.id] = u
        except:
            pass
    print '*************profile file finished************'
    print time.time() - starttime  
    profile.close()
#     for e in users:
#         users[e].printinfo()

def readsnsfile(filename):
    snsfile = open(filename)
    for line in snsfile:
    #1000324    2105532
    #1000324    2383983
    #for line in open("snstest.txt"):
        #print line
        ids=line.split('\t')
        uid = int(ids[0])
        if users.has_key(uid):
            users[uid].outdegree += 1    
        else:
            u = user(uid)
            u.outdegree = 1
            users[uid]=u
        
        
        vid = int(ids[1])
        pair = uvkey(uid,vid)
        pair.label = 1
        userpairs[pair.key]=pair
        
        if users.has_key(vid):   
            users[vid].indegree +=1;   
        else:
            u = user(vid)
            u.indegree = 1
            users[vid]=u
       
    snsfile.close()
    
    
    print '*************sns file finished************'
    print time.time() - starttime   
    
    for e in userpairs:
        pair=userpairs[e]
        if userpairs.has_key(int(str(pair.vid)+str(pair.uid))):
            users[pair.uid].twodegree+=1       
            
#     for e in users:
#         users[e].printinfo()    

def readactionfile(filename):
    actionfile = open(filename,'r')
    pairfile = open('pairwise.txt','w+')
    for line in actionfile:
    #1000324    2105532
    #1000324    2383983
    #for line in open("snstest.txt"):
         
        ids=line.split('\t')
         
        uid = int(ids[0])
        vid = int(ids[1])
        if uid == vid:
            continue
        key = int(str(uid)+str(vid))
        
        if userpairs.has_key(key):
            userpairs[key].atnum = int(ids[2])
            userpairs[key].retweetnum = int(ids[3])
            userpairs[key].replaynum = int(ids[4])   
            pairfile.write(userpairs[key].featureinfo())
            del userpairs[key]
              
        else:
            pair = uvkey(uid,vid)
            pair.label=2
            pair.atnum = int(ids[2])
            pair.retweetnum = int(ids[3])
            pair.replaynum = int(ids[4]) 
            
            pairfile.write(pair.featureinfo())
            
    
    actionfile.close()
    
    for e in userpairs:
        pairfile.write(userpairs[e].featureinfo())
    pairfile.close()
    print "*********actionfile finished************"
#     for e in userpairs:
#         userpairs[e].printinfo()
            
        
if __name__ == '__main__':
    starttime = time.time()
    readprofile('../data/profiletest.txt')
    readsnsfile("../data/snstest.txt")

#     readprofile('../data/3user_profile.txt')
#     readsnsfile("../data/6user_sns.txt")
    
    snswfile = open('snsw.txt','w+')
    for e in users:
        snswfile.write(users[e].featureinfo())
    snswfile.close()
    users.clear()
    
#     readactionfile('../data/a5user_action.txt') 
    readactionfile('../data/actiontest.txt')   
    
    
    
    
    print time.time()-starttime

#print users
#{516096: '0\t2', 2105346: '0\t1', 1400835: '0\t1'}