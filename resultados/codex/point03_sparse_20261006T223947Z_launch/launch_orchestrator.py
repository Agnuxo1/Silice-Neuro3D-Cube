from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,time
ROOT=Path(r'D:\PROJECTS\Silice-Neuro3D-Cube-work-20261006')
OUT=Path("D:\\PROJECTS\\Silice-Neuro3D-Cube-work-20261006\\resultados\\codex\\point03_sparse_20261006T223947Z")
LAUNCH=Path(str(OUT)+'_launch')
LAUNCH.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):
    with (LAUNCH/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,indent=2);f.write('\n')
env=dict(os.environ)
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):env[key]='1'
command=[str(ROOT/'.venv/Scripts/python.exe'),'-B','-u',str(ROOT/'scripts/audit_point03_sparse_adi.py'),'--study',str(ROOT/'resultados/codex/point03_refinement_20261006T220909702270Z/manifest.json'),'--out-dir',str(OUT)]
commit=subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],capture_output=True,check=True,text=True).stdout.strip()
assert commit=='005dae057df0a264ad8372be905d24644715373a'
source=Path(__file__).read_bytes();(LAUNCH/'launch_orchestrator.py').write_bytes(source)
write('launch.json',{'utc':datetime.now(timezone.utc).isoformat(),'command':command,'source_commit':commit,'driver_sha256':sha(ROOT/'scripts/audit_point03_sparse_adi.py'),'out_dir':str(OUT),'outer_safeguard_s':640,'scope':'Driver enforces its own 600 s study limit and 40 s numerical children.'})
started=time.monotonic()
with (LAUNCH/'stdout.log').open('x',encoding='utf-8',newline='\n') as stdout,(LAUNCH/'stderr.log').open('x',encoding='utf-8',newline='\n') as stderr:
    try:
        p=subprocess.run(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,timeout=640)
        result={'returncode':p.returncode}
    except subprocess.TimeoutExpired:
        result={'returncode':None,'outer_timeout':True}
result.update(elapsed_s=time.monotonic()-started,out_dir=str(OUT))
write('completion.json',result)
print(json.dumps(result))
