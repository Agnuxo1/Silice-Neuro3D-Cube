import sys, math, json, numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
LAM=1.55; K0=2*math.pi/LAM
d=float(sys.argv[1]); L=float(sys.argv[2]); h=float(sys.argv[3]); s=8
nh=int(round(L/h)); N=2*nh+1; x=(np.arange(N)-(N-1)/2)*h
offs=(np.arange(s)+.5)/s*h-.5*h
xs=(x[:,None]+offs[None,:]).ravel()
n2=np.empty((N,N))
for j0 in range(0,N,32):
    j1=min(N,j0+32); ys=(x[j0:j1,None]+offs[None,:]).ravel(); X,Y=np.meshgrid(xs,ys)
    ins=(np.hypot(X-d/2,Y)<=6)|(np.hypot(X+d/2,Y)<=6)
    n2[j0:j1]=np.where(ins,1.444**2,1.439**2).reshape(j1-j0,s,N,s).mean(axis=(1,3))
M=N-2
T=sp.diags([np.ones(M-1),-2*np.ones(M),np.ones(M-1)],[-1,0,1],format="csr")/h**2
I=sp.identity(M,format="csr")
P=(sp.kron(I,T)+sp.kron(T,I)+sp.diags(K0**2*n2[1:-1,1:-1].ravel())).tocsc()
w,v=sla.eigsh(P,k=2,sigma=K0**2*n2.max(),which="LM")
w=np.sort(w)[::-1]; ne=np.sqrt(w)/K0
kap=K0*(ne[0]-ne[1])/2
print(json.dumps(dict(d=d,L=L,h=h,n_even=ne[0],n_odd=ne[1],kappa_per_um=kap,Lc_um=math.pi/(2*kap))))
