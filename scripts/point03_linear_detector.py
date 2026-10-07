"""K: bilinear field/intensity disk integrals with verified local moments."""
import argparse
import json
import math
import os
from pathlib import Path

for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'

def cuts(x0,x1,y0,y1):
    points=[max(x0,-1.),min(x1,1.)]
    for y in (y0,y1):
        if abs(y)<1:
            x=math.sqrt(1-y*y)
            points.extend(t for t in (-x,x) if points[0]<t<points[1])
    return sorted(set(points))

def moments_theta(rect,order):
    import numpy as np
    from scipy.special import roots_legendre
    x0,x1,y0,y1=rect;h=x1-x0;assert abs((y1-y0)/h-1)<1e-12
    moments=np.zeros((3,3));nodes,weights=roots_legendre(order)
    points=cuts(*rect)
    for a,b in zip(points,points[1:]):
        if not b>a:continue
        midpoint=(a+b)/2;boundary=math.sqrt(max(0.,1-midpoint*midpoint))
        if min(y1,boundary)<=max(y0,-boundary):continue
        lo,hi=math.asin(a),math.asin(b)
        theta=lo+(nodes+1)*(hi-lo)/2;x=np.sin(theta);boundary=np.cos(theta)
        lower=np.maximum(y0,-boundary);upper=np.minimum(y1,boundary)
        tx=(x-x0)/h;u=(upper-y0)/h;l=(lower-y0)/h
        wy=np.array([h*(u**(q+1)-l**(q+1))/(q+1) for q in range(3)])
        wx=weights*boundary*(hi-lo)/2
        for p in range(3):
            for q in range(3):moments[p,q]+=float(np.sum(wx*tx**p*wy[q]))
    return moments

def moments_reference(rect):
    import numpy as np
    from scipy.integrate import quad_vec
    x0,x1,y0,y1=rect;h=x1-x0
    def integrand(x):
        boundary=math.sqrt(max(0.,1-x*x));lower=max(y0,-boundary);upper=min(y1,boundary)
        if upper<=lower:return np.zeros((3,3))
        tx=(x-x0)/h;u=(upper-y0)/h;l=(lower-y0)/h
        return np.outer(np.array([1,tx,tx*tx]),np.array([h*(u**(q+1)-l**(q+1))/(q+1) for q in range(3)]))
    points=cuts(*rect)
    result,error=quad_vec(integrand,points[0],points[-1],points=points[1:-1],epsabs=1e-12*h*h,epsrel=1e-12,limit=300)
    return result,float(error)

class Detector:
    def __init__(self):self.cache={}
    def geometry(self,n):
        import numpy as np
        if n in self.cache:return self.cache[n]
        radius=6e-6;dx=128e-6/n;h=dx/radius
        axis=(np.arange(n)-n//2)*h
        eligible=[i for i in range(n-1) if axis[i]<1 and axis[i+1]>-1]
        indices=[];m16=[];m32=[];partials=[]
        for iy in eligible:
            for ix in eligible:
                rect=[float(axis[ix]),float(axis[ix+1]),float(axis[iy]),float(axis[iy+1])]
                x0,x1,y0,y1=rect
                closest_x=max(x0,min(0.,x1));closest_y=max(y0,min(0.,y1))
                if closest_x**2+closest_y**2>=1:continue
                full=max(x*x+y*y for x in (x0,x1) for y in (y0,y1))<=1
                if full:
                    a=np.array([[h*h/((p+1)*(q+1)) for q in range(3)] for p in range(3)]);b=a.copy()
                else:
                    a=moments_theta(rect,16);b=moments_theta(rect,32)
                    partials.append(dict(iy=iy,ix=ix,rect=rect,index=len(indices)))
                assert np.max(np.abs(a-b))<=1e-13
                assert b[0,0]>0 and np.min(b)>=-1e-13 and np.max(b)<=b[0,0]+1e-13
                indices.append((iy,ix));m16.append(a);m32.append(b)
        data=dict(N=n,h=h,radius_m=radius,indices=np.array(indices,dtype=int),moments16=np.array(m16),moments32=np.array(m32),partials=partials)
        for key in ('moments16','moments32'):
            assert abs(float(data[key][:,0,0].sum())/math.pi-1)<=1e-12,'Circle area closure'
        self.cache[n]=data;return data

    def measure(self,field,n,pin=1.):
        import numpy as np
        assert field.shape==(n,n) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field)) and pin>0
        data=self.geometry(n);iy,ix=data['indices'].T
        a00=field[iy,ix];a10=field[iy,ix+1];a01=field[iy+1,ix];a11=field[iy+1,ix+1]
        coeff=(a00,a10-a00,a01-a00,a11-a10-a01+a00);exp=((0,0),(1,0),(0,1),(1,1))
        i00,i10,i01,i11=(np.abs(a)**2 for a in (a00,a10,a01,a11))
        ci=(i00,i10-i00,i01-i00,i11-i10-i01+i00)
        values={'field':[],'intensity':[]}
        for key in ('moments16','moments32'):
            mom=data[key];pf=0.;pi=0.
            for i,(p,q) in enumerate(exp):
                pi+=float(np.sum(ci[i]*mom[:,p,q]))
                for j,(r,s) in enumerate(exp):pf+=float(np.sum(np.real(coeff[i]*np.conj(coeff[j]))*mom[:,p+r,q+s]))
            factor=data['radius_m']**2/pin;pf*=factor;pi*=factor
            assert pf>=0 and pi>=0 and pf<=pi+1e-12,'Positivity/Jensen'
            values['field'].append(pf);values['intensity'].append(pi)
        return {key:dict(P_core=v[-1],levels=v,change=abs(v[-1]-v[0])) for key,v in values.items()}

def preflight():
    import numpy as np
    from assess_point03_exponential import spatial
    det=Detector();report=dict(pass_=False,geometry=[],polynomials=[],gaussians=[])
    for n in (256,320,400,500,640):
        data=det.geometry(n);report['geometry'].append(dict(N=n,cells=len(data['indices']),partials=len(data['partials']),area_relative_error=abs(float(data['moments32'][:,0,0].sum())/math.pi-1),moment_level_delta=float(np.abs(data['moments16']-data['moments32']).max())))
    n=500;data=det.geometry(n);pool=data['partials'];selection=[pool[i] for i in np.linspace(0,len(pool)-1,16,dtype=int)]
    report['reference_selection']=selection;report['references']=[]
    for item in selection:
        ref,err=moments_reference(item['rect']);actual=data['moments32'][item['index']]
        delta=float(np.abs(ref-actual).max()/data['h']**2);assert delta<=1e-10 and err/data['h']**2<=1e-10
        report['references'].append(dict(iy=item['iy'],ix=item['ix'],delta_relative_cell_area=delta,reference_error_relative_cell_area=err/data['h']**2))
    for n in (256,500,640):
        ax=(np.arange(n)-n//2)*(128e-6/n)/(6e-6);xx,yy=np.meshgrid(ax,ax)
        fields=[('constant',np.ones((n,n),dtype=np.complex128),math.pi*(6e-6)**2),('affine',(xx+1j*yy).astype(np.complex128),math.pi*(6e-6)**2/2),('bilinear',(xx+1j*yy+(1+2j)*xx*yy).astype(np.complex128),17*math.pi*(6e-6)**2/24)]
        for name,field,exact in fields:
            vals=det.measure(field,n);err=abs(vals['field']['P_core']/exact-1);assert err<=1e-10
            report['polynomials'].append(dict(N=n,name=name,field_relative_error=err))
        density=1+.005*xx+.005*yy+.005*xx*yy;assert np.min(density)>0
        vals=det.measure(np.sqrt(density).astype(np.complex128),n);err=abs(vals['intensity']['P_core']/(math.pi*(6e-6)**2)-1);assert err<=1e-10
        report['polynomials'].append(dict(N=n,name='bilinear_density',intensity_relative_error=err))
    truth=1-math.exp(-2)
    for k in (0.,2e5,4e5):
        rows=[]
        for n in (256,320,400,500,640):
            ax=(np.arange(n)-n//2)*128e-6/n;xx,yy=np.meshgrid(ax,ax)
            field=(math.sqrt(2/(math.pi*(6e-6)**2))*np.exp(-(xx*xx+yy*yy)/(6e-6)**2)*np.exp(1j*k*xx)).astype(np.complex128)
            rows.append(dict(N=n,methods=det.measure(field,n)))
        controls={}
        for method in ('field','intensity'):
            powers=[r['methods'][method]['P_core'] for r in rows[:4]];screen=spatial(powers)
            covered=abs(powers[-1]-truth)<=screen.get('u_space',-1.)
            assert screen['pass_'] and covered
            controls[method]=dict(screen=screen,N500_exact_error=abs(powers[-1]-truth),indicator_covers_error=covered)
        report['gaussians'].append(dict(k_m_inverse=k,rows=rows,controls=controls))
    report['pass_']=True;return report

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--preflight',type=Path,required=True);args=p.parse_args()
    try:report=preflight()
    except Exception as err:
        import traceback
        report=dict(pass_=False,error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    with args.preflight.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(pass_=report['pass_'],error=report.get('error'))))
    return 0 if report['pass_'] else 1

if __name__=='__main__':raise SystemExit(main())
