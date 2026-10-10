import os, sys, json, math
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
import numpy as np
from scipy import special as sp, integrate, optimize
a=6.0; lam=1.55; n1=1.444; n2=1.439; k0=2*math.pi/lam
V=k0*a*math.sqrt(n1*n1-n2*n2)
def F(u):
    w=math.sqrt(V*V-u*u); return u*sp.j1(u)*sp.k0(w)-w*sp.k1(w)*sp.j0(u)
u=optimize.brentq(F,1e-6,min(V,2.4048)-1e-9,xtol=1e-15); w=math.sqrt(V*V-u*u)
# Gamma por cuadratura propia de la funcion de onda, sin formula cerrada
c=sp.j0(u); kk=sp.k0(w)
Pc=integrate.quad(lambda r:2*math.pi*r*(sp.j0(u*r/a)/c)**2,0,a,epsabs=1e-14,epsrel=1e-13)[0]
Po=integrate.quad(lambda r:2*math.pi*r*(sp.k0(w*r/a)/kk)**2,a,np.inf,epsabs=1e-14,epsrel=1e-13)[0]
Gamma=Pc/(Pc+Po); Ptot=Pc+Po
def psi_grid(N,h):
    ax=(np.arange(N)-N//2)*h; X,Y=np.meshgrid(ax,ax,indexing="xy"); r=np.hypot(X,Y)
    p=np.where(r<a,sp.j0(u*r/a)/c,sp.k0(w*np.maximum(r,1e-12)/a)/kk)/math.sqrt(Ptot)
    return X,Y,r,p
def cover_area(X,Y,r,h,m=400):
    wgt=(r<a-h*0.7072).astype(float)
    band=np.abs(r-a)<=h*0.7072
    xb=X[band]; yb=Y[band]
    t=(np.arange(m)+0.5)/m-0.5
    acc=np.zeros(xb.shape)
    for tt in t:
        xx=xb+tt*h
        half=np.sqrt(np.maximum(a*a-xx*xx,0.0))
        lo=np.maximum(yb-h/2,-half); hi=np.minimum(yb+h/2,half)
        acc+=np.maximum(hi-lo,0.0)
    wgt[band]=acc/m/h
    return wgt
def run(hs,Lhalf=40.0):
    rows=[]
    for h in hs:
        N=int(round(2*Lhalf/h)); X,Y,r,p=psi_grid(N,h)
        wc=cover_area(X,Y,r,h)
        Ow=float((wc*p*p).sum()*h*h); Oc=float((p*p*(r<a)).sum()*h*h)
        rows.append(dict(h=h,N=N,err_cov=Ow-Gamma,err_cen=Oc-Gamma,area_rel=float(wc.sum()*h*h/(math.pi*a*a)-1)))
        print(rows[-1],flush=True)
    hh=np.array([q["h"] for q in rows])
    po=lambda key: float(np.polyfit(np.log(hh),np.log(np.abs([q[key] for q in rows])),1)[0])
    return rows,po("err_cov"),po("err_cen")
out={"Gamma_mia":Gamma,"u":u,"w":w}
r1,pw1,pc1=run([0.4,0.2,0.1,0.05]); out["serie_H"]=dict(rows=r1,order_cov=pw1,order_center=pc1)
r2,pw2,pc2=run([6/17.3,6/34.6,6/69.2,6/138.4]); out["serie_no_conmensurable"]=dict(rows=r2,order_cov=pw2,order_center=pc2)
# serie extra de 8 mallas no conmensurables para robustez del orden del indicador
r3,pw3,pc3=run([6/k for k in (11.3,16.1,22.7,32.3,45.7,64.9,91.7,129.7)]); out["serie_8_no_conm"]=dict(rows=r3,order_cov=pw3,order_center=pc3)
H=json.load(open("../observable_claude/out/h2_guia_salto.json"))
out["Gamma_H"]=H["referencia"]["Gamma_closed"]; out["dif_Gamma"]=abs(Gamma-H["referencia"]["Gamma_closed"])
out["H_json_G3_max_rel"]=H["H1"]["H1_G3_max_rel"]; out["H_json_G3_PASS"]=H["H1"]["H1_G3_PASS"]
print("orders",pw1,pc1,pw2,pc2,pw3,pc3,"dGamma",out["dif_Gamma"])
json.dump(out,open("v4_h_resultados.json","w"),indent=1)
