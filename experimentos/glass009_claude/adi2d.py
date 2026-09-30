"""Solver ADI-Crank-Nicolson 2D (Peaceman-Rachford) para dA/dz=i/(2b0)lap A + i k0 dn A - sigma A. Independiente de bpm.py (no FFT)."""
import math, numpy as np
lam=1550e-9; n0=1.444; k0=2*math.pi/lam; b0=k0*n0
def coords(N,dx):
    ax=(np.arange(N)-N//2)*dx; return np.meshgrid(ax,ax,indexing="xy")
def sigma_map(N,dx,smax=4e4,frac=0.2):
    x,y=coords(N,dx); e=np.maximum(np.abs(x),np.abs(y))/(N*dx/2)
    return smax*np.maximum((e-(1-frac))/frac,0)**4
def gaussian(N,dx,w,x0=0.0,kt=0.0):
    x,y=coords(N,dx); f=np.exp(-((x-x0)**2+y*y)/w**2)*np.exp(1j*kt*x); return (f/math.sqrt((abs(f)**2).sum()*dx*dx)).astype(complex)
def power(A,dx): return float((np.abs(A)**2).sum()*dx*dx)
class Stepper:
    def __init__(s,dn,sig,dx,dz):
        s.dx=dx; s.h=dz/2; s.c=1j/(2*b0*dx*dx); s.V=1j*k0*dn-sig; h,c,V=s.h,s.c,s.V
        s.sub=-h*c; s.sup=-h*c; s.diag=1+2*h*c-h*V/2      # (I - h Lx - hV/2); misma forma en y
        N=dn.shape[0]
        # factorizacion Thomas a lo largo de axis1 (x) para filas: diag varia con (iy,ix)
        s.fx=s._fact(s.diag); s.fy=s._fact(s.diag.T.copy())
    def _fact(s,d):                      # d[l,i]: l=linea, i=posicion a lo largo
        N=d.shape[1]; cp=np.zeros_like(d); den=np.zeros_like(d)
        den[:,0]=d[:,0]; cp[:,0]=s.sup/den[:,0]
        for i in range(1,N):
            den[:,i]=d[:,i]-s.sub*cp[:,i-1]; cp[:,i]=s.sup/den[:,i]
        return cp,den
    def _solve(s,f,r):                   # r[l,i]
        cp,den=f; N=r.shape[1]; y=np.zeros_like(r)
        y[:,0]=r[:,0]/den[:,0]
        for i in range(1,N): y[:,i]=(r[:,i]-s.sub*y[:,i-1])/den[:,i]
        x=np.zeros_like(r); x[:,-1]=y[:,-1]
        for i in range(N-2,-1,-1): x[:,i]=y[:,i]-cp[:,i]*x[:,i+1]
        return x
    def _lap(s,A,axis):                  # c*(A+ -2A + A-) Dirichlet 0
        L=-2*A; 
        if axis==1: L[:,1:]+=A[:,:-1]; L[:,:-1]+=A[:,1:]
        else: L[1:,:]+=A[:-1,:]; L[:-1,:]+=A[1:,:]
        return s.c*L
    def step(s,A):
        h,V=s.h,s.V
        rhs=(1+h*V/2)*A+h*s._lap(A,0)                   # I + h(Ly+V/2)
        As=s._solve(s.fx,rhs)                            # resolver en x (filas): A*[iy,ix]
        rhs2=(1+h*V/2)*As+h*s._lap(As,1)                 # I + h(Lx+V/2)
        return s._solve(s.fy,rhs2.T.copy()).T            # resolver en y (transpuesta)
def propagate(A,dn,dx,dz,steps,smax=4e4,sponge=True):
    sig=sigma_map(A.shape[0],dx,smax) if sponge else np.zeros_like(dn)
    st=Stepper(dn,sig,dx,dz)
    P0=power(A,dx)
    for _ in range(steps): A=st.step(A)
    return A,dict(P0=P0,P=power(A,dx))
def core_fraction(A,dx,a,P0=None):
    x,y=coords(A.shape[0],dx); return float((np.abs(A)**2)[x*x+y*y<a*a].sum()*dx*dx/(P0 if P0 else 1.0))
