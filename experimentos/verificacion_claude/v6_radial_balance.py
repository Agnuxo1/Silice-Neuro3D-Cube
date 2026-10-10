"""V6: balance de energia independiente de Im g: 2 Im g * int_0^b |psi|^2 r dr = Re(k_o) b |psi(b)|^2 / B0 (modelo paraxial)."""
import json, numpy as np
from scipy import special as sp
from scipy.integrate import quad
import v6_radial_analitico as Rv
a=6e-6
res=[]
for dn,t in ((-0.003,6),(-0.003,12),(-0.005,6),(-0.005,12)):
    t*=1e-6; b=a+t
    g=Rv.newton(-6140+100j if dn==-0.003 else -7300+30j,a,t,dn)
    B0,K0=Rv.B0,Rv.K0
    kc=np.sqrt(-2*B0*g+0j); q=np.sqrt(-(2*B0*(K0*dn-g))+0j); ko=np.sqrt(-2*B0*g+0j)
    if ko.real<0: ko=-ko
    psa=sp.jv(0,kc*a); dpa=-kc*sp.jv(1,kc*a)
    i0,i1,k0_,k1_=sp.iv(0,q*a),sp.iv(1,q*a),sp.kv(0,q*a),sp.kv(1,q*a)
    det=i0*(-q*k1_)-k0_*(q*i1)
    Aa=(psa*(-q*k1_)-k0_*dpa)/det; Bb=(i0*dpa-psa*(q*i1))/det
    psi=lambda r: sp.jv(0,kc*r) if r<=a else Aa*sp.iv(0,q*r)+Bb*sp.kv(0,q*r)
    f=lambda r: abs(psi(r))**2*r
    I=quad(f,0,a,epsabs=0,epsrel=1e-12,limit=200)[0]+quad(f,a,b,epsabs=0,epsrel=1e-12,limit=200)[0]
    psb=psi(b)
    lhs=2*g.imag*I; dpb=q*(Aa*sp.iv(1,q*b)-Bb*sp.kv(1,q*b)); rhs=b*(np.conj(psb)*dpb).imag/B0
    core=quad(f,0,a,epsabs=0,epsrel=1e-12)[0]/I
    res.append(dict(dn=dn,t_um=t*1e6,Im_g=g.imag,lhs=lhs,rhs=rhs,rel=abs(lhs-rhs)/lhs,core_frac_hasta_b=core))
    print(json.dumps(res[-1]))
