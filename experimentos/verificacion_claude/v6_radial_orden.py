"""V6: orden observado REAL del disparo RK4 a pasos gruesos (el contrato C3 solo midio a h0=5 nm, ya saturado)."""
import sys, json, numpy as np
sys.dont_write_bytecode=True
sys.path.insert(0,'../radial2_claude')
import radial2 as R
import v6_radial_analitico as Rv
a=6e-6; UM=1e-6
Dl=0.010; n1=R.N0+Dl
closed=sorted(R.closed_roots(a,n1,R.N0,0),reverse=True)[0]
print('closed LP01',repr(closed))
errs=[]
hs=[0.8,0.4,0.2,0.1,0.05]
for h in hs:
    xs=np.linspace(R.N0+1e-9,n1-1e-9,400)
    rt=max(R.real_roots(xs,[(0.0,a,Dl)],0,'E',h*UM))
    errs.append(abs(rt-closed)); print('modelo E h(um)=',h,'err',errs[-1])
print('ordenes E',[float(np.log2(errs[i]/errs[i+1])) for i in range(len(errs)-1)])
# trinchera t=12 dn=-0.003 contra analitica
dn=-0.003; t=12e-6
layers=[(0.0,a,0.0),(a,a+t,dn)]
gA=Rv.newton(-6144.77+8.5j,a,t,dn)
import run_radial2_r2 as RR
e=[]
for h in [0.8,0.4,0.2,0.1,0.05]:
    g,conv=RR.sec_root(gA+3.0,gA+3.3,layers,h*UM,R.R0_DEFAULT)
    e.append(abs(g-gA)); print('trinchera t=12 h(um)',h,'conv',conv,'|g-g_ana|',e[-1],'rel',e[-1]/abs(gA))
print('ordenes trinchera',[float(np.log2(e[i]/e[i+1])) for i in range(len(e)-1)])
# sensibilidad a r0
for r0 in (0.04e-6,0.02e-6,0.01e-6,0.005e-6):
    g,conv=RR.sec_root(gA+3.0,gA+3.3,layers,0.1*UM,r0)
    print('r0(um)',r0/UM,'|g-g_ana|',abs(g-gA))
