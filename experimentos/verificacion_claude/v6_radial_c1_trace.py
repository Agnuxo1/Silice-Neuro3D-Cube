import json, numpy as np
from scipy import special as sp
from scipy.optimize import brentq
import v6_radial_analitico as Rv
LAM=1550e-9; N0=1.444; K0=2*np.pi/LAM; a=6e-6
R=json.load(open('../radial2_claude/resultados_radial2.json'))
# 1) winding robusto
for dn,t in ((-0.003,6),(-0.003,12),(-0.005,6),(-0.005,12)):
    for n in (40000,400000):
        seg=lambda p,q: p+(q-p)*np.linspace(0,1,n,endpoint=False)
        c=[Rv.K0*dn*1.0000001-100j*0+(-100j),-1.0-100j,-1.0+600j,Rv.K0*dn*1.0000001+600j]
        pts=np.concatenate([seg(c[i],c[(i+1)%4]) for i in range(4)]+[np.array([c[0]])])
        D=Rv.D_and_F(pts,6e-6,t*1e-6,dn)[0]
        ph=np.unwrap(np.angle(D)); 
        print('winding',dn,t,n,round((ph[-1]-ph[0])/(2*np.pi),4),'max|dphase|',round(float(np.max(np.abs(np.diff(ph)))),3))
# 2) traza de continuacion t=7..11
for key,st in R['C2_trace'].items():
    dn=float(key.split('=')[1])
    for s in st:
        r=s.get('root') or s.get('selected')
        if r is None: continue
        gs=complex(r['g_re'],r['g_im']); tu=s['t_um']
        gg=Rv.newton(gs,a,tu*1e-6,dn)
        print(key,'t',tu,'dRe_rel',abs(gg.real-gs.real)/abs(gg.real),'dIm_rel',abs(gg.imag-gs.imag)/abs(gg.imag))
# 3) C1: V y n_eff cerradas propios
for Dl in (0.003,0.005,0.010):
    n1=N0+Dl; V=a*K0*np.sqrt(n1**2-N0**2)
    f0=lambda U: U*sp.jv(1,U)*sp.kv(0,np.sqrt(V*V-U*U))-np.sqrt(V*V-U*U)*sp.kv(1,np.sqrt(V*V-U*U))*sp.jv(0,U)
    f1=lambda U: U*sp.jv(0,U)*sp.kv(1,np.sqrt(V*V-U*U))+np.sqrt(V*V-U*U)*sp.kv(0,np.sqrt(V*V-U*U))*sp.jv(1,U)
    us=np.linspace(1e-6,V-1e-9,20001)
    out={}
    for nm,f in (('l0',f0),('l1',f1)):
        v=f(us); idx=np.where(np.sign(v[:-1])!=np.sign(v[1:]))[0]
        rt=[brentq(f,us[i],us[i+1],xtol=1e-15) for i in idx if np.isfinite(v[i]) and np.isfinite(v[i+1])]
        out[nm]=sorted([float(np.sqrt(K0**2*n1**2-(U/a)**2)/K0) for U in rt],reverse=True)
    rec=[x for x in R['C1'] if abs(x['Delta']-Dl)<1e-12][0]
    print('Delta',Dl,'V',round(V,4),'propio',out)
    for l in ('l0','l1'):
        m=rec['modes'][l]; print('   ',l,'json closed',m['closed_neff'],'E',m['solver_E_neff'],'P',m['solver_P_neff'],'errP/Delta',m.get('abs_err_P_over_Delta'))
