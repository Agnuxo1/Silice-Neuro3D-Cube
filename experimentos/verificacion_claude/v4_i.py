import os, sys, json, math, time
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
import numpy as np
from v4_fd2d import solve, K0
a=6.0; n1=1.444; n2=1.439
def nxy2(R):
    def f(X,Y):
        n=np.where(np.hypot(X,Y)<a,n1,n2)
        return (n*(1+(X/R if R else 0.0)))**2
    return f
out={}
cfgs=[(0.5,40.0),(0.25,40.0),(0.5,30.0),(0.25,30.0)]
for h,L in cfgs:
    rows={}
    t=time.time()
    ne,ps,x=solve(nxy2(None),L,h,1.44219,8,ss=4)
    X,Y=np.meshgrid(x,x); rr=np.hypot(X,Y)
    j=int(np.argmax([float((p*p)[rr<a].sum()*h*h) for p in ps])); n0=float(ne[j]); p0=ps[j]
    rows["straight"]=dict(neff=n0)
    for Rmm in [50,20,10,5]:
        R=Rmm*1000.0
        K=24 if Rmm==5 else 14
        sg=n0+(3e-4 if Rmm==5 else 1e-4)
        ne,ps,x=solve(nxy2(R),L,h,sg,K,ss=4)
        S=np.array([abs(float((p*p0).sum()*h*h))**2 for p in ps])
        Pc=np.array([float((p*p)[rr<a].sum()*h*h) for p in ps])
        xc=np.array([float((p*p*X).sum()*h*h) for p in ps])
        j=int(np.argmax(S))
        rows[f"R{Rmm}"]=dict(neff_best_overlap=float(ne[j]),S=float(S[j]),Pcore=float(Pc[j]),xcentroid=float(xc[j]),D=float(ne[j]-n0),
                              maxPcore=float(Pc.max()),n_at_maxPcore=float(ne[int(np.argmax(Pc))]),neff_range=[float(ne.min()),float(ne.max())])
    out[f"h{h:g}_L{L:g}"]=rows
    print(f"h={h} L={L} t={time.time()-t:.0f}s",json.dumps(rows),flush=True)
    json.dump(out,open("v4_i_resultados.json","w"),indent=1)
