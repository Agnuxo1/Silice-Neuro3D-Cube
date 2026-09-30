"""Uso: python run009.py CASO [trozo]. Un hijo por invocacion; estado en out/state_CASO.npy si el caso se parte."""
import os,sys,json,time,math,hashlib; os.environ["OMP_NUM_THREADS"]="1"; os.environ["OPENBLAS_NUM_THREADS"]="1"
sys.dont_write_bytecode=True
import numpy as np
from adi2d import *
A0=6e-6; T0=time.time()
def profile(kind,N,dx):
    x,y=coords(N,dx); r=np.hypot(x,y); mask=(r>=A0)&(r<A0+6e-6)
    if kind=="cont": return np.where(mask,-0.003,0.0),None
    per={"t48":16,"t96":32,"t192":64,"t88":32}[kind]; wedge=math.radians(30) if kind=="t88" else 0.0
    cs=[]
    for ring,rad in enumerate([7.25e-6,9e-6,10.75e-6]):
        off=math.pi/per if ring%2 else 0
        for j in range(per):
            ang=2*math.pi*j/per+off; sg=(ang+math.pi)%(2*math.pi)-math.pi
            if wedge and abs(sg)<wedge/2: continue
            cs.append((rad*math.cos(ang),rad*math.sin(ang)))
    m=np.zeros_like(x,bool)
    for cx,cy in cs: m|=(x-cx)**2+(y-cy)**2<=(1.25e-6)**2
    m&=mask; return np.where(m,-0.003,0.0),len(cs)
def save(name,d):
    d["elapsed_s"]=round(time.time()-T0,3); d["case"]=name
    json.dump(d,open(f"out/{name}.json","w"),indent=1); print(json.dumps(d))
case=sys.argv[1]; chunk=int(sys.argv[2]) if len(sys.argv)>2 else 0
N=256; dx=0.5e-6; dz=2.5e-6; steps=800
if case=="K1":
    A,r=propagate(gaussian(N,dx,6e-6),np.zeros((N,N)),dx,dz,200); f=core_fraction(A,dx,A0,r["P0"])
    z=200*dz; zR=b0*36e-12/2; w=6e-6*math.sqrt(1+(z/zR)**2); an=1-math.exp(-2*A0**2/w**2)
    save(case,dict(numeric=f,analytic=an,abs_err=abs(f-an),gate=1e-3,PASS=abs(f-an)<1e-3,z_m=z))
elif case=="K2":
    A,_=propagate(gaussian(N,dx,6e-6),np.zeros((N,N)),dx,dz,200); B,_=propagate(gaussian(N,dx,6e-6),np.full((N,N),-1e-3),dx,dz,200)
    c=N//2; ph=np.angle(B[c,c]/A[c,c]); exp_=(k0*(-1e-3)*200*dz); dph=abs((ph-exp_+math.pi)%(2*math.pi)-math.pi)
    df=abs(core_fraction(A,dx,A0)-core_fraction(B,dx,A0))
    save(case,dict(frac_diff=df,phase_err_rad=dph,PASS=bool(df<1e-6 and dph<1e-3)))
elif case=="K3":
    A,r=propagate(gaussian(N,dx,6e-6),np.zeros((N,N)),dx,dz,100,sponge=False)
    save(case,dict(P_ratio_minus1=r["P"]/r["P0"]-1,PASS=abs(r["P"]/r["P0"]-1)<1e-10))
elif case=="K5":
    A,r=propagate(gaussian(N,dx,6e-6,x0=40e-6,kt=2e5),np.zeros((N,N)),dx,dz,200)
    x,y=coords(N,dx); rem=float((np.abs(A)**2)[np.hypot(x,y)<50e-6].sum()*dx*dx)
    save(case,dict(P_in_r50um_final=rem,gate=1e-3,PASS=rem<1e-3,P_total_final=r["P"]))
elif case=="G0":
    sys.path.insert(0,"../../src")
    from silice import bpm, tracks
    g=bpm.Grid(256,128e-6); rows={}
    for k,(per,wd) in {"t48":(16,0),"t96":(32,0),"t192":(64,0),"t88":(32,math.radians(30))}.items():
        mine,_=profile(k,N,dx); theirs,_=tracks.discrete_profile(g,per_ring=per,missing_wedge_rad=wd)
        rows[k]=int(((mine!=0)!=(theirs!=0)).sum())
    ref=bpm.index_profile(g,6e-6,6e-6,-0.003); mine,_=profile("cont",N,dx); rows["cont"]=int(((mine!=0)!=(ref!=0)).sum())
    save(case,dict(pixels_different=rows,PASS=all(v==0 for v in rows.values())))
elif case in ("cont","t48","t96","t192","t88"):
    dn,n=profile(case,N,dx); A,r=propagate(gaussian(N,dx,6e-6),dn,dx,dz,steps)
    save(case,dict(core_fraction=core_fraction(A,dx,A0,r["P0"]),tracks=n,P_final=r["P"],P0=r["P0"],mask_area_m2=float((dn!=0).sum()*dx*dx)))
elif case in ("K4dz","K4dx"):       # continuo, partido en trozos con estado en disco
    if case=="K4dz": Nn,dxx,dzz,tot,per_chunk=256,0.5e-6,1.25e-6,1600,400
    else: Nn,dxx,dzz,tot,per_chunk=320,0.4e-6,2.5e-6,800,400
    sf=f"out/state_{case}.npy"
    if chunk==0: A=gaussian(Nn,dxx,6e-6); done=0
    else: A=np.load(sf); done=chunk*per_chunk
    dn,_=profile("cont",Nn,dxx); sig=sigma_map(Nn,dxx); st=Stepper(dn,sig,dxx,dzz)
    for _ in range(per_chunk): A=st.step(A)
    np.save(sf,A); fin=(done+per_chunk>=tot)
    d=dict(chunk=chunk,steps_done=done+per_chunk,final=fin)
    if fin: d["core_fraction"]=core_fraction(A,dxx,A0,1.0); d["P"]=power(A,dxx)
    save(f"{case}_c{chunk}",d)
