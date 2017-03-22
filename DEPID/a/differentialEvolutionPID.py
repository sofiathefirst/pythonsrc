
# -*- coding: utf-8 -*-
#PD tuning control based on DE
#clear all;
#close all;
import numpy as np
from a import costJf
from math import floor
import random
#from  pkgcost import costJf
global yd, y ,timef
import matplotlib.pyplot as plt
#def costJf(kx,BsJ):
#    return 1
F=1.20;      #变异因子：[1,2]
cr=0.6;      # 交叉因子

Size=30;
CodeL=2;
MinX=[0 ,0];
MaxX=[20, 1];
kxi=np.zeros((30,2));
h=np.zeros((30,2));
v=np.zeros((30,2));
#for i in range(CodeL)

for i in range(CodeL):
    kxi[:,i]=MinX[i]+(MaxX[i]-MinX[i])*np.random.random(size=Size)

print kxi

BestS=kxi[0,:]; #全局最优个体
BsJ=0;
for i in range(1,Size):
    print i
    if costJf(kxi[i,:],BsJ)<costJf(BestS,BsJ):        
        BestS=kxi[i,:];

BsJ=costJf(BestS,BsJ);


#进入主要循环，直到满足精度要求
G=50; #最大迭代次数 
time=np.zeros((G,1))
kp=np.zeros(G)
kd=np.zeros(G)
for kg in range(G):
    time[kg]=kg;
    
#变异
    for i in range(Size):
        kx=kxi[i,:];
        r1 = 1;r2=1;r3=1;r4=1;
        while(r1 == r2 or r1 ==r3 or r2 == r3 or r1 == i or r2 ==i or r3 == i or r4==i or r1==r4 or r2==r4 or r3==r4  or r1 == Size or r2 ==Size or r3 == Size or r4==Size ):
            r1 =int( floor(Size * random.random()));
            r2 = int( floor(Size * random.random()));
            r3 = int( floor(Size * random.random()));
            r4 = int( floor(Size * random.random()));
        
        h[i,:]=BestS+F*(kxi[r1,:]-kxi[r2,:]);
        #h[i,:]=X(r1,:)+F*(X(r2,:)-X(r3,:));

        for j in range(CodeL):  #检查值是否越界        
            if h[i,j]<MinX[j]:
                h[i,j]=MinX[j];
            elif h[i,j]>MaxX[j]:
                h[i,j]=MaxX[j];
          
#交叉
        for j in range(CodeL):      
            tempr = random.random();
            if(tempr<cr):
                v[i,j] = h[i,j];
            else:   
                v[i,j] = kxi[i,j];
    
#选择   
        if(costJf(v[i,:],BsJ)<costJf(kxi[i,:],BsJ)):
            kxi[i,:]=v[i,:];
        
#判断和更新      
        if costJf(kxi[i,:],BsJ)<BsJ: #判断当此时的指标是否为最优的情况
            BsJ=costJf(kxi[i,:],BsJ);
            BestS=kxi[i,:];
        
    
    BestS
    kp[kg]=BestS[0];
    kd[kg]=BestS[1];
    
    BsJ
print 'over'
#plt.plot(kxi[:,0], kxi[:,1], 'r-')
#plt.show()
#print BsJ
'''   
BsJ_kg[kg]=costJf(BestS,BsJ);
end
display('kp,kd');
BestS

figure(1);
plot(timef,yd,'r',timef,y,'k:','linewidth',2);
xlabel('Time(s)');ylabel('yd,y');
legend('Ideal position signal','Position tracking');
figure(2);
plot(time,BsJ_kg,'r','linewidth',2);
xlabel('Times');ylabel('Best J');

figure(3);
plot(time,kp,'r',time,kd,'k','linewidth',2);
xlabel('Time(s)');ylabel('kp,kd');
legend('kp','kd');
'''
