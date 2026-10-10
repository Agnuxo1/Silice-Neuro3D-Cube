import os, sys, json, math, time
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
sys.argv=[sys.argv[0]]+sys.argv[1:]
import numpy as np
from v4_fd2d import solve
import importlib
# reutilizar las definiciones de formas de v4_f_spec sin ejecutar su bucle
src=open("v4_f_spec.py").read().split("L=float(sys.argv[1])")[0]
exec(src)
out={}
for L in [30.0,50.0,60.0]:
    for name,fn,sg in [("i",n2_ring(6,12,NJ),1.44219587),("iv",n2_ring(7.5,10.5,NJ),1.4427327),("ii_N48",n2_tracks(48),1.4427),("ii_N96",n2_tracks(96),1.4427)]:
        h=0.25; t=time.time()
        neff,psis,x=solve(fn,L,h,sg,60,ss=4)
        X,Y=np.meshgrid(x,x); ins=np.hypot(X,Y)<=RO
        W=np.array([float((p*p)[ins].sum()*h*h) for p in psis]); j=int(np.argmax(W))
        out[f"{name}_L{L:g}"]=dict(n_peak=float(neff[j]),Wpeak=float(W[j]),n_second=float(neff[np.argsort(-W)[1]]),W_second=float(np.sort(W)[-2]),t=round(time.time()-t))
        print(name,L,json.dumps(out[f"{name}_L{L:g}"]),flush=True)
        json.dump(out,open("v4_f_L_resultados.json","w"),indent=1)
