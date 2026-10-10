import os, sys, json, math, importlib.util, time
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
import numpy as np
from v4_fd2d import solve, K0
a=6.0; n1=1.444; n2=1.439
spec=importlib.util.spec_from_file_location("ap","../acoplo_claude/acoplo_paralelo.py"); AP=importlib.util.module_from_spec(spec); spec.loader.exec_module(AP)
out={}
for d,h,L in [(20.0,0.5,40.0),(20.0,0.25,40.0),(16.0,0.5,40.0),(16.0,0.25,40.0),(24.0,0.25,40.0),(20.0,0.25,50.0)]:
    def f(X,Y,d=d):
        c=((X-d/2)**2+Y**2<a*a)|((X+d/2)**2+Y**2<a*a); return np.where(c,n1*n1,n2*n2)
    t=time.time()
    ne,ps,x=solve(f,L,h,1.44219,6,ss=4)
    # los dos primeros (simetrico/antisimetrico)
    b=np.sqrt(ne**2*K0**2); b2=(ne*K0)**2
    ds=b2[0]-b2[1]; dbeta=ds/(b[0]+b[1]); kfd=dbeta/2
    kc=AP.kappa(d)
    # simetria para etiquetar: paridad en x
    X,Y=np.meshgrid(x,x)
    par=[float((p*p[:, ::-1]).sum()*h*h) for p in ps[:2]]
    out[f"d{d:g}_h{h:g}_L{L:g}"]=dict(neff=[float(v) for v in ne[:4]],parity=par,dbeta=float(dbeta),kappa_FD=float(kfd),kappa_acoplo=float(kc),ratio=float(kfd/kc),t=round(time.time()-t))
    print(f"d={d} h={h} L={L}",json.dumps(out[f"d{d:g}_h{h:g}_L{L:g}"]),flush=True)
    json.dump(out,open("v4_k2_resultados.json","w"),indent=1)
