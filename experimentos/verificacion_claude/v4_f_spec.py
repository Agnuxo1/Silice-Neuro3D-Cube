import os, sys, json, math, time
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
import numpy as np
from v4_fd2d import solve, K0
A_,T_,RM,RT=6.0,6.0,9.0,1.5
NB,NJ=1.444,1.439; RO=12.0
def n2_ring(r1,r2,n):
    def f(X,Y):
        r=np.hypot(X,Y); return np.where((r>=r1)&(r<r2),n*n,NB*NB)
    return f
def n2_tracks(N):
    th=2*math.pi*np.arange(N)/N; cx=RM*np.cos(th); cy=RM*np.sin(th)
    def f(X,Y):
        r=np.hypot(X,Y); m=np.zeros(X.shape,bool)
        near=(r>RM-RT-0.1)&(r<RM+RT+0.1)
        if near.any():
            xs=X[near]; ys=Y[near]; mm=np.zeros(xs.shape,bool)
            for a,b in zip(cx,cy): mm|=((xs-a)**2+(ys-b)**2<=RT*RT)
            m[near]=mm
        return np.where(m,NJ*NJ,NB*NB)
    return f
L=float(sys.argv[1]) if len(sys.argv)>1 else 40.0
h=float(sys.argv[2]) if len(sys.argv)>2 else 0.25
K=int(sys.argv[3]) if len(sys.argv)>3 else 60
cases=[("i",n2_ring(6,12,NJ),1.44219587),("iv",n2_ring(7.5,10.5,NJ),1.4427327)]
for N in [24,48,96,192]: cases.append((f"ii_N{N}",n2_tracks(N),1.4425))
out={}
outp=f"v4_f_spec_L{L:g}_h{h:g}.json"
for name,fn,sg in cases:
    t=time.time()
    neff,psis,x=solve(fn,L,h,sg,K,ss=4)
    X,Y=np.meshgrid(x,x); rr=np.hypot(X,Y); ins=rr<=RO
    W=np.array([float((p*p)[ins].sum()*h*h) for p in psis])
    sel=W>=0.02
    cen=float((W[sel]*neff[sel]).sum()/W[sel].sum()) if sel.any() else None
    jmax=int(np.argmax(W))
    out[name]={"sigma":sg,"n_of_maxW":float(neff[jmax]),"Wmax":float(W[jmax]),"centroid_W>=0.02":cen,"sumW_sel":float(W[sel].sum()),
               "n_sel":[float(v) for v in neff[sel]],"W_sel":[float(v) for v in W[sel]],"neff_range":[float(neff.min()),float(neff.max())],"t_s":round(time.time()-t,1)}
    print(name,json.dumps({k:v for k,v in out[name].items() if k not in("n_sel","W_sel")}),flush=True)
    json.dump(out,open(outp,"w"),indent=1)
