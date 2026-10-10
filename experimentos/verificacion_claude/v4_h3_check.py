import os, sys, json, math
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
import numpy as np
a=6.0
H=json.load(open("../observable_claude/out/h3_analisis.json"))["detalle"]
def cover(N,h,m=400):
    ax=(np.arange(N)-N//2)*h; X,Y=np.meshgrid(ax,ax,indexing="xy"); r=np.hypot(X,Y)
    w=(r<a-h*0.7072).astype(float); band=np.abs(r-a)<=h*0.7072
    xb=X[band]; yb=Y[band]; t=(np.arange(m)+0.5)/m-0.5; acc=np.zeros(xb.shape)
    for tt in t:
        xx=xb+tt*h; half=np.sqrt(np.maximum(a*a-xx*xx,0.0))
        lo=np.maximum(yb-h/2,-half); hi=np.minimum(yb+h/2,half); acc+=np.maximum(hi-lo,0.0)
    w[band]=acc/m/h
    return w,(r<a)
out={}
for kind in ["Cd","T96d"]:
    for tag,dx in [("dx4",0.4),("dx5",0.5),("dx6",0.625)]:
        A=np.load(f"../observable_claude/out/state_{kind}_{tag}.npy")
        N=A.shape[0]; h=dx
        w,c=cover(N,h)
        I=np.abs(A)**2
        Pw=float((w*I).sum()*h*h); Pc=float((I*c).sum()*h*h)
        key=f"{dx:g}"
        rec=H[kind]
        out[f"{kind}_{key}"]=dict(N=N,P_exact_mia=Pw,P64_H=rec["P64"]["P"][key],dif_exact_vs_P64=Pw-rec["P64"]["P"][key],
              P_center_mia=Pc,Pc_H=rec["Pc"]["P"][key],dif_center=Pc-rec["Pc"]["P"][key],P_total_remaining=float(I.sum()*h*h))
        print(kind,key,json.dumps(out[f"{kind}_{key}"]),flush=True)
# veredictos Q con mi observable exacto
def Pm(kind,key): return out[f"{kind}_{key}"]["P_exact_mia"]
v={}
for kind in ["Cd","T96d"]:
    d45=abs(Pm(kind,"0.4")-Pm(kind,"0.5")); d56=abs(Pm(kind,"0.5")-Pm(kind,"0.625"))
    v[kind]=dict(diff_04_05=d45,rel=d45/Pm(kind,"0.5"),Q_thr=bool(d45<0.005 and d45/Pm(kind,"0.5")<0.10),diff_05_0625=d56,Q4_monotone=bool(d56>=d45))
print(json.dumps(v,indent=1))
json.dump(dict(estados=out,veredictos_Q_mios=v),open("v4_h3_check.json","w"),indent=1)
