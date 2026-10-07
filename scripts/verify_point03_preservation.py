"""Verify the main checkout and frozen E outputs without changing either."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
    base=ROOT/'resultados/codex/point03_recovery_20261007_run2/main_preservation_baseline.json'
    baseline=json.loads(base.read_text(encoding='utf-8'));main=Path('D:/PROJECTS/Silice-Neuro3D-Cube')
    changed=[p for p,d in baseline['tracked_sha256'].items() if sha(main/p)!=d]
    status=subprocess.check_output(['git','-c','safe.directory='+str(main),'-C',str(main),'status','--porcelain=v1','-z'])
    status_equal=hashlib.sha256(status).hexdigest()==baseline['status_sha256']
    epath=ROOT/'resultados/codex/point03_analytic_20261007T004526617696Z/execution.json'
    e=json.loads(epath.read_text(encoding='utf-8'));e_changed=[p for p,d in e['produced_sha256'].items() if sha(p)!=d]
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),pass_=not changed and status_equal and not e_changed,main_tracked_files_checked=len(baseline['tracked_sha256']),main_changed_tracked=changed,main_porcelain_status_equal=status_equal,E_produced_files_checked=len(e['produced_sha256']),E_changed_produced=e_changed,baseline_sha256=sha(base),scope='Tracked main bytes and original Git porcelain status; E603 produced bytes. Does not certify every untracked main file content.')

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=run()
    with a.output.open('x',encoding='utf-8') as f:json.dump(r,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(r));return 0 if r['pass_'] else 1
if __name__=='__main__':raise SystemExit(main())
