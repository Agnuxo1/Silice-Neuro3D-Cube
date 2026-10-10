import os, sys, json
os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True
sys.path.insert(0,"D:/PROJECTS/.cognition/audit/silice-origin-main/experimentos/bpm_claude")
import numpy as np, bpm, verificar_bpm as v
ref=json.load(open("D:/PROJECTS/.cognition/audit/silice-origin-main/experimentos/bpm_claude/resultados_bpm.json"))
u,w,neff_an=v.lp01_solve()
x=bpm.axis_coords(v.N_BASE,v.H_BASE); E0=v.lp01_field(x,0.0,u,w); n=v.n_xy_cell(x,v.H_BASE,[0.0])
rec=v.Recorder(E0,v.H_BASE)
bpm.propagate(n,E0,v.LAM,v.H_BASE,1.0,[1000.0],v.NREF,cap=True,observe=rec)
ne,_=rec.n_impl_at(1000.0); ov,_=rec.overlap2_at(1000.0); lo,_=rec.loss_at(1000.0)
b=ref["bloques"]["B1"]
out=dict(neff=ne,dif_json=ne-b["neff_impl_1mm"],ov2=ov,dov=ov-b["overlap2_1mm"],loss=lo,dloss=lo-b["perdida_1mm"])
print(json.dumps(out))
json.dump(out,open("v1_b_theirs.json","w"))
