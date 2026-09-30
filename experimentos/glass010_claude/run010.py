"""GLASS-010 (radial). Uso: python run010.py INDICE_CASO. Un hijo por caso (5 configuraciones, <30 s)."""
import os,sys,json,time,math,hashlib
os.environ["OMP_NUM_THREADS"]="1"; os.environ["OPENBLAS_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
import numpy as np, scipy.linalg as la
T0=time.time()
lam=1550e-9; n0=1.444; k0=2*np.pi/lam; b0=k0*n0; RC=60e-6; WG=6e-6
CASES=[(6,6,-0.003),(6,6,-0.005),(6,12,-0.005),(10,6,-0.005),(10,12,-0.003),(15,10,-0.003)]
ZS=[0.5e-3,1e-3,1.5e-3,2e-3]
def build(dn_ring,a,t,h,R0,Rmax,theta):
    N=int(round(Rmax/h)); x=(np.arange(N)+0.5)*h
    s=np.where(x>R0,np.exp(1j*theta),1.0+0j); r=np.where(x>R0,R0+(x-R0)*np.exp(1j*theta),x)
    dn=np.where((x>=a)&(x<a+t),dn_ring,0.0)
    xf=np.arange(N+1)*h; sf=np.where(xf>R0,np.exp(1j*theta),1.0+0j); rf=np.where(xf>R0,R0+(xf-R0)*np.exp(1j*theta),xf); wf=rf/sf
    L=np.zeros((N,N),complex)
    for j in range(N):
        p=1.0/(r[j]*s[j]*h*h); L[j,j]-=p*(wf[j]+wf[j+1])
        if j>0: L[j,j-1]+=p*wf[j]
        if j<N-1: L[j,j+1]+=p*wf[j+1]
    return x,r,s,L/(2*b0)+np.diag(k0*dn),dn
def analyse(a,t,dn_ring,h,R0,Rmax,theta):
    x,r,s,H,dn=build(dn_ring,a,t,h,R0,Rmax,theta); ev,V=la.eig(H); W=r*s*h
    Vn=V/np.sqrt((V*V*W[:,None]).sum(0))
    ph=x<RC; wr=x*h   # peso fisico real 2*pi omitido (se cancela en cocientes)
    core_frac=np.array([(np.abs(Vn[x<a,i])**2*wr[x<a]).sum()/(np.abs(Vn[ph,i])**2*wr[ph]).sum() for i in range(len(ev))])
    psi_in=np.exp(-(x/WG)**2).astype(complex); c=(Vn*W[:,None]).T@psi_in
    Pin=(np.abs(psi_in[ph])**2*wr[ph]).sum()
    M1=dict(core_nodes_times_h_um=float((x<a).sum()*h*1e6),ring_nodes_times_h_um=float(((x>=a)&(x<a+t)).sum()*h*1e6))
    recon=np.linalg.norm((Vn@c-psi_in)[ph])/np.linalg.norm(psi_in[ph])
    return dict(x=x,ev=ev,Vn=Vn,core=core_frac,c=c,Pin=Pin,wr=wr,ph=ph,M1=M1,recon=float(recon),a=a)
def grid_fn(x,v,ph,grid):
    f=np.interp(grid,x[ph],v[ph].real)+1j*np.interp(grid,x[ph],v[ph].imag); return f
def pick_nominal(d):
    ok=[i for i in np.argsort(-d["ev"].real) if abs(d["ev"][i].imag)<3000 and d["core"][i]>0.3]; return ok
if __name__=="__main__":
    ci=int(sys.argv[1]); a_um,t_um,dn=CASES[ci]; a=a_um*1e-6; t=t_um*1e-6
    configs={"nom":dict(h=0.25e-6,R0=70e-6,Rmax=150e-6,theta=0.6),"h0.2":dict(h=0.2e-6,R0=70e-6,Rmax=150e-6,theta=0.6),"h0.125":dict(h=0.125e-6,R0=70e-6,Rmax=150e-6,theta=0.6),
             "R0_90":dict(h=0.25e-6,R0=90e-6,Rmax=170e-6,theta=0.6),"theta0.8":dict(h=0.25e-6,R0=70e-6,Rmax=150e-6,theta=0.8)}
    grid=np.linspace(0.3e-6,RC,300); out=dict(case=dict(a_um=a_um,t_um=t_um,dn=dn),configs={}); ref=None
    for name,cf in configs.items():
        d=analyse(a,t,dn,cf["h"],cf["R0"],cf["Rmax"],cf["theta"]); ok=pick_nominal(d)
        if name=="nom":
            if not ok: out["configs"][name]=dict(note="sin modo cuasi-ligado (criterio 006a)",M1=d["M1"],M2_recon=d["recon"]); break
            j=ok[0]; ref=grid_fn(d["x"],d["Vn"][:,j],d["ph"],grid)
        else:
            pool=ok[:6] if ok else []
            ov=[abs(np.sum(ref*grid_fn(d["x"],d["Vn"][:,k],d["ph"],grid)*grid))/math.sqrt(abs(np.sum(ref*ref*grid))*abs(np.sum(grid_fn(d["x"],d["Vn"][:,k],d["ph"],grid)**2*grid))) for k in pool]
            if not pool: out["configs"][name]=dict(note="sin candidato",M1=d["M1"]); continue
            j=pool[int(np.argmax(ov))]
        g=d["ev"][j]; psi0=d["Vn"][:,j]; c0=d["c"][j]; x=d["x"]; ph=d["ph"]; wr=d["wr"]; a_=d["a"]; Pin=d["Pin"]
        eta=float(abs(c0)**2*(np.abs(psi0[ph])**2*wr[ph]).sum()/Pin)
        zs={}
        for z in ZS:
            full=d["Vn"]@(d["c"]*np.exp(1j*d["ev"]*z)); mode=c0*psi0*np.exp(1j*g*z); rest=full-mode
            P=lambda f,m: float((np.abs(f[m])**2*wr[m]).sum()/Pin)
            core=x<a_; zs[f"{z*1e3:.1f}"]=dict(P_core_total=P(full,core),P_core_mode=P(mode,core),P_core_rest=P(rest,core),P_mode_total=P(mode,ph),P_phys_total=P(full,ph),ratio_mode_over_total=P(mode,core)/max(P(full,core),1e-300))
        out["configs"][name]=dict(cfg={k:(v*1e6 if k!="theta" else v) for k,v in cf.items()},gamma_re=float(g.real),gamma_im=float(g.imag),loss_dB_per_cm=float(2*g.imag*4.343e-2),core_frac=float(d["core"][j]),
            overlap_bilinear=(1.0 if name=="nom" else float(max(ov))),eta=eta,M1=d["M1"],M2_recon=d["recon"],z_mm=zs,top_candidates_re=[float(d["ev"][k].real) for k in ok[:3]],growth=bool(g.imag<-1e-6*abs(g.real)))
    out["elapsed_s"]=round(time.time()-T0,2); out["script_sha256"]=hashlib.sha256(open(__file__,"rb").read()).hexdigest()
    json.dump(out,open(f"out/case{ci}.json","w"),indent=1); print(ci,out["elapsed_s"],"s")
