"""Explicit H2 recovery: retained four references; N640 partitions 11/17."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
from run_point03_exponential import ROOT,sha,write,load,guard,worker,operator

def odd_preflight():
    import numpy as np
    from scipy.linalg import expm
    from scipy.sparse.linalg import expm_multiply
    rng=np.random.default_rng(401);n=7;z=8e-6
    dn=rng.uniform(-.003,.001,(n,n));sigma=rng.uniform(0,12000,(n,n))
    field=(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))).astype(np.complex128)
    matrix,trace=operator(dn,sigma,2e-6);exact=expm(z*matrix.toarray())@field.ravel()
    fields={};rows=[]
    for segments in (11,17):
        result=field.ravel().copy();length=z/segments
        for _ in range(segments):result=expm_multiply(length*matrix,result,traceA=length*trace)
        error=float(np.linalg.norm(result-exact)/np.linalg.norm(exact));assert error<=1e-11
        fields[segments]=result;rows.append(dict(segments=segments,dense_relative_error=error))
    delta=float(np.linalg.norm(fields[11]-fields[17])/np.linalg.norm(exact));assert delta<=1e-11
    return dict(pass_=True,rows=rows,partition_difference=delta,scope='Manufactured small case only; no new optical fields')

def recover(out,h1):
    start=time.monotonic();assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    out.mkdir(parents=True);report=dict(status='running',recovery_started_utc=datetime.now(timezone.utc).isoformat(),results=[],children=[])
    try:
        guard(out);prior=json.loads((h1/'execution.json').read_text(encoding='utf-8'))
        assert prior['status']=='failed' and prior['error_type']=='TimeoutExpired' and len(prior['results'])==4
        assert prior['sources_unchanged'] and not (h1/'n640_segments4/segment_01.json').exists() and not (h1/'n640_segments4/segment_01.npz').exists()
        manifest=json.loads(Path(prior['manifest_path']).read_text(encoding='utf-8'))
        assert sha(prior['manifest_path'])==prior['manifest_sha256']
        for p,d in manifest['source_sha256'].items():assert sha(p)==d
        assert sha(prior['prediction_path'])==prior['prediction_sha256']
        extra=[Path(__file__),ROOT/'scripts/assess_point03_h_recovered.py',ROOT/'Docs/POINT-03-H-RECOVERY-CONTRACT.md',h1/'execution.json',Path(prior['manifest_path']),Path(prior['prediction_path']),h1/'n640_segments4/segment_01.log']
        manifest['source_sha256'].update({str(p):sha(p) for p in extra})
        manifest['recovery']=dict(H1_execution_path=str(h1/'execution.json'),H1_execution_sha256=sha(h1/'execution.json'),retained_cases=4,retained_checkpoints=48,new_N=640,new_partitions=[11,17])
        manifest['odd_partition_preflight']=odd_preflight()
        write(out/'manifest.json',manifest)
        report.update(manifest_path=str(out/'manifest.json'),manifest_sha256=sha(out/'manifest.json'),results=prior['results'],prediction_path=prior['prediction_path'],prediction_sha256=prior['prediction_sha256'],holdout_started_utc=prior['holdout_started_utc'],recovery=manifest['recovery'])
        n=640;result=dict(N=n,solutions={});case=next(c for c in manifest['plan'] if c['N']==n)
        assert sha(case['input_path'])==case['input_sha256']
        for segments in (11,17):
            caseout=out/f'n{n}_segments{segments}';caseout.mkdir();previous=None;chain=[]
            for segment in range(1,segments+1):
                assert time.monotonic()-start<7200;guard(out)
                prefix=caseout/f'segment_{segment:02d}'
                cmd=[sys.executable,str(Path(__file__).resolve()),'--worker','--manifest',report['manifest_path'],'--manifest-sha',report['manifest_sha256'],'--n',str(n),'--segments',str(segments),'--segment',str(segment),'--prefix',str(prefix)]
                if previous:cmd+=['--previous',str(previous)]
                with Path(str(prefix)+'.log').open('xb') as log:
                    childstart=time.monotonic();child=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=370,check=False)
                report['children'].append(dict(N=n,segments=segments,segment=segment,returncode=child.returncode,elapsed_s=time.monotonic()-childstart))
                cp=Path(str(prefix)+'.json');assert cp.exists() and child.returncode==0,'Recovery worker failed'
                data=json.loads(cp.read_text(encoding='utf-8'));assert data['status']=='completed'
                chain.append(dict(path=str(cp),sha256=sha(cp)));previous=cp
                print(json.dumps(dict(N=n,segments=segments,segment=segment,child_s=round(data['elapsed_s'],2),recovery_elapsed_s=round(time.monotonic()-start,1))),flush=True)
            result['solutions'][str(segments)]=dict(checkpoints=chain,field_path=data['field_path'],field_sha256=data['field_sha256'])
        report['results'].append(result);report.update(status='completed',finished_utc=datetime.now(timezone.utc).isoformat())
        write(out/'pre_assessment_execution.json',report)
        evaluator=load('h2_final_assess',ROOT/'scripts/assess_point03_h_recovered.py')
        assessed=evaluator.assess(out/'pre_assessment_execution.json',prediction=False)
        assert sum(len(c['checkpoints']) for r in report['results'] for c in r['solutions'].values())==76
        write(out/'assessment.json',assessed)
        report.update(scientific_pass=assessed['scientific_pass'],point03_closed=assessed['point03_closed'],assessment_path=str(out/'assessment.json'),assessment_sha256=sha(out/'assessment.json'))
    except Exception as err:
        report.update(status='failed',error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    report['recovery_elapsed_s']=time.monotonic()-start
    report['sources_unchanged']=all(sha(p)==d for p,d in locals().get('manifest',{}).get('source_sha256',{}).items())
    write(out/'execution.json',report)
    print(json.dumps({k:report.get(k) for k in ('status','scientific_pass','point03_closed','recovery_elapsed_s','error')}),flush=True)
    return 0 if report.get('scientific_pass') else 2 if report['status']=='completed' else 1

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path);p.add_argument('--h1',type=Path);p.add_argument('--preflight',type=Path)
    p.add_argument('--worker',action='store_true');p.add_argument('--manifest',type=Path);p.add_argument('--manifest-sha');p.add_argument('--n',type=int);p.add_argument('--segments',type=int);p.add_argument('--segment',type=int);p.add_argument('--prefix',type=Path);p.add_argument('--previous',type=Path)
    a=p.parse_args()
    if a.preflight:write(a.preflight,odd_preflight());return 0
    return worker(a) if a.worker else recover(a.out.resolve(),a.h1.resolve())

if __name__=='__main__':raise SystemExit(main())
