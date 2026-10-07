"""L2: direct precision only, one new N400 trajectory; preserves negative L1."""
import argparse
import ast
from datetime import datetime,timezone
import inspect
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
from run_point03_exponential import ROOT,sha,write,guard
import run_point03_fdst_pilot as l1

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def adapted_worker():
    tree=ast.parse(inspect.getsource(l1.worker))
    class Change(ast.NodeTransformer):
        def __init__(self):self.count=0
        def visit_Constant(self,node):
            if node.value==626:self.count+=1;return ast.copy_location(ast.Constant(400),node)
            return node
    adapter=Change();tree=adapter.visit(tree);ast.fix_missing_locations(tree);assert adapter.count==3
    ns=dict(l1.__dict__);exec(compile(tree,'registered_L1_worker_N400','exec'),ns)
    return ns['worker'],ast.unparse(tree)+'\n',adapter.count

def contrast(field,refs,n,pin):
    import numpy as np
    from point03_linear_detector import Detector
    d=Detector();dx=128e-6/n;primary=refs[-1];methods=d.measure(field,n,pin);reference_methods=[d.measure(x,n,pin) for x in refs]
    nf=[float(np.linalg.norm(x)) for x in (field,primary,refs[0])];difference=float(np.linalg.norm(field-primary));refdifference=float(np.linalg.norm(refs[0]-primary))
    bound=dx*dx*(nf[0]+nf[1])*difference/pin;reference_bound=dx*dx*(nf[2]+nf[1])*refdifference/pin
    errors={m:abs(methods[m]['P_core']-reference_methods[-1][m]['P_core']) for m in ('field','intensity')}
    quad=max(v['change'] for mm in [methods]+reference_methods for v in mm.values())
    gates=dict(field=difference/nf[1]<=1e-4,power=all(x<=1e-6 for x in errors.values()),reference_field=refdifference/nf[1]<=1e-9,quadrature=quad<=1e-10,observable_bound=bound+reference_bound+quad<=1e-5)
    return dict(N=n,methods=methods,reference_methods=reference_methods,field_relative_error=difference/nf[1],power_errors=errors,reference_field_difference=refdifference/nf[1],bound_vs_computed_reference=bound,reference_consistency_bound=reference_bound,quadrature_change=quad,combined_reference_relative_indicator=bound+reference_bound+quad,gates=gates,pass_=all(gates.values()))

def assess(e):
    import numpy as np
    m=l1.verify_manifest(e['manifest_path'],e['manifest_sha256']);dx=128e-6/400
    with np.load(m['input_path'],allow_pickle=False) as data:pin=float(np.sum(np.abs(data['A0'])**2)*dx*dx)
    previous=None;digest=None;power=pin
    assert len(e['checkpoints'])==32
    for i,link in enumerate(e['checkpoints'],1):
        assert sha(link['path'])==link['sha256'];cp=read(link['path']);assert cp['status']=='completed' and cp['chunk']==i and cp['steps_total']==12800 and cp['steps_done']==400*i
        assert cp['previous_report_path']==previous and cp['previous_report_sha256']==digest and cp['elapsed_s']<=360 and cp['started_utc']>m['created_utc']
        assert cp['dz_m']==.002/12800 and cp['max_negative_amplification']<=1.10
        assert sha(cp['field_path'])==cp['field_sha256']
        with np.load(cp['field_path'],allow_pickle=False) as data:field=data['field'].copy()
        assert field.shape==(400,400) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
        actual=float(np.vdot(field,field).real*dx*dx);assert abs(actual-cp['raw_total'])<=1e-12 and abs(power-cp['previous_power'])<=1e-12 and 0<actual<=power+1e-9
        for key in ('resource_start','resource_end'):assert cp[key]['available_ram_bytes']>1.5*1024**3 and cp[key]['free_disk_bytes']>2*1024**3
        previous=link['path'];digest=link['sha256'];power=actual
    refs=[]
    for ref in m['reference_fields']:
        assert sha(ref['path'])==ref['sha256']
        with np.load(ref['path'],allow_pickle=False) as data:refs.append(data['field'].copy())
    n400=contrast(field,refs,400,pin)
    olde=read(m['L1_execution_path']);oldm=l1.verify_manifest(olde['manifest_path'],olde['manifest_sha256'])
    with np.load(oldm['input_path'],allow_pickle=False) as data:oldpin=float(np.sum(np.abs(data['A0'])**2)*(128e-6/626)**2)
    oldcp=read(olde['solutions'][-1]['checkpoints'][-1]['path']);assert sha(oldcp['field_path'])==oldcp['field_sha256']
    with np.load(oldcp['field_path'],allow_pickle=False) as data:oldfield=data['field'].copy()
    ke=read(m['K626_execution_path']);oldrefs=[]
    for part in ('11','17'):
        sol=ke['solutions'][part];assert sha(sol['field_path'])==sol['field_sha256']
        with np.load(sol['field_path'],allow_pickle=False) as data:oldrefs.append(data['field'].copy())
    n626=contrast(oldfield,oldrefs,626,oldpin)
    assert not read(m['L1_assessment_path'])['pilot_pass']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,L2_accuracy_pass=n400['pass_'] and n626['pass_'],point03_closed=False,L1_still_negative=True,rows=[n400,n626],new_checkpoints_checked=32,P_in=pin,P_total=power/pin,scope='Direct practical precision only for N400/N626 relative to computed FD references; no observed-order or spatial-convergence acceptance.')

def run(out):
    import platform
    from importlib.metadata import version
    assert platform.python_version()=='3.13.7' and version('numpy')=='2.2.6' and version('scipy')=='1.15.1'
    start=time.monotonic();assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    lp=ROOT/'resultados/codex/point03_fdst_pilot_20261007_L1';hp=ROOT/'resultados/codex/point03_exponential_20261007_H2';kp=ROOT/'resultados/codex/point03_linear_probe_20261007_K626'
    a=read(lp/'assessment.json');assert read(lp/'execution.json')['status']=='completed' and read(lp/'integrity_audit.json')['integrity_pass']
    assert not a['pilot_pass'] and a['gates']['field_fine'] and a['gates']['power_fine'] and not a['gates']['observed_order']
    assert read(hp/'integrity_audit.json')['integrity_pass'] and read(ROOT/'resultados/codex/point03_fdst400_timing_20261007.json')['pass_']
    hm=read(hp/'manifest.json');he=read(hp/'execution.json');assert sha(hp/'manifest.json')==he['manifest_sha256']
    for path,digest in hm['source_sha256'].items():assert sha(path)==digest
    case=next(x for x in hm['plan'] if x['N']==400);r=next(x for x in he['results'] if x['N']==400)
    assert sha(case['input_path'])==case['input_sha256'];out.mkdir();_,worker_source,changes=adapted_worker();(out/'worker_source.txt').write_text(worker_source,encoding='utf-8')
    e=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),N=400,checkpoints=[],children=[],point03_closed=False)
    try:
        guard(out);references=[dict(path=r['solutions'][str(part)]['field_path'],sha256=r['solutions'][str(part)]['field_sha256']) for part in (4,8)]
        sources=[Path(__file__).resolve(),ROOT/'scripts/run_point03_fdst_pilot.py',ROOT/'scripts/point03_fdst.py',ROOT/'scripts/run_point03_exponential.py',ROOT/'scripts/point03_linear_detector.py',ROOT/'Docs/POINT-03-FDST-ACCURACY-CONTRACT.md',ROOT/'resultados/codex/point03_fdst400_timing_20261007.json',lp/'assessment.json',lp/'execution.json',lp/'integrity_audit.json',hp/'manifest.json',hp/'execution.json',hp/'integrity_audit.json',kp/'execution.json',out/'worker_source.txt']
        sources += [Path(v['path']) for v in references]
        oldcp=read(read(lp/'execution.json')['solutions'][-1]['checkpoints'][-1]['path']);sources.append(Path(oldcp['field_path']))
        m=dict(created_utc=datetime.now(timezone.utc).isoformat(),N=400,input_path=case['input_path'],input_sha256=case['input_sha256'],source_sha256={str(p):sha(p) for p in sources},reference_fields=references,L1_execution_path=str(lp/'execution.json'),L1_assessment_path=str(lp/'assessment.json'),K626_execution_path=str(kp/'execution.json'),worker_numeric_changes=changes,numerical_threads=1,steps_total=12800)
        write(out/'manifest.json',m);e.update(manifest_path=str(out/'manifest.json'),manifest_sha256=sha(out/'manifest.json'));previous=None
        directory=out/'n400_steps12800';directory.mkdir()
        for chunk in range(1,33):
            assert time.monotonic()-start<=7200;guard(out);prefix=directory/f'chunk{chunk:02d}'
            cmd=[sys.executable,str(Path(__file__).resolve()),'--worker','--manifest',e['manifest_path'],'--manifest-sha',e['manifest_sha256'],'--steps','12800','--chunk',str(chunk),'--prefix',str(prefix)]
            if previous:cmd+=['--previous',str(previous)]
            t=time.monotonic()
            with Path(str(prefix)+'.log').open('xb') as log:child=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=370,check=False)
            e['children'].append(dict(chunk=chunk,returncode=child.returncode,elapsed_s=time.monotonic()-t));cp=Path(str(prefix)+'.json')
            assert child.returncode==0 and read(cp)['status']=='completed';e['checkpoints'].append(dict(path=str(cp),sha256=sha(cp)));previous=cp
            print(json.dumps(dict(N=400,chunk=chunk,total_chunks=32,elapsed_s=round(time.monotonic()-start,1))),flush=True)
        a=assess(e);write(out/'assessment.json',a);e.update(status='completed',L2_accuracy_pass=a['L2_accuracy_pass'],assessment_path=str(out/'assessment.json'),assessment_sha256=sha(out/'assessment.json'))
    except Exception as err:e.update(status='failed',error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    e.update(elapsed_s=time.monotonic()-start,finished_utc=datetime.now(timezone.utc).isoformat(),sources_unchanged=all(sha(p)==d for p,d in locals().get('m',{}).get('source_sha256',{}).items()))
    write(out/'execution.json',e);print(json.dumps({q:e.get(q) for q in ('status','L2_accuracy_pass','point03_closed','elapsed_s','error')}),flush=True);return 0 if e.get('L2_accuracy_pass') else 2 if e['status']=='completed' else 1

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path);p.add_argument('--source-check',action='store_true');p.add_argument('--worker',action='store_true');p.add_argument('--manifest',type=Path);p.add_argument('--manifest-sha');p.add_argument('--steps',type=int);p.add_argument('--chunk',type=int);p.add_argument('--prefix',type=Path);p.add_argument('--previous',type=Path);a=p.parse_args()
    if a.source_check:
        _,_,changes=adapted_worker()
        result=dict(created_utc=datetime.now(timezone.utc).isoformat(),source_adapter_pass=True,numeric_changes=changes,no_T96_propagation=True,source_sha256={str(p):sha(p) for p in (Path(__file__).resolve(),ROOT/'scripts/run_point03_fdst_pilot.py',ROOT/'Docs/POINT-03-FDST-ACCURACY-CONTRACT.md')})
        write(ROOT/'resultados/codex/point03_fdst_accuracy_source_preflight_run2_20261007.json',result);print(json.dumps(result));return 0
    if a.worker:f,_,_=adapted_worker();return f(a)
    return run(a.out.resolve())
if __name__=='__main__':raise SystemExit(main())
