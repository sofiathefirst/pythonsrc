'''
Created on 2015-4-9

@author: may
'''
class uvkey(object):
    def __init__(self,uid,vid):
        self.uid = uid
        self.vid = vid
#         self.key = int(str(uid)+str(vid))
        
#         self.tagcn = 0
#         self.uncnnum = 0
#         self.uncnnumperu = 0.0
#         self.uncnnumperv = 0.0
#         self.uncnnumperuv = 0.0
#         
#         self.twocnnum = 0
#         self.twocnnumperu = 0.0
#         self.twocnnumperv = 0.0
#         self.twocnnumperuv =0.0
#         
#         self.cnfollowernum = 0
#         self.cnfollowernumperu = 0.0
#         self.cnfollowernumperv = 0.0
#         self.cnfollowernumperuv =0.0
#         
#         self.cnfollweenum = 0
#         self.cnfolloweenumperu = 0.0
#         self.cnfolloweenumperv = 0.0
#         self.cnfolloweenumperuv =0.0
#         
#         self.atnum = 0
#         self.retweetnum = 0
#         self.replaynum = 0
#         
#         self.label = 0 # 0:unkonw, 1:true,2:false
#     def printinfo(self):
#         print self.uid,self.vid,self.key,self.atnum,self.retweetnum,self.replaynum,self.label
    
#     def featureinfo(self):
#         return str(self.uid)+'\t'+str(self.vid)+'\t'+str(self.key)+'\t'+str(self.atnum)+'\t'+str(self.retweetnum)+'\t'+str(self.replaynum)+'\t'+str(self.label)+'\n'
        
class user(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
#         self.id = uid
        self.indegree = 0
        self.outdegree = 0
        self.twodegree = 0

        
#     def printinfo(self):
#         print self.id,self.indegree,self.outdegree,self.bathyear,self.sex,self.tweetnum,self.tags,self.twodegree
#         
    def featureinfo(self):
        return str(self.indegree)+'\t'+str(self.outdegree)+'\t'+str(self.twodegree)+'\n'
     
#     def setprofile(self,bathy,sex,tweetn,tags):
#         self.bathyear = bathy
#         self.sex = sex
#         self.tweetnum = tweetn
#         self.tags = tags.strip()
#         