"""Static generalized exponential Padé[3/3]; never normalize output states."""
import numpy as np
from scipy.sparse.linalg import splu


class Pade6:
    def __init__(self,mass,generator,step):
        self.roots=np.roots([1.,12.,60.,120.])
        assert np.max(abs(np.poly(self.roots)-np.array([1.,12.,60.,120.])))<=1e-11
        self.factors=[]
        M=mass.astype(np.complex128).tocsc();B=generator.astype(np.complex128).tocsc()
        for root in self.roots:
            coefficient=step/root
            left=M+coefficient*B;right=M-coefficient*B
            self.factors.append((splu(left),right))

    def advance(self,field,steps):
        value=np.asarray(field,dtype=np.complex128).copy()
        for _ in range(steps):
            for factor,right in self.factors:value=factor.solve(right@value)
        return value
