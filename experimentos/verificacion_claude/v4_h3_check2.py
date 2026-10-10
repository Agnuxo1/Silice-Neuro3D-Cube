import json, math, sys, os
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
import numpy as np
J=json.load(open("v4_h3_check.json"))["estados"]
H=json.load(open("../observable_claude/out/h3_analisis.json"))["detalle"]
res={}
for kind in ["Cd","T96d"]:
    P={k:J[f"{kind}_{k}"]["P_exact_mia"]*1e-12 for k in ["0.4","0.5","0.625"]}
    Pc={k:J[f"{kind}_{k}"]["P_center_mia"]*1e-12 for k in ["0.4","0.5","0.625"]}
    d45=abs(P["0.4"]-P["0.5"]); d56=abs(P["0.5"]-P["0.625"])
    c45=abs(Pc["0.4"]-Pc["0.5"]); c56=abs(Pc["0.5"]-Pc["0.625"])
    res[kind]=dict(P_exact=P,d45=d45,rel45=d45/P["0.5"],Q_thr=bool(d45<0.005 and d45/P["0.5"]<0.10),d56=d56,Q4_monotone=bool(d56>=d45),
        Pc_mia_um=Pc,Pc_H={k:H[kind]["Pc"]["P"][k] for k in P},c45_mia=c45,c56_mia=c56,
        max_dif_exact_vs_H_P64=max(abs(P[k]-H[kind]["P64"]["P"][k]) for k in P))
    print(kind,json.dumps(res[kind]),flush=True)
# tie-breaking del indicador en el centro a dx=0.4: unidades SI vs um
for dxum in [0.4,0.5,0.625]:
    N=int(round(128e-6/(dxum*1e-6)))
    idx=np.arange(N)-N//2
    dxsi=dxum*1e-6
    xs=idx*dxsi; X,Y=np.meshgrid(xs,xs)
    insi=(X*X+Y*Y<(6e-6)**2)
    xu=idx*dxum; Xu,Yu=np.meshgrid(xu,xu)
    inum=(Xu*Xu+Yu*Yu<36.0)
    exact_ties=int(((idx[:,None]**2+idx[None,:]**2)*dxum**2==36.0).sum())  # no fiable en float
    print("dx",dxum,"N",N,"nodos in(SI)",int(insi.sum()),"nodos in(um)",int(inum.sum()),"dif",int(insi.sum()-inum.sum()))
    res[f"tie_dx{dxum}"]=dict(N=N,in_SI=int(insi.sum()),in_um=int(inum.sum()))
json.dump(res,open("v4_h3_check2.json","w"),indent=1)
