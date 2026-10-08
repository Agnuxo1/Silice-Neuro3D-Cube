"""Piecewise-polynomial positive damping quadrature, split at all kinks."""
import numpy as np
from scipy.sparse import coo_matrix
from skfem.quadrature import get_quadrature_tri
from point03_fem_detector import physical_shapes


def clip(poly,normal,offset):
    output=[]
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        da=float(normal@a-offset);db=float(normal@b-offset)
        if da>=0:output.append(a)
        if (da>=0)!=(db>=0):output.append(a+(b-a)*da/(da-db))
    return np.asarray(output).reshape(-1,2)


def assemble(basis,order):
    reference,weights=get_quadrature_tri(order);rr=[];cc=[];vv=[];count=0
    for element in range(basis.mesh.nelements):
        ids=basis.element_dofs[:,element];coords=basis.doflocs[:,ids]
        vertices=coords[:,:3].T/1e-6
        if np.max(abs(vertices))<51.2:continue
        mids=(coords[:,[0,1,0]]+coords[:,[1,2,2]])/2
        assert np.max(abs(coords[:,3:]-mids))<=1e-12*np.max(np.linalg.norm(coords[:,1:]-coords[:,[0]],axis=0))
        local=np.zeros((6,6));active=False
        for axis,sign in ((0,1),(0,-1),(1,1),(1,-1)):
            other=1-axis;normal=np.zeros(2);normal[axis]=sign
            n1=normal.copy();n1[other]=-1;n2=normal.copy();n2[other]=1
            poly=vertices.copy()
            for n,offset in ((n1,0.),(n2,0.),(normal,51.2)):
                if not len(poly):break
                poly=clip(poly,n,offset)
            if len(poly)<3:continue
            for j in range(1,len(poly)-1):
                triangle=np.array([poly[0],poly[j],poly[j+1]]).T
                transform=triangle[:,1:]-triangle[:,[0]];jac=abs(np.linalg.det(transform))
                if jac<=1e-20:continue
                points=triangle[:,[0]]+transform@reference
                sigma=4e4*np.maximum((sign*points[axis]-51.2)/12.8,0)**4
                shape=physical_shapes(points*1e-6,coords)
                w=weights*jac*1e-12*sigma
                local+=(shape*w)@shape.T;active=True
        if active:
            rr.extend(np.repeat(ids,6));cc.extend(np.tile(ids,6));vv.extend(local.ravel());count+=1
    return coo_matrix((vv,(rr,cc)),shape=(basis.N,basis.N)).tocsr(),count
