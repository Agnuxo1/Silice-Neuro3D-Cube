"""Registered same-operator FDST temporal pilot. Never closes point03."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback
from run_point03_exponential import ROOT,sha,write,guard

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def verify_manifest(p,digest):
    assert sha(p)==digest
    m=read(p)
    for source,d in m['source_sha256'].items():assert sha(source)==d
    assert sha(m['input_path'])==m['input_sha256']
    return m

def worker(args):
    import numpy as np
    from point03_fdst import Solver
    start=time.monotonic()
    r=dict(status='failed',started_utc=datetime.now(timezone.utc).isoformat(),steps_total=args.steps,chunk=args.chunk,previous_report_path=str(args.previous) if args.previous else None)
    try:
        m=verify_manifest(args.manifest,args.manifest_sha);r['resource_start']=guard(args.prefix.parent)
        with np.load(m['input_path'],allow_pickle=False) as data:field=data['A0'].copy();dn=data['dn'];sigma=data['sigma']
        if args.previous:
            p=read(args.previous);assert p['status']=='completed' and p['steps_total']==args.steps and p['chunk']==args.chunk-1
            assert sha(p['field_path'])==p['field_sha256']
            with np.load(p['field_path'],allow_pickle=False) as data:field=data['field'].copy()
            r['previous_report_sha256']=sha(args.previous)
        else:assert args.chunk==1;r['previous_report_sha256']=None
        dx=128e-6/626;previous_power=float(np.sum(np.abs(field)**2)*dx*dx)
        solver=Solver(dn,sigma,dx,.002/args.steps);field=solver.advance(field,400)
        assert field.shape==(626,626) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
        total=float(np.sum(np.abs(field)**2)*dx*dx);assert 0<total<=previous_power+1e-9
        r.update(status='completed',raw_total=total,previous_power=previous_power,steps_done=400*args.chunk,dz_m=.002/args.steps,max_negative_amplification=solver.max_negative_amplification,resource_end=guard(args.prefix.parent))
        np.savez(str(args.prefix)+'.npz',field=field);r.update(field_path=str(args.prefix)+'.npz',field_sha256=sha(str(args.prefix)+'.npz'))
    except Exception as err:r.update(error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    r['elapsed_s']=time.monotonic()-start
    if r['elapsed_s']>360:r.update(status='failed',error='360s child budget exceeded')
    write(str(args.prefix)+'.json',r);return 0 if r['status']=='completed' else 1

def assess(execution):
    import numpy as np
    from point03_linear_detector import Detector
    m=verify_manifest(execution['manifest_path'],execution['manifest_sha256']);detector=Detector();dx=128e-6/626
    with np.load(m['input_path'],allow_pickle=False) as data:pin=float(np.sum(np.abs(data['A0'])**2)*dx*dx)
    reference=read(m['reference_execution_path']);ref_fields={};ref_measure={}
    for part in ('11','17'):
        sol=reference['solutions'][part];assert sha(sol['field_path'])==sol['field_sha256']
        with np.load(sol['field_path'],allow_pickle=False) as data:ref_fields[part]=data['field'].copy()
        ref_measure[part]=detector.measure(ref_fields[part],626,pin)
    rows=[];count=0
    for sol in execution['solutions']:
        previous=None;digest=None;power=pin;assert len(sol['checkpoints'])==sol['steps_total']//400
        for i,link in enumerate(sol['checkpoints'],1):
            assert sha(link['path'])==link['sha256'];cp=read(link['path'])
            assert cp['status']=='completed' and cp['steps_total']==sol['steps_total'] and cp['chunk']==i and cp['steps_done']==400*i
            assert cp['previous_report_path']==previous and cp['previous_report_sha256']==digest
            assert cp['elapsed_s']<=360 and cp['max_negative_amplification']<=1.10
            assert sha(cp['field_path'])==cp['field_sha256']
            with np.load(cp['field_path'],allow_pickle=False) as data:field=data['field']
            assert field.shape==(626,626) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
            actual=float(np.sum(np.abs(field)**2)*dx*dx)
            assert abs(actual-cp['raw_total'])<=1e-12 and abs(cp['previous_power']-power)<=1e-12 and 0<actual<=power+1e-9
            for key in ('resource_start','resource_end'):assert cp[key]['available_ram_bytes']>1.5*1024**3 and cp[key]['free_disk_bytes']>2*1024**3
            previous=link['path'];digest=link['sha256'];power=actual;count+=1
        measures=detector.measure(field,626,pin)
        row=dict(steps=sol['steps_total'],dz_m=.002/sol['steps_total'],raw_total=actual,methods=measures,errors={})
        row['errors']['field']=float(np.linalg.norm(field-ref_fields['17'])/np.linalg.norm(ref_fields['17']))
        for method in ('field','intensity'):row['errors']['power_'+method]=abs(measures[method]['P_core']-ref_measure['17'][method]['P_core'])
        row['reference11_field_error']=float(np.linalg.norm(field-ref_fields['11'])/np.linalg.norm(ref_fields['11']))
        rows.append(row)
    assert count==56 and [r['steps'] for r in rows]==[3200,6400,12800]
    orders={};order_pass=True
    for quantity in ('field','power_field','power_intensity'):
        errors=[r['errors'][quantity] for r in rows]
        p=[math.log2(a/b) if a>0 and b>0 else None for a,b in zip(errors,errors[1:])];orders[quantity]=p
        order_pass=order_pass and all(x is not None and 3.5<=x<=4.5 for x in p)
    gates=dict(integrity=True,field_fine=rows[-1]['errors']['field']<=1e-4,power_fine=all(rows[-1]['errors'][q]<=1e-6 for q in ('power_field','power_intensity')),observed_order=order_pass,quadrature=all(r['methods'][method]['change']<=1e-10 for r in rows for method in ('field','intensity')))
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),pilot_pass=all(gates.values()),point03_closed=False,gates=gates,rows=rows,observed_orders=orders,reference_methods=ref_measure,reference_field_difference=float(np.linalg.norm(ref_fields['11']-ref_fields['17'])/np.linalg.norm(ref_fields['17'])),checkpoints_checked=count,scope='Temporal same-FD-operator pilot only; no spatial convergence closure.')

def run(out):
    import platform
    from importlib.metadata import version
    assert platform.python_version()=='3.13.7' and version('numpy')=='2.2.6' and version('scipy')=='1.15.1'
    start=time.monotonic();assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    k=ROOT/'resultados/codex/point03_linear_probe_20261007_K626';pre=ROOT/'resultados/codex/point03_fdst_preflight_attempt1_20261007.json'
    assert read(pre)['pass_'] and read(k/'integrity_audit.json')['integrity_pass'] and read(k/'execution.json')['status']=='completed'
    original=read(k/'manifest.json');case=original['plan'][0];assert sha(case['input_path'])==case['input_sha256']
    out.mkdir();r=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),solutions=[],children=[],point03_closed=False)
    try:
        guard(out)
        sources=[Path(__file__).resolve(),ROOT/'scripts/point03_fdst.py',ROOT/'scripts/run_point03_exponential.py',ROOT/'scripts/point03_linear_detector.py',ROOT/'Docs/POINT-03-FDST-PILOT-CONTRACT.md',ROOT/'Docs/POINT-03-FDST-KERNEL-CONTRACT.md',pre,k/'execution.json',k/'integrity_audit.json',k/'assessment.json',k/'manifest.json']
        for part in ('11','17'):sources.append(Path(read(k/'execution.json')['solutions'][part]['field_path']))
        m=dict(created_utc=datetime.now(timezone.utc).isoformat(),input_path=case['input_path'],input_sha256=case['input_sha256'],source_sha256={str(p):sha(p) for p in sources},reference_execution_path=str(k/'execution.json'),steps=[3200,6400,12800],numerical_threads=1)
        write(out/'manifest.json',m);r.update(manifest_path=str(out/'manifest.json'),manifest_sha256=sha(out/'manifest.json'))
        for steps in m['steps']:
            directory=out/f'steps{steps}';directory.mkdir();previous=None;chain=[]
            for chunk in range(1,steps//400+1):
                assert time.monotonic()-start<7200;guard(out);prefix=directory/f'chunk{chunk:02d}'
                cmd=[sys.executable,str(Path(__file__).resolve()),'--worker','--manifest',r['manifest_path'],'--manifest-sha',r['manifest_sha256'],'--steps',str(steps),'--chunk',str(chunk),'--prefix',str(prefix)]
                if previous:cmd+=['--previous',str(previous)]
                t=time.monotonic()
                with Path(str(prefix)+'.log').open('xb') as log:child=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=370,check=False)
                r['children'].append(dict(steps=steps,chunk=chunk,returncode=child.returncode,elapsed_s=time.monotonic()-t));cp=Path(str(prefix)+'.json')
                assert child.returncode==0 and read(cp)['status']=='completed'
                chain.append(dict(path=str(cp),sha256=sha(cp)));previous=cp
                print(json.dumps(dict(steps=steps,chunk=chunk,total_chunks=steps//400,elapsed_s=round(time.monotonic()-start,1))),flush=True)
            r['solutions'].append(dict(steps_total=steps,checkpoints=chain))
        assessment=assess(r);write(out/'assessment.json',assessment);r.update(status='completed',pilot_pass=assessment['pilot_pass'],assessment_path=str(out/'assessment.json'),assessment_sha256=sha(out/'assessment.json'))
    except Exception as err:r.update(status='failed',error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    r.update(elapsed_s=time.monotonic()-start,finished_utc=datetime.now(timezone.utc).isoformat(),sources_unchanged=all(sha(p)==d for p,d in locals().get('m',{}).get('source_sha256',{}).items()))
    write(out/'execution.json',r);print(json.dumps({q:r.get(q) for q in ('status','pilot_pass','point03_closed','elapsed_s','error')}),flush=True)
    return 0 if r.get('pilot_pass') else 2 if r['status']=='completed' else 1

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path);p.add_argument('--worker',action='store_true');p.add_argument('--manifest',type=Path);p.add_argument('--manifest-sha');p.add_argument('--steps',type=int);p.add_argument('--chunk',type=int);p.add_argument('--prefix',type=Path);p.add_argument('--previous',type=Path);a=p.parse_args()
    return worker(a) if a.worker else run(a.out.resolve())
if __name__=='__main__':raise SystemExit(main())
