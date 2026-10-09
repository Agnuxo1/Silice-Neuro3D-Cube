"""Bounded sequential G experiment; preserves E and uses its frozen ADI."""
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
E=ROOT/'resultados/codex/point03_analytic_20261007T004526617696Z'
D=ROOT/'resultados/codex/point03_geometry_20261006234649Z'
NEW_PLAN=[('g_n256_mid',256,.3125e-6,6400),('g_n320_mid',320,.3125e-6,6400),
          ('g_n400_fine',400,.15625e-6,12800),('g_n500_fine',500,.15625e-6,12800),
          ('g_n640_holdout',640,.3125e-6,6400)]
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):
    os.environ[name]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,data):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(data,f,indent=2,allow_nan=False);f.write('\n')


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module


def guard(out,deadline):
    import psutil
    assert time.monotonic()<deadline,'Work deadline exceeded'
    ram=psutil.virtual_memory().available;disk=psutil.disk_usage(str(out)).free
    assert ram>1.5*1024**3,'RAM below 1.5 GiB'
    assert disk>2*1024**3,'Disk below 2 GiB'
    return dict(utc=datetime.now(timezone.utc).isoformat(),available_ram_bytes=ram,free_disk_bytes=disk)


def prepare640(out,deadline):
    import numpy as np
    regionmod=load('g_union',ROOT/'scripts/point03_union_geometry.py')
    refmod=load('g_reference',ROOT/'scripts/point03_geometry_reference.py')
    spec=json.loads((D/'inputs/centres.json').read_text())['spec_um']
    region=regionmod.UnionRegion(spec)
    n=640; dx_um=128/n; dx=128e-6/n
    ax=(np.arange(n)-n//2)*dx_um
    fraction=np.zeros((n,n),dtype=np.float64);raw=fraction.copy()
    correction=fraction.copy();chosen={}
    indices=np.flatnonzero(np.abs(ax)<=12+dx_um)
    for iy in indices:
        guard(out,deadline)
        for ix in indices:
            rect=[ax[ix]-dx_um/2,ax[ix]+dx_um/2,ax[iy]-dx_um/2,ax[iy]+dx_um/2]
            result=region.cell(rect)
            assert result['within_guard'] and result['boundary_closed']
            raw[iy,ix]=result['raw_fraction'];fraction[iy,ix]=result['fraction']
            correction[iy,ix]=result['correction']
            if 0<result['fraction']<1:
                chosen[(int(iy),int(ix))]=rect
    np.savez(out/'geometry640.npz',raw_fraction=raw,fraction=fraction,correction=correction)
    global_area=region.global_area()['area_um2']
    area=float(np.sum(fraction)*dx_um**2)
    assert abs(area/global_area-1)<=1e-12,'Global coverage area mismatch'
    pools={name:sorted(k for k in chosen if abs(math.hypot(ax[k[1]],ax[k[0]])-radius)<=dx_um)
           for name,radius in (('inner',6),('outer',12))}
    selection=[]
    for name,pool in pools.items():
        assert len(pool)>=16
        selection += [(name,pool[i]) for i in np.linspace(0,len(pool)-1,16,dtype=int)]
    used={k for _,k in selection}
    pool=sorted(set(chosen)-used);assert len(pool)>=16
    selection += [('partial',pool[i]) for i in np.linspace(0,len(pool)-1,16,dtype=int)]
    assert len({k for _,k in selection})==48
    report=dict(spec_um=spec,N=n,global_area=global_area,grid_area=area,
                maximum_endpoint_correction=float(np.abs(correction).max()),reference_cells=[],
                selection=[dict(group=g,iy=k[0],ix=k[1],rect=chosen[k]) for g,k in selection])
    # Selection is retained before independent area errors are calculated.
    write(out/'geometry_selection.json',report['selection'])
    try:
        for group,k in selection:
            guard(out,deadline)
            ref=refmod.cell_reference(spec,chosen[k],deadline=deadline)
            delta=abs(ref['fraction_fine']-fraction[k])
            report['reference_cells'].append(dict(group=group,iy=k[0],ix=k[1],reference=ref,delta=delta))
            assert ref['quality_pass'] and ref['quality_total']<=1e-13 and delta<=1e-12
        report['geometry_pass']=True
    finally:
        write(out/'geometry_report.json',report)
    adi=load('g_input_adi',ROOT/'experimentos/glass009_claude/adi2d.py')
    sys.path.insert(0,str(ROOT/'src'))
    from silice.coverage import circle_coverage
    class Grid:
        points=n; width_m=128e-6; dx_m=dx
        def coordinates(self):
            axis=(np.arange(n)-n//2)*dx
            return np.meshgrid(axis,axis,indexing='xy')
    a0=adi.gaussian(n,dx,6e-6);sig=adi.sigma_map(n,dx,smax=4e4,frac=.2)
    weights=circle_coverage(Grid(),6e-6)
    assert abs(float(np.sum(np.abs(a0)**2)*dx*dx)-1)<=1e-12
    assert abs(float(weights.sum()*dx*dx)/(math.pi*(6e-6)**2)-1)<=1e-12
    path=out/'n640_input.npz';np.savez(path,A0=a0,sigma=sig,dn=-.003*fraction,weights=weights)
    return path


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
        for i in range(200):
            assert time.monotonic()<deadline,'Worker retention reserve reached'
            if i%20==0:report['resource_samples'].append(guard(prefix.parent,deadline))
            field=stepper.step(field);report['steps_done']=i+1
        assert field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
        total=float(np.sum(np.abs(field)**2)*(128e-6/case['N'])**2)
        assert 0<total<=1.001
        report.update(status='completed',completed_step=args.start+200,raw_total=total)
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


def run(out):
    start=time.monotonic();deadline=start+7200
    assert out.is_relative_to(ROOT/'resultados/codex') and not out.exists()
    out.mkdir(parents=True,exist_ok=False)
    report=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),results=[],children=[],new_plan=NEW_PLAN,gpu_used=False)
    try:
        guard(out,deadline)
        sources=[Path(__file__).resolve(),ROOT/'scripts/assess_point03_reconstructed.py',
                 ROOT/'scripts/assess_point03_analytic.py',ROOT/'scripts/point03_sparse_adi.py',
                 ROOT/'scripts/point03_union_geometry.py',ROOT/'scripts/point03_geometry_reference.py',
                 ROOT/'experimentos/glass009_claude/adi2d.py',ROOT/'src/silice/coverage.py',ROOT/'src/silice/tracks.py',
                 ROOT/'Docs/POINT-03-RECONSTRUCTED-REFINEMENT-CONTRACT.md',D/'inputs/centres.json',
                 E/'assessment.json',E/'manifest.json',E/'execution.json',
                 ROOT/'resultados/codex/point03_reconstruction_20261007_run2/diagnostic.json']
        frozen={str(p):sha(p) for p in sources}
        e=json.loads((E/'assessment.json').read_text());assert e['integrity_pass']
        original={c['case_id']:c for c in e['independent_measurements']}
        inputs={n:Path(original[f'n{n}_geom_z0625']['input_npz_path']) for n in (256,320,400,500)}
        for n,ip in inputs.items():assert sha(ip)==original[f'n{n}_geom_z0625']['input_npz_sha256']
        inputs[640]=prepare640(out,time.monotonic()+180)
        new_plan=[dict(id=id_,N=n,dz_m=dz,steps=steps,input_path=str(inputs[n]),input_sha256=sha(inputs[n])) for id_,n,dz,steps in NEW_PLAN]
        manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),source_sha256=frozen,new_plan=new_plan,
                      geometry_pass=True,geometry_report_path=str(out/'geometry_report.json'),
                      geometry_report_sha256=sha(out/'geometry_report.json'),input_sha256={str(p):sha(p) for p in inputs.values()},
                      environment=dict(python=sys.version,numerical_threads=1),E_original_assessment_sha256=sha(E/'assessment.json'))
        write(out/'manifest.json',manifest)
        report.update(manifest_path=str(out/'manifest.json'),manifest_sha256=sha(out/'manifest.json'))
        print(json.dumps({'phase':'prepared','new_cases':5,'reused_cases':4}),flush=True)

        def new_case(case):
            previous=None; checkpoints=[]; n=case['N']
            caseout=out/case['id'];caseout.mkdir()
            for step in range(0,case['steps'],200):
                guard(out,deadline)
                prefix=caseout/f'step_{step+200:05d}'
                cmd=[sys.executable,str(Path(__file__).resolve()),'--worker','--manifest',str(out/'manifest.json'),
                     '--manifest-sha',report['manifest_sha256'],'--case',case['id'],'--start',str(step),'--prefix',str(prefix)]
                if previous:cmd += ['--previous',str(previous)]
                with Path(str(prefix)+'.stdout.log').open('xb') as stdout,Path(str(prefix)+'.stderr.log').open('xb') as stderr:
                    childstart=time.monotonic()
                    result=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=40,check=False)
                cp=Path(str(prefix)+'.json')
                report['children'].append(dict(case=case['id'],step=step,returncode=result.returncode,elapsed_s=time.monotonic()-childstart,
                                               stdout=str(prefix)+'.stdout.log',stderr=str(prefix)+'.stderr.log'))
                assert result.returncode==0,'Propagation child failed: '+str(cp)
                workerreport=json.loads(cp.read_text());assert workerreport['status']=='completed'
                checkpoints.append(dict(path=str(cp),sha256=sha(cp)));previous=cp
                print(json.dumps({'case':case['id'],'steps':step+200,'target':case['steps'],'elapsed_s':round(time.monotonic()-start,1)}),flush=True)
            return dict(id=case['id'],N=n,dz_m=case['dz_m'],steps=case['steps'],input_path=case['input_path'],input_sha256=case['input_sha256'],
                        field_path=workerreport['field_path'],field_sha256=workerreport['field_sha256'],checkpoints=checkpoints,reused=False)

        def reused(id_):
            c=original[id_]
            assert sha(c['final_npz_path'])==c['final_npz_sha256']
            return dict(id=id_,N=c['N'],dz_m=c['dz_m'],steps=c['steps_completed'],input_path=c['input_npz_path'],input_sha256=c['input_npz_sha256'],
                        field_path=c['final_npz_path'],field_sha256=c['final_npz_sha256'],reused=True,E_case_path=c['case_path'],E_case_sha256=c['case_sha256'])
        for case in new_plan[:2]:report['results'].append(new_case(case))
        for id_ in ('n400_geom_z03125','n500_geom_z03125','n400_geom_z0625','n500_geom_z0625'):
            report['results'].append(reused(id_))
        for case in new_plan[2:4]:report['results'].append(new_case(case))
        write(out/'pre_holdout_execution.json',report)
        prediction=out/'prediction.json'
        result=subprocess.run([sys.executable,str(ROOT/'scripts/assess_point03_reconstructed.py'),'--execution',str(out/'pre_holdout_execution.json'),
                               '--mode','prediction','--out',str(prediction)],capture_output=True,timeout=120)
        (out/'prediction.stdout.log').write_bytes(result.stdout);(out/'prediction.stderr.log').write_bytes(result.stderr)
        assert result.returncode==0,'Prediction assessor failed'
        report.update(prediction_path=str(prediction),prediction_sha256=sha(prediction),holdout_started_utc=datetime.now(timezone.utc).isoformat())
        print(json.dumps({'phase':'prediction_saved','elapsed_s':round(time.monotonic()-start,1)}),flush=True)
        report['results'].append(new_case(new_plan[4]))
        assert all(sha(p)==d for p,d in frozen.items())
        assert all(sha(p)==d for p,d in manifest['input_sha256'].items())
        report.update(status='completed',sources_unchanged=True,inputs_unchanged=True,elapsed_s=time.monotonic()-start)
        write(out/'propagation_execution.json',report)
        final=out/'assessment.json'
        result=subprocess.run([sys.executable,str(ROOT/'scripts/assess_point03_reconstructed.py'),'--execution',str(out/'propagation_execution.json'),
                               '--mode','final','--out',str(final)],capture_output=True,timeout=120)
        (out/'assessment.stdout.log').write_bytes(result.stdout);(out/'assessment.stderr.log').write_bytes(result.stderr)
        assert result.returncode in (0,2),'Final assessor failed'
        report.update(scientific_pass=result.returncode==0,assessment_path=str(final),assessment_sha256=sha(final))
    except Exception as err:
        report.update(status='failed',scientific_pass=None,error_type=type(err).__name__,error=str(err),diagnostic=traceback.format_exc())
    report['elapsed_s']=time.monotonic()-start
    write(out/'execution.json',report)
    print(json.dumps({k:report.get(k) for k in ['status','scientific_pass','elapsed_s','error']}),flush=True)
    return 0 if report.get('scientific_pass') else 2 if report['status']=='completed' else 1


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--worker',action='store_true')
    parser.add_argument('--manifest',type=Path);parser.add_argument('--manifest-sha')
    parser.add_argument('--case');parser.add_argument('--start',type=int)
    parser.add_argument('--prefix',type=Path);parser.add_argument('--previous',type=Path)
    args=parser.parse_args()
    return worker(args) if args.worker else run(args.out.resolve())


if __name__=='__main__':
    raise SystemExit(main())
