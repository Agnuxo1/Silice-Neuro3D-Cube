"""Oraculo GLASS-MIN-1: algebra lineal pura. Sin propagacion. Backend a MATRIZ (etiquetado)."""
import numpy as np
def dft4(): 
    w=np.exp(-2j*np.pi/4); return np.array([[w**(j*k) for k in range(4)] for j in range(4)])/2
def target_intensity(x, U=None):
    U = dft4() if U is None else U
    return np.abs(U@x)**2
def test_states(n=32, seed=0):
    r=np.random.default_rng(seed); x=r.normal(size=(n,4))+1j*r.normal(size=(n,4))
    basis=np.eye(4,dtype=complex); x=np.vstack([basis,x]); return x/np.linalg.norm(x,axis=1,keepdims=True)
