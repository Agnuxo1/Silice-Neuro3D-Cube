"""One-sample resource reservation; retain all 89 completed Radau chunks."""
import argparse
from datetime import datetime,timezone
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
import psutil
import run_point03_p4i as base
from run_point03_p4i3_recovery import measure
from audit_point03_p4i3_recovery2 import PREVIOUS,PRIOR,partial,prepare_source
from run_point03_exponential import ROOT,sha,write


def run(out):
    start=time.monotonic();assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex');out.mkdir()
    olde=base.read(PREVIOUS/'execution.json');oldm=base.read(PREVIOUS/'manifest.json');original=base.read(PRIOR/'execution.json')
    elapsed_before=(datetime.now(timezone.utc)-datetime.fromisoformat(original['started_utc'])).total_seconds()
    e=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),original_started_utc=original['started_utc'],
           elapsed_before_recovery_s=elapsed_before,children=olde['children'].copy(),checkpoints=olde['checkpoints'].copy(),
           resource_wait_s=olde['resource_wait_s'],point03_closed=False);m={}
    try:
        proof=partial();write(out/'partial_integrity_audit.json',proof);source=prepare_source(out)
        files=[Path(__file__).resolve(),ROOT/'scripts/audit_point03_p4i3_recovery2.py',ROOT/'scripts/run_point03_p4i3_recovery.py',
               ROOT/'Docs/POINT-03-P4I3-RECOVERY2-CONTRACT.md',PREVIOUS/'execution.json',PREVIOUS/'manifest.json',out/'partial_integrity_audit.json',source]
        m={**oldm,'created_utc':datetime.now(timezone.utc).isoformat(),'retained_checkpoint_count':89,
           'original_manifest_created_utc':base.read(PRIOR/'manifest.json')['created_utc'],
           'first_recovery_manifest_created_utc':oldm['created_utc'],'independent_auditor_source_path':str(source),
           'source_sha256':{**oldm['source_sha256'],**{str(p):sha(p) for p in files}}}
        write(out/'manifest.json',m);e['manifest_sha256']=sha(out/'manifest.json');folder=out/'R5_65536';folder.mkdir()
        previous=Path(e['checkpoints'][-1]['path'])
        for index in range(90,257):
            while True:
                assert elapsed_before+time.monotonic()-start<=22000 and e['resource_wait_s']<=1800
                resource=dict(utc=datetime.now(timezone.utc).isoformat(),available_ram_bytes=psutil.virtual_memory().available,
                              free_disk_bytes=psutil.disk_usage(str(out)).free)
                assert resource['free_disk_bytes']>2*1024**3
                if resource['available_ram_bytes']>=6*1024**3:break
                assert e['resource_wait_s']<1800
                before=time.monotonic();time.sleep(min(10,1800-e['resource_wait_s']));e['resource_wait_s']+=time.monotonic()-before
                print(f'P4I3 recovery2 memory wait {e["resource_wait_s"]:.1f}s',flush=True)
            prefix=folder/f'part{index:03d}'
            cmd=[sys.executable,str(ROOT/'scripts/run_point03_p4i.py'),'--worker','--manifest',str(out/'manifest.json'),'--manifest-sha',
                 e['manifest_sha256'],'--case','R5_65536','--index',str(index),'--prefix',str(prefix),'--previous',str(previous)]
            before=time.monotonic()
            with Path(str(prefix)+'.log').open('xb') as log:child=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=370)
            cp=Path(str(prefix)+'.json');e['children'].append(dict(index=index,returncode=child.returncode,elapsed_s=time.monotonic()-before,parent_resource_start=resource))
            assert child.returncode==0 and base.read(cp)['status']=='completed'
            e['checkpoints'].append(dict(path=str(cp),sha256=sha(cp)));previous=cp
            print(f'P4I3 recovery2 checkpoint {index}/256, 89 retained',flush=True)
        a=measure(m,e);write(out/'assessment.json',a)
        assert elapsed_before+time.monotonic()-start<=22000
        e.update(status='completed',temporal_precision_pass=a['temporal_precision_pass'],assessment_sha256=sha(out/'assessment.json'))
    except Exception as error:e.update(status='failed',error=str(error),error_type=type(error).__name__,diagnostic=traceback.format_exc())
    e.update(finished_utc=datetime.now(timezone.utc).isoformat(),recovery_elapsed_s=time.monotonic()-start,
             elapsed_s=elapsed_before+time.monotonic()-start,sources_unchanged=all(sha(p)==v for p,v in m.get('source_sha256',{}).items()))
    write(out/'execution.json',e);print({k:e.get(k) for k in ('status','temporal_precision_pass','elapsed_s','resource_wait_s','error')},flush=True)
    return 0 if e['status']=='completed' and e.get('temporal_precision_pass') else 2 if e['status']=='completed' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();raise SystemExit(run(a.out.resolve()))
