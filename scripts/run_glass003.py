"""Frozen bounded experiment; persist results even if convergence gates fail."""
import os
for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ[name]="1"
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import numpy as np
from silice.bpm import Grid,gaussian,index_profile,metrics,propagate


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    target=args.out.resolve()
    if not target.is_relative_to(ROOT/"resultados"/"codex") or target.exists():
        parser.error("new output must be under resultados/codex; no overwrite")
    started=time.monotonic(); deadline=started+40
    cases=[]
    for kind,thickness,contrast in [("free",6e-6,0),
                ("ring",3e-6,-0.001),("ring",6e-6,-0.001),
                ("ring",9e-6,-0.001),("core",6e-6,0.001)]:
        for length in (0.5e-3,2e-3):
            g=Grid(128,96e-6)
            dn=np.zeros((128,128)) if kind=="free" else index_profile(g,6e-6,thickness,contrast,kind)
            field,budget=propagate(gaussian(g,6e-6),dn,g,
                                  length_m=length,steps=round(length/10e-6),deadline=deadline)
            m=metrics(field,g,6e-6)
            cases.append(dict(kind=kind,thickness_m=thickness,delta_n=contrast,
                length_m=length,**m,**budget,
                core_power_fraction_input=m["core_fraction_remaining"]*budget["output_power"]))
    nominal=next(c for c in cases if c["kind"]=="ring" and c["thickness_m"]==6e-6 and c["length_m"]==2e-3)
    refinements=[]
    for name,g,steps in [("dz",Grid(128,96e-6),400),
                         ("domain",Grid(192,144e-6),200),
                         ("dx",Grid(192,96e-6),200)]:
        dn=index_profile(g,6e-6,6e-6,-0.001)
        field,budget=propagate(gaussian(g,6e-6),dn,g,length_m=2e-3,steps=steps,deadline=deadline)
        m=metrics(field,g,6e-6)
        delta=abs(m["core_fraction_remaining"]-nominal["core_fraction_remaining"])
        refinements.append(dict(name=name,points=g.points,width_m=g.width_m,
            change_core_fraction=delta,gate=delta<0.02,**m,**budget))
    files=[ROOT/"src/silice/bpm.py",Path(__file__).resolve(),ROOT/"Docs/RESEARCH-CONTRACT.md"]
    report=dict(experiment="GLASS-003-v1",time_utc=datetime.now(timezone.utc).isoformat(),
        backend="scalar_paraxial_cpu_ssfm",gpu_used=False,
        parameters_status="assumed_not_measured",elapsed_s=time.monotonic()-started,
        python=sys.version,numpy=np.__version__,cases=cases,refinements=refinements,
        gate_balance=all(c["balance_relative"]<1e-10 for c in cases+refinements),
        gate_convergence=all(c["gate"] for c in refinements),
        sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    target.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(dict(report=str(target),elapsed_s=report["elapsed_s"],
        gate_balance=report["gate_balance"],gate_convergence=report["gate_convergence"],
        cases=[{k:c[k] for k in ("kind","thickness_m","length_m","core_power_fraction_input")} for c in cases],
        refinements=[dict(name=c["name"],delta=c["change_core_fraction"],gate=c["gate"]) for c in refinements])))
    return 0 if report["gate_balance"] and report["gate_convergence"] else 2


if __name__=="__main__":sys.exit(main())
