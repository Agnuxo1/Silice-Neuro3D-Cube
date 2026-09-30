"""Simulador de modos acoplados por secciones (independiente del oraculo): dA/dz=-i M A, expm por tramo.
Parametros de acoplo: kappa(g)=k0*exp(-(g-g_ref)/g0) [SUPUESTO, no medido]."""
import numpy as np
from scipy.linalg import expm
def section(n, pairs, kappa, L, dbeta=None):
    M=np.zeros((n,n),complex)
    for (i,j),k in zip(pairs,kappa): M[i,j]=M[j,i]=k
    if dbeta is not None: M+=np.diag(dbeta)
    return expm(-1j*M*L)
def phase_layer(ph): return np.diag(np.exp(1j*np.asarray(ph)))
def mesh(theta, phi, klen=np.pi/4, dkl=(0,0,0,0), dph_in=0, dph_mid=0, loss_db=0.0):
    """Coupler layers: (0,2),(1,3) then (0,1),(2,3). klen = kappa*L nominal (pi/4 => 50/50)."""
    dkl=np.asarray(dkl)
    A=section(4,[(0,2),(1,3)],[1,1],1.0)  # placeholder, replaced below
    k1=klen+dkl[:2]; k2=klen+dkl[2:]
    S1=section(4,[(0,2),(1,3)],k1,1.0)  # kappa*L folded: L=1, kappa=klen
    S2=section(4,[(0,1),(2,3)],k2,1.0)
    P0=phase_layer(np.asarray(theta)+dph_in); P1=phase_layer(np.asarray(phi)+dph_mid)
    U=S2@P1@S1@P0
    return U*10**(-loss_db/20)
