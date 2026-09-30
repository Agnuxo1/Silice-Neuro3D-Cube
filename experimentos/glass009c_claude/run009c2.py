"""GLASS-009c-2. Uso: python run009c2.py THETA DOM_um DX_um DZ_um TOTAL_PASOS PASOS_POR_TROZO TROZO. Un hijo <30 s; estado en disco."""
import os,sys,json,time,math,hashlib
os.environ["OMP_NUM_THREADS"]="1"; os.environ["OPENBLAS_NUM_THREADS"]="1"
sys.dont_write_bytecode=True; sys.path.insert(0,"../glass009_claude")
import numpy as np
from adi2d import *
T0=time.time()
theta=float(sys.argv[1]); dom=float(sys.argv[2])*1e-6; dx=float(sys.argv[3])*1e-6; dz=float(sys.argv[4])*1e-6
total=int(sys.argv[5]); per=int(sys.argv[6]); chunk=int(sys.argv[7])
N=int(round(dom/dx)); w0=6e-6; kt=b0*theta; RU=40e-6; every=40 if dz>2e-6 else 80
x,y=coords(N,dx); R=np.hypot(x,y); useful=R<RU
edge=np.maximum(np.abs(x),np.abs(y))/(N*dx/2); band=edge>0.8; zR=b0*w0**2/2; d2=dx*dx
A0=gaussian(N,dx,w0,0.0,kt); N0=A0[N//2,N//2].real
def analytic(z):
    zeta=z/zR; xs=kt*z/b0
    return N0/(1+1j*zeta)*np.exp(-(((x-xs)**2+y*y)/(w0**2*(1+1j*zeta))))*np.exp(1j*kt*x)*np.exp(-1j*kt**2*z/(2*b0))
assert np.abs(analytic(0.0)-A0).max()<1e-9*np.abs(A0).max()
tag=f"th{int(round(theta*1000)):03d}_dom{int(round(dom*1e6))}_dx{int(round(dx*1e7))}_dz{int(round(dz*1e8))}"
sf=f"out2/state_{tag}.npy"; rf=f"out2/rows_{tag}.json"
A=A0 if chunk==0 else np.load(sf); rows=[] if chunk==0 else json.load(open(rf))
st=Stepper(np.zeros((N,N)),sigma_map(N,dx),dx,dz)
def record(step,A):
    z=step*dz; Aa=analytic(z); na=np.linalg.norm(Aa[useful])
    rows.append(dict(z_m=z,E=float(np.linalg.norm((A-Aa)[useful])/na),Pu_num=float((np.abs(A[useful])**2).sum()*d2),Pu_an=float((np.abs(Aa[useful])**2).sum()*d2),
        P_total_num=float((np.abs(A)**2).sum()*d2),P_band_an=float((np.abs(Aa[band])**2).sum()*d2)))
base=chunk*per
if chunk==0: record(0,A)
for s in range(1,per+1):
    A=st.step(A)
    if (base+s)%every==0: record(base+s,A)
np.save(sf,A); json.dump(rows,open(rf,"w"))
fin=(chunk+1)*per>=total
if fin:
    arr=[r["z_m"] for r in rows if r["P_band_an"]>1e-4]
    res=dict(theta_rad=theta,domain_um=N*dx*1e6,dx_um=dx*1e6,dz_um=dz*1e6,N=N,useful_radius_um=RU*1e6,z_arr_m=(min(arr) if arr else None),rows=rows,
             adi2d_sha256=hashlib.sha256(open("../glass009_claude/adi2d.py","rb").read()).hexdigest())
    json.dump(res,open(f"out2/{tag}.json","w"),indent=1)
print(tag,"chunk",chunk,"fin",fin,round(time.time()-T0,2),"s")
