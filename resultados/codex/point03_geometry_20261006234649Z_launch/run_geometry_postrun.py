from pathlib import Path
import hashlib,os,subprocess,time,json,sys
root=Path(r"D:\PROJECTS\Silice-Neuro3D-Cube-work-20261006")
out=Path(sys.argv[1])
launch=Path(str(out)+"_launch")
source=root/".audit_tmp/summarize_point03_geometry.py"
assert hashlib.sha256(source.read_bytes()).hexdigest()=="8bb430322e46c5617de991caa2b1ccd232786f682bc82cccb09de7f6f16db46f"
target=launch/"summarize_point03_geometry.py"
with target.open("xb") as f:f.write(source.read_bytes())
env=dict(os.environ)
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS","BLIS_NUM_THREADS"):env[key]="1"
command=[str(root/".venv/Scripts/python.exe"),"-B","-u",str(source),"--out",str(out),"--output",str(launch/"independent_audit.json")]
started=time.monotonic()
record={"command":command,"status":"failed","timeout_s":40}
try:
 with (launch/"audit.stdout.log").open("xb") as stdout,(launch/"audit.stderr.log").open("xb") as stderr:
  p=subprocess.run(command,env=env,cwd=root,stdout=stdout,stderr=stderr,timeout=40)
 record.update(returncode=p.returncode,status="completed")
except subprocess.TimeoutExpired:
 record["timed_out"]=True
record["elapsed_s"]=time.monotonic()-started
with (launch/"audit_execution.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(record,f,indent=2);f.write("\n")
print(json.dumps(record),flush=True)
print((launch/"audit.stdout.log").read_text(),flush=True)
print((launch/"audit.stderr.log").read_text(),flush=True)
