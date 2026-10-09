import os,json,psutil,time
from pathlib import Path
time.sleep(.1)
h=json.loads(Path(r"D:/PROJECTS/.cognition/gpu_queue/holder.json").read_text(encoding="utf-8"))
chain=[]
for p in [psutil.Process()]+psutil.Process().parents()[:4]:
    chain.append(dict(pid=p.pid,ppid=p.ppid(),ctime=p.create_time(),exe=p.exe()))
print(json.dumps(dict(queue_holder={k:h.get(k) for k in ["name","pid","ctime","child_pid","child_ctime"]},self_pid=os.getpid(),parent_pid=os.getppid(),chain=chain,gpuq_env=os.environ.get("GPUQ_HOLDER"),new_gpu_execution=False)))
