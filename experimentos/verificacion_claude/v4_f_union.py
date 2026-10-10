import os, sys, json, math, time
os.environ["OMP_NUM_THREADS"]="1"
sys.dont_write_bytecode=True
import numpy as np
from v4_fd2d import solve, K0
A_,T_,RM,RT=6.0,6.0,9.0,1.5
NB,NJ=1.444,1.439
RO=A_+T_

# (a) fraccion de union por integracion angular (independiente de la malla fina de F)
def f_union_angular(N, nr=4000):
    th=2*math.pi*np.arange(N)/N
    # gauss-legendre en r in [6,12]
    xg,wg=np.polynomial.legendre.leggauss(nr)
    r=0.5*(RO-A_)*(xg+1)+A_; w=0.5*(RO-A_)*wg
    tot=0.0
    for ri,wi in zip(r,w):
        # el disco k cubre el arco |phi-th_k|<=acos((r^2+RM^2-RT^2)/(2 r RM)) si |argumento|<=1
        c=(ri*ri+RM*RM-RT*RT)/(2*ri*RM)
        if c>=1.0: continue
        if c<=-1.0: cov=2*math.pi
        else:
            half=math.acos(c)
            # union de N arcos [th_k-half, th_k+half] en el circulo
            if 2*half*N>=2*math.pi*(1+1e-12) and (2*math.pi/N)<=2*half:
                cov=2*math.pi
            else:
                cov=N*2*half
        tot+=wi*ri*cov
    return tot/(math.pi*(RO**2-A_**2))
res={}
for N in [8,16,24,32,48,64,96,12,20,40,72,128,256,1024]:
    res[N]=f_union_angular(N)
print("f_union angular:",{k:round(v,5) for k,v in res.items()})
json.dump({"f_union_angular":res},open("v_f_union.json","w"),indent=1)
