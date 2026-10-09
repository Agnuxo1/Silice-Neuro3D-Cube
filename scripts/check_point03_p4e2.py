"""Extend retained short-time levels; preserve prior failed comparison."""
import argparse
from datetime import datetime,timezone
import json
import math
import os
from pathlib import Path
import time
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
import psutil
from scipy.sparse import load_npz
from point03_fem_time import Pade6
from run_point03_exponential import ROOT,sha,write


def run(out):
    assert not out.exists();out.mkdir();start=time.monotonic()
    base=ROOT/'resultados/codex/point03_p4c_mesh_20261008';previous=ROOT/'resultados/codex/point03_p4e_cost_20261008'
    report=json.loads((previous/'report.json').read_text());assert not report['controls_pass']
    for name,digest in report['artifacts'].items():assert sha(previous/name)==digest
    with np.load(previous/'field_steps200.npz',allow_pickle=False) as data:
        old=data['field'].copy();initial=data['initial'].copy();free=data['free_dofs'].copy()
    M=load_npz(base/'mass.npz')[free,:][:,free].tocsc();K=load_npz(base/'stiffness.npz')[free,:][:,free];C=load_npz(base/'cladding_mass.npz')[free,:][:,free];D=load_npz(previous/'damping.npz')[free,:][:,free]
    k0=2*math.pi/1550e-9;B=-1j*K/(2*1.444*k0)-1j*k0*.003*C-D
    rows=[];differences=[]
    for steps,total in ((400,32768),(800,65536),(1600,131072)):
        assert psutil.virtual_memory().available>3*1024**3 and psutil.disk_usage(str(out)).free>2*1024**3
        before=time.monotonic();solver=Pade6(M,B,.002/total);factor=time.monotonic()-before
        before=time.monotonic();field=solver.advance(initial,steps);elapsed=time.monotonic()-before
        power=float(np.vdot(field,M@field).real);assert np.all(np.isfinite(field)) and 0<power<=1+1e-9
        error=field-old;relative=math.sqrt(float(np.vdot(error,M@error).real)/power);differences.append(relative)
        file=out/f'field_steps{steps}.npz';np.savez(file,field=field,initial=initial,free_dofs=free)
        rows.append(dict(steps=steps,equivalent_full_steps=total,dt_m=.002/total,field_relative_difference=relative,physical_power=power,factor_elapsed_s=factor,advance_elapsed_s=elapsed,forecast_full_s=elapsed/steps*total,field_path=str(file),field_sha256=sha(file)))
        old=field;assert time.monotonic()-start<=900
    passed=differences[-1]<=1e-6 and all(a>b for a,b in zip(differences,differences[1:]))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),controls_pass=passed,rows=rows,orders=[math.log2(a/b) for a,b in zip(differences,differences[1:])],elapsed_s=time.monotonic()-start,old_P4E_pass=False,Gaussian_T96_propagated=False,core_power_measured=False,point03_closed=False,source_sha256={str(path):sha(path) for path in (Path(__file__),ROOT/'Docs/POINT-03-P4E2-CONTRACT.md',previous/'report.json',ROOT/'scripts/point03_fem_time.py')})
    write(out/'report.json',result);print(json.dumps(result))


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();run(args.out.resolve())
