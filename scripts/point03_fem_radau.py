"""Generalized Padé[2/3] (Radau IIA order five), independent time family."""
import numpy as np
from scipy.sparse.linalg import splu


class Radau5:
    def __init__(self,mass,generator,step):
        self.poles=np.roots([-1.,9.,-36.,60.]);self.zeros=np.roots([3.,24.,60.])
        assert np.max(abs(-np.poly(self.poles)-np.array([-1.,9.,-36.,60.])))<1e-11
        assert np.max(abs(3*np.poly(self.zeros)-np.array([3.,24.,60.])))<1e-11
        M=mass.astype(np.complex128).tocsc();B=generator.astype(np.complex128).tocsc();self.factors=[]
        for index,pole in enumerate(self.poles):
            left=M-step*B/pole;right=M-step*B/self.zeros[index] if index<2 else M
            self.factors.append((splu(left),right))

    def advance(self,field,steps):
        value=np.asarray(field,dtype=np.complex128).copy()
        for _ in range(steps):
            for factor,right in self.factors:value=factor.solve(right@value)
        return value
