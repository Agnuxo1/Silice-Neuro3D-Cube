import os; os.environ["OMP_NUM_THREADS"]="1"
import numpy as np, scipy.linalg as la, json
from radial_ecs import build, k0, n0
res=[]
for a,t,dn in [(6e-6,6e-6,-0.005),(6e-6,12e-6,-0.005),(10e-6,6e-6,-0.005),(10e-6,6e-6,-0.003),(10e-6,12e-6,-0.003),(15e-6,10e-6,-0.003)]:
    x,r,s,h,H=build(dn,a,t,R0=70e-6,Rmax=150e-6,N=800)
    ev,V=la.eig(H); wgt=r*s*h
    Vn=V/np.sqrt((V*V*wgt[:,None]).sum(0))
    core=np.array([(np.abs(Vn[:,i])**2*wgt.real)[x<a].sum()/(np.abs(Vn[:,i])**2*wgt.real)[x<70e-6].sum() for i in range(len(ev))])
    ok=(ev.real>-2e4)&(np.abs(ev.imag)<5e3)&(x[-1]>0)   # candidatos cercanos al eje real, por debajo del borde
    idx=[i for i in np.argsort(-ev.real) if abs(ev[i].imag)<3e3 and core[i]>0.3][:1]
    for i in idx:
        alpha_db_cm=-2*ev[i].imag*4.343*1e-2
        res.append(dict(a_um=a*1e6,t_um=t*1e6,dn=dn,gamma_re=float(ev[i].real),loss_dB_per_cm=float(abs(alpha_db_cm)),core_frac=float(core[i])))
    if not idx: res.append(dict(a_um=a*1e6,t_um=t*1e6,dn=dn,note="sin modo cuasi-ligado (core_frac>0.3)"))
for r_ in res: print(r_)
json.dump(res,open("modes.json","w"),indent=1)
