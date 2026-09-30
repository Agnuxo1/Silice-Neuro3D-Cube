import os,sys,json,math,time; sys.dont_write_bytecode=True
import numpy as np
t0=time.time(); A0=6e-6; T=6e-6; n=4096; ext=13.5e-6; h=2*ext/n
ax=(np.arange(n)+0.5)*h-ext; r=np.hypot(*np.meshgrid(ax,ax,indexing="xy")); ring=(r>=A0)&(r<A0+T)
u=np.zeros((n,n),bool)
for k,rad in enumerate([7.25e-6,9e-6,10.75e-6]):
    off=math.pi/32 if k%2 else 0
    for j in range(32):
        an=2*math.pi*j/32+off; cx,cy=rad*math.cos(an),rad*math.sin(an); R=1.25e-6
        i0=max(0,int((cx-R+ext)/h)-1); i1=min(n,int((cx+R+ext)/h)+2); j0=max(0,int((cy-R+ext)/h)-1); j1=min(n,int((cy+R+ext)/h)+2)
        X,Y=np.meshgrid(ax[i0:i1],ax[j0:j1],indexing="xy"); u[j0:j1,i0:i1]|=(X-cx)**2+(Y-cy)**2<=R*R
area=float((u&ring).sum()*h*h); json.dump(dict(kind="T96d",exact_area_m2=area,raster=n,elapsed_s=round(time.time()-t0,2)),open("out/exact_T96d.json","w")); print(area,round(time.time()-t0,2))
