'''
Created on 2015-6-17

@author: may
'''
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

def gettimegeneratorlen(u,v,net,sanet,newnet,newsanet):
    timeuf=0
    timevf=0
    timeufsan=0
    timevfsan=0
    
    timeuf=nx.degree(net, u)
    timeuf=(nx.degree(newnet, u)-timeuf)*1.0/timeuf
    
    timevf=nx.degree(net, v)
    timevf=(nx.degree(newnet, u)-timevf)*1.0/timevf
    
    timeufsan=nx.degree(sanet, u)
    timeufsan=(nx.degree(newsanet, u)-timeufsan)*1.0/timeufsan
    timevfsan=nx.degree(sanet,v)
    timevfsan =(nx.degree(newsanet,v)-timevfsan)*1.0/timevfsan
    
    return timeuf+timevf,timeufsan+timevfsan

def gettimefilterlen(u,v,net,sanet,newnet,newsanet):
    
    return nx.degree(newnet, u)-nx.degree(net, u),nx.degree(newnet, v)-nx.degree(net, v)

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

def getgeneratorlen(g):
    i = 0
    for e in g:
        i += 1
    return i

def listtodict(dela):
    label = dict()
    for e in dela:
        if not label.has_key(e[0]):
            label[int(e[0])]= [int(e[1])]
        else:
            label[int(e[0])].append(int(e[1]))

    return label

# def listtodicttest():
#     dela=[(1931, 2666), (1478, 2578), (1035, 1832), (2765, 3855),(1931, 1), (1478, 2), (1035, 3), (2765, 4), (1909, 5), (1319, 1909), (595, 3561), (971, 2543), (1421, 4340)]
#     label = listtodict(dela)
    
def getdiffgraph(net,addnet):
    nete = net.edges()
    addnete = addnet.edges()
    
    dela = list(set(addnete).difference(set(nete)))
    label = listtodict(dela)
    return label

def getnewlinksfeature(net,anet,sanet,labels,filename):
    
    netnodes = net.nodes()
    lenn = len(netnodes)       
#     cluster = nx.clustering(sanet)
#     betw = nx.betweenness_centrality(sanet)
#     path_len = nx.all_pairs_shortest_path_length(sanet)
    cluster = nx.clustering(net)
    betw = nx.betweenness_centrality(net)
    path_len = nx.all_pairs_shortest_path_length(net)
    
    f = open(filename,'w+')
    for i in labels.keys():
        for j in labels[i]:
            try:
                cn=nx.common_neighbors(net,netnodes[i],netnodes[j])
                acn = nx.common_neighbors(anet,netnodes[i],netnodes[j])
                
    
                cnlen = getgeneratorlen(cn)
                acnlen = getgeneratorlen(acn)
                sacnlen = cnlen+acnlen
                if cnlen ==0: 
                    jc=0
                else:
                    jc = cnlen*1.0/len(list(set(nx.neighbors(net,netnodes[i])).union(set(nx.neighbors(net,netnodes[j])))))
                if acnlen ==0: 
                    ajc=0
                else:
                    ajc = acnlen*1.0/len(list(set(nx.neighbors(anet,netnodes[i])).union(set(nx.neighbors(anet,netnodes[j])))))
                     
                label = path_len[netnodes[i]][netnodes[j]]
                                                              
                    
                f.write(str(netnodes[i])+'\t'+str(netnodes[j])+'\t'\
                           +str(acnlen)+'\t'+str(ajc)+'\t'\
                           +str(cnlen)+'\t'+str(path_len[netnodes[i]][netnodes[j]])+'\t'\
                           +str(jc)+'\t'+str(cluster[netnodes[i]])+'\t'\
                           +str(cluster[netnodes[j]])+'\t'+str(betw[netnodes[i]])+'\t'+str(betw[netnodes[j]])+'\t'+str(label) +'\n')
                  
                 
                del path_len[j][i]
                 
            except KeyError:
                path_len[netnodes[i]][netnodes[j]] = 100
                f.write(str(netnodes[i])+'\t'+str(netnodes[j])+'\t'\
                           +str(cnlen)+'\t'+str(path_len[netnodes[i]][netnodes[j]])+'\t'\
                           +str(jc)+'\t'+str(cluster[netnodes[i]])+'\t'\
                           +str(cluster[netnodes[j]])+'\t'+str(betw[netnodes[i]])+'\t'+str(betw[netnodes[j]])+'\t'+str(label) +'\n')
                  
                print '**\n'
            
    f.close()
    
def gettimefilterfeature(net,anet,sanet,onet,oanet,osanet,outfile):
    oupf = open(outfile,'w+')
    netnodes = net.nodes()
    lenn = len(netnodes)
    
    path_len = nx.all_pairs_shortest_path_length(sanet)
     
#     up triangular
    for i in range(lenn):
        for j in range(i+1,lenn):
            try:
                cn=nx.common_neighbors(net,netnodes[i],netnodes[j])
                acn = nx.common_neighbors(anet,netnodes[i],netnodes[j])           
    
                cnlen = getgeneratorlen(cn)
                acnlen = getgeneratorlen(acn)
                id,jd = gettimefilterlen(i,j,onet,osanet,net,sanet)
                label = path_len[netnodes[i]][netnodes[j]]
                if label!=1:
                    label = 0
                else:
                    sanet.remove_edge(netnodes[i],netnodes[j])
                    print path_len[netnodes[i]][netnodes[j]]
                    try:
                        path_len[netnodes[i]][netnodes[j]]=len(nx.shortest_path(sanet,netnodes[i],netnodes[j]))-1
                    except nx.exception.NetworkXNoPath:
                        path_len[netnodes[i]][netnodes[j]]=18
                    print path_len[netnodes[i]][netnodes[j]]
                    print netnodes[i],netnodes[j]
                    print '***************'
                    sanet.add_edge(netnodes[i],netnodes[j]) 
                oupf.write(str(netnodes[i])+'\t'+str(netnodes[j])+'\t'\
                           +str(acnlen)+'\t'\
                           +str(cnlen)+'\t'+str(path_len[netnodes[i]][netnodes[j]])+'\t'\
                           +str(id)+'\t'+str(jd)+'\t'+str(label) +'\n')
                  
                 
                del path_len[netnodes[j]][netnodes[i]]
                 
            except KeyError:
                path_len[netnodes[i]][netnodes[j]] = 100
                oupf.write(str(netnodes[i])+'\t'+str(netnodes[j])+'\t'\
                           +str(acnlen)+'\t'\
                           +str(cnlen)+'\t'+str(path_len[netnodes[i]][netnodes[j]])+'\t'\
                           +str(label) +'\n')
                print '**\n'
    oupf.close()
        
def getfilterfeature(net,anet,sanet,outfile):
    oupf = open(outfile,'w+')
    netnodes = net.nodes()
    lenn = len(netnodes)

    path_len = nx.all_pairs_shortest_path_length(sanet)
     
#     up triangular
    for i in range(lenn):
        for j in range(i+1,lenn):
            try:
                cn=nx.common_neighbors(net,netnodes[i],netnodes[j])
                acn = nx.common_neighbors(anet,netnodes[i],netnodes[j])           
    
                cnlen = getgeneratorlen(cn)
                acnlen = getgeneratorlen(acn)
                
                label = path_len[netnodes[i]][netnodes[j]]
                if label!=1:
                    label = 0
                else:
                    sanet.remove_edge(netnodes[i],netnodes[j])
                    print path_len[netnodes[i]][netnodes[j]]
                    try:
                        path_len[netnodes[i]][netnodes[j]]=len(nx.shortest_path(sanet,netnodes[i],netnodes[j]))-1
                    except nx.exception.NetworkXNoPath:
                        path_len[netnodes[i]][netnodes[j]]=18
                    print path_len[netnodes[i]][netnodes[j]]
                    print netnodes[i],netnodes[j]
                    print '***************'
                    sanet.add_edge(netnodes[i],netnodes[j]) 
                oupf.write(str(netnodes[i])+'\t'+str(netnodes[j])+'\t'\
                           +str(acnlen)+'\t'\
                           +str(cnlen)+'\t'+str(path_len[netnodes[i]][netnodes[j]])+'\t'\
                           +str(label) +'\n')
                  
                 
                del path_len[netnodes[j]][netnodes[i]]
                 
            except KeyError:
                path_len[netnodes[i]][netnodes[j]] = 100
                oupf.write(str(netnodes[i])+'\t'+str(netnodes[j])+'\t'\
                           +str(acnlen)+'\t'\
                           +str(cnlen)+'\t'+str(path_len[netnodes[i]][netnodes[j]])+'\t'\
                           +str(label) +'\n')
                print '**\n'
    oupf.close()
    
def getfeature(net,anet,sanet,outfile):
    oupf = open(outfile,'w+')
    netnodes = net.nodes()
    lenn = len(netnodes)
    
    
    cluster = nx.clustering(sanet)
    betw = nx.betweenness_centrality(sanet)
    path_len = nx.all_pairs_shortest_path_length(sanet)
     
#     up triangular
    for i in range(lenn):
        for j in range(i+1,lenn):
            try:
                cn=nx.common_neighbors(net,netnodes[i],netnodes[j])
                acn = nx.common_neighbors(anet,netnodes[i],netnodes[j])
                
                cnlen = getgeneratorlen(cn)
                acnlen = getgeneratorlen(acn)
                sacnlen = cnlen+acnlen
                if cnlen ==0: 
                    jc=0
                else:
                    jc = cnlen*1.0/len(list(set(nx.neighbors(net,netnodes[i])).union(set(nx.neighbors(net,netnodes[j])))))
                if acnlen ==0: 
                    ajc=0
                else:
                    ajc = acnlen*1.0/len(list(set(nx.neighbors(anet,netnodes[i])).union(set(nx.neighbors(anet,netnodes[j])))))
                     
                label = path_len[netnodes[i]][netnodes[j]]
                if label!=1:
                    label = 0
                else:
                    sanet.remove_edge(netnodes[i],netnodes[j])
                    print path_len[netnodes[i]][netnodes[j]]
                    try:
                        path_len[netnodes[i]][netnodes[j]]=len(nx.shortest_path(sanet,netnodes[i],netnodes[j]))-1
                    except nx.exception.NetworkXNoPath:
                        path_len[netnodes[i]][netnodes[j]]=18
                    print path_len[netnodes[i]][netnodes[j]]
                    print netnodes[i],netnodes[j]
                    
                    sanet.add_edge(netnodes[i],netnodes[j]) 
                oupf.write(str(netnodes[i])+'\t'+str(netnodes[j])+'\t'\
                           +str(acnlen)+'\t'+str(ajc)+'\t'\
                           +str(cnlen)+'\t'+str(path_len[netnodes[i]][netnodes[j]])+'\t'\
                           +str(jc)+'\t'+str(cluster[netnodes[i]])+'\t'\
                           +str(cluster[netnodes[j]])+'\t'+str(betw[netnodes[i]])+'\t'+str(betw[netnodes[j]])+'\t'+str(label) +'\n')
                  
                 
                del path_len[netnodes[j]][netnodes[i]]
                 
            except KeyError:
                path_len[netnodes[i]][netnodes[j]] = 100
                oupf.write(str(netnodes[i])+'\t'+str(netnodes[j])+'\t'\
                           +str(cnlen)+'\t'+str(path_len[netnodes[i]][netnodes[j]])+'\t'\
                           +str(jc)+'\t'+str(cluster[netnodes[i]])+'\t'\
                           +str(cluster[netnodes[j]])+'\t'+str(betw[netnodes[i]])+'\t'+str(betw[netnodes[j]])+'\t'+str(label) +'\n')
                  
                print '**\n'
    oupf.close()
    
def gettimefeature(net,anet,sanet,newnet,newanet,newsanet,outfile):
    oupf = open(outfile,'w+')
    netnodes = net.nodes()
    lenn = len(netnodes)
    

    path_len = nx.all_pairs_shortest_path_length(sanet)
    cluster = nx.clustering(sanet)
    betw = nx.betweenness_centrality(sanet)
#     up triangular
    for i in range(lenn):
        for j in range(i+1,lenn):
            try:
                cn=nx.common_neighbors(net,i,j)
                acn = nx.common_neighbors(anet,i,j)
                
                timef,timefsan = gettimegeneratorlen(i,j,net,sanet,newnet,newsanet)
                cnlen = getgeneratorlen(cn)
                acnlen = getgeneratorlen(acn)
                sacnlen = cnlen+acnlen
                if cnlen ==0: 
                    jc=0
                else:
                    jc = cnlen*1.0/len(list(set(nx.neighbors(net,i)).union(set(nx.neighbors(net,j)))))
                if acnlen ==0: 
                    ajc=0
                else:
                    ajc = acnlen*1.0/len(list(set(nx.neighbors(anet,i)).union(set(nx.neighbors(anet,j)))))
                     
                label = path_len[i][j]
                if label!=1:
                    label = 0
                else:
                    sanet.remove_edge(i,j)
                    print path_len[i][j]
                    try:
                        path_len[i][j]=len(nx.shortest_path(sanet,i,j))-1
                    except nx.exception.NetworkXNoPath:
                        path_len[i][j]=18

                    sanet.add_edge(i,j) 
                oupf.write(str(i)+'\t'+str(j)+'\t'\
                           +str(acnlen)+'\t'+str(ajc)+'\t'\
                           +str(cnlen)+'\t'+str(path_len[i][j])+'\t'\
                           +str(jc)+'\t'+str(cluster[i])+'\t'\
                           +str(cluster[j])+'\t'+str(betw[i])+'\t'+str(betw[j])+'\t'\
                           +str(timef)+'\t'+str(timefsan)+'\t'+str(label) +'\n')
                  
                 
                del path_len[netnodes[j]][netnodes[i]]
                 
            except KeyError:
                path_len[i][j] = 100
                oupf.write(str(i)+'\t'+str(j)+'\t'\
                           +str(acnlen)+'\t'+str(ajc)+'\t'\
                           +str(cnlen)+'\t'+str(path_len[i][j])+'\t'\
                           +str(jc)+'\t'+str(cluster[i])+'\t'\
                           +str(cluster[j])+'\t'+str(betw[i])+'\t'+str(betw[j])+'\t'\
                           +str(timef)+'\t'+str(timefsan)+'\t'+str(label) +'\n')
                  
    oupf.close()
    
def getattributeReferencefeature(net,anet,outfile):
    oupf = open(outfile,'w+')
    netnodes = net.nodes()
    lenn = len(netnodes)
    anetnodes = np.array(anet.nodes())
    anodes = anetnodes<0
    anodes = anetnodes[anodes]
    alenn = len(anodes)
    
    cluster = nx.clustering(sanet)
    betw = nx.betweenness_centrality(sanet)
    path_len = nx.all_pairs_shortest_path_length(sanet)
    print 'lenn,alenn'
    print lenn,alenn
    
#     up triangular
    for i in range(lenn):
        for j in anodes:
            try:
                cn=nx.common_neighbors(net,netnodes[i],netnodes[j])
                acn = nx.common_neighbors(anet,netnodes[i],netnodes[j])
                cnlen = getgeneratorlen(cn)
                acnlen = getgeneratorlen(acn)
                if cnlen ==0: 
                    jc=0
                else:
                    jc = cnlen*1.0/len(list(set(nx.neighbors(net,netnodes[i])).union(set(nx.neighbors(net,netnodes[j])))))
                if acnlen ==0: 
                    ajc=0
                else:
                    ajc = acnlen*1.0/len(list(set(nx.neighbors(anet,netnodes[i])).union(set(nx.neighbors(anet,netnodes[j])))))
                    
                label = path_len[netnodes[i]][netnodes[j]]
                if label!=1:
                    label = 0
                oupf.write(str(netnodes[i])+'\t'+str(netnodes[j])+'\t'\
                           +str(acnlen)+'\t'+str(ajc)+'\t'\
                           +str(cnlen)+'\t'+str(path_len[netnodes[i]][netnodes[j]])+'\t'\
                           +str(jc)+'\t'+str(cluster[netnodes[i]])+'\t'\
                           +str(cluster[netnodes[j]])+'\t'+str(betw[netnodes[i]])+'\t'+str(betw[netnodes[j]])+'\t'+str(label) +'\n')
                 
                
                del path_len[netnodes[j]][netnodes[i]]
                
            except KeyError:
                path_len[netnodes[i]],[netnodes[j]] = 100
                oupf.write(str(netnodes[i])+'\t'+str(netnodes[j])+'\t'\
                           +str(cnlen)+'\t'+str(path_len[netnodes[i]][netnodes[j]])+'\t'\
                           +str(jc)+'\t'+str(cluster[netnodes[i]])+'\t'\
                           +str(cluster[netnodes[j]])+'\t'+str(betw[netnodes[i]])+'\t'+str(betw[netnodes[j]])+'\t'+str(label) +'\n')
                 
                print '**\n'
    oupf.close()

if __name__ == '__main__':
     
    juldatafile='data/JUL4.txt'
    augdatafile='data/AUG4.txt'
    sepdatafile='data/SEP4.txt'
    jsnet,janetjsanet=getsnet(juldatafile)
    asnet,aanet,asanet=getsnet(augdatafile)
    ssnet,sanet,ssanet=getsnet(sepdatafile)
    jul_auglabel = getdiffgraph(jsnet,asnet)
    jul_seplabel = getdiffgraph(jsnet,ssnet)
    aug_seplabel = getdiffgraph(asnet,ssnet)
# #     getfeature(snet,'jul4.csv')
# #     nx.draw(snet)
# #     plt.show()
#     print nx.neighbors(snet, 0)
#     print nx.neighbors(snet, 2305)
#     
    
    
    