import os, sys, json, math
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import hankel1
from scipy.optimize import root
K0=2*math.pi/1.55; NB=1.444
def mismatch(neff, r1, r2, nring):
    neff=complex(neff)
    def seg(rs,re,n,y0):
        k2=K0**2*(n*n-neff**2)
        f=lambda r,y:[y[1],-y[1]/r-k2*y[0]]
        s=solve_ivp(f,[rs,re],y0,method="DOP853",rtol=1e-12,atol=1e-14); return s.y[:,-1]
    # nucleo: y=J0 regular: y(r)=1 + ..., arrancar en r=1e-6 con y=1,y'=-k2 r/2
    k2c=K0**2*(NB**2-neff**2); r0=1e-6
    y0=[1+0j,-k2c*r0/2]
    y=seg(r0,r1,NB,y0) if r1>r0 else y0
    y=seg(r1,r2,nring,list(y))
    q0=K0*np.sqrt(NB**2-neff**2+0j)
    H0=hankel1(0,q0*r2); H1=hankel1(1,q0*r2)
    return y[1]*H0+y[0]*q0*H1   # y'/y = -q0 H1/H0
def find(r1,r2,nring,start):
    f=lambda v:[mismatch(v[0]+1j*v[1],r1,r2,nring).real, mismatch(v[0]+1j*v[1],r1,r2,nring).imag]
    s=root(f,[start.real,start.imag],tol=1e-14,method="hybr")
    return complex(s.x[0],s.x[1]),bool(s.success)
F=json.load(open("../tracks_claude/resultados.json"))["analytic"]
out={}
for name,(r1,r2,nr) in {"i":(6,12,1.439),"iv":(7.5,10.5,1.439)}.items():
    z,ok=find(r1,r2,nr,complex(F[name]["Re_neff"]+3e-5,F[name]["Im_neff"]*0.5))
    out[name]=dict(mia=[z.real,z.imag],F=[F[name]["Re_neff"],F[name]["Im_neff"]],dRe=z.real-F[name]["Re_neff"],dIm=z.imag-F[name]["Im_neff"],ok=ok)
    print(name,out[name],flush=True)
for N in [24,48,64]:
    key=f"iii_N{N}"; nr=F[key]["n_ring"]
    z,ok=find(6,12,nr,complex(F[key]["Re_neff"]+3e-5,F[key]["Im_neff"]*0.5))
    out[key]=dict(mia=[z.real,z.imag],F=[F[key]["Re_neff"],F[key]["Im_neff"]],dRe=z.real-F[key]["Re_neff"],dIm=z.imag-F[key]["Im_neff"],ok=ok)
    print(key,out[key],flush=True)
json.dump(out,open("v4_f_analitica.json","w"),indent=1)
