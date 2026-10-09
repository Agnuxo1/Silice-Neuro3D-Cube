"""Gaussian weak T96 temporal pilot with independently verified time families."""
import argparse
from datetime import datetime,timezone
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
import psutil
from scipy.sparse import load_npz
from point03_fem_time import Pade6
from point03_fem_radau import Radau5
from run_point03_exponential import ROOT,sha,write


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def guard(folder):
    ram=psutil.virtual_memory().available;disk=psutil.disk_usage(str(folder)).free
    assert ram>3*1024**3 and disk>2*1024**3
    return dict(utc=datetime.now(timezone.utc).isoformat(),available_ram_bytes=ram,free_disk_bytes=disk)


def matrices(m):
    geom=Path(m['geometry_folder']);det=Path(m['detector_folder']);damp=Path(m['damping_folder'])
    with np.load(det/'gaussian_q16.npz',allow_pickle=False) as data:initial=data['field'].copy();free=data['free_dofs'].copy()
    mass=load_npz(geom/'mass.npz')[free,:][:,free].tocsc();K=load_npz(geom/'stiffness.npz')[free,:][:,free];C=load_npz(geom/'cladding_mass.npz')[free,:][:,free];D=load_npz(damp/'damping_q12.npz')[free,:][:,free]
    k0=2*math.pi/1550e-9;B=-1j*K/(2*1.444*k0)-1j*k0*.003*C-D
    return mass,B,initial[free],free


def worker(args):
    start=time.monotonic();cp=dict(status='failed',started_utc=datetime.now(timezone.utc).isoformat(),case=args.case,index=args.index,previous_report_path=str(args.previous) if args.previous else None)
    try:
        cp['resource_start']=guard(args.prefix.parent);m=read(args.manifest);assert sha(args.manifest)==args.manifest_sha
        for path,digest in m['source_sha256'].items():assert sha(path)==digest
        mass,B,initial,free=matrices(m);case=next(case for case in m['plan'] if case['id']==args.case);power=m['P_in']
        if args.previous:
            old=read(args.previous);assert old['status']=='completed' and old['case']==args.case and old['index']==args.index-1 and sha(old['field_path'])==old['field_sha256']
            with np.load(old['field_path'],allow_pickle=False) as data:initial=data['field'].copy()
            power=old['physical_power'];cp['previous_report_sha256']=sha(args.previous)
        else:assert args.index==1;cp['previous_report_sha256']=None
        solver=(Pade6 if case['method']=='P6' else Radau5)(mass,B,.002/case['steps'])
        field=solver.advance(initial,256);physical=float(np.vdot(field,mass@field).real)
        assert np.all(np.isfinite(field)) and 0<physical<=power+1e-9
        cp.update(status='completed',physical_power=physical,previous_power=power,steps_done=args.index*256,steps_total=case['steps'],dt_m=.002/case['steps'],resource_end=guard(args.prefix.parent))
    except Exception as error:cp.update(error=str(error),error_type=type(error).__name__,diagnostic=traceback.format_exc())
    if 'field' in locals():
        path=Path(str(args.prefix)+'.npz');np.savez(path,field=field);cp.update(field_path=str(path),field_sha256=sha(path))
    cp['elapsed_s']=time.monotonic()-start
    if cp['elapsed_s']>360:cp.update(status='failed',error='360s child budget exceeded')
    write(str(args.prefix)+'.json',cp);return 0 if cp['status']=='completed' else 1


def measure(out,e,m):
    mass,B,initial,free=matrices(m);det=Path(m['detector_folder']);C=load_npz(det/'core_q32.npz')[free,:][:,free]
    weights=np.load(det/'intensity_q32.npy',allow_pickle=False)[free]
    fields={};powers={};norms={}
    for label,solution in e['solutions'].items():
        cp=read(solution['checkpoints'][-1]['path']);assert sha(cp['field_path'])==cp['field_sha256']
        with np.load(cp['field_path'],allow_pickle=False) as data:field=data['field'].copy()
        fields[label]=field;powers[label]=dict(field=float(np.vdot(field,C@field).real),intensity=float(weights@abs(field)**2));norms[label]=math.sqrt(float(np.vdot(field,mass@field).real))
    a=fields['P6_16384'];b=fields['R5_32768'];diff=a-b
    relative=math.sqrt(float(np.vdot(diff,mass@diff).real))/norms['R5_32768']
    local={};changes={}
    for method in ('field','intensity'):
        square=float(np.vdot(diff,C@diff).real) if method=='field' else float(weights@abs(diff)**2)
        assert square>=-1e-20
        local[method]=(math.sqrt(powers['P6_16384'][method])+math.sqrt(powers['R5_32768'][method]))*math.sqrt(max(0.,square))
        changes[method]=abs(powers['P6_16384'][method]-powers['R5_32768'][method])
    passed=relative<=1e-4 and max(changes.values())<=1e-6 and max(local.values())<=1e-5
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),temporal_precision_pass=passed,point03_closed=False,requires_independent_audit=True,powers=powers,physical_norms=norms,relative_field_difference=relative,power_differences=changes,PSD_observable_bounds=local,global_mass_bound=(norms['P6_16384']+norms['R5_32768'])*relative*norms['R5_32768'],scope='Practical time-family consistency at one conforming mesh only; no spatial or exact physical validation.')


def run(out):
    start=time.monotonic();assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex');out.mkdir()
    geom=ROOT/'resultados/codex/point03_p4c_mesh_20261008';det=ROOT/'resultados/codex/point03_p4f_detector_20261008';damp=ROOT/'resultados/codex/point03_p4g_damping_20261008'
    e=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),children=[],solutions={},point03_closed=False);m={}
    try:
        guard(out)
        assert read(geom/'report_recovered.json')['integrity_pass'] and read(det/'report.json')['controls_pass'] and read(damp/'report.json')['controls_pass']
        assert read(ROOT/'resultados/codex/point03_p4d_time_20261008/report.json')['controls_pass'] and read(ROOT/'resultados/codex/point03_p4h_radau_20261008/report.json')['controls_pass']
        sources=[Path(__file__).resolve(),ROOT/'scripts/audit_point03_p4i.py',ROOT/'Docs/POINT-03-P4I-CONTRACT.md',ROOT/'scripts/point03_fem_time.py',ROOT/'scripts/point03_fem_radau.py',geom/'report_recovered.json',geom/'mass.npz',geom/'stiffness.npz',geom/'cladding_mass.npz',det/'report.json',det/'gaussian_q16.npz',det/'core_q32.npz',det/'intensity_q32.npy',damp/'report.json',damp/'damping_q12.npz',ROOT/'resultados/codex/point03_p4d_time_20261008/report.json',ROOT/'resultados/codex/point03_p4h_radau_20261008/report.json']
        m=dict(created_utc=datetime.now(timezone.utc).isoformat(),geometry_folder=str(geom),detector_folder=str(det),damping_folder=str(damp),source_sha256={str(path):sha(path) for path in sources},plan=[dict(id='P6_8192',method='P6',steps=8192),dict(id='P6_16384',method='P6',steps=16384),dict(id='R5_32768',method='R5',steps=32768)],numerical_threads=1)
        mass,B,initial,free=matrices(m);m['P_in']=float(np.vdot(initial,mass@initial).real);assert abs(m['P_in']-1)<=1e-12
        write(out/'manifest.json',m);e['manifest_sha256']=sha(out/'manifest.json')
        for case in m['plan']:
            folder=out/case['id'];folder.mkdir();previous=None;chain=[]
            for index in range(1,case['steps']//256+1):
                assert time.monotonic()-start<=18000;guard(out);prefix=folder/f'part{index:03d}'
                command=[sys.executable,str(Path(__file__).resolve()),'--worker','--manifest',str(out/'manifest.json'),'--manifest-sha',e['manifest_sha256'],'--case',case['id'],'--index',str(index),'--prefix',str(prefix)]
                if previous:command+=['--previous',str(previous)]
                before=time.monotonic()
                with Path(str(prefix)+'.log').open('xb') as log:child=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=370)
                cp=Path(str(prefix)+'.json');e['children'].append(dict(case=case['id'],index=index,returncode=child.returncode,elapsed_s=time.monotonic()-before));assert child.returncode==0 and read(cp)['status']=='completed'
                chain.append(dict(path=str(cp),sha256=sha(cp)));previous=cp
                print(json.dumps(dict(case=case['id'],index=index,total=case['steps']//256,elapsed_s=round(time.monotonic()-start,1))),flush=True)
            e['solutions'][case['id']]=dict(checkpoints=chain)
        a=measure(out,e,m);write(out/'assessment.json',a);e.update(status='completed',temporal_precision_pass=a['temporal_precision_pass'],assessment_sha256=sha(out/'assessment.json'))
    except Exception as error:e.update(status='failed',error=str(error),error_type=type(error).__name__,diagnostic=traceback.format_exc())
    e.update(finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_s=time.monotonic()-start,sources_unchanged=all(sha(path)==digest for path,digest in m.get('source_sha256',{}).items()))
    write(out/'execution.json',e);print(json.dumps({key:e.get(key) for key in ('status','temporal_precision_pass','elapsed_s','error')}),flush=True)
    return 0 if e.get('temporal_precision_pass') else 2 if e['status']=='completed' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path);parser.add_argument('--worker',action='store_true');parser.add_argument('--manifest',type=Path);parser.add_argument('--manifest-sha');parser.add_argument('--case');parser.add_argument('--index',type=int);parser.add_argument('--prefix',type=Path);parser.add_argument('--previous',type=Path);args=parser.parse_args();raise SystemExit(worker(args) if args.worker else run(args.out.resolve()))
