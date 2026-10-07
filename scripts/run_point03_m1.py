"""Prospective N767: frozen exponential worker and adapted FDST worker."""
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
from run_point03_exponential import ROOT,sha,write,guard,load,worker as exponential_worker
import run_point03_fdst_pilot as l1

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def order(ns,powers):
    from scipy.optimize import brentq
    h=[128/n for n in ns];d0=powers[0]-powers[1];d1=powers[1]-powers[2]
    assert d0*d1>0 and min(abs(d0),abs(d1))>1e-12
    ratio=d0/d1
    return float(brentq(lambda p:((h[0]/h[2])**p-(h[1]/h[2])**p)/((h[1]/h[2])**p-1)-ratio,.05,8))

def adapted_workers():
    original=load('m1_geometry_original',ROOT/'scripts/run_point03_reconstructed.py')
    geometry=ast.parse(inspect.getsource(original.prepare640))
    class Geometry(ast.NodeTransformer):
        def __init__(self):self.count=0
        def visit_FunctionDef(self,node):
            if node.name=='prepare640':node.name='prepare767';self.count+=1
            return self.generic_visit(node)
        def visit_Constant(self,node):
            if node.value==640:self.count+=1;return ast.copy_location(ast.Constant(767),node)
            if node.value in ('geometry640.npz','n640_input.npz'):
                self.count+=1;return ast.copy_location(ast.Constant(node.value.replace('640','767')),node)
            return node
    ga=Geometry();geometry=ga.visit(geometry);ast.fix_missing_locations(geometry);assert ga.count==4
    namespace=dict(original.__dict__);exec(compile(geometry,'registered_M1_geometry','exec'),namespace)
    temporal=ast.parse(inspect.getsource(l1.worker))
    class Temporal(ast.NodeTransformer):
        def __init__(self):self.counts={626:0,400:0}
        def visit_Constant(self,node):
            if node.value in self.counts:
                self.counts[node.value]+=1;return ast.copy_location(ast.Constant({626:767,400:512}[node.value]),node)
            return node
    ta=Temporal();temporal=ta.visit(temporal);ast.fix_missing_locations(temporal);assert ta.counts=={626:3,400:2}
    ns=dict(l1.__dict__);exec(compile(temporal,'registered_M1_FDST','exec'),ns)
    return namespace['prepare767'],ns['worker'],ast.unparse(geometry)+'\n',ast.unparse(temporal)+'\n'

def prediction():
    initial=read(ROOT/'resultados/codex/point03_linear_prediction_20261007.json')['rows']
    k640=read(ROOT/'resultados/codex/point03_linear_K640_20261007.json')
    rows=[r for r in initial if r['N'] in (320,400,500)]
    values={m:[r['methods'][m]['P_core'] for r in rows]+[k640['gates'][m]['actual']] for m in ('field','intensity')}
    reports={}
    for m,powers in values.items():
        p0=order([320,400,500],powers[:3]);p1=order([400,500,640],powers[1:])
        discrepancy=abs(p0-p1)/max(abs(p0),abs(p1));assert discrepancy<=.2
        forecast=powers[-1]+(powers[-1]-powers[-2])*(1-(640/767)**p1)/((640/500)**p1-1)
        reports[m]=dict(powers=powers,orders=[p0,p1],discrepancy=discrepancy,prediction=forecast)
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),N=767,prediction=reports,point03_closed=False,no_N767_geometry_prepared=True,source_sha256={str(p):sha(p) for p in (Path(__file__).resolve(),ROOT/'Docs/POINT-03-M1-CONTRACT.md',ROOT/'resultados/codex/point03_linear_prediction_20261007.json',ROOT/'resultados/codex/point03_linear_K640_20261007.json')})

def fields_and_measures(e):
    import numpy as np
    from point03_linear_detector import Detector
    m=l1.verify_manifest(e['manifest_path'],e['manifest_sha256']);dx=128e-6/767
    with np.load(m['input_path'],allow_pickle=False) as z:pin=float(np.sum(abs(z['A0'])**2)*dx**2)
    fields={};measures={};count=0;detector=Detector()
    for label,solution in e['solutions'].items():
        previous=digest=None;power=pin
        for index,link in enumerate(solution['checkpoints'],1):
            assert sha(link['path'])==link['sha256'];cp=read(link['path'])
            assert cp['status']=='completed' and cp['previous_report_path']==previous and cp['previous_report_sha256']==digest
            assert cp['elapsed_s']<=360 and cp['started_utc']>m['created_utc']
            if label=='FDST':assert cp['chunk']==index and cp['steps_done']==512*index and cp['steps_total']==20480 and cp['dz_m']==.002/20480
            else:assert cp['N']==767 and cp['segment']==index and cp['segments']==int(label) and cp['length_m']==.002/int(label)
            assert sha(cp['field_path'])==cp['field_sha256']
            with np.load(cp['field_path'],allow_pickle=False) as z:field=z['field'].copy()
            assert field.shape==(767,767) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
            actual=float(np.vdot(field,field).real*dx**2);assert abs(actual-cp['raw_total'])<=1e-12 and 0<actual<=power+1e-9
            for key in ('resource_start','resource_end'):
                assert cp[key]['available_ram_bytes']>1.5*1024**3 and cp[key]['free_disk_bytes']>2*1024**3
            previous,digest,power=link['path'],link['sha256'],actual;count+=1
        fields[label]=field;measures[label]=detector.measure(field,767,pin)
    assert count==90
    return m,pin,fields,measures

def assess(e):
    import numpy as np
    m,pin,fields,measures=fields_and_measures(e);pred=read(m['prediction_path']);dx=128e-6/767
    norms={key:float(np.linalg.norm(value)) for key,value in fields.items()}
    ref_distance=float(np.linalg.norm(fields['19']-fields['31']));time_distance=float(np.linalg.norm(fields['FDST']-fields['31']))
    ref_bound=dx**2*(norms['19']+norms['31'])*ref_distance/pin
    time_bound=dx**2*(norms['FDST']+norms['31'])*time_distance/pin
    quad=max(v['change'] for row in measures.values() for v in row.values());gates={}
    reconstruction=abs(measures['31']['field']['P_core']-measures['31']['intensity']['P_core'])
    for method in ('field','intensity'):
        old=pred['prediction'][method];actual=measures['31'][method]['P_core'];last=old['powers'][-1]
        order_failure=None
        try:
            p=order([500,640,767],[old['powers'][-2],last,actual]);disagreement=abs(p-old['orders'][-1])/max(abs(p),abs(old['orders'][-1]))
        except (AssertionError,ValueError) as error:
            p=disagreement=None;order_failure=type(error).__name__
        residual=abs(actual-old['prediction']);limit=.1*abs(actual-last)
        ref_error=abs(measures['19'][method]['P_core']-actual);temporal_error=abs(measures['FDST'][method]['P_core']-actual)
        spatial=1.25*abs(actual-last)/((767/640)**min(p,2)-1) if p is not None else None
        total=spatial+temporal_error+ref_error+quad+reconstruction if spatial is not None else None
        conditions=dict(holdout=abs(actual-last)>1e-12 and residual<=limit,order=disagreement is not None and disagreement<=.2,reference_power=ref_error<=1e-8,temporal_power=temporal_error<=1e-6,uncertainty=total is not None and total<=1e-3 and total<=.01*abs(actual))
        gates[method]=dict(actual=actual,prediction=old['prediction'],residual=residual,limit=limit,new_order=p,order_disagreement=disagreement,order_failure=order_failure,reference_error=ref_error,temporal_error=temporal_error,space_indicator=spatial,total_indicator=total,conditions=conditions,pass_=all(conditions.values()))
    global_gates=dict(reference_field=ref_distance/norms['31']<=1e-9,reference_bound=ref_bound<=1e-6,temporal_field=time_distance/norms['31']<=1e-4,temporal_bound=time_bound+ref_bound+quad<=1e-5,quadrature=quad<=1e-10)
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,scientific_pass=all(global_gates.values()) and all(row['pass_'] for row in gates.values()),point03_closed=False,closure_requires_independent_audit=True,P_in=pin,methods=measures,gates=gates,global_gates=global_gates,reference_field_difference=ref_distance/norms['31'],temporal_field_difference=time_distance/norms['31'],reference_bound=ref_bound,temporal_bound=time_bound,reconstruction_difference=reconstruction,quadrature_change=quad,checkpoints_checked=90,scope='Conditional local scalar core power only; all historical failures retained.')

def run(out):
    start=time.monotonic();assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    old=ROOT/'resultados/codex/point03_fdst_accuracy_20261007_L2'
    assert read(old/'assessment.json')['L2_accuracy_pass'] and read(old/'integrity_audit.json')['integrity_pass']
    assert read(ROOT/'resultados/codex/point03_fdst_finer_cost_20261007/n767.json')['pass_']
    assert read(ROOT/'resultados/codex/point03_m1_source_preflight_final_20261007.json')['source_sha256']==sha(__file__)
    assert read(ROOT/'resultados/codex/point03_linear_detector_preflight_20261007.json')['pass_']
    predpath=ROOT/'resultados/codex/point03_m1_prediction_20261007.json';pred=read(predpath)
    for path,digest in pred['source_sha256'].items():assert sha(path)==digest
    out.mkdir();execution=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),solutions={},children=[],point03_closed=False)
    try:
        guard(out);prepare,_,geometry_source,temporal_source=adapted_workers()
        (out/'geometry_source.txt').write_text(geometry_source,encoding='utf-8');(out/'temporal_source.txt').write_text(temporal_source,encoding='utf-8')
        input_path=prepare(out,start+18000);geometry=read(out/'geometry_report.json');assert geometry['N']==767 and geometry['geometry_pass'] and len(geometry['reference_cells'])==48
        sources=[Path(__file__).resolve(),ROOT/'Docs/POINT-03-M1-CONTRACT.md',predpath,ROOT/'scripts/run_point03_exponential.py',ROOT/'scripts/run_point03_fdst_pilot.py',ROOT/'scripts/point03_fdst.py',ROOT/'scripts/run_point03_reconstructed.py',ROOT/'scripts/point03_union_geometry.py',ROOT/'scripts/point03_geometry_reference.py',ROOT/'experimentos/glass009_claude/adi2d.py',ROOT/'src/silice/coverage.py',ROOT/'src/silice/tracks.py',ROOT/'scripts/point03_linear_detector.py',out/'geometry_source.txt',out/'temporal_source.txt',out/'geometry_report.json',out/'geometry_selection.json',ROOT/'resultados/codex/point03_geometry_20261006234649Z/inputs/centres.json',old/'assessment.json',old/'integrity_audit.json']
        manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),N=767,input_path=str(input_path),input_sha256=sha(input_path),prediction_path=str(predpath),prediction_sha256=sha(predpath),plan=[dict(N=767,input_path=str(input_path),input_sha256=sha(input_path))],source_sha256={str(path):sha(path) for path in sources},numerical_threads=1)
        write(out/'manifest.json',manifest);execution.update(manifest_path=str(out/'manifest.json'),manifest_sha256=sha(out/'manifest.json'))
        for label,total in (('19',19),('31',31),('FDST',40)):
            directory=out/label;directory.mkdir();previous=None;chain=[]
            for index in range(1,total+1):
                assert time.monotonic()-start<=18000;guard(out);prefix=directory/f'part{index:03d}'
                command=[sys.executable,str(Path(__file__).resolve()),'--worker','--integrator',label,'--manifest',execution['manifest_path'],'--manifest-sha',execution['manifest_sha256'],'--prefix',str(prefix)]
                command+=['--steps','20480','--chunk',str(index)] if label=='FDST' else ['--n','767','--segments',label,'--segment',str(index)]
                if previous:command+=['--previous',str(previous)]
                before=time.monotonic()
                with Path(str(prefix)+'.log').open('xb') as log:child=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=370,check=False)
                cp=Path(str(prefix)+'.json');execution['children'].append(dict(integrator=label,index=index,returncode=child.returncode,elapsed_s=time.monotonic()-before))
                assert child.returncode==0 and read(cp)['status']=='completed';chain.append(dict(path=str(cp),sha256=sha(cp)));previous=cp
                print(json.dumps(dict(N=767,integrator=label,index=index,total=total,elapsed_s=round(time.monotonic()-start,1))),flush=True)
            execution['solutions'][label]=dict(checkpoints=chain)
        assessment=assess(execution);write(out/'assessment.json',assessment);execution.update(status='completed',scientific_pass=assessment['scientific_pass'],assessment_path=str(out/'assessment.json'),assessment_sha256=sha(out/'assessment.json'))
    except Exception as error:execution.update(status='failed',error_type=type(error).__name__,error=str(error),diagnostic=traceback.format_exc())
    execution.update(elapsed_s=time.monotonic()-start,finished_utc=datetime.now(timezone.utc).isoformat(),sources_unchanged=all(sha(path)==digest for path,digest in locals().get('manifest',{}).get('source_sha256',{}).items()))
    write(out/'execution.json',execution);print(json.dumps({key:execution.get(key) for key in ('status','scientific_pass','point03_closed','elapsed_s','error')}),flush=True)
    return 0 if execution.get('scientific_pass') else 2 if execution['status']=='completed' else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path);parser.add_argument('--source-check',action='store_true');parser.add_argument('--prediction',action='store_true');parser.add_argument('--worker',action='store_true');parser.add_argument('--integrator');parser.add_argument('--manifest',type=Path);parser.add_argument('--manifest-sha');parser.add_argument('--prefix',type=Path);parser.add_argument('--previous',type=Path);parser.add_argument('--n',type=int);parser.add_argument('--segments',type=int);parser.add_argument('--segment',type=int);parser.add_argument('--steps',type=int);parser.add_argument('--chunk',type=int);args=parser.parse_args()
    if args.source_check:
        _,_,geometry,temporal=adapted_workers();write(ROOT/'resultados/codex/point03_m1_source_preflight_final_20261007.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),pass_=True,no_geometry_or_propagation=True,geometry_changes=4,temporal_changes=dict(N=3,chunk=2),geometry_generated_sha256=__import__('hashlib').sha256(geometry.encode()).hexdigest(),temporal_generated_sha256=__import__('hashlib').sha256(temporal.encode()).hexdigest(),source_sha256=sha(__file__)));print('M1 source adapter PASS');raise SystemExit(0)
    if args.prediction:
        result=prediction();write(ROOT/'resultados/codex/point03_m1_prediction_20261007.json',result);print(json.dumps(result));raise SystemExit(0)
    if args.worker:
        if args.integrator=='FDST':_,function,_,_=adapted_workers();raise SystemExit(function(args))
        raise SystemExit(exponential_worker(args))
    raise SystemExit(run(args.out.resolve()))
