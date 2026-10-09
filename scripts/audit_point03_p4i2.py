"""Re-audit retained cases plus all new refinement fields, without its evaluator."""
import argparse
from datetime import datetime,timezone
import math
import os
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from scipy.sparse import load_npz
from audit_point03_p4i import audit as old_audit,read
from run_point03_exponential import ROOT,sha,write


def audit(out):
    old=old_audit(ROOT/'resultados/codex/point03_p4i_gaussian_time_20261008');assert old['integrity_pass'] and not old['temporal_precision_pass']
    e=read(out/'execution.json');m=read(out/'manifest.json');a=read(out/'assessment.json')
    assert e['status']=='completed' and e['sources_unchanged'] and e['elapsed_s']<=11000 and len(e['children'])==len(e['checkpoints'])==128
    assert sha(out/'manifest.json')==e['manifest_sha256'] and sha(out/'assessment.json')==e['assessment_sha256']
    for path,digest in m['source_sha256'].items():assert sha(path)==digest
    geom=Path(m['geometry_folder']);det=Path(m['detector_folder'])
    with np.load(det/'gaussian_q16.npz',allow_pickle=False) as data:free=data['free_dofs'].copy()
    M=load_npz(geom/'mass.npz')[free,:][:,free];C=load_npz(det/'core_q32.npz')[free,:][:,free];w=np.load(det/'intensity_q32.npy',allow_pickle=False)[free]
    previous=digest=None;power=m['P_in'];residual=0.
    for index,link in enumerate(e['checkpoints'],1):
        cp=read(link['path']);assert sha(link['path'])==link['sha256'] and cp['status']=='completed' and cp['case']=='P6_32768' and cp['index']==index
        event=e['children'][index-1];assert event['index']==index and event['returncode']==0 and event['elapsed_s']<=370
        assert cp['previous_report_path']==previous and cp['previous_report_sha256']==digest and cp['elapsed_s']<=360 and cp['steps_total']==32768 and cp['steps_done']==256*index and cp['dt_m']==.002/32768
        for sample in ('resource_start','resource_end'):assert cp[sample]['available_ram_bytes']>3*1024**3 and cp[sample]['free_disk_bytes']>2*1024**3
        assert sha(cp['field_path'])==cp['field_sha256']
        with np.load(cp['field_path'],allow_pickle=False) as data:field=data['field'].copy()
        assert field.shape==(len(free),) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
        physical=float(np.vdot(field,M@field).real);residual=max(residual,abs(physical-cp['physical_power']))
        assert abs(physical-cp['physical_power'])<=1e-12 and 0<physical<=power+1e-9 and abs(cp['previous_power']-power)<=1e-12
        previous,digest,power=link['path'],link['sha256'],physical
    refcp=read(m['reference']['checkpoints'][-1]['path']);assert sha(refcp['field_path'])==refcp['field_sha256']
    with np.load(refcp['field_path'],allow_pickle=False) as data:reference=data['field'].copy()
    fields={'P6':field,'R5':reference};norms={label:math.sqrt(float(np.vdot(f,M@f).real)) for label,f in fields.items()}
    powers={label:dict(field=float(np.vdot(f,C@f).real),intensity=float(w@abs(f)**2)) for label,f in fields.items()}
    diff=field-reference;relative=math.sqrt(float(np.vdot(diff,M@diff).real))/norms['R5'];bounds={};errors={}
    for method in ('field','intensity'):
        squared=float(np.vdot(diff,C@diff).real) if method=='field' else float(w@abs(diff)**2);assert squared>=-1e-20
        bounds[method]=(math.sqrt(powers['P6'][method])+math.sqrt(powers['R5'][method]))*math.sqrt(max(0,squared));errors[method]=abs(powers['P6'][method]-powers['R5'][method])
        assert abs(bounds[method]-a['PSD_observable_bounds'][method])<=1e-12 and abs(errors[method]-a['power_differences'][method])<=1e-12
    passed=relative<=1e-4 and max(bounds.values())<=1e-5 and max(errors.values())<=1e-6
    assert passed==a['temporal_precision_pass']==e['temporal_precision_pass']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,temporal_precision_pass=passed,point03_closed=False,new_checkpoints_checked=128,retained_checkpoints_rechecked=224,PSD_observable_bounds=bounds,power_differences=errors,powers=powers,relative_field_difference=relative,max_power_residual=residual,previous_P4I_pass=False,scope='Refined one-mesh practical time check only; no spatial closure.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args();result=audit(args.out.resolve());write(args.out/'integrity_audit.json',result);print(result)
