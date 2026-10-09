"""Prospective fixed-ghost boundary contrast using exact retained T96 interiors."""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from scipy.sparse.linalg import expm_multiply
from run_point03_exponential import ROOT, sha, write, operator, guard
from point03_linear_detector import Detector

DX=128e-6/400


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def controls():
    n=7
    rng=np.random.default_rng(947)
    dn=rng.uniform(-.003,0,(n,n));sigma=rng.uniform(0,1e4,(n,n))
    old,_=operator(dn,sigma,DX)
    new,_=operator(dn[1:,1:],sigma[1:,1:],DX)
    keep=np.arange(n*n).reshape(n,n)[1:,1:].ravel()
    delta=old[keep,:][:,keep]-new
    assert delta.nnz==0
    n=6;j=np.arange(1,n+1)
    field=np.sin(math.pi*j/(n+1))[:,None]*np.sin(2*math.pi*j/(n+1))[None,:]
    dn0=-.0007;s=1000.;k0=2*math.pi/1550e-9
    matrix,trace=operator(np.full((n,n),dn0),np.full((n,n),s),DX)
    c=1j/(2*1.444*k0*DX**2)
    eigenvalue=c*(2*math.cos(math.pi/(n+1))+2*math.cos(2*math.pi/(n+1))-4)+1j*k0*dn0-s
    np.random.seed(0)
    actual=expm_multiply(.002*matrix,field.ravel().astype(complex),traceA=.002*trace)
    exact=field.ravel()*np.exp(.002*eigenvalue)
    error=float(np.linalg.norm(actual-exact)/np.linalg.norm(exact))
    power=abs(float(np.vdot(actual,actual).real/np.vdot(field.ravel(),field.ravel()).real)-math.exp(-4))
    assert error<=1e-9 and power<=1e-10
    return dict(pass_=True,principal_submatrix_exact=True,sine_field_error=error,sine_power_error=power)


def worker(args):
    start=time.monotonic();np.random.seed(0)
    cp=dict(status='failed',started_utc=datetime.now(timezone.utc).isoformat(),segment=args.segment,segments=args.segments,N=399,dx_m=DX,previous_report_path=str(args.previous) if args.previous else None)
    try:
        cp['resource_start']=guard(args.prefix.parent)
        assert sha(args.manifest)==args.manifest_sha
        m=read(args.manifest)
        for path,digest in m['source_sha256'].items():assert sha(path)==digest
        assert sha(m['input_path'])==m['input_sha256']
        with np.load(m['input_path'],allow_pickle=False) as data:
            field=data['A0'].copy();dn=data['dn'];sigma=data['sigma']
        previous_power=m['P_in']
        if args.previous:
            p=read(args.previous)
            assert p['status']=='completed' and p['segment']==args.segment-1 and p['segments']==args.segments
            assert sha(p['field_path'])==p['field_sha256']
            with np.load(p['field_path'],allow_pickle=False) as data:field=data['field'].copy()
            cp['previous_report_sha256']=sha(args.previous);previous_power=p['raw_total']
        else:
            assert args.segment==1;cp['previous_report_sha256']=None
        assert field.shape==(399,399)
        matrix,trace=operator(dn,sigma,DX)
        length=.002/args.segments
        field=expm_multiply(length*matrix,field.ravel(),traceA=length*trace).reshape(399,399)
        total=float(np.vdot(field,field).real*DX**2)
        assert np.all(np.isfinite(field)) and 0<total<=previous_power+1e-9
        cp.update(status='completed',raw_total=total,previous_power=previous_power,length_m=length)
        cp['resource_end']=guard(args.prefix.parent)
    except Exception as error:
        cp.update(error=str(error),error_type=type(error).__name__,diagnostic=traceback.format_exc())
    if 'field' in locals():
        np.savez(str(args.prefix)+'.npz',field=field)
        cp.update(field_path=str(args.prefix)+'.npz',field_sha256=sha(str(args.prefix)+'.npz'))
    cp['elapsed_s']=time.monotonic()-start
    if cp['elapsed_s']>360:cp.update(status='failed',error='360s budget exceeded')
    write(str(args.prefix)+'.json',cp)
    return 0 if cp['status']=='completed' else 1


def assess(folder,e,m):
    detector=Detector();fields={};measurements={}
    for label,solution in e['solutions'].items():
        cp=read(solution['checkpoints'][-1]['path'])
        with np.load(cp['field_path'],allow_pickle=False) as data:fields[label]=np.pad(data['field'],((1,0),(1,0)))
        measurements[label]=detector.measure(fields[label],400,m['P_in'])
    with np.load(m['baseline_path'],allow_pickle=False) as data:baseline=data['field'].copy()
    baseline_measure=detector.measure(baseline,400,m['baseline_P_in'])
    distance=float(np.linalg.norm(fields['5']-fields['7']))
    norms={label:float(np.linalg.norm(value)) for label,value in fields.items()}
    bound=DX**2*(norms['5']+norms['7'])*distance/m['P_in']
    quadrature=max(value['change'] for row in (*measurements.values(),baseline_measure) for value in row.values())
    rows={}
    for method in ('field','intensity'):
        change=abs(measurements['7'][method]['P_core']-baseline_measure[method]['P_core'])
        ref=abs(measurements['7'][method]['P_core']-measurements['5'][method]['P_core'])
        rows[method]=dict(actual=measurements['7'][method]['P_core'],baseline=baseline_measure[method]['P_core'],change=change,reference_change=ref,hypothesis_pass=change<=1e-6,reference_pass=ref<=1e-8)
    eligible=distance/norms['7']<=1e-9 and bound<=1e-6 and quadrature<=1e-10 and all(row['reference_pass'] for row in rows.values())
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),rows=rows,reference_field_difference=distance/norms['7'],reference_bound=bound,quadrature_change=quadrature,controls_eligible=eligible,hypothesis_pass=eligible and all(row['hypothesis_pass'] for row in rows.values()),point03_closed=False,requires_independent_audit=True,scope='Boundary-placement diagnostic N400 only; no convergence closure.')


def run(folder):
    start=time.monotonic()
    assert not folder.exists() and folder.is_relative_to(ROOT/'resultados/codex')
    folder.mkdir();e=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),solutions={},children=[],point03_closed=False)
    m={}
    try:
        guard(folder);preflight=controls();write(folder/'preflight.json',preflight)
        old=read(ROOT/'resultados/codex/point03_fdst_accuracy_20261007_L2/manifest.json')
        original=Path(old['input_path']);assert sha(original)==old['input_sha256']
        baseline=old['reference_fields'][-1];assert sha(baseline['path'])==baseline['sha256']
        with np.load(original,allow_pickle=False) as data:
            arrays={key:data[key].copy() for key in ('A0','dn','sigma','weights')}
        assert all(value.shape==(400,400) for value in arrays.values())
        pin=float(np.vdot(arrays['A0'],arrays['A0']).real*DX**2)
        cropped={key:value[1:,1:].copy() for key,value in arrays.items()}
        cropped_pin=float(np.vdot(cropped['A0'],cropped['A0']).real*DX**2)
        assert abs(pin-cropped_pin)<=1e-12 and cropped_pin>0
        path=folder/'n399_fixed_input.npz';np.savez(path,**cropped)
        sources=[Path(__file__).resolve(),ROOT/'Docs/POINT-03-P1-CONTRACT.md',ROOT/'scripts/audit_point03_p1.py',ROOT/'scripts/run_point03_exponential.py',ROOT/'scripts/point03_linear_detector.py',ROOT/'resultados/codex/point03_fdst_accuracy_20261007_L2/manifest.json']
        m=dict(created_utc=datetime.now(timezone.utc).isoformat(),input_path=str(path),input_sha256=sha(path),original_input_path=str(original),original_input_sha256=sha(original),baseline_path=baseline['path'],baseline_sha256=baseline['sha256'],P_in=cropped_pin,baseline_P_in=pin,dx_m=DX,N=399,source_sha256={str(p):sha(p) for p in sources},preflight=preflight,numerical_threads=1)
        write(folder/'manifest.json',m);e.update(manifest_path=str(folder/'manifest.json'),manifest_sha256=sha(folder/'manifest.json'))
        for segments in (5,7):
            label=str(segments);directory=folder/label;directory.mkdir();previous=None;chain=[]
            for index in range(1,segments+1):
                assert time.monotonic()-start<=2400;guard(folder)
                prefix=directory/f'part{index:03d}'
                command=[sys.executable,str(Path(__file__).resolve()),'--worker','--manifest',e['manifest_path'],'--manifest-sha',e['manifest_sha256'],'--segments',label,'--segment',str(index),'--prefix',str(prefix)]
                if previous:command+=['--previous',str(previous)]
                before=time.monotonic()
                with Path(str(prefix)+'.log').open('xb') as log:child=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=370)
                cp=Path(str(prefix)+'.json');e['children'].append(dict(segments=segments,index=index,returncode=child.returncode,elapsed_s=time.monotonic()-before))
                assert child.returncode==0 and read(cp)['status']=='completed'
                chain.append(dict(path=str(cp),sha256=sha(cp)));previous=cp
                print(json.dumps(dict(segments=segments,index=index,total=segments,elapsed_s=round(time.monotonic()-start,1))),flush=True)
            e['solutions'][label]=dict(checkpoints=chain)
        a=assess(folder,e,m);write(folder/'assessment.json',a)
        e.update(status='completed',hypothesis_pass=a['hypothesis_pass'],assessment_sha256=sha(folder/'assessment.json'))
    except Exception as error:e.update(status='failed',error=str(error),error_type=type(error).__name__,diagnostic=traceback.format_exc())
    e.update(elapsed_s=time.monotonic()-start,finished_utc=datetime.now(timezone.utc).isoformat(),sources_unchanged=all(sha(path)==digest for path,digest in m.get('source_sha256',{}).items()))
    write(folder/'execution.json',e)
    print(json.dumps({key:e.get(key) for key in ('status','hypothesis_pass','elapsed_s','error')}),flush=True)
    return 0 if e.get('hypothesis_pass') else 2 if e['status']=='completed' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path);parser.add_argument('--worker',action='store_true');parser.add_argument('--manifest',type=Path);parser.add_argument('--manifest-sha');parser.add_argument('--segments',type=int);parser.add_argument('--segment',type=int);parser.add_argument('--prefix',type=Path);parser.add_argument('--previous',type=Path);args=parser.parse_args()
    raise SystemExit(worker(args) if args.worker else run(args.out.resolve()))
