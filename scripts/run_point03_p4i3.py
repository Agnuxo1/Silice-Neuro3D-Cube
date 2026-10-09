"""One new Radau reference against retained Padé; prior rejections remain."""
import argparse
from datetime import datetime,timezone
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
from scipy.sparse import load_npz
import run_point03_p4i as base
from run_point03_exponential import ROOT,sha,write


def run(out):
    start=time.monotonic()
    assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    prior=ROOT/'resultados/codex/point03_p4i2_gaussian_time_20261008'
    pe=base.read(prior/'execution.json');pm=base.read(prior/'manifest.json');pa=base.read(prior/'integrity_audit.json')
    assert pe['status']=='completed' and pa['integrity_pass'] and not pa['temporal_precision_pass']
    out.mkdir()
    e=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),children=[],checkpoints=[],point03_closed=False)
    m={}
    try:
        sources=[Path(__file__).resolve(),ROOT/'scripts/audit_point03_p4i3.py',ROOT/'Docs/POINT-03-P4I3-CONTRACT.md',
                 prior/'execution.json',prior/'manifest.json',prior/'assessment.json',prior/'integrity_audit.json']
        m={**pm,'created_utc':datetime.now(timezone.utc).isoformat(),
           'plan':[dict(id='R5_65536',method='R5',steps=65536)],
           'reference':dict(checkpoints=pe['checkpoints']),'reference_label':'P6_32768',
           'previous_Radau_reference':pm['reference'],
           'source_sha256':{**pm['source_sha256'],**{str(p):sha(p) for p in sources}}}
        write(out/'manifest.json',m);e['manifest_sha256']=sha(out/'manifest.json')
        folder=out/'R5_65536';folder.mkdir();previous=None
        for index in range(1,257):
            assert time.monotonic()-start<=22000;base.guard(out);prefix=folder/f'part{index:03d}'
            command=[sys.executable,str(ROOT/'scripts/run_point03_p4i.py'),'--worker','--manifest',str(out/'manifest.json'),
                     '--manifest-sha',e['manifest_sha256'],'--case','R5_65536','--index',str(index),'--prefix',str(prefix)]
            if previous:command+=['--previous',str(previous)]
            before=time.monotonic()
            with Path(str(prefix)+'.log').open('xb') as log:
                child=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=370)
            cp=Path(str(prefix)+'.json')
            e['children'].append(dict(index=index,returncode=child.returncode,elapsed_s=time.monotonic()-before))
            assert child.returncode==0 and base.read(cp)['status']=='completed'
            e['checkpoints'].append(dict(path=str(cp),sha256=sha(cp)));previous=cp
            print(f'P4I3 checkpoint {index}/256 elapsed {time.monotonic()-start:.1f}s',flush=True)
        M,B,initial,free=base.matrices(m);det=Path(m['detector_folder'])
        C=load_npz(det/'core_q32.npz')[free,:][:,free];w=np.load(det/'intensity_q32.npy',allow_pickle=False)[free]
        fields={}
        for label,links in (('P6',m['reference']['checkpoints']),('R5',e['checkpoints']),('R5_old',m['previous_Radau_reference']['checkpoints'])):
            cp=base.read(links[-1]['path']);assert sha(cp['field_path'])==cp['field_sha256']
            with np.load(cp['field_path'],allow_pickle=False) as data:fields[label]=data['field'].copy()
        powers={label:dict(field=float(np.vdot(f,C@f).real),intensity=float(w@abs(f)**2)) for label,f in fields.items()}
        d=fields['P6']-fields['R5'];relative=math.sqrt(float(np.vdot(d,M@d).real)/float(np.vdot(fields['R5'],M@fields['R5']).real))
        bounds={};changes={}
        for method in ('field','intensity'):
            squared=float(np.vdot(d,C@d).real) if method=='field' else float(w@abs(d)**2)
            assert squared>=-1e-20
            bounds[method]=(math.sqrt(powers['P6'][method])+math.sqrt(powers['R5'][method]))*math.sqrt(max(0.,squared))
            changes[method]=abs(powers['P6'][method]-powers['R5'][method])
        diagnostic=fields['R5_old']-fields['R5']
        rd=math.sqrt(float(np.vdot(diagnostic,M@diagnostic).real)/float(np.vdot(fields['R5'],M@fields['R5']).real))
        passed=relative<=1e-4 and max(bounds.values())<=1e-5 and max(changes.values())<=1e-6
        a=dict(created_utc=datetime.now(timezone.utc).isoformat(),temporal_precision_pass=passed,point03_closed=False,
               powers=powers,relative_field_difference=relative,PSD_observable_bounds=bounds,power_differences=changes,
               diagnostic_Radau_refinement_relative_field=rd,previous_P4I_pass=False,previous_P4I2_pass=False)
        write(out/'assessment.json',a)
        e.update(status='completed',temporal_precision_pass=passed,assessment_sha256=sha(out/'assessment.json'))
        assert time.monotonic()-start<=22000
    except Exception as error:
        e.update(status='failed',error=str(error),error_type=type(error).__name__,diagnostic=traceback.format_exc())
    e.update(finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_s=time.monotonic()-start,
             sources_unchanged=all(sha(p)==v for p,v in m.get('source_sha256',{}).items()))
    write(out/'execution.json',e)
    print({k:e.get(k) for k in ('status','temporal_precision_pass','elapsed_s','error')},flush=True)
    return 0 if e.get('temporal_precision_pass') else 2 if e['status']=='completed' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    raise SystemExit(run(args.out.resolve()))
