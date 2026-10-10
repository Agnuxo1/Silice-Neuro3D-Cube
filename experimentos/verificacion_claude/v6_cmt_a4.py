"""V6: estimacion independiente de kappa (A4) por teoria de modos acoplados con el campo LP01 analitico."""
import numpy as np, json
from scipy.special import jv, kv
from scipy.optimize import brentq
LAM,A,N1,N2=1.55,6.0,1.444,1.439; K0=2*np.pi/LAM
V=K0*A*np.sqrt(N1**2-N2**2)
f=lambda U: U*jv(1,U)*kv(0,np.sqrt(V*V-U*U))-np.sqrt(V*V-U*U)*kv(1,np.sqrt(V*V-U*U))*jv(0,U)
U=brentq(f,1e-3,2.4,xtol=1e-15); W=np.sqrt(V*V-U*U)
beta=np.sqrt(K0**2*N1**2-(U/A)**2)
def psi(x,y,x0):
    r=np.hypot(x-x0,y); C=jv(0,U)/kv(0,W)
    return np.where(r<=A,jv(0,U*np.minimum(r,A)/A),C*kv(0,W*np.maximum(r,A)/A))
h=0.05; xs=np.arange(-60,60+h/2,h); X,Y=np.meshgrid(xs,xs)
p1=psi(X,Y,-8.0); p2=psi(X,Y,8.0)
core2=(np.hypot(X-8.0,Y)<=A)
core1=(np.hypot(X+8.0,Y)<=A)
dn2=N1**2-N2**2
norm=np.sum(p1*p1)*h*h
kap12=K0**2/(2*beta)*dn2*np.sum(p1*p2*core2)*h*h/norm   # kappa_12 (perturbacion del nucleo 2 sobre campo 1)
ov=np.sum(p1*p2)*h*h/norm
print(json.dumps(dict(beta=beta,kappa_cmt_um_inv=kap12,overlap=ov,pred_dn_par_impar=2*kap12/K0)))
