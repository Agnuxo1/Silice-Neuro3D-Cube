"""Complete only the three pending cases after the retained 40 s timeout.

Same scientific contract, per-child time bound unchanged; previous cases
are reused only after validating original source hashes and lineage.
"""
import os
for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ[name]="1"
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from silice.bpm import Grid,gaussian,index_profile,metrics,propagate
from silice.tracks import discrete_profile
from run_glass007 import comparison


def validate_parent(parent):
    if parent.get("status")!="timeout_partial_retained" or parent.get("gpu_used") is not False:
        raise ValueError("expected original CPU partial timeout report")
    if not parent.get("sources_unchanged") or parent.get("hashes_before")!=parent.get("hashes_after"):
        raise ValueError("partial run source drift")
    for rel,sha in parent["hashes_before"].items():
        source=(ROOT/rel).resolve()
        if not source.is_relative_to(ROOT) or hashlib.sha256(source.read_bytes()).hexdigest()!=sha:
            raise ValueError("source changed since partial run")
    names=[c["name"] for c in parent.get("cases",[])]
    required=["continuous","tracks16","tracks32","tracks64",
              "tracks32_equal_integral","tracks32_missing","tracks32_coarse"]
    if names!=required:raise ValueError("unexpected checkpoint, do not duplicate finished cases")


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--parent",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True);args=parser.parse_args()
    parent_path=args.parent.resolve();target=args.out.resolve()
    if not parent_path.is_relative_to(ROOT/"resultados/codex"):
        parser.error("parent must be in resultados/codex")
    if not target.is_relative_to(ROOT/"resultados/codex") or target.exists():
        parser.error("new output in resultados/codex, no overwrite")
    parent=json.loads(parent_path.read_text(encoding="utf-8"));validate_parent(parent)
    started=time.monotonic();deadline=started+40
    import psutil
    if psutil.virtual_memory().available<1024**3:raise RuntimeError("CPU pilot >=1GiB free")
    report=dict(parent)
    report["parent_sha256"]=hashlib.sha256(parent_path.read_bytes()).hexdigest()
    report["parent_report"]=str(parent_path.relative_to(ROOT))
    report["continuation_sha256"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["cases"]=list(parent["cases"])
    report["time_utc"]=datetime.now(timezone.utc).isoformat()
    for name,grid,steps,continuous in [
        ("tracks32_wide_coarse",Grid(256,128e-6*256/192),800,False),
        ("tracks32_dz2",Grid(256,128e-6),1000,False),
        ("continuous_dz2",Grid(256,128e-6),1000,True)]:
        if continuous:
            dn=index_profile(grid,6e-6,6e-6,-0.003)
            import numpy as np
            meta=dict(tracks_count=None,peak_delta_n=-0.003,
                integral_abs_delta_n_m2=float(np.abs(dn).sum()*grid.dx_m**2),
                modified_area_m2=float(np.count_nonzero(dn)*grid.dx_m**2),
                core_untouched=True,outside_untouched=True)
        else:dn,meta=discrete_profile(grid)
        out,budget=propagate(gaussian(grid,6e-6),dn,grid,length_m=2e-3,steps=steps,deadline=deadline)
        m=metrics(out,grid,6e-6)
        report["cases"].append(dict(name=name,width_m=grid.width_m,points=grid.points,
            core_power_fraction_input=m["core_fraction_remaining"]*budget["output_power"]/budget["input_power"],
            **meta,**m,**budget,rss_mib=psutil.Process().memory_info().rss/1024**2,
            profile_sha256=hashlib.sha256(dn.tobytes()).hexdigest()))
    cases={c["name"]:c for c in report["cases"]}
    report["gates"]=[]
    for name,ref,candidate in [("dx","tracks32_coarse","tracks32"),
           ("domain_equal_dx","tracks32_coarse","tracks32_wide_coarse"),
           ("dz_tracks","tracks32","tracks32_dz2"),
           ("dz_continuous","continuous","continuous_dz2")]:
        report["gates"].append(dict(name=name,reference=ref,candidate=candidate,
            **comparison(cases[ref]["core_power_fraction_input"],cases[candidate]["core_power_fraction_input"])))
    dose=abs(cases["tracks32_equal_integral"]["integral_abs_delta_n_m2"]/
             cases["continuous"]["integral_abs_delta_n_m2"]-1)
    report["integral_error_relative"]=dose
    report["gate_profile"]=all(c["core_untouched"] and c["outside_untouched"] for c in report["cases"]) and dose<1e-12
    report["gate_balance"]=all(c["balance_relative"]<1e-10 for c in report["cases"])
    report["gate_refinements"]=all(g["gate"] for g in report["gates"])
    report["status"]="completed_two_bounded_jobs"
    report["partial_elapsed_s"]=parent["elapsed_s"]
    report["continuation_elapsed_s"]=time.monotonic()-started
    # elapsed_s inherited is not this child's time; make the semantics explicit.
    report["elapsed_s"]=report["partial_elapsed_s"]+report["continuation_elapsed_s"]
    validate_parent(parent)  # validate immutable source hashes again after run
    target.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(dict(status=report["status"],continuation_s=report["continuation_elapsed_s"],
        gates=report["gates"],gate_balance=report["gate_balance"],gate_profile=report["gate_profile"],
        cases=[dict(name=c["name"],power=c["core_power_fraction_input"]) for c in report["cases"]])))
    return 0 if report["gate_profile"] and report["gate_balance"] and report["gate_refinements"] else 2


if __name__=="__main__":sys.exit(main())
