"""Physical-circle quadrature of curved P2 fields; no wave propagation."""
import math
import numpy as np
from scipy.special import roots_legendre
from scipy.sparse import coo_matrix

R=6e-6


def shapes(ref):
    x,y=ref;z=1-x-y
    value=np.array([z*(2*z-1),x*(2*x-1),y*(2*y-1),4*z*x,4*x*y,4*z*y])
    dx=np.array([-(4*z-1),4*x-1,0*x,4*(z-x),4*y,-4*y])
    dy=np.array([-(4*z-1),0*x,4*y-1,-4*x,4*x,4*(z-y)])
    return value,dx,dy


def physical_shapes(points,coords):
    offsets=coords-coords[:,[0]];target=points-coords[:,[0]]
    ref=np.linalg.solve(offsets[:,[1,2]],target)
    for _ in range(15):
        value,dx,dy=shapes(ref);error=target-offsets@value
        jx=offsets@dx;jy=offsets@dy;det=jx[0]*jy[1]-jy[0]*jx[1]
        move=np.array([(jy[1]*error[0]-jy[0]*error[1])/det,(-jx[1]*error[0]+jx[0]*error[1])/det])
        ref+=move
        if np.max(abs(move))<5e-14:break
    value,dx,dy=shapes(ref)
    assert np.max(abs(offsets@value-target))<=1e-12*np.max(abs(offsets))
    return value


def curved_outside(basis):
    coords=basis.doflocs;ed=basis.element_dofs;smallest=chord_min=math.inf
    for k,(i,j) in enumerate(((0,1),(1,2),(0,2))):
        A=coords[:,ed[i]].T/R;E=coords[:,ed[j]].T/R;mid=coords[:,ed[3+k]].T/R
        curved=np.linalg.norm(mid-(A+E)/2,axis=1)>1e-15/R
        for a,z,m in zip(A[curved],E[curved],mid[curved]):
            q=4*m-3*a-z;s=2*(a+z-2*m)
            poly=[float(s@s),2*float(q@s),float(q@q+2*a@s),2*float(a@q),float(a@a)]
            roots=np.roots([4*poly[0],3*poly[1],2*poly[2],poly[3]])
            times=[0.,1.]+[float(root.real) for root in roots if abs(root.imag)<1e-9 and 0<root.real<1]
            smallest=min(smallest,min(float(np.polyval(poly,t)) for t in times))
            d=z-a;t=np.clip(-a@d/(d@d),0,1);chord_min=min(chord_min,float((a+t*d)@(a+t*d)))
    assert smallest>=1-1e-12 and chord_min>=1-1e-12
    return dict(curve_min_radius2=smallest,chord_min_radius2=chord_min)


def classify(vertices):
    r=np.sum(vertices**2,axis=0)
    if r.max()<=1:return 'inside'
    Q=np.vstack((vertices,np.ones(3)));bary=np.linalg.solve(Q,np.array([0.,0.,1.]))
    if np.all(bary>=0):return 'partial'
    distance=math.inf
    for i,j in ((0,1),(1,2),(0,2)):
        a=vertices[:,i];d=vertices[:,j]-a;t=np.clip(-a@d/(d@d),0,1)
        distance=min(distance,float((a+t*d)@(a+t*d)))
    return 'outside' if distance>=1 else 'partial'


def partial(vertices,coords,order):
    cuts=list(vertices[0])+[-1.,1.];lines=[]
    for i,j in ((0,1),(1,2),(0,2)):
        a=vertices[:,i];d=vertices[:,j]-a;dd=float(d@d);dot=float(a@d)
        disc=dot*dot-dd*(float(a@a)-1)
        if disc>=0:
            for t in ((-dot-math.sqrt(disc))/dd,(-dot+math.sqrt(disc))/dd):
                if 0<t<1:cuts.append(float((a+t*d)[0]))
        if abs(d[0])>1e-15:lines.append((min(a[0],a[0]+d[0]),max(a[0],a[0]+d[0]),d[1]/d[0],a[1]-d[1]/d[0]*a[0]))
    lo=max(-1,float(vertices[0].min()));hi=min(1,float(vertices[0].max()))
    cuts=sorted(set([lo,hi]+[float(x) for x in cuts if lo<x<hi]));nodes,weights=roots_legendre(order)
    matrix=np.zeros((6,6));intensity=np.zeros(3);Qinv=np.linalg.inv(np.vstack((vertices,np.ones(3))))
    for left,right in zip(cuts,cuts[1:]):
        if right<=left:continue
        midpoint=(left+right)/2
        active=sorted((line for line in lines if line[0]<midpoint<line[1]),key=lambda line:line[2]*midpoint+line[3])
        if len(active)!=2:continue
        tl,tr=math.asin(left),math.asin(right);theta=tl+(nodes+1)*(tr-tl)/2;x=np.sin(theta);cap=np.cos(theta)
        lower=np.maximum(active[0][2]*x+active[0][3],-cap);upper=np.minimum(active[1][2]*x+active[1][3],cap)
        valid=upper>lower
        if not np.any(valid):continue
        x=x[valid];cap=cap[valid];lower=lower[valid];upper=upper[valid]
        y=lower[:,None]+(nodes[None,:]+1)*(upper-lower)[:,None]/2
        xx=np.broadcast_to(x[:,None],y.shape)
        w=(weights[valid]*cap*(tr-tl)/2)[:,None]*(weights[None,:]*(upper-lower)[:,None]/2)*R**2
        points=np.array([xx.ravel(),y.ravel()]);values=physical_shapes(points*R,coords)
        matrix+=(values*w.ravel())@values.T
        bary=Qinv@np.vstack((points,np.ones(points.shape[1])));assert bary.min()>=-1e-10
        intensity+=bary@w.ravel()
    return matrix,intensity


def assemble(basis,order):
    from skfem.models.poisson import mass
    kinds=[classify(basis.mesh.p[:,basis.mesh.t[:,k]]/R) for k in range(basis.mesh.nelements)]
    full=np.array([k for k,kind in enumerate(kinds) if kind=='inside'],dtype=int)
    pieces=[k for k,kind in enumerate(kinds) if kind=='partial'];C=mass.assemble(basis.with_elements(full))
    rr=[];cc=[];vv=[];intensity=np.zeros(basis.N)
    for k in full:
        ids=basis.element_dofs[:3,k];points=basis.doflocs[:,ids];area=abs(np.linalg.det(points[:,1:]-points[:,[0]]))/2
        intensity[ids]+=area/3
    for k in pieces:
        ids=basis.element_dofs[:,k];vertices=basis.mesh.p[:,basis.mesh.t[:,k]]/R
        local,weights=partial(vertices,basis.doflocs[:,ids],order)
        rr.extend(np.repeat(ids,6));cc.extend(np.tile(ids,6));vv.extend(local.ravel());intensity[ids[:3]]+=weights
    C+=coo_matrix((vv,(rr,cc)),shape=(basis.N,basis.N)).tocsr()
    return C,intensity,dict(full_elements=len(full),partial_elements=len(pieces))
