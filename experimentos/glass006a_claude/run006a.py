import os,sys,json,time,hashlib; os.environ["OMP_NUM_THREADS"]="1"; os.environ["OPENBLAS_NUM_THREADS"]="1"
sys.dont_write_bytecode=True; sys.path.insert(0,"../glass005_claude")
import numpy as np, scipy.linalg as la
from radial_ecs import build,k0,n0
sha=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()
CFG={"nom":dict(N=500,R0=70e-6,Rmax=150e-6,theta=0.6),"A":dict(N=800,R0=70e-6,Rmax=150e-6,theta=0.8),"B":dict(N=700,R0=90e-6,Rmax=200e-6,theta=0.5)}
RC=60e-6
def modes(a,t,dn,c):
    x,r,s,h,H=build(dn,a,t,**c); ev,V=la.eig(H); w=r*s*h
    Vn=V/np.sqrt((V*V*w[:,None]).sum(0)); ph=(x<RC)
    d=np.abs(Vn)**2*np.abs(w)[:,None]
    core=d[x<a].sum(0)/d[ph].sum(0)
    return x,ev,Vn,core,ph
def cands(ev,core):
    ok=[i for i in np.argsort(-ev.real) if abs(ev[i].imag)<3000 and core[i]>0.3]
    return ok
def fun(x,v,ph,grid):  # perfil en malla comun, normalizado (fase global fijada)
    f=np.interp(grid,x[ph],v[ph].real)+1j*np.interp(grid,x[ph],v[ph].imag); f/=np.linalg.norm(f)
    k=np.argmax(np.abs(f)); return f*np.exp(-1j*np.angle(f[k]))
grid=np.linspace(0.2e-6,RC,400)
out={"contract_sha256":sha("CONTRACT.md"),"radial_ecs_sha256":sha("../glass005_claude/radial_ecs.py"),"cases":[]}
t0=time.time()
for a in [6e-6,10e-6]:
  for dn in [-0.003,-0.005]:
    for t in [3e-6,6e-6,9e-6,12e-6,18e-6]:
      rec=dict(a_um=a*1e6,t_um=t*1e6,dn=dn,configs={})
      ref=None
      for name,c in CFG.items():
        x,ev,Vn,core,ph=modes(a,t,dn,c); cs=cands(ev,core)
        if name=="nom":
            if not cs: rec["configs"][name]=dict(note="sin modo cuasi-ligado"); break
            i=cs[0]; ref=fun(x,Vn[:,i],ph,grid)
        else:
            if ref is None: break
            pool=cs[:6] if cs else []
            ov=[abs(np.vdot(ref,fun(x,Vn[:,j],ph,grid))) for j in pool]
            i=pool[int(np.argmax(ov))] if pool else None
        if i is None: rec["configs"][name]=dict(note="sin candidato"); continue
        g=ev[i]; rec["configs"][name]=dict(gamma_re=float(g.real),gamma_im=float(g.imag),loss_dB_per_cm=float(2*g.imag*4.343e-2),core_frac=float(core[i]),
              overlap=(1.0 if name=="nom" else float(max(ov))),top_candidates_re=[float(ev[j].real) for j in cs[:3]],growth=bool(g.imag<-1e-6*abs(g.real)))
      out["cases"].append(rec)
print("tiempo",round(time.time()-t0,1))
# gates
def get(r,k): return r["configs"].get(k,{})
for r in out["cases"]:
    cf=[v for v in r["configs"].values() if "gamma_im" in v]
    r["G1_sign"]=all(v["gamma_im"]>=-1e-6*abs(v["gamma_re"]) for v in cf) if cf else None
    if len(cf)==3:
        L=[v["loss_dB_per_cm"] for v in cf]; R=[v["gamma_re"] for v in cf]
        rel=(max(L)-min(L))/max(abs(np.mean(L)),1e-12); ab=max(L)-min(L)
        r["G2_conv"]=bool((rel<0.10 or ab<0.005) and (max(R)-min(R))/abs(np.mean(R))<0.01)
        r["G2_detail"]=dict(rel=float(rel),abs_dB_cm=float(ab),re_change=float((max(R)-min(R))/abs(np.mean(R))),overlaps=[v["overlap"] for v in cf],loss=L)
    else: r["G2_conv"]=None
# G3
g3=[]
for a in [6.0,10.0]:
  for dn in [-0.003,-0.005]:
    rows=sorted([r for r in out["cases"] if r["a_um"]==a and r["dn"]==dn and get(r,"nom").get("loss_dB_per_cm",0)>0.005 and r["G2_conv"]],key=lambda r:r["t_um"])
    for r1,r2 in zip(rows,rows[1:]):
        gre=get(r1,"nom")["gamma_re"]; kap=np.sqrt(2*k0*n0*(gre-k0*dn))
        pred=np.exp(2*kap*(r2["t_um"]-r1["t_um"])*1e-6); obs=get(r1,"nom")["loss_dB_per_cm"]/get(r2,"nom")["loss_dB_per_cm"]
        g3.append(dict(a_um=a,dn=dn,t1=r1["t_um"],t2=r2["t_um"],ratio_obs=float(obs),ratio_pred=float(pred),within_x2=bool(0.5<obs/pred<2)))
out["G3_tunnel"]=g3
json.dump(out,open("resultados.json","w"),indent=1)
for r in out["cases"]:
    n=get(r,"nom"); print(f"a={r['a_um']:.0f} t={r['t_um']:4.0f} dn={r['dn']}: loss={n.get('loss_dB_per_cm','-')} core={n.get('core_frac','-')} G1={r['G1_sign']} G2={r['G2_conv']} {r.get('G2_detail','')}")
for g in g3: print(g)
