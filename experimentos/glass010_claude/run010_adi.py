"""GLASS-010 M7: ADI (observable ponderado + indice por cobertura) vs radial, continuo (6,6,-0.003), P_core(z) en z=0.5,1,1.5,2 mm."""
import os,sys,json,time,math,hashlib
os.environ["OMP_NUM_THREADS"]="1"; os.environ["OPENBLAS_NUM_THREADS"]="1"; sys.dont_write_bytecode=True; sys.path.insert(0,"../glass009_claude")
import numpy as np
from adi2d import *
T0=time.time(); A0=6e-6; T=6e-6; DN=-0.003; SS=16; dx=0.5e-6; N=256; dz=2.5e-6
ax=(np.arange(N)-N//2)*dx; x,y=np.meshgrid(ax,ax,indexing="xy"); off=(np.arange(SS)+0.5)/SS-0.5
cov=np.zeros((N,N)); w=np.zeros((N,N))
for oy in off:
    for ox in off:
        r=np.hypot(x+ox*dx,y+oy*dx); cov+=((r>=A0)&(r<A0+T)); w+=(r<A0)
cov/=SS*SS; w/=SS*SS
st=Stepper(DN*cov,sigma_map(N,dx),dx,dz); A=gaussian(N,dx,6e-6); rad=json.load(open("resultados010_radial.json"))["cases"][0]["series"]
rows=[]
for s in range(1,801):
    A=st.step(A)
    if s%200==0:
        z=s*dz*1e3; p=float((w*np.abs(A)**2).sum()*dx*dx); pr=rad[f"{z:.1f}"]["total"]; rows.append(dict(z_mm=z,adi=p,radial=pr,abs_diff=abs(p-pr),PASS=bool(abs(p-pr)<0.01)))
json.dump(dict(rows=rows,elapsed_s=round(time.time()-T0,2),adi2d_sha256=hashlib.sha256(open("../glass009_claude/adi2d.py","rb").read()).hexdigest(),script_sha256=hashlib.sha256(open(__file__,"rb").read()).hexdigest()),open("out/M7.json","w"),indent=1)
for r in rows: print(r)
print(round(time.time()-T0,1),"s")
