"""Fixed physical domain study; freeze holdout prediction before its geometry."""
import argparse
import ast
from datetime import datetime,timezone
import inspect
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
from run_point03_exponential import ROOT,sha,write,operator,guard
from point03_fdst import Solver
from point03_linear_detector import Detector
from audit_point03_m1 import observed


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def worker(args):
    start=time.monotonic();np.random.seed(0)
    cp=dict(status='failed',started_utc=datetime.now(timezone.utc).isoformat(),M=args.M,N=args.M-1,integrator=args.integrator,index=args.index,total=args.total,previous_report_path=str(args.previous) if args.previous else None)
    try:
        cp['resource_start']=guard(args.prefix.parent)
        assert sha(args.manifest)==args.manifest_sha
        m=read(args.manifest)
        for path,digest in m['source_sha256'].items():assert sha(path)==digest
        case=next(case for case in m['plan'] if case['M']==args.M)
        assert sha(case['input_path'])==case['input_sha256']
        with np.load(case['input_path'],allow_pickle=False) as data:field=data['A0'].copy();dn=data['dn'];sigma=data['sigma']
        dx=128e-6/args.M;power=case['P_in']
        if args.previous:
            old=read(args.previous)
            assert old['status']=='completed' and old['M']==args.M and old['index']==args.index-1 and old['integrator']==args.integrator and old['total']==args.total
            assert sha(old['field_path'])==old['field_sha256']
            with np.load(old['field_path'],allow_pickle=False) as data:field=data['field'].copy()
            cp['previous_report_sha256']=sha(args.previous);power=old['raw_total']
        else:assert args.index==1;cp['previous_report_sha256']=None
        assert field.shape==(args.M-1,args.M-1)
        if args.integrator=='E':
            matrix,trace=operator(dn,sigma,dx);length=.002/args.total
            field=expm_multiply(length*matrix,field.ravel(),traceA=length*trace).reshape(field.shape)
            cp['length_m']=length
        else:
            assert args.M==800 and args.total==64
            solver=Solver(dn,sigma,dx,.002/25600);field=solver.advance(field,400)
            cp.update(steps_total=25600,steps_done=args.index*400,dz_m=.002/25600,max_negative_amplification=solver.max_negative_amplification)
        total=float(np.vdot(field,field).real*dx**2)
        assert field.dtype==np.dtype('complex128') and np.all(np.isfinite(field)) and 0<total<=power+1e-9
        cp.update(status='completed',raw_total=total,previous_power=power,dx_m=dx,resource_end=guard(args.prefix.parent))
    except Exception as error:cp.update(error=str(error),error_type=type(error).__name__,diagnostic=traceback.format_exc())
    if 'field' in locals():
        np.savez(str(args.prefix)+'.npz',field=field)
        cp.update(field_path=str(args.prefix)+'.npz',field_sha256=sha(str(args.prefix)+'.npz'))
    cp['elapsed_s']=time.monotonic()-start
    if cp['elapsed_s']>360:cp.update(status='failed',error='360s budget exceeded')
    write(str(args.prefix)+'.json',cp)
    return 0 if cp['status']=='completed' else 1


def cropped(path,digest,M,out):
    assert sha(path)==digest
    with np.load(path,allow_pickle=False) as data:original={key:data[key].copy() for key in ('A0','dn','sigma','weights')}
    assert all(value.shape==(M,M) for value in original.values())
    assert np.all(original['dn'][0,:]==0) and np.all(original['dn'][:,0]==0) and np.all(original['weights'][0,:]==0) and np.all(original['weights'][:,0]==0)
    arrays={key:value[1:,1:].copy() for key,value in original.items()};dx=128e-6/M
    pin=float(np.vdot(arrays['A0'],arrays['A0']).real*dx**2)
    original_pin=float(np.vdot(original['A0'],original['A0']).real*dx**2)
    assert abs(pin-original_pin)<=1e-12
    target=out/f'n{M-1}_input.npz';np.savez(target,**arrays)
    area=float(-arrays['dn'].sum()*dx**2/.003)
    return dict(M=M,N=M-1,dx_m=dx,P_in=pin,input_path=str(target),input_sha256=sha(target),original_input_path=str(path),original_input_sha256=digest,cladding_area_m2=area,removed_input_power=abs(pin-original_pin))


def trajectory(out,manifest_path,e,M,total,integrator,start):
    label='F64' if integrator=='F' else f'E{total}'
    directory=out/f'm{M}_{label}';directory.mkdir();chain=[];previous=None
    for index in range(1,total+1):
        assert time.monotonic()-start<=36000;guard(out)
        prefix=directory/f'part{index:03d}'
        command=[sys.executable,str(Path(__file__).resolve()),'--worker','--manifest',str(manifest_path),'--manifest-sha',sha(manifest_path),'--M',str(M),'--integrator',integrator,'--index',str(index),'--total',str(total),'--prefix',str(prefix)]
        if previous:command+=['--previous',str(previous)]
        before=time.monotonic()
        with Path(str(prefix)+'.log').open('xb') as log:child=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=370)
        cp=Path(str(prefix)+'.json');event=dict(M=M,label=label,index=index,returncode=child.returncode,elapsed_s=time.monotonic()-before)
        e['children'].append(event);assert child.returncode==0 and read(cp)['status']=='completed'
        chain.append(dict(path=str(cp),sha256=sha(cp)));previous=cp
        print(json.dumps(dict(M=M,label=label,index=index,total=total,elapsed_s=round(time.monotonic()-start,1))),flush=True)
    return dict(checkpoints=chain,label=label,manifest_path=str(manifest_path))


def fields(solution):
    cp=read(solution['checkpoints'][-1]['path']);assert sha(cp['field_path'])==cp['field_sha256']
    with np.load(cp['field_path'],allow_pickle=False) as data:return np.pad(data['field'],((1,0),(1,0)))


def pair_metrics(M,solutions,pin,detector):
    labels=list(solutions);values={label:fields(solution) for label,solution in solutions.items()}
    measured={label:detector.measure(value,M,pin) for label,value in values.items()}
    norms={label:float(np.linalg.norm(value)) for label,value in values.items()}
    distance=float(np.linalg.norm(values[labels[0]]-values[labels[1]]))
    bound=(128e-6/M)**2*(norms[labels[0]]+norms[labels[1]])*distance/pin
    quad=max(row['change'] for measurement in measured.values() for row in measurement.values())
    power_errors={method:abs(measured[labels[0]][method]['P_core']-measured[labels[1]][method]['P_core']) for method in ('field','intensity')}
    eligible=distance/norms[labels[1]]<=1e-9 and bound<=1e-6 and quad<=1e-10 and max(power_errors.values())<=1e-8
    return dict(measured=measured,fine_label=labels[1],reference_field=distance/norms[labels[1]],reference_bound=bound,quadrature_change=quad,power_errors=power_errors,eligible=eligible),values


def forecast(coarse):
    result={};eligible=all(row['eligible'] for row in coarse.values())
    for method in ('field','intensity'):
        powers=[coarse[str(M)]['measured'][coarse[str(M)]['fine_label']][method]['P_core'] for M in (320,400,500,640)]
        orders=[observed((320,400,500),powers[:3]),observed((400,500,640),powers[1:])]
        stable=all(p is not None for p in orders) and abs(orders[0]-orders[1])/max(abs(orders[0]),abs(orders[1]))<=.2
        value=powers[-1]+(powers[-1]-powers[-2])*(1-(640/800)**orders[-1])/((640/500)**orders[-1]-1) if stable else None
        result[method]=dict(powers=powers,orders=orders,eligible=stable,prediction=value)
        eligible=eligible and stable
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),eligible=eligible,methods=result,point03_closed=False)


def gaussian_control():
    detector=Detector();truth=1-math.exp(-2);rows=[]
    for phase in (0.,2e5,4e5):
        measures={}
        for M in (500,640,800):
            dx=128e-6/M;axis=(np.arange(M)-M//2)*dx;x,y=np.meshgrid(axis,axis)
            field=np.exp(-(x*x+y*y)/(6e-6)**2+1j*phase*x).astype(complex)
            pin=float(np.vdot(field,field).real*dx**2);measures[M]=detector.measure(field,M,pin)
        for method in ('field','intensity'):
            powers=[measures[M][method]['P_core'] for M in (500,640,800)]
            p=observed((500,640,800),powers);indicator=1.25*abs(powers[-1]-powers[-2])/(1.25**min(p,2)-1) if p is not None else None
            error=abs(powers[-1]-truth);passed=p is not None and 1.8<=p<=2.2 and error<=indicator
            rows.append(dict(phase_m_inverse=phase,method=method,order=p,known_error=error,indicator=indicator,pass_=passed))
    return dict(pass_=all(row['pass_'] for row in rows),truth=truth,rows=rows)


def prepare800(out,start):
    import run_point03_reconstructed as g
    function=ast.parse(inspect.getsource(g.prepare640)).body[0];function.name='prepare800'
    class Change(ast.NodeTransformer):
        count=0
        def visit_Constant(self,node):
            if node.value==640:self.count+=1;return ast.copy_location(ast.Constant(800),node)
            if node.value in ('geometry640.npz','n640_input.npz'):
                self.count+=1;return ast.copy_location(ast.Constant(node.value.replace('640','800')),node)
            return node
    transformer=Change();function=transformer.visit(function);assert transformer.count==3
    source=ast.unparse(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])))
    target=out/'geometry_source.txt';target.write_text(source+'\n',encoding='utf-8')
    namespace=g.__dict__.copy();exec(compile(target.read_text(encoding='utf-8'),str(target),'exec'),namespace)
    original=namespace['prepare800'](out,start+36000)
    case=cropped(original,sha(original),800,out)
    return case


def final_assessment(coarse,prediction,fine_case,solutions):
    detector=Detector();ref_solutions={label:solutions[label] for label in ('E29','E41')}
    ref,values=pair_metrics(800,ref_solutions,fine_case['P_in'],detector)
    fd=fields(solutions['F64']);fd_measure=detector.measure(fd,800,fine_case['P_in']);fine=values['E41'];dx=128e-6/800
    distance=float(np.linalg.norm(fd-fine));field_error=distance/float(np.linalg.norm(fine))
    bound=dx**2*(float(np.linalg.norm(fd))+float(np.linalg.norm(fine)))*distance/fine_case['P_in']
    quad=max(ref['quadrature_change'],max(row['change'] for row in fd_measure.values()))
    global_ok=ref['eligible'] and field_error<=1e-4 and quad<=1e-10 and bound+ref['reference_bound']+quad<=1e-5
    reconstruction=abs(ref['measured']['E41']['field']['P_core']-ref['measured']['E41']['intensity']['P_core'])
    rows={}
    for method in ('field','intensity'):
        old=prediction['methods'][method];value=ref['measured']['E41'][method]['P_core'];last=old['powers'][-1]
        p=observed((500,640,800),(old['powers'][-2],last,value))
        disagreement=abs(p-old['orders'][-1])/max(abs(p),abs(old['orders'][-1])) if p is not None else None
        residual=abs(value-old['prediction']);limit=.1*abs(value-last)
        temporal=abs(value-fd_measure[method]['P_core']);space=1.25*abs(value-last)/(1.25**min(p,2)-1) if p is not None else None
        indicator=space+temporal+ref['power_errors'][method]+quad+reconstruction if space is not None else None
        conditions=dict(holdout=abs(value-last)>1e-12 and residual<=limit,order=disagreement is not None and disagreement<=.2,temporal=temporal<=1e-6,indicator=indicator is not None and indicator<=1e-3 and indicator<=.01*abs(value))
        rows[method]=dict(actual=value,prediction=old['prediction'],residual=residual,limit=limit,new_order=p,order_disagreement=disagreement,temporal_error=temporal,space_indicator=space,total_indicator=indicator,conditions=conditions)
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),scientific_pass=global_ok and all(all(row['conditions'].values()) for row in rows.values()),point03_closed=False,requires_independent_audit=True,coarse=coarse,prediction=prediction,fine_reference=ref,FDST_measurements=fd_measure,temporal_field_error=field_error,temporal_bound=bound,global_eligible=global_ok,rows=rows,scope='Conditional local scalar core power for fixed ghosts only; all historic failures retained.')


def run(out):
    start=time.monotonic();assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    out.mkdir();e=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),solutions={},children=[],point03_closed=False)
    manifests=[]
    try:
        assert read(ROOT/'resultados/codex/point03_p2_cost_20261007.json')['pass_']
        p1=ROOT/'resultados/codex/point03_fixed_domain_20261007_P1';p1a=read(p1/'integrity_audit.json');assert p1a['integrity_pass'] and p1a['controls_eligible']
        p1e=read(p1/'execution.json');p1m=read(p1/'manifest.json')
        sources=[Path(__file__).resolve(),ROOT/'scripts/audit_point03_p2.py',ROOT/'Docs/POINT-03-P2-CONTRACT.md',ROOT/'scripts/run_point03_exponential.py',ROOT/'scripts/point03_fdst.py',ROOT/'scripts/point03_linear_detector.py',ROOT/'scripts/audit_point03_m1.py',ROOT/'scripts/run_point03_reconstructed.py',ROOT/'scripts/point03_union_geometry.py',ROOT/'scripts/point03_geometry_reference.py',ROOT/'experimentos/glass009_claude/adi2d.py',ROOT/'src/silice/coverage.py',ROOT/'src/silice/tracks.py',ROOT/'resultados/codex/point03_p2_cost_20261007.json',p1/'execution.json',p1/'manifest.json',p1/'assessment.json',p1/'integrity_audit.json',ROOT/'resultados/codex/point03_geometry_20261006234649Z/inputs/centres.json']
        sources += [ROOT/'resultados/codex/point03_analytic_20261007T004526617696Z/manifest.json',ROOT/'resultados/codex/point03_exponential_20261007_H2/manifest.json']
        original=read(ROOT/'resultados/codex/point03_analytic_20261007T004526617696Z/manifest.json')
        plan=[]
        for M in (320,500):
            old=next(row for row in original['case_plan'] if row['N']==M)
            plan.append(cropped(Path(old['input_npz_path']),old['input_npz_sha256'],M,out))
        old=next(row for row in read(ROOT/'resultados/codex/point03_exponential_20261007_H2/manifest.json')['plan'] if row['N']==640)
        plan.append(cropped(Path(old['input_path']),old['input_sha256'],640,out))
        p1case=dict(M=400,N=399,dx_m=128e-6/400,P_in=p1m['P_in'],input_path=p1m['input_path'],input_sha256=p1m['input_sha256'])
        with np.load(p1m['input_path'],allow_pickle=False) as data:p1case['cladding_area_m2']=float(-data['dn'].sum()*(128e-6/400)**2/.003)
        area=p1case['cladding_area_m2'];assert all(abs(case['cladding_area_m2']/area-1)<=1e-12 for case in plan)
        m=dict(created_utc=datetime.now(timezone.utc).isoformat(),plan=plan,source_sha256={str(path):sha(path) for path in sources},numerical_threads=1,ghost_bounds_m=[-64e-6,64e-6])
        manifest=out/'coarse_manifest.json';write(manifest,m);manifests.append(m)
        e['solutions']['400']={f'E{label}':dict(**solution,reused_P1=True) for label,solution in p1e['solutions'].items()}
        for M,partitions in ((320,(4,9)),(500,(9,13)),(640,(17,23))):
            e['solutions'][str(M)]={f'E{total}':trajectory(out,manifest,e,M,total,'E',start) for total in partitions}
        detector=Detector();coarse={}
        for M in (320,400,500,640):
            case=p1case if M==400 else next(case for case in plan if case['M']==M)
            coarse[str(M)],_=pair_metrics(M,e['solutions'][str(M)],case['P_in'],detector)
        prediction=forecast(coarse);write(out/'coarse_assessment.json',coarse);write(out/'prediction.json',prediction)
        if not prediction['eligible']:
            e.update(status='completed',scientific_pass=False,stage='prerequisites_failed',coarse_assessment_sha256=sha(out/'coarse_assessment.json'),prediction_sha256=sha(out/'prediction.json'))
        else:
            command=['git','-c',f'safe.directory={ROOT.as_posix()}','add','--',(out/'prediction.json').relative_to(ROOT).as_posix()]
            subprocess.run(command,cwd=ROOT,check=True)
            subprocess.run(['git','-c',f'safe.directory={ROOT.as_posix()}','-c','gc.auto=0','commit','-m','Freeze controlled P2 M800 prediction before its geometry'],cwd=ROOT,check=True,stdout=subprocess.PIPE)
            e['prediction_git_commit']=subprocess.check_output(['git','-c',f'safe.directory={ROOT.as_posix()}','rev-parse','HEAD'],cwd=ROOT).decode().strip()
            controls=gaussian_control();write(out/'gaussian_control.json',controls)
            assert controls['pass_'];fine=prepare800(out,start)
            assert abs(fine['cladding_area_m2']/area-1)<=1e-12
            added=[out/'prediction.json',out/'gaussian_control.json',out/'geometry_source.txt',out/'geometry_report.json',out/'geometry_selection.json']
            fm=dict(created_utc=datetime.now(timezone.utc).isoformat(),plan=[fine],source_sha256={**m['source_sha256'],**{str(path):sha(path) for path in added}},numerical_threads=1,ghost_bounds_m=[-64e-6,64e-6])
            fine_manifest=out/'fine_manifest.json';write(fine_manifest,fm);manifests.append(fm)
            e['solutions']['800']={f'E{total}':trajectory(out,fine_manifest,e,800,total,'E',start) for total in (29,41)}
            e['solutions']['800']['F64']=trajectory(out,fine_manifest,e,800,64,'F',start)
            a=final_assessment(coarse,prediction,fine,e['solutions']['800']);write(out/'assessment.json',a)
            e.update(status='completed',stage='holdout_complete',scientific_pass=a['scientific_pass'],assessment_sha256=sha(out/'assessment.json'))
    except Exception as error:e.update(status='failed',error=str(error),error_type=type(error).__name__,diagnostic=traceback.format_exc())
    e.update(finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_s=time.monotonic()-start,sources_unchanged=all(sha(path)==digest for m in manifests for path,digest in m['source_sha256'].items()))
    write(out/'execution.json',e);print(json.dumps({key:e.get(key) for key in ('status','stage','scientific_pass','elapsed_s','error')}),flush=True)
    return 0 if e.get('scientific_pass') else 2 if e['status']=='completed' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path);parser.add_argument('--worker',action='store_true');parser.add_argument('--manifest',type=Path);parser.add_argument('--manifest-sha');parser.add_argument('--M',type=int);parser.add_argument('--integrator',choices=('E','F'));parser.add_argument('--index',type=int);parser.add_argument('--total',type=int);parser.add_argument('--prefix',type=Path);parser.add_argument('--previous',type=Path);args=parser.parse_args()
    raise SystemExit(worker(args) if args.worker else run(args.out.resolve()))
