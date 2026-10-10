"""Absorbente de 009c SIN pared de Dirichlet: espectral periodico en caja de 256 um; sigma(|x|,|y|) igual al de la caja de
128 um (banda 51,2-64 um, p=4, smax=4e4) y sigma=smax constante fuera (continua en e=1). El haz que sale decae sin volver.
Uso: python -B verif_vacio_pad.py THETA DX_um   (CPU, OMP=1)"""
import os, sys, math, json
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
import numpy as np
from scipy.fft import fft2, ifft2, fftfreq
lam=1550e-9; n0=1.444; k0=2*math.pi/lam; b0=k0*n0
theta=float(sys.argv[1]); dx=float(sys.argv[2])*1e-6; dom=256e-6; half=64e-6; dz=2.5e-6; every=40
N=int(round(dom/dx)); d2=dx*dx; w0=6e-6; RU=40e-6; kt=b0*theta; zR=b0*w0**2/2
ax=(np.arange(N)-N//2)*dx; x,y=np.meshgrid(ax,ax,indexing="xy")
f=np.exp(-(x*x+y*y)/w0**2)*np.exp(1j*kt*x); A=f/math.sqrt((abs(f)**2).sum()*d2); N0=A[N//2,N//2].real
P0=float((abs(A)**2).sum()*d2)
e=np.maximum(abs(x),abs(y))/half
sig=4e4*np.minimum(np.maximum((e-0.8)/0.2,0),1)**4
band=(e>0.8)&(e<=1.0)   # misma banda que la caja de 128 um
useful=np.hypot(x,y)<RU
def an(z):
    zeta=z/zR; xs=kt*z/b0
    return N0/(1+1j*zeta)*np.exp(-(((x-xs)**2+y*y)/(w0**2*(1+1j*zeta))))*np.exp(1j*kt*x)*np.exp(-1j*kt**2*z/(2*b0))
kx=2*np.pi*fftfreq(N,dx); K2=kx[:,None]**2+kx[None,:]**2
prop=np.exp(-1j*K2*dz/(2*b0)); ah=np.exp(-sig*dz/2)
rows=[]
def rec(s,A):
    z=s*dz; Aa=an(z)
    rows.append(dict(z=z,dP=float((abs(A[useful])**2).sum()*d2-(abs(Aa[useful])**2).sum()*d2)/P0,
      Pband_an=float((abs(Aa[band])**2).sum()*d2), E=float(np.linalg.norm((A-Aa)[useful])/np.linalg.norm(Aa[useful]))))
rec(0,A)
for s in range(1,801):
    A=ifft2(prop*fft2(A*ah))*ah
    if s%every==0: rec(s,A)
zarr=min(r["z"] for r in rows if r["Pband_an"]>1e-4*P0)
W=[r for r in rows if r["z"]>=zarr-1e-12]; m=max(W,key=lambda r:abs(r["dP"]))
print("pad th=%g dx=%g z_arr=%.2f max|dP|/P0=%.3e @ z=%.2f mm ; dP(z=1,2mm)=%.3e %.3e"%(theta,dx*1e6,zarr*1e3,abs(m["dP"]),m["z"]*1e3,
      [r for r in rows if abs(r["z"]-1e-3)<1e-9][0]["dP"],rows[-1]["dP"]))
json.dump(rows,open("verif_vacio_out/pad_th%g_dx%g.json"%(theta,dx*1e6),"w"))
