import os, sys, json, time
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
import numpy as np
from v4_fd2d import solve
a=6.0; n1=1.444; n2=1.439
def nxy2(R):
    def f(X,Y):
        n=np.where(np.hypot(X,Y)<a,n1,n2); return (n*(1+(X/R if R else 0.0)))**2
    return f
out={}
for L in [40.0,60.0,80.0]:
    h=0.5
    ne,ps,x=solve(nxy2(None),L,h,1.44219,6,ss=4)
    X,Y=np.meshgrid(x,x); rr=np.hypot(X,Y)
    j=int(np.argmax([float((p*p)[rr<a].sum()*h*h) for p in ps])); n0=float(ne[j]); p0=ps[j]
    ne,ps,x=solve(nxy2(10000.0),L,h,n0+7.4e-5,60,ss=4)
    S=np.array([abs(float((p*p0).sum()*h*h))**2 for p in ps]); Pc=np.array([float((p*p)[rr<a].sum()*h*h) for p in ps])
    o=np.argsort(-S)[:5]
    out[f"L{L:g}"]=dict(n_straight=n0,top5=[dict(neff=float(ne[i]),S=float(S[i]),Pcore=float(Pc[i])) for i in o],
        n_highest=float(ne.max()), centroid_S=float((S*ne).sum()/S.sum()), sumS=float(S.sum()))
    print(L,json.dumps(out[f"L{L:g}"]),flush=True)
json.dump(out,open("v4_i2_resultados.json","w"),indent=1)
