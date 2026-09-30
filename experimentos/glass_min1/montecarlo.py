import numpy as np, sys
sys.path.insert(0,'.')
from oracle import *; from sim_cmt import *
X=test_states(); T=np.array([target_intensity(x) for x in X])[:,[0,2,1,3]]
p=np.load('phases.npy'); th,ph=p[:4],p[4:]
def relerr(U):
    I=np.abs(X@U.T)**2; m=T>0.05     # ignora salidas casi nulas (ruido de medida domina)
    return np.mean(np.abs(I-T)[m]/T[m])
r=np.random.default_rng(7); N=400
print("sanity nominal relerr", relerr(mesh(th,ph)))
print("--- (a) error de fase sigma (rad), acoplo perfecto")
for s in [0.02,0.05,0.1,0.2,0.4]:
    e=[relerr(mesh(th,ph,dph_in=r.normal(0,s,4),dph_mid=r.normal(0,s,4))) for _ in range(N)]
    print(f"sigma_phi={s:5.2f} rad  relerr mean={np.mean(e):.3f} p95={np.percentile(e,95):.3f}")
print("--- (b) error de acoplo kappa*L (sigma en rad; pi/4 nominal), fase perfecta")
for s in [0.01,0.03,0.05,0.1,0.2]:
    e=[relerr(mesh(th,ph,dkl=r.normal(0,s,4))) for _ in range(N)]
    print(f"sigma_kL={s:5.2f} rad  relerr mean={np.mean(e):.3f} p95={np.percentile(e,95):.3f}")
print("--- (c) control negativo: fase mid[1] += pi ; acoplador (0,2) anulado")
print("phase+pi:", relerr(mesh(th,ph+np.array([0,np.pi,0,0]))))
print("coupler off:", relerr(mesh(th,ph,dkl=[-np.pi/4,0,0,0])))
print("--- (d) conservacion de energia (perdida 1 dB): norma^2 de salida/entrada")
U=mesh(th,ph,loss_db=1.0); print(np.mean(np.sum(np.abs(X@U.T)**2,axis=1)), "esperado",10**-0.1)
print("--- (e) mapeo a indice: dphi=2*pi*dn*L/lam, L=10mm, lam=1550nm")
for s in [0.05,0.1,0.2]: print(f"sigma_phi={s} rad => dn_rms={s*1.55e-6/(2*np.pi*1e-2):.2e}")
print("--- (f) mapeo a gap: kL ~ exp(-g/g0); dkL=kL*dg/g0, kL=pi/4, g0 SUPUESTO 1.5um")
for s in [0.03,0.05,0.1]: print(f"sigma_kL={s} => sigma_gap={s/(np.pi/4)*1.5*1000:.0f} nm")
