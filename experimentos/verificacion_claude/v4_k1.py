import os, sys, json, math, importlib.util, time
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
import numpy as np
from scipy.optimize import brentq
from scipy.interpolate import CubicSpline
from scipy.stats import norm
spec=importlib.util.spec_from_file_location("ap","../acoplo_claude/acoplo_paralelo.py"); AP=importlib.util.module_from_spec(spec); spec.loader.exec_module(AP)
L=10000.0; XT=math.asin(math.sqrt(0.10))
dstar=brentq(lambda d: AP.kappa(float(d))*L-XT,16.0,30.0,xtol=1e-12)
print("d*",dstar,"delta_max",20-dstar,"P2(20)",math.sin(AP.kappa(20.0)*L)**2,flush=True)
# kappa propia: spline cubica de ln kappa con paso 0.05 en [12,40]
t=time.time()
dg=np.round(np.arange(12.0,40.0+1e-9,0.05),4); lk=np.log([AP.kappa(float(d)) for d in dg]); cs=CubicSpline(dg,lk)
print("tabla kappa",time.time()-t,"s",flush=True)
def passes(d):
    d=np.asarray(d,float); k=np.exp(cs(np.clip(d,12.0,40.0))); return (np.sin(k*L)**2<=0.10)&(d>=12.0)
N=200; SEED=11; R=2000; D0=20.0
U=np.linspace(-12,12,240001)
def E_ana(sig): return float(np.trapezoid(passes(D0+sig*U)*norm.pdf(U),U))
# E de K
K=json.load(open("../registro_claude/registro_resultados.json"))
cells={(c["sigma_um"],c["l_celdas"]):c for c in K["K2_celdas"]}
Z=np.random.default_rng(SEED).standard_normal((R,N))
rows=[]; mx=0; mxa=0
for s in [0.5,1.0,2.0]:
    for l in [0,1,3,10]:
        if l==0: A=np.eye(N)
        else:
            C=np.exp(-np.abs(np.subtract.outer(np.arange(N),np.arange(N)))/l); w,V=np.linalg.eigh(C); A=V*np.sqrt(np.clip(w,0,None))
        f=passes(D0+s*(Z@A.T)).mean(axis=1); Em=float(f.mean())
        Ea=E_ana(s); EK=cells[(s,l)]["E_mc_d20"]; EaK=cells[(s,l)]["E_ana_d20"]
        rows.append(dict(sigma=s,l=l,E_mio=Em,E_K=EK,dif=Em-EK,E_ana_mio=Ea,E_ana_K=EaK,dif_ana=Ea-EaK,dif_mio_vs_ana=Em-Ea,sd_mio=float(f.std(ddof=1)),sd_K=cells[(s,l)]["sd_f_d20"]))
        mx=max(mx,abs(Em-EK)); mxa=max(mxa,abs(Em-EaK)); print(json.dumps(rows[-1]),flush=True)
out=dict(dstar=dstar,delta_max=20-dstar,max_dif_MC_vs_K=mx,max_dif_vs_ana_K=mxa,rows=rows,
  VK1_pass=bool(abs(dstar-20.4345)<=1e-3), VK2_pass=bool(mx<=0.02 and mxa<=0.02))
# K3-C2 identidad
sr=0.2; dcal=dstar+norm.ppf(0.95)*sr
out["K3C2_E_ana_mio"]=float(np.trapezoid(passes(dcal+sr*U)*norm.pdf(U),U)); out["dcal"]=dcal
# cobertura teorica: E(d,sigma)= Phi((d-d*)/sigma) en la rama monotona
out["K3C2_E_formula_Phi"]=float(norm.cdf((dcal-dstar)/sr))
json.dump(out,open("v4_k1_resultados.json","w"),indent=1)
print("VK1",out["VK1_pass"],"VK2",out["VK2_pass"],"max",mx,mxa,"K3C2",out["K3C2_E_ana_mio"],out["K3C2_E_formula_Phi"])
