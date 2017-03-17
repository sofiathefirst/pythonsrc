'''
Created on 2015-4-9

@author: may
'''
import time
from userdata import *

starttime = time.time()

userpairs = {}
users={}

def getvukey(uvkey,uid):
    struvkey = str(uvkey)
    struid = str(uid)
    strvid = struvkey[len(struid):len(struvkey)]
    return [int(strvid+struid),int(strvid)]

def readuserfile(filename):
    snsfile = open(filename)
    
    for line in snsfile:
    #1000324    2105532
    #1000324    2383983
        ids=line.split(',')
        uid = int(ids[0])
        print ids
        if users.has_key(uid):
            users[uid].outdegree += 1    
        else:
            u = user()
            u.outdegree = 1
            users[uid]=u
         
        vid = int(ids[1])   
        key = int(str(uid)+str(vid))
        userpairs[key]=int(str(uid)+str(1))#label = 1 true
        
        if users.has_key(vid):   
            users[vid].indegree +=1;   
        else:
            u = user()
            u.indegree = 1
            users[vid]=u
       
    snsfile.close()
    
    
    print '*************sns file finished************'
    print time.time() - starttime   
    
    for uvkey in userpairs:
        print uvkey
#         uid_label = userpairs[uvkey]# the last digit is label
        uid_label = userpairs[uvkey]
        uid = uid_label/10
        vukey = getvukey(uvkey, uid)[0] 
        if userpairs.has_key(vukey):
            users[uid].twodegree+=1       
            
    userpairs.clear()
if __name__ == '__main__':
    starttime = time.time()
#     readprofile('../data/profiletest.txt')
#     readsnsfile("../data/snstest.txt")

#     readprofile('../data/3user_profile.txt')
    readsnsfile("../data/6user_sns.txt")
    
    snswfile = open('users.txt','w+')
    for e in users:
        snswfile.write(str(e)+'\t'+users[e].featureinfo())
    snswfile.close()
    users.clear()
    
#     readactionfile('../data/a5user_action.txt') 
#     readactionfile('../data/actiontest.txt')   
    
    
    
    
    print time.time()-starttime

#print users
#{516096: '0\t2', 2105346: '0\t1', 1400835: '0\t1'}