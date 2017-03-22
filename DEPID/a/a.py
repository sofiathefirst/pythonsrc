# -*- coding: utf-8 -*-
import numpy as np
def costJf(kx,BsJ):

    global yd, y ,timef
    ts=0.001; 
    #sys=tf(400,[1,50,0]);
    #dsys=c2d(sys,ts,'z');
    #[num,den]=tfdata(dsys,'v');

    u_1=0;u_2=0;
    y_1=0;y_2=0;
    e_1=0;
    B=0;
    
    G=500;
    e=np.zeros((G,1));
    yd=np.zeros((G,1));
    y=np.zeros((G,1));
    de=np.zeros((G,1));
    u=np.zeros((G,1));
    Ji=np.zeros((G,1));
    for k in range(G):
        #timef(k)=k*ts;
        yd[k]=1.0;
    
        #y[k]=-den(2)*y_1-den(3)*y_2+num(2)*u_1+num(3)*u_2;
        e[k]=yd[k]-y[k];  
        de[k]=(e[k]-e_1)/ts;
        #speed(k)=(y[k]-y_1)/ts;
    
        kp=kx[0];kd=kx[1];
        u[k]=kp*e[k]+kd*de[k];   #PID control
        
        u_2=u_1;u_1=u[k];
        y_2=y_1;y_1=y[k];
        e_1=e[k];
    
    for i  in range(G):
        Ji[i]=0.999*abs(e[i])+0.01*u[i]**2*0.1;
        B=B+Ji[i];   
        if e[i]<0:    #Punishment
            B=B+10*abs(e[i]);
 
    BsJ=B;
    return BsJ