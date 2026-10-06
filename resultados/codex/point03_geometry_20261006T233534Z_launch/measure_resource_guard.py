"""Bounded resource-query timing diagnostic; no geometry or quadrature."""
from pathlib import Path
import argparse,hashlib,json,os,platform,shutil,statistics,subprocess,sys,time
THREADS=("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS","BLIS_NUM_THREADS")
for name in THREADS:os.environ[name]="1"
parser=argparse.ArgumentParser();parser.add_argument("--out",type=Path,required=True);parser.add_argument("--child",action="store_true")
args=parser.parse_args();out=args.out.resolve();launch=Path(str(out)+"_launch")
if not args.child:
 source=launch/"measure_resource_guard.py"
 with source.open("xb") as handle:handle.write(Path(__file__).read_bytes())
 command=[sys.executable,"-B","-u",str(source),"--out",str(out),"--child"]
 start=time.monotonic();record={"command":command,"timeout_s":40,"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest()}
 try:
  with (launch/"guard_cost.stdout.log").open("xb") as stdout,(launch/"guard_cost.stderr.log").open("xb") as stderr:
   result=subprocess.run(command,stdout=stdout,stderr=stderr,timeout=40,env=dict(os.environ))
  record["returncode"]=result.returncode
 except subprocess.TimeoutExpired:
  record["timed_out"]=True
 record["elapsed_s"]=time.monotonic()-start
 with (launch/"guard_cost_execution.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(record,f,indent=2);f.write("\n")
 print(json.dumps(record),flush=True)
 print((launch/"guard_cost.stdout.log").read_text(),flush=True)
 print((launch/"guard_cost.stderr.log").read_text(),flush=True)
 raise SystemExit(0)
import psutil
start=time.monotonic();deadline=start+25
report={"schema":"silice.point03-geometry.resource-query-cost.v1","status":"failed","measurements":{},"python":platform.python_version(),"psutil":psutil.__version__,"threads":{k:os.environ[k] for k in THREADS},"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"scope":"Resource query timing only. No geometry, field propagation, quadrature, criterion relaxation, or scientific validation."}
try:
 assert platform.python_version()=="3.13.7" and psutil.__version__=="6.1.1"
 for label,count in (("clock_only",1000),("available_memory",100),("free_disk",100),("memory_and_disk",100)):
  times=[];report["measurements"][label]={"requested_calls":count,"seconds":times}
  for i in range(count):
   assert time.monotonic()<deadline,"Diagnostic deadline"
   t=time.monotonic()
   if label in ("available_memory","memory_and_disk"):assert psutil.virtual_memory().available>1.5*1024**3
   if label in ("free_disk","memory_and_disk"):assert shutil.disk_usage(out).free>2*1024**3
   if label=="clock_only":assert time.monotonic()<deadline
   times.append(time.monotonic()-t)
  report["measurements"][label].update(completed_calls=len(times),total_s=sum(times),mean_s=statistics.mean(times),median_s=statistics.median(times),min_s=min(times),max_s=max(times))
 report["status"]="completed"
except BaseException as error:
 report.update(error_type=type(error).__name__,error=str(error))
report["elapsed_s"]=time.monotonic()-start
with (launch/"guard_cost.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(report,f,indent=2);f.write("\n")
print(json.dumps({k:v for k,v in report.items() if k!="measurements"}|{"measurements":{k:{a:b for a,b in v.items() if a!="seconds"} for k,v in report["measurements"].items()}}),flush=True)
raise SystemExit(0 if report["status"]=="completed" else 1)
