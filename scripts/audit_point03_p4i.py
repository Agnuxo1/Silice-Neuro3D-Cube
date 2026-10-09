"""Independent generalized-mass temporal audit from all saved fields."""
import argparse
from datetime import datetime,timezone
import json
import math
import os
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from scipy.sparse import load_npz
from run_point03_exponential import sha,write


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def audit(out):
    e=read(out/'execution.json');m=read(out/'manifest.json');a=read(out/'assessment.json')
    assert e['status']=='completed' and e['sources_unchanged'] and e['elapsed_s']<=18000 and not e['point03_closed']
    assert sha(out/'manifest.json')==e['manifest_sha256'] and sha(out/'assessment.json')==e['assessment_sha256']
    for path,digest in m['source_sha256'].items():assert sha(path)==digest
    assert m['numerical_threads']==1 and len(e['children'])==224
    geom=Path(m['geometry_folder']);det=Path(m['detector_folder'])
    with np.load(det/'gaussian_q16.npz',allow_pickle=False) as data:initial=data['field'].copy();free=data['free_dofs'].copy()
    M=load_npz(geom/'mass.npz')[free,:][:,free];C=load_npz(det/'core_q32.npz')[free,:][:,free];w=np.load(det/'intensity_q32.npy',allow_pickle=False)[free]
    pin=float(np.vdot(initial[free],M@initial[free]).real);assert abs(pin-m['P_in'])<=1e-12 and abs(pin-1)<=1e-12
    fields={};measure={};norms={};count=child_index=0;max_residual=0.
    for case,steps in (('P6_8192',8192),('P6_16384',16384),('R5_32768',32768)):
        links=e['solutions'][case]['checkpoints'];assert len(links)==steps//256
        previous=digest=None;power=pin
        for index,link in enumerate(links,1):
            event=e['children'][child_index];child_index+=1
            assert event['case']==case and event['index']==index and event['returncode']==0 and event['elapsed_s']<=370
            cp=read(link['path']);assert sha(link['path'])==link['sha256'] and cp['status']=='completed' and cp['case']==case and cp['index']==index
            assert cp['previous_report_path']==previous and cp['previous_report_sha256']==digest and cp['elapsed_s']<=360
            assert cp['steps_done']==index*256 and cp['steps_total']==steps and cp['dt_m']==.002/steps and cp['started_utc']>m['created_utc']
            for sample in ('resource_start','resource_end'):assert cp[sample]['available_ram_bytes']>3*1024**3 and cp[sample]['free_disk_bytes']>2*1024**3
            assert sha(cp['field_path'])==cp['field_sha256']
            with np.load(cp['field_path'],allow_pickle=False) as data:field=data['field'].copy()
            assert field.shape==(len(free),) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
            actual=float(np.vdot(field,M@field).real);max_residual=max(max_residual,abs(actual-cp['physical_power']))
            assert abs(actual-cp['physical_power'])<=1e-12 and 0<actual<=power+1e-9 and abs(cp['previous_power']-power)<=1e-12
            previous,digest,power=link['path'],link['sha256'],actual;count+=1
        fields[case]=field;norms[case]=math.sqrt(power)
        measure[case]=dict(field=float(np.vdot(field,C@field).real),intensity=float(w@abs(field)**2))
        for method in ('field','intensity'):assert abs(measure[case][method]-a['powers'][case][method])<=1e-12
    diff=fields['P6_16384']-fields['R5_32768'];difference=math.sqrt(float(np.vdot(diff,M@diff).real));relative=difference/norms['R5_32768']
    bounds={};errors={}
    for method in ('field','intensity'):
        sq=float(np.vdot(diff,C@diff).real) if method=='field' else float(w@abs(diff)**2)
        assert sq>=-1e-20
        bounds[method]=(math.sqrt(measure['P6_16384'][method])+math.sqrt(measure['R5_32768'][method]))*math.sqrt(max(0.,sq))
        errors[method]=abs(measure['P6_16384'][method]-measure['R5_32768'][method])
        assert abs(bounds[method]-a['PSD_observable_bounds'][method])<=1e-12 and abs(errors[method]-a['power_differences'][method])<=1e-12
    passed=relative<=1e-4 and max(errors.values())<=1e-6 and max(bounds.values())<=1e-5
    assert passed==a['temporal_precision_pass']==e['temporal_precision_pass']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,temporal_precision_pass=passed,point03_closed=False,checkpoints_checked=count,max_power_residual=max_residual,powers=measure,relative_field_difference=relative,PSD_observable_bounds=bounds,power_differences=errors,scope='One-mesh practical temporal consistency only; no spatial or physical-device closure.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();result=audit(args.out.resolve());write(args.out/'integrity_audit.json',result);print(json.dumps(result))
