"""V6: dispersion analitica por Bessel (nucleo J0, trinchera I0/K0, exterior H1_0) del modelo paraxial radial.
Independiente de RK4/disparo. Resuelve g complejo por Newton y cuenta raices con el principio del argumento.
Modelo (contrato): psi''+psi'/r + Phi psi=0, Phi=2 b0 (k0 dn(r) - g); nucleo y exterior dn=0, trinchera dn."""
import json, numpy as np
from scipy import special as sp
LAM=1550e-9; N0=1.444; K0=2*np.pi/LAM; B0=K0*N0; UM=1e-6
def D_and_F(g,a,t,dn):
    g=np.asarray(g,dtype=complex)
    kc=np.sqrt(-2*B0*g+0j)
    q=np.sqrt(-(2*B0*(K0*dn-g))+0j)
    ko=np.sqrt(-2*B0*g+0j); ko=np.where(ko.real<0,-ko,ko)
    b=a+t
    psa=sp.jv(0,kc*a); dpa=-kc*sp.jv(1,kc*a)
    # psi=A I0(q r)+B K0(q r); psi'=q(A I1 - B K1). Wronskian I0K1+I1K0=1/(q r)
    i0,i1,k0_,k1_=sp.iv(0,q*a),sp.iv(1,q*a),sp.kv(0,q*a),sp.kv(1,q*a)
    # resolver 2x2
    det=i0*(-q*k1_)-k0_*(q*i1)
    Aa=(psa*(-q*k1_)-k0_*dpa)/det
    Bb=(i0*dpa-psa*(q*i1))/det
    psb=Aa*sp.iv(0,q*b)+Bb*sp.kv(0,q*b)
    dpb=q*(Aa*sp.iv(1,q*b)-Bb*sp.kv(1,q*b))
    h0=sp.hankel1(0,ko*b); h1=sp.hankel1(1,ko*b)
    D=dpb*h0+ko*h1*psb          # psi' f - psi f' con f=H0, f'=-k H1
    F=dpb/psb+ko*h1/h0
    return D,F
def newton(g0,a,t,dn,it=60):
    g=complex(g0)
    for _ in range(it):
        e=1e-3*max(abs(g),1)
        f=D_and_F(g,a,t,dn)[0]
        d=(D_and_F(g+e,a,t,dn)[0]-D_and_F(g-e,a,t,dn)[0])/(2*e)
        gn=g-f/d
        if abs(gn-g)<1e-12*abs(g): g=gn;break
        g=gn
    return g
def winding(a,t,dn,re_lo,re_hi,im_lo,im_hi,n=40000):
    seg=lambda p,q: p+(q-p)*np.linspace(0,1,n,endpoint=False)
    c=[re_lo+1j*im_lo,re_hi+1j*im_lo,re_hi+1j*im_hi,re_lo+1j*im_hi]
    pts=np.concatenate([seg(c[i],c[(i+1)%4]) for i in range(4)]+[np.array([c[0]])])
    D=D_and_F(pts,a,t,dn)[0]
    ph=np.unwrap(np.angle(D))
    return (ph[-1]-ph[0])/(2*np.pi), np.max(np.abs(np.diff(np.angle(D)))) 
if __name__=="__main__":
    R=json.load(open('../radial2_claude/resultados_radial2.json'))
    out=[]
    for rec in R['C2']:
        t=rec['t_um']; dn=rec['dn']; sel=rec['selected']
        gs=complex(sel['g_re'],sel['g_im'])
        res={}
        for name,g0 in (('desde_radial2',gs),('desde_-5000+50j',-5000+50j),('desde_-7000+300j',-7000+300j)):
            try:
                gg=newton(g0,6*UM,t*UM,dn)
                res[name]=(gg.real,gg.imag, abs(D_and_F(gg,6*UM,t*UM,dn)[1]))
            except Exception as ex: res[name]=str(ex)
        gA=newton(gs,6*UM,t*UM,dn)
        w,maxstep=winding(6*UM,t*UM,dn,K0*dn*1.0000001,-1.0,-100.0,600.0)
        ecs=rec['ecs_nominal']
        out.append(dict(t=t,dn=dn,g_radial2=(gs.real,gs.imag),g_analitico=(gA.real,gA.imag),
            dRe_rel_radial2_vs_ana=abs(gA.real-gs.real)/abs(gA.real), dIm_rel=abs(gA.imag-gs.imag)/abs(gA.imag),
            loss_ana=2*gA.imag*4.343e-2, loss_radial2=sel['loss_dB_cm'], loss_ecs=ecs['loss'],
            g_ecs=(ecs['gamma_re'],ecs['gamma_im']),
            dRe_rel_ecs_vs_ana=abs(ecs['gamma_re']-gA.real)/abs(gA.real),
            dIm_rel_ecs_vs_ana=abs(ecs['gamma_im']-gA.imag)/abs(gA.imag),
            dloss_rel_ecs_vs_ana=abs(ecs['loss']-2*gA.imag*4.343e-2)/(2*gA.imag*4.343e-2),
            starts=res, n_raices_ventana=round(w,3), max_salto_fase=maxstep))
    for o in out: print(json.dumps(o)); print()
    json.dump(out,open('v6_radial_analitico.json','w'),indent=1)
