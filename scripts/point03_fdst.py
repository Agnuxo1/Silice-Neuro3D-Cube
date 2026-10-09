"""Fourth-order splitting with exact FD kinetic propagation by DST-I."""
import argparse
from datetime import datetime,timezone
import json
import math
from pathlib import Path
from run_point03_exponential import operator,write
import numpy as np
from scipy.fft import dstn

class Solver:
    def __init__(self,dn,sigma,dx,dz):
        self.n=dn.shape[0];assert dn.shape==sigma.shape==(self.n,self.n) and np.min(sigma)>=0
        self.dz=dz;self.w1=1/(2-2**(1/3));self.w0=1-2*self.w1
        assert abs(2*self.w1+self.w0-1)<=1e-13 and abs(2*self.w1**3+self.w0**3)<=1e-13
        k0=2*math.pi/1550e-9;beta0=1.444*k0
        j=np.arange(1,self.n+1);lam=-4*np.sin(math.pi*j/(2*(self.n+1)))**2/(dx*dx)
        kinetic=(lam[:,None]+lam[None,:])/(2*beta0)
        self.T1=np.exp(1j*dz*self.w1*kinetic);self.T0=np.exp(1j*dz*self.w0*kinetic)
        potential=1j*k0*dn-sigma;positive=self.w1/2;negative=(self.w1+self.w0)/2
        self.D1=np.exp(dz*positive*potential);self.Dm=np.exp(dz*negative*potential)
        self.max_negative_amplification=float(np.exp(dz*abs(negative)*np.max(sigma)))
        assert self.max_negative_amplification<=1.10
    @staticmethod
    def transform(a):return dstn(a,type=1,axes=(0,1),norm='ortho',workers=1)
    def kinetic(self,a,phase):return self.transform(self.transform(a)*phase)
    def step(self,a):
        a=self.kinetic(a*self.D1,self.T1)*self.Dm
        a=self.kinetic(a,self.T0)*self.Dm
        return self.kinetic(a,self.T1)*self.D1
    def advance(self,a,steps):
        for _ in range(steps):a=self.step(a)
        return a

def preflight():
    from scipy.linalg import expm
    rng=np.random.default_rng(937);n=7;dx=2e-6;dn=rng.uniform(-.003,.001,(n,n));sigma=rng.uniform(0,3e4,(n,n))
    field=(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))).astype(np.complex128)
    zero=np.zeros_like(dn);kin,_=operator(zero,zero,dx);solver=Solver(zero,zero,dx,2e-6)
    actual=solver.kinetic(field,np.exp(1j*(np.angle(solver.T1)/solver.w1)))
    # The kinetic test uses a small enough phase to avoid angle wrapping.
    exact=(expm(2e-6*kin.toarray())@field.ravel()).reshape((n,n))
    error=float(np.linalg.norm(actual-exact)/np.linalg.norm(exact));assert error<=1e-11
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),pass_=False,kinetic_dense_error=error,sine_controls=[],order_controls=[])
    for damping in (0.,12000.):
        n=9;dx=1.4e-6;z=80e-6;steps=160;dn0=-.0007;j=np.arange(1,n+1)
        sine=(np.sin(2*math.pi*j/(n+1))[:,None]*np.sin(3*math.pi*j/(n+1))[None,:]).astype(np.complex128)
        k0=2*math.pi/1550e-9;c=1j/(2*1.444*k0*dx*dx)
        eigenvalue=c*(2*math.cos(2*math.pi/(n+1))+2*math.cos(3*math.pi/(n+1))-4)+1j*k0*dn0-damping
        solver=Solver(np.full((n,n),dn0),np.full((n,n),damping),dx,z/steps);actual=solver.advance(sine,steps);exact=np.exp(z*eigenvalue)*sine
        error=float(np.linalg.norm(actual-exact)/np.linalg.norm(exact));power=abs(float(np.vdot(actual,actual).real/np.vdot(sine,sine).real)-math.exp(-2*z*damping))
        assert error<=1e-10 and power<=1e-10
        report['sine_controls'].append(dict(sigma=damping,field_relative_error=error,power_error=power,max_negative_amplification=solver.max_negative_amplification))
    n=7;dx=2e-6;z=200e-6;matrix,_=operator(dn,sigma,dx);exact=(expm(z*matrix.toarray())@field.ravel()).reshape((n,n));errors=[]
    for steps in (400,800,1600):
        solver=Solver(dn,sigma,dx,z/steps);actual=solver.advance(field,steps);error=float(np.linalg.norm(actual-exact)/np.linalg.norm(exact));errors.append(error)
        report['order_controls'].append(dict(steps=steps,error=error,max_negative_amplification=solver.max_negative_amplification))
    orders=[math.log2(a/b) for a,b in zip(errors,errors[1:])];assert all(3.8<=p<=4.2 for p in orders) and errors[-1]<=1e-7
    report.update(pass_=True,observed_orders=orders,no_optical_propagation=True);return report

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--preflight',type=Path,required=True);args=p.parse_args()
    try:report=preflight()
    except Exception as err:
        import traceback
        report=dict(pass_=False,error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc(),no_optical_propagation=True)
    write(args.preflight,report);print(json.dumps(report));return 0 if report['pass_'] else 1
if __name__=='__main__':raise SystemExit(main())
