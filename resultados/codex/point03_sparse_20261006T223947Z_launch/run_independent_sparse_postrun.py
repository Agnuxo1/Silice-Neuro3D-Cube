from pathlib import Path
import json,subprocess,time,hashlib
ROOT=Path(r'D:\PROJECTS\Silice-Neuro3D-Cube-work-20261006')
OUT=Path("D:\\PROJECTS\\Silice-Neuro3D-Cube-work-20261006\\resultados\\codex\\point03_sparse_20261006T223947Z")
LAUNCH=Path(str(OUT)+'_launch')
command=[str(ROOT/'.venv/Scripts/python.exe'),'-B',str(ROOT/'.audit_tmp/independent_sparse_postrun.py'),'--out-dir',str(OUT),'--output',str(OUT/'independent_audit.json')]
started=time.monotonic()
run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=40)
for label,text in (('stdout',run.stdout),('stderr',run.stderr)):
    with (LAUNCH/('independent.'+label+'.log')).open('x',encoding='utf-8',newline='\n') as f:f.write(text)
report={'command':command,'returncode':run.returncode,'elapsed_s':time.monotonic()-started,'stdout':run.stdout,'stderr':run.stderr}
with (LAUNCH/'independent_execution.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report))
if run.returncode==0:
    result=json.loads((OUT/'independent_audit.json').read_text(encoding='utf-8'))
    print(json.dumps({k:result[k] for k in ('status','independent_equivalence_pass','max_recorded_metric_recalculation_error','operations','memory','permutations')}))
