"""GLASS-009b. Uso: python run009b.py CASO DX_um [trozo]. CASO in K1w, Cw, T96w. Un hijo por invocacion."""
import os,sys,json,time,math,hashlib
os.environ["OMP_NUM_THREADS"]="1"; os.environ["OPENBLAS_NUM_THREADS"]="1"
sys.dont_write_bytecode=True; sys.path.insert(0,"../glass009_claude")
import numpy as np
from adi2d import *
T0=time.time(); A0=6e-6
def area_weights(N,dx,a=A0,ss=16):
    ax=(np.arange(N)-N//2)*dx; x,y=np.meshgrid(ax,ax,indexing="xy"); w=np.zeros((N,N))
    off=(np.arange(ss)+0.5)/ss-0.5
    for oy in off:
        for ox in off: w+=((x+ox*dx)**2+(y+oy*dx)**2<a*a)
    return w/(ss*ss)
def profile(kind,N,dx):
    x,y=coords(N,dx); r=np.hypot(x,y); ring=(r>=A0)&(r<A0+6e-6)
    if kind=="Cw": return np.where(ring,-0.003,0.0)
    cs=[]
    for k,rad in enumerate([7.25e-6,9e-6,10.75e-6]):
        off=math.pi/32 if k%2 else 0
        for j in range(32):
            an=2*math.pi*j/32+off; cs.append((rad*math.cos(an),rad*math.sin(an)))
    m=np.zeros_like(x,bool)
    for cx,cy in cs: m|=(x-cx)**2+(y-cy)**2<=(1.25e-6)**2
    return np.where(m&ring,-0.003,0.0)
def obs(A,dx,w):
    x,y=coords(A.shape[0],dx); I=np.abs(A)**2
    return float((w*I).sum()*dx*dx), float(I[x*x+y*y<A0*A0].sum()*dx*dx)     # ponderado, sin ponderar (P0=1)
case=sys.argv[1]; dx=float(sys.argv[2])*1e-6; chunk=int(sys.argv[3]) if len(sys.argv)>3 else 0
N=int(round(128e-6/dx)); w=area_weights(N,dx); dz=2.5e-6
tag=f"{case}_dx{int(round(dx*1e7))}"
def save(d):
    d.update(case=case,dx_um=dx*1e6,N=N,elapsed_s=round(time.time()-T0,3),area_weighted_over_exact=float(w.sum()*dx*dx/(math.pi*A0**2)),adi2d_sha256=hashlib.sha256(open("../glass009_claude/adi2d.py","rb").read()).hexdigest())
    name=f"out/{tag}"+(f"_c{chunk}" if case!="K1w" and dx<0.45e-6 else "")+".json"; json.dump(d,open(name,"w"),indent=1); print(json.dumps(d))
if case=="K1w":
    A,r=propagate(gaussian(N,dx,6e-6),np.zeros((N,N)),dx,dz,200); pw,pu=obs(A,dx,w)
    z=200*dz; zR=b0*36e-12/2; ww=6e-6*math.sqrt(1+(z/zR)**2); an=1-math.exp(-2*A0**2/ww**2)
    save(dict(weighted=pw,unweighted=pu,analytic=an,err_weighted=abs(pw-an),err_unweighted=abs(pu-an)))
else:
    dn=profile(case,N,dx); sig=sigma_map(N,dx); st=Stepper(dn,sig,dx,dz)
    per=400 if dx<0.45e-6 else 800; sf=f"out/state_{tag}.npy"
    A=gaussian(N,dx,6e-6) if chunk==0 else np.load(sf)
    for _ in range(per): A=st.step(A)
    np.save(sf,A); fin=(chunk+1)*per>=800
    d=dict(chunk=chunk,steps_done=(chunk+1)*per,final=fin)
    if fin: d["weighted"],d["unweighted"]=obs(A,dx,w)
    save(d)
