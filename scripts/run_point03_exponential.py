"""H: independent bounded sparse exponential reference, after G completes."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS'):
    os.environ[key]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,data):
    with Path(p).open('x',encoding='utf-8') as f:
        json.dump(data,f,indent=2,allow_nan=False);f.write('\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def guard(out):
    import psutil
    ram=psutil.virtual_memory().available;disk=psutil.disk_usage(str(out)).free
    assert ram>1.5*1024**3 and disk>2*1024**3
    return dict(utc=datetime.now(timezone.utc).isoformat(),available_ram_bytes=ram,free_disk_bytes=disk)

def operator(dn,sigma,dx):
    import numpy as np
    from scipy.sparse import diags
    n=dn.shape[0];assert dn.shape==sigma.shape==(n,n)
    k0=2*math.pi/1550e-9;c=1j/(2*1.444*k0*dx*dx)
    horizontal=np.ones(n*n-1,dtype=np.complex128)*c
    horizontal[np.arange(1,n)*n-1]=0
    vertical=np.ones(n*n-n,dtype=np.complex128)*c
    diagonal=-4*c+1j*k0*dn.ravel(order='C')-sigma.ravel(order='C')
    matrix=diags([vertical,horizontal,diagonal,horizontal,vertical],[-n,-1,0,1,n],shape=(n*n,n*n),format='csr')
    return matrix,complex(diagonal.sum())

def selfcheck():
    import numpy as np
    from scipy.linalg import expm
    from scipy.sparse.linalg import expm_multiply
    np.random.seed(0);reports=[]
    n=7;dx=2e-6;z=8e-6;rng=np.random.default_rng(937)
    dn=rng.uniform(-.003,.001,(n,n));sigma=rng.uniform(0,3e4,(n,n))
    a=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n));v=a.ravel()
    matrix,trace=operator(dn,sigma,dx);c=1j/(2*1.444*(2*math.pi/1550e-9)*dx*dx)
    loop=np.empty_like(a)
    for y in range(n):
        for x in range(n):
            lap=-4*a[y,x]
            for dy,dxi in ((-1,0),(1,0),(0,-1),(0,1)):
                yy,xx=y+dy,x+dxi
                if 0<=yy<n and 0<=xx<n:lap+=a[yy,xx]
            loop[y,x]=c*lap+(1j*(2*math.pi/1550e-9)*dn[y,x]-sigma[y,x])*a[y,x]
    stencil=float(np.linalg.norm(matrix@v-loop.ravel())/np.linalg.norm(loop))
    exact=expm(z*matrix.toarray())@v
    sparse=expm_multiply(z*matrix,v,traceA=z*trace)
    dense_error=float(np.linalg.norm(sparse-exact)/np.linalg.norm(exact))
    half=expm_multiply(z/2*matrix,v,traceA=z/2*trace)
    half=expm_multiply(z/2*matrix,half,traceA=z/2*trace)
    semigroup=float(np.linalg.norm(half-sparse)/np.linalg.norm(sparse))
    reports += [dict(name='independent_loop_stencil',error=stencil),dict(name='dense_exponential',error=dense_error),dict(name='semigroup',error=semigroup)]
    for damping in (0.,12000.):
        n=9;dx=1.4e-6;dn0=-.0007;j=np.arange(1,n+1)
        sine=np.sin(2*math.pi*j/(n+1))[:,None]*np.sin(3*math.pi*j/(n+1))[None,:]
        matrix,trace=operator(np.full((n,n),dn0),np.full((n,n),damping),dx)
        k0=2*math.pi/1550e-9;c=1j/(2*1.444*k0*dx*dx)
        eigenvalue=c*(2*math.cos(2*math.pi/(n+1))+2*math.cos(3*math.pi/(n+1))-4)+1j*k0*dn0-damping
        exact=np.exp(z*eigenvalue)*sine.ravel()
        sparse=expm_multiply(z*matrix,sine.ravel().astype(np.complex128),traceA=z*trace)
        err=float(np.linalg.norm(sparse-exact)/np.linalg.norm(exact))
        perr=abs(float(np.vdot(sparse,sparse).real/np.vdot(sine.ravel(),sine.ravel()).real)-math.exp(-2*z*damping))
        reports += [dict(name=f'sine_mode_sigma_{damping}',error=err),dict(name=f'power_sigma_{damping}',error=perr)]
    assert all(r['error']<=1e-11 for r in reports)
    return dict(pass_=True,checks=reports,random_seed=0)

def worker(args):
    import numpy as np
    from scipy.sparse.linalg import expm_multiply
    start=time.monotonic();np.random.seed(0)
    report=dict(status='failed',started_utc=datetime.now(timezone.utc).isoformat(),N=args.n,segments=args.segments,segment=args.segment,previous_report_path=str(args.previous) if args.previous else None)
    try:
        report['resource_start']=guard(args.prefix.parent)
        assert sha(args.manifest)==args.manifest_sha
        manifest=json.loads(args.manifest.read_text())
        for p,d in manifest['source_sha256'].items():assert sha(p)==d
        case=next(c for c in manifest['plan'] if c['N']==args.n)
        assert sha(case['input_path'])==case['input_sha256']
        with np.load(case['input_path'],allow_pickle=False) as inp:
            field=inp['A0'].copy();dn=inp['dn'];sigma=inp['sigma']
        if args.previous:
            previous=json.loads(args.previous.read_text());assert previous['segment']==args.segment-1
            assert previous['N']==args.n and previous['segments']==args.segments and previous['status']=='completed'
            assert sha(previous['field_path'])==previous['field_sha256']
            with np.load(previous['field_path'],allow_pickle=False) as inp:field=inp['field'].copy()
            report['previous_report_sha256']=sha(args.previous)
        else:
            assert args.segment==1;report['previous_report_sha256']=None
        dx=128e-6/args.n;matrix,trace=operator(dn,sigma,dx);length=.002/args.segments
        field=expm_multiply(length*matrix,field.ravel(order='C'),traceA=length*trace).reshape((args.n,args.n))
        assert field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
        total=float(np.sum(np.abs(field)**2)*dx*dx);assert 0<total<=1.001
        report.update(status='completed',raw_total=total,nnz=matrix.nnz,trace_real=trace.real,trace_imag=trace.imag,length_m=length)
        report['resource_end']=guard(args.prefix.parent)
    except Exception as err:
        report.update(error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    finally:
        if 'field' in locals():
            np.savez(str(args.prefix)+'.npz',field=field)
            report['field_path']=str(args.prefix)+'.npz';report['field_sha256']=sha(report['field_path'])
        report['elapsed_s']=time.monotonic()-start
        if report['elapsed_s']>360:report.update(status='failed',error='360 s budget exceeded')
        write(str(args.prefix)+'.json',report)
    return 0 if report['status']=='completed' else 1

def run(out,g):
    start=time.monotonic();assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    out.mkdir(parents=True);report=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),results=[])
    try:
        guard(out)
        assert (g/'execution.json').exists() and (g/'assessment.json').exists()
        ge=json.loads((g/'execution.json').read_text());ga=json.loads((g/'assessment.json').read_text())
        assert ge['status']=='completed' and ga['integrity_pass']
        assert json.loads((g/'integrity_audit.json').read_text())['integrity_pass']
        sources=[Path(__file__),ROOT/'scripts/assess_point03_exponential.py',ROOT/'scripts/assess_point03_reconstructed.py',ROOT/'Docs/POINT-03-EXPONENTIAL-REFERENCE-CONTRACT.md',g/'assessment.json',g/'execution.json',g/'integrity_audit.json']
        plan=[]
        for n in (256,320,400,500,640):
            c=next(r for r in ga['rows'] if r['N']==n)
            assert sha(c['input_path'])==c['input_sha256']
            plan.append(dict(N=n,input_path=c['input_path'],input_sha256=c['input_sha256']))
        manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),source_sha256={str(p):sha(p) for p in sources},plan=plan,selfcheck=selfcheck(),g_path=str(g),numerical_threads=1)
        write(out/'manifest.json',manifest);report.update(manifest_path=str(out/'manifest.json'),manifest_sha256=sha(out/'manifest.json'))
        for case in plan:
            n=case['N']
            if n==640:
                write(out/'pre_holdout_execution.json',report)
                assessment=load('h_assess',ROOT/'scripts/assess_point03_exponential.py')
                prediction=assessment.assess(out/'pre_holdout_execution.json',prediction=True)
                write(out/'prediction.json',prediction)
                report.update(prediction_path=str(out/'prediction.json'),prediction_sha256=sha(out/'prediction.json'),holdout_started_utc=datetime.now(timezone.utc).isoformat())
            result=dict(N=n,solutions={})
            for segments in (4,8):
                previous=None;chain=[];caseout=out/f'n{n}_segments{segments}';caseout.mkdir()
                for segment in range(1,segments+1):
                    assert time.monotonic()-start<7200;guard(out)
                    prefix=caseout/f'segment_{segment:02d}'
                    cmd=[sys.executable,str(Path(__file__)), '--worker','--manifest',report['manifest_path'],'--manifest-sha',report['manifest_sha256'],'--n',str(n),'--segments',str(segments),'--segment',str(segment),'--prefix',str(prefix)]
                    if previous:cmd += ['--previous',str(previous)]
                    with Path(str(prefix)+'.log').open('xb') as log:
                        child=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=370,check=False)
                    cp=Path(str(prefix)+'.json');assert cp.exists(),'Missing child report'
                    data=json.loads(cp.read_text());chain.append(dict(path=str(cp),sha256=sha(cp)))
                    assert child.returncode==0 and data['status']=='completed',f'Worker failed N{n} segment{segment}'
                    previous=cp
                    print(json.dumps(dict(N=n,segments=segments,segment=segment,child_s=round(data['elapsed_s'],2),elapsed_s=round(time.monotonic()-start,1))),flush=True)
                result['solutions'][str(segments)]=dict(checkpoints=chain,field_path=data['field_path'],field_sha256=data['field_sha256'])
            report['results'].append(result)
        report.update(status='completed',finished_utc=datetime.now(timezone.utc).isoformat())
        write(out/'pre_assessment_execution.json',report)
        assessment=load('h_assess_final',ROOT/'scripts/assess_point03_exponential.py')
        result=assessment.assess(out/'pre_assessment_execution.json',prediction=False)
        write(out/'assessment.json',result)
        report['scientific_pass']=result['scientific_pass'];report['point03_closed']=result['point03_closed']
    except Exception as err:
        report.update(status='failed',error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    finally:
        report['elapsed_s']=time.monotonic()-start
        report['sources_unchanged']=all(sha(p)==d for p,d in locals().get('manifest',{}).get('source_sha256',{}).items())
        write(out/'execution.json',report)
    print(json.dumps({k:report.get(k) for k in ('status','scientific_pass','point03_closed','elapsed_s','error')}),flush=True)
    return 0 if report.get('scientific_pass') else 2 if report['status']=='completed' else 1

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--selfcheck',type=Path);p.add_argument('--out',type=Path);p.add_argument('--g',type=Path)
    p.add_argument('--worker',action='store_true');p.add_argument('--manifest',type=Path);p.add_argument('--manifest-sha');p.add_argument('--n',type=int);p.add_argument('--segments',type=int);p.add_argument('--segment',type=int);p.add_argument('--prefix',type=Path);p.add_argument('--previous',type=Path)
    a=p.parse_args()
    if a.selfcheck:write(a.selfcheck,selfcheck());return 0
    if a.worker:return worker(a)
    return run(a.out.resolve(),a.g.resolve())

if __name__=='__main__':raise SystemExit(main())
