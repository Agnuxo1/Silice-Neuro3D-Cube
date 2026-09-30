"""GLASS-009c. Uso: python run009c.py THETA DOMINIO_um DX_um. Un hijo por invocacion (<30 s)."""
import os,sys,json,time,math,hashlib
os.environ["OMP_NUM_THREADS"]="1"; os.environ["OPENBLAS_NUM_THREADS"]="1"
sys.dont_write_bytecode=True; sys.path.insert(0,"../glass009_claude")
import numpy as np
from adi2d import *
T0=time.time()
theta=float(sys.argv[1]); dom=float(sys.argv[2])*1e-6; dx=float(sys.argv[3])*1e-6
N=int(round(dom/dx)); dz=2.5e-6; steps=800; every=40; w0=6e-6; kt=b0*theta; RU=40e-6
x,y=coords(N,dx); R=np.hypot(x,y); useful=R<RU
edge=np.maximum(np.abs(x),np.abs(y))/(N*dx/2); band=edge>0.8
zR=b0*w0**2/2
A=gaussian(N,dx,w0,0.0,kt); N0=A[N//2,N//2].real      # x=y=0 -> fase de inclinacion 1
def analytic(z):
    zeta=z/zR; xs=kt*z/b0
    return N0/(1+1j*zeta)*np.exp(-(((x-xs)**2+y*y)/(w0**2*(1+1j*zeta))))*np.exp(1j*kt*x)*np.exp(-1j*kt**2*z/(2*b0))
assert np.abs(analytic(0.0)-A).max()<1e-9*np.abs(A).max()
st=Stepper(np.zeros((N,N)),sigma_map(N,dx),dx,dz)
d2=dx*dx; rows=[]
def record(step,A):
    z=step*dz; Aa=analytic(z); na=np.linalg.norm(Aa[useful])
    rows.append(dict(z_m=z,E=float(np.linalg.norm((A-Aa)[useful])/na),Pu_num=float((np.abs(A[useful])**2).sum()*d2),Pu_an=float((np.abs(Aa[useful])**2).sum()*d2),
        P_total_num=float((np.abs(A)**2).sum()*d2),P_band_an=float((np.abs(Aa[band])**2).sum()*d2)))
record(0,A)
for s in range(1,steps+1):
    A=st.step(A)
    if s%every==0: record(s,A)
arr=[r["z_m"] for r in rows if r["P_band_an"]>1e-4]; z_arr=min(arr) if arr else None
res=dict(theta_rad=theta,domain_um=N*dx*1e6,dx_um=dx*1e6,N=N,useful_radius_um=RU*1e6,z_arr_m=z_arr,rows=rows,elapsed_s=round(time.time()-T0,3),
         adi2d_sha256=hashlib.sha256(open("../glass009_claude/adi2d.py","rb").read()).hexdigest())
name=f"out/th{int(round(theta*1000)):03d}_dom{int(round(dom*1e6))}_dx{int(round(dx*1e7))}.json"; json.dump(res,open(name,"w"),indent=1)
print(name,res["elapsed_s"],"z_arr",z_arr,"Emax",max(r["E"] for r in rows))
