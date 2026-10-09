"""GLASS-009d. Uso: python run009d.py PERFIL DX_um [trozo]. PERFIL in Cd, T96d. Un hijo por invocacion."""
import os,sys,json,time,math,hashlib
os.environ["OMP_NUM_THREADS"]="1"; os.environ["OPENBLAS_NUM_THREADS"]="1"
sys.dont_write_bytecode=True; sys.path.insert(0,"../glass009_claude")
import numpy as np
from adi2d import *
T0=time.time(); A0=6e-6; T=6e-6; DN=-0.003; SS=16

def centres():
    cs=[]
    for k,rad in enumerate([7.25e-6,9e-6,10.75e-6]):
        off=math.pi/32 if k%2 else 0
        for j in range(32):
            an=2*math.pi*j/32+off; cs.append((rad*math.cos(an),rad*math.sin(an)))
    return cs

def modified(px,py,kind,cs):
    r=np.hypot(px,py); m=(r>=A0)&(r<A0+T)
    if kind=="Cd": return m
    u=np.zeros_like(m)
    for cx,cy in cs: u|=(px-cx)**2+(py-cy)**2<=(1.25e-6)**2
    return m&u

def coverage(N,dx,kind):
    """fraccion de cada pixel dentro de la region modificada (supersampling SSxSS) -> array NxN"""
    ax=(np.arange(N)-N//2)*dx; ext=13.5e-6
    ii=np.where(np.abs(ax)<=ext+dx)[0]; x,y=np.meshgrid(ax[ii],ax[ii],indexing="xy"); cov=np.zeros_like(x)
    off=(np.arange(SS)+0.5)/SS-0.5; cs=centres()
    for oy in off:
        for ox in off: cov+=modified(x+ox*dx,y+oy*dx,kind,cs)
    full=np.zeros((N,N)); full[np.ix_(ii,ii)]=cov/(SS*SS); return full

def exact_area(kind,n=4096,ext=13.5e-6):
    ax=(np.arange(n)+0.5)/n*2*ext-ext; x,y=np.meshgrid(ax,ax,indexing="xy"); h=2*ext/n
    return float(modified(x,y,kind,centres()).sum()*h*h)

def area_weights(N,dx,ss=16):
    ax=(np.arange(N)-N//2)*dx; x,y=np.meshgrid(ax,ax,indexing="xy"); w=np.zeros((N,N)); off=(np.arange(ss)+0.5)/ss-0.5
    for oy in off:
        for ox in off: w+=((x+ox*dx)**2+(y+oy*dx)**2<A0*A0)
    return w/(ss*ss)

kind=sys.argv[1]; dx=float(sys.argv[2])*1e-6; chunk=int(sys.argv[3]) if len(sys.argv)>3 else 0; DOM_UM=float(sys.argv[4]) if len(sys.argv)>4 else 128.0
N=int(round(DOM_UM*1e-6/dx)); dz=2.5e-6; tag=f"{kind}_dx{int(round(dx*1e7))}_dom{int(DOM_UM)}"
cov=coverage(N,dx,kind); dn=DN*cov; w=area_weights(N,dx)
ex=json.load(open('out/exact_T96d.json'))['exact_area_m2'] if kind=='T96d' else exact_area(kind)
q1=float(np.abs(dn).sum()*dx*dx/abs(DN)/ex-1)
sig=sigma_map(N,dx); st=Stepper(dn,sig,dx,dz)
per=200; sf=f"out/state_{tag}.npy"
A=gaussian(N,dx,6e-6) if chunk==0 else np.load(sf)
for _ in range(per): A=st.step(A)
np.save(sf,A); fin=(chunk+1)*per>=800
d=dict(kind=kind,dx_um=dx*1e6,N=N,domain_um=N*dx*1e6,chunk=chunk,steps_done=(chunk+1)*per,final=fin,Q1_integral_rel_err=q1,adi2d_sha256=hashlib.sha256(open("../glass009_claude/adi2d.py","rb").read()).hexdigest())
if fin: d["weighted"]=float((w*np.abs(A)**2).sum()*dx*dx)
d["elapsed_s"]=round(time.time()-T0,3)
name=f"out/{tag}"+(f"_c{chunk}" if dx<0.45e-6 else "")+".json"; json.dump(d,open(name,"w"),indent=1); print(json.dumps(d))
