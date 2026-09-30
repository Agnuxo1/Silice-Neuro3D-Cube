"""Segundo oraculo GLASS-005: problema radial m=0, mismo modelo escalar paraxial que bpm.py,
diferencias finitas + escalado complejo exterior (sin sponge, sin dominio periodico).
A(r,z)=psi(r)exp(i g z); [ (1/2b0)(psi''+psi'/r) + k0 dn psi ] = g psi. Perdida potencia = -2 Im g."""
import os; os.environ["OMP_NUM_THREADS"]="1"; os.environ["OPENBLAS_NUM_THREADS"]="1"
import numpy as np, scipy.linalg as la, math, time
lam=1550e-9; n0=1.444; k0=2*np.pi/lam; b0=k0*n0
def build(dn_ring, a=6e-6, t=6e-6, R0=60e-6, Rmax=140e-6, N=700, theta=0.6):
    h=Rmax/N; x=(np.arange(N)+0.5)*h                       # nodos centrados (evita r=0)
    s=np.where(x>R0, np.exp(1j*theta), 1.0+0j)             # dr/dx
    r=np.where(x>R0, R0+(x-R0)*np.exp(1j*theta), x)
    dn=np.where((x>=a)&(x<a+t), dn_ring, 0.0)
    # laplaciano radial: (1/(r s)) d/dx( (r/s) dpsi/dx ), flujos en caras
    xf=np.arange(N+1)*h; sf=np.where(xf>R0,np.exp(1j*theta),1.0+0j)
    rf=np.where(xf>R0,R0+(xf-R0)*np.exp(1j*theta),xf)
    w=rf/sf                                                # (r/s) en caras; w[0]=0 => regularidad
    L=np.zeros((N,N),complex)
    for j in range(N):
        pref=1.0/(r[j]*s[j]*h*h)
        L[j,j]-=pref*(w[j]+w[j+1])
        if j>0: L[j,j-1]+=pref*w[j]
        if j<N-1: L[j,j+1]+=pref*w[j+1]
    H=L/(2*b0)+np.diag(k0*dn)
    return x,r,s,h,H
def core_fraction(dn_ring, z=2e-3, a=6e-6, t=6e-6, w=6e-6, **kw):
    x,r,s,h,H=build(dn_ring,a,t,**kw)
    ev,V=la.eig(H)
    psi0=np.exp(-(x/w)**2).astype(complex)
    # producto no conjugado (operador complejo-simetrico): c=(V^T W psi0)/(V^T W V) con peso W=r s h
    wgt=(r*s*h)
    Vn=V/np.sqrt((V*V*wgt[:,None]).sum(0))
    c=(Vn*wgt[:,None]).T@psi0
    psi=Vn@(c*np.exp(1j*ev*z))
    dens=np.abs(psi)**2                                    # solo valido en region fisica x<=R0
    phys=x<=kw.get('R0',60e-6)
    P=lambda m: 2*np.pi*np.sum(dens[m]*x[m]*h)
    P0=2*np.pi*np.sum(np.abs(psi0)**2*x*h)
    return P(phys&(x<a))/P0, P(phys)/P0, ev, c
if __name__=="__main__":
    t0=time.time()
    print("V=a*k0*sqrt(2 n0|dn|) y cota j01:")
    for dn in [-0.001,-0.003,-0.005]:
        V=6e-6*k0*math.sqrt(2*n0*abs(dn)); f,ftot,ev,c=core_fraction(dn)
        print(f"dn={dn}: V={V:.2f} (j01=2.405)  core/entrada(z=2mm)={f*100:.3f}%  potencia fisica r<60um={ftot*100:.1f}%")
    print("tiempo",round(time.time()-t0,1),"s")
