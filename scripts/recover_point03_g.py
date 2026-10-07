"""Explicit G2 recovery after a confirmed worker-time failure."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
from run_point03_reconstructed import ROOT, sha, write, load, guard
def worker(args):
    import numpy as np
    start=time.monotonic();deadline=start+31
    manifest=json.loads(args.manifest.read_text())
    assert sha(args.manifest)==args.manifest_sha
    case=next(c for c in manifest['new_plan'] if c['id']==args.case)
    prefix=args.prefix
    report=dict(status='failed',start_step=args.start,steps_done=0,N=case['N'],case_id=args.case,resource_samples=[],
                previous_report_path=str(args.previous) if args.previous else None,started_utc=datetime.now(timezone.utc).isoformat())
    try:
        report['resource_samples'].append(guard(prefix.parent,deadline))
        for p,digest in manifest['source_sha256'].items():assert sha(p)==digest
        assert sha(case['input_path'])==case['input_sha256']
        with np.load(case['input_path'],allow_pickle=False) as z:
            data={k:z[k] for k in z.files}
        if args.previous:
            previous=json.loads(args.previous.read_text());assert previous['completed_step']==args.start
            assert sha(previous['field_path'])==previous['field_sha256']
            report['previous_report_sha256']=sha(args.previous)
            with np.load(previous['field_path'],allow_pickle=False) as z:field=z['field']
        else:
            assert args.start==0;field=data['A0'].copy();report['previous_report_sha256']=None
        adi=load('g_worker_adi',ROOT/'experimentos/glass009_claude/adi2d.py')
        backend=load('g_sparse',ROOT/'scripts/point03_sparse_adi.py')
        cls=backend.make_sparse_stepper(adi.Stepper)
        assert cls.__init__ is adi.Stepper.__init__ and cls.step is adi.Stepper.step and cls._lap is adi.Stepper._lap
        stepper=cls(data['dn'],data['sigma'],128e-6/case['N'],case['dz_m'])
        report['factor_metadata']=stepper.sparse_metadata()
        for i in range(100):
            assert time.monotonic()<deadline,'Worker retention reserve reached'
            if i%20==0:report['resource_samples'].append(guard(prefix.parent,deadline))
            field=stepper.step(field);report['steps_done']=i+1
        assert field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
        total=float(np.sum(np.abs(field)**2)*(128e-6/case['N'])**2)
        assert 0<total<=1.001
        report.update(status='completed',completed_step=args.start+100,raw_total=total)
        report['factor_metadata']=stepper.sparse_metadata()
        report['resource_samples'].append(guard(prefix.parent,deadline))
    except Exception as err:
        report.update(error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    finally:
        if 'field' in locals():
            np.savez(str(prefix)+'.npz',field=field)
            report['field_path']=str(prefix)+'.npz';report['field_sha256']=sha(report['field_path'])
        report['elapsed_s']=time.monotonic()-start
        if report['elapsed_s']>=35:report['status']='failed';report['error']='35 s worker budget exceeded'
        write(str(prefix)+'.json',report)
    print(json.dumps({k:report.get(k) for k in ['status','case_id','completed_step','elapsed_s','error']}),flush=True)
    return 0 if report['status']=='completed' else 1

def recover(out,g1):
    start=time.monotonic();deadline=start+900
    assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    out.mkdir(parents=True)
    prior=json.loads((g1/'execution.json').read_text())
    report=dict(prior,status='running',scientific_pass=None,recovery_started_utc=datetime.now(timezone.utc).isoformat())
    try:
        assert prior['status']=='failed' and len(prior['results'])==8
        original_manifest=Path(prior['manifest_path']);manifest=json.loads(original_manifest.read_text())
        assert sha(original_manifest)==prior['manifest_sha256']
        failed=g1/'g_n640_holdout/step_04800.json';failure=json.loads(failed.read_text())
        assert failure['status']=='failed' and failure['start_step']==4600 and failure['steps_done']==195
        assert failure['error']=='Worker retention reserve reached'
        assert sha(failure['field_path'])==failure['field_sha256']
        previous=Path(failure['previous_report_path']);assert sha(previous)==failure['previous_report_sha256']
        oldcp=json.loads(previous.read_text());assert oldcp['status']=='completed' and oldcp['completed_step']==4600
        case=next(c for c in manifest['new_plan'] if c['id']=='g_n640_holdout')
        chain=[]
        for step in range(200,4601,200):
            p=g1/'g_n640_holdout'/f'step_{step:05d}.json';cp=json.loads(p.read_text())
            assert cp['status']=='completed' and cp['completed_step']==step and sha(cp['field_path'])==cp['field_sha256']
            chain.append(dict(path=str(p),sha256=sha(p)))
        assert chain[-1]['path']==str(previous)
        extra=[Path(__file__),ROOT/'scripts/assess_point03_g_recovered.py',ROOT/'scripts/audit_point03_g_recovered_integrity.py',ROOT/'Docs/POINT-03-G-RECOVERY-CONTRACT.md',original_manifest,g1/'execution.json',failed,Path(failure['field_path']),Path(prior['prediction_path'])]
        manifest['source_sha256'].update({str(p):sha(p) for p in extra})
        for p,d in manifest['source_sha256'].items():assert sha(p)==d
        for p,d in manifest['input_sha256'].items():assert sha(p)==d
        manifest['recovery']=dict(G1_execution_path=str(g1/'execution.json'),G1_execution_sha256=sha(g1/'execution.json'),restart_step=4600,partial_failed_steps_repeated=195,new_steps=1800,new_chunk_steps=100)
        write(out/'manifest.json',manifest)
        report.update(manifest_path=str(out/'manifest.json'),manifest_sha256=sha(out/'manifest.json'),recovery=manifest['recovery'])
        caseout=out/'g_n640_holdout';caseout.mkdir()
        for step in range(4600,6400,100):
            guard(out,deadline);prefix=caseout/f'step_{step+100:05d}'
            cmd=[sys.executable,str(Path(__file__).resolve()),'--worker','--manifest',str(out/'manifest.json'),'--manifest-sha',report['manifest_sha256'],'--case',case['id'],'--start',str(step),'--prefix',str(prefix),'--previous',str(previous)]
            with Path(str(prefix)+'.stdout.log').open('xb') as stdout,Path(str(prefix)+'.stderr.log').open('xb') as stderr:
                childstart=time.monotonic();child=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=40,check=False)
            report['children'].append(dict(case=case['id'],step=step,returncode=child.returncode,elapsed_s=time.monotonic()-childstart,stdout=str(prefix)+'.stdout.log',stderr=str(prefix)+'.stderr.log'))
            cp=Path(str(prefix)+'.json');assert child.returncode==0 and cp.exists(),'Recovery worker failed'
            data=json.loads(cp.read_text());assert data['status']=='completed' and data['completed_step']==step+100
            chain.append(dict(path=str(cp),sha256=sha(cp)));previous=cp
            print(json.dumps(dict(case=case['id'],steps=step+100,target=6400,elapsed_s=round(time.monotonic()-start,1))),flush=True)
        report['results'].append(dict(id=case['id'],N=case['N'],dz_m=case['dz_m'],steps=case['steps'],input_path=case['input_path'],input_sha256=case['input_sha256'],field_path=data['field_path'],field_sha256=data['field_sha256'],checkpoints=chain,reused=False))
        report.update(status='completed',sources_unchanged=all(sha(p)==d for p,d in manifest['source_sha256'].items()),inputs_unchanged=all(sha(p)==d for p,d in manifest['input_sha256'].items()))
        assert report['sources_unchanged'] and report['inputs_unchanged']
        write(out/'propagation_execution.json',report)
        assessment=out/'assessment.json'
        r=subprocess.run([sys.executable,str(ROOT/'scripts/assess_point03_g_recovered.py'),'--execution',str(out/'propagation_execution.json'),'--mode','final','--out',str(assessment)],capture_output=True,timeout=120)
        (out/'assessment.stdout.log').write_bytes(r.stdout);(out/'assessment.stderr.log').write_bytes(r.stderr)
        assert r.returncode in (0,2),'Recovery assessor failed'
        report.update(scientific_pass=r.returncode==0,assessment_path=str(assessment),assessment_sha256=sha(assessment))
    except Exception as err:
        report.update(status='failed',error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    report['recovery_elapsed_s']=time.monotonic()-start
    write(out/'execution.json',report)
    print(json.dumps({k:report.get(k) for k in ('status','scientific_pass','recovery_elapsed_s','error')}),flush=True)
    return 0 if report.get('scientific_pass') else 2 if report['status']=='completed' else 1

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path);p.add_argument('--g1',type=Path)
    p.add_argument('--worker',action='store_true');p.add_argument('--manifest',type=Path);p.add_argument('--manifest-sha');p.add_argument('--case');p.add_argument('--start',type=int);p.add_argument('--prefix',type=Path);p.add_argument('--previous',type=Path)
    a=p.parse_args();return worker(a) if a.worker else recover(a.out.resolve(),a.g1.resolve())

if __name__=='__main__':raise SystemExit(main())

