"""New V2 contract; leave V1 failed report and solver intact."""
import os
for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ[name]="1"
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import numpy as np
from silice.bpm import Grid,gaussian,index_profile,metrics,propagate


def convergence_gate(reference,candidate):
    absolute=abs(candidate-reference)
    relative=absolute/abs(reference) if reference else None
    return dict(absolute=absolute,relative=relative,
                gate=reference>=1e-6 and absolute<0.005 and relative<0.1)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args();target=args.out.resolve()
    if not target.is_relative_to(ROOT/"resultados/codex") or target.exists():
        parser.error("new output under resultados/codex only, no overwrite")
    started=time.monotonic();deadline=started+40
    report=dict(experiment="GLASS-003-v2",backend="scalar_paraxial_cpu_ssfm",
        gpu_used=False,time_utc=datetime.now(timezone.utc).isoformat(),
        parameters_status="assumed_not_measured",cases=[],gates=[],
        combined_convergence_certified=False)
    for contrast in (-0.001,-0.003,-0.005):
        values={}
        for name,grid,steps in [("nominal",Grid(128,96e-6),200),
                  ("domain144",Grid(192,144e-6),200),
                  ("domain192",Grid(256,192e-6),200),
                  ("dz",Grid(128,96e-6),400),
                  ("dx",Grid(192,96e-6),200)]:
            field,budget=propagate(gaussian(grid,6e-6),index_profile(grid,6e-6,6e-6,contrast),
                grid,length_m=2e-3,steps=steps,deadline=deadline)
            m=metrics(field,grid,6e-6)
            value=m["core_fraction_remaining"]*budget["output_power"]/budget["input_power"]
            values[name]=value
            report["cases"].append(dict(name=name,delta_n=contrast,width_m=grid.width_m,
                points=grid.points,core_power_fraction_input=value,**m,**budget))
        for name,ref,candidate in [("domain144to192",values["domain144"],values["domain192"]),
                                   ("dz",values["nominal"],values["dz"]),
                                   ("dx",values["nominal"],values["dx"])]:
            report["gates"].append(dict(name=name,delta_n=contrast,**convergence_gate(ref,candidate)))
    report["elapsed_s"]=time.monotonic()-started
    report["gate_balance"]=all(c["balance_relative"]<1e-10 for c in report["cases"])
    report["gate_partial_refinements"]=all(c["gate"] for c in report["gates"])
    report["sha256"]={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [Path(__file__).resolve(),ROOT/"src/silice/bpm.py",ROOT/"Docs/GLASS-003-V2-CONTRACT.md"]}
    target.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(dict(elapsed_s=report["elapsed_s"],gate_balance=report["gate_balance"],
        gate_partial_refinements=report["gate_partial_refinements"],gates=report["gates"],
        domain192=[dict(delta_n=c["delta_n"],core_power=c["core_power_fraction_input"]) for c in report["cases"] if c["name"]=="domain192"])))
    return 0 if report["gate_balance"] and report["gate_partial_refinements"] else 2


if __name__=="__main__":sys.exit(main())
