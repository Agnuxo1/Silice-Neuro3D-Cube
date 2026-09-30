import os,sys,time,json; os.environ["OMP_NUM_THREADS"]="1"
sys.dont_write_bytecode=True
sys.path.insert(0,"../../src")
import numpy as np
from silice import bpm
from radial_ecs import core_fraction
out={}
print("== convergencia del solver radial (core/entrada %, z=2mm)")
for dn in [-0.001,-0.003,-0.005]:
    row=[]
    for kw in [dict(N=700),dict(N=1200),dict(N=700,theta=0.9),dict(N=700,R0=80e-6,Rmax=180e-6)]:
        row.append(round(core_fraction(dn,**kw)[0]*100,3))
    print(dn,row); out[f"radial_{dn}"]=row
print("== BPM de Codex (importado sin modificar), dominio 192um, 256 pts, dz 10um")
g=bpm.Grid(256,192e-6)
for dn in [-0.001,-0.003,-0.005]:
    for steps in [200,400]:
        f=bpm.gaussian(g,6e-6); prof=bpm.index_profile(g,6e-6,6e-6,dn)
        a,rep=bpm.propagate(f,prof,g,steps=steps)
        m=np.abs(a)**2; x,y=g.coordinates(); c=m[(x*x+y*y)<36e-12].sum()*g.dx_m**2/1.0
        print(dn,steps,"core/entrada %",round(100*c,3)); out[f"bpm_{dn}_{steps}"]=100*c
json.dump(out,open("compare.json","w"),indent=1)
