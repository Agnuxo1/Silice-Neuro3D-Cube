"""Prospective discrete-jacket experiment; CPU only, old solvers immutable."""
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
import numpy as np
from silice.bpm import Grid,gaussian,index_profile,metrics,propagate
from silice.tracks import discrete_profile


def comparison(reference,candidate):
    absolute=abs(reference-candidate)
    relative=absolute/abs(reference) if reference else None
    return dict(absolute=absolute,relative=relative,
        gate=reference>=1e-6 and absolute<0.005 and relative<0.1)


def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();target=args.out.resolve()
    if not target.is_relative_to(ROOT/"resultados/codex") or target.exists():
        p.error("new output under resultados/codex only; no overwrite")
    started=time.monotonic();deadline=started+40
    import psutil
    free=psutil.virtual_memory().available
    if free<1024**3:raise RuntimeError("CPU pilot needs >=1GiB free, peak budget100MiB")
    files=[ROOT/"src/silice/bpm.py",ROOT/"src/silice/tracks.py",
           ROOT/"Docs/GLASS-007-DISCRETE-CONTRACT.md",Path(__file__).resolve()]
    frozen={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    profiles=[("continuous",None,0,False),("tracks16",16,0,False),
              ("tracks32",32,0,False),("tracks64",64,0,False),
              ("tracks32_equal_integral",32,0,True),
              ("tracks32_missing",32,np.pi/6,False)]
    runs=[(name,Grid(256,128e-6),800,count,wedge,equal)
          for name,count,wedge,equal in profiles]
    runs+=[("tracks32_coarse",Grid(192,128e-6),800,32,0,False),
           ("tracks32_wide_coarse",Grid(256,128e-6*256/192),800,32,0,False),
           ("tracks32_dz2",Grid(256,128e-6),1000,32,0,False),
           ("continuous_dz2",Grid(256,128e-6),1000,None,0,False)]
    report=dict(experiment="GLASS-007-v1",time_utc=datetime.now(timezone.utc).isoformat(),
        backend="scalar_paraxial_cpu_ssfm",gpu_used=False,ram_free_before_gib=free/1024**3,
        parameters_status="ideal_hypothetical_profiles_not_laser_recipe",cases=[],gates=[],
        hashes_before=frozen,combined_convergence_certified=False)
    try:
        for name,grid,steps,count,wedge,equal in runs:
            if count is None:
                dn=index_profile(grid,6e-6,6e-6,-0.003)
                meta=dict(tracks_count=None,peak_delta_n=-0.003,
                    modified_area_m2=float(np.count_nonzero(dn)*grid.dx_m**2),
                    integral_abs_delta_n_m2=float(np.abs(dn).sum()*grid.dx_m**2),
                    core_untouched=True,outside_untouched=True)
            else:
                dn,meta=discrete_profile(grid,per_ring=count,missing_wedge_rad=wedge,match_integral=equal)
            out,budget=propagate(gaussian(grid,6e-6),dn,grid,length_m=2e-3,steps=steps,deadline=deadline)
            m=metrics(out,grid,6e-6)
            report["cases"].append(dict(name=name,width_m=grid.width_m,points=grid.points,
                core_power_fraction_input=m["core_fraction_remaining"]*budget["output_power"]/budget["input_power"],
                **meta,**m,**budget,rss_mib=psutil.Process().memory_info().rss/1024**2,
                profile_sha256=hashlib.sha256(dn.tobytes()).hexdigest()))
        cases={c["name"]:c for c in report["cases"]}
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
        report["status"]="completed"
    except TimeoutError:
        report["status"]="timeout_partial_retained"
    report["elapsed_s"]=time.monotonic()-started
    report["hashes_after"]={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    report["sources_unchanged"]=report["hashes_before"]==report["hashes_after"]
    target.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(dict(status=report["status"],elapsed_s=report["elapsed_s"],gates=report["gates"],
        cases=[dict(name=c["name"],power=c["core_power_fraction_input"],
               tracks=c["tracks_count"],peak=c["peak_delta_n"]) for c in report["cases"]],
        rss_max_mib=max(c["rss_mib"] for c in report["cases"]))))
    return 0 if report["status"]=="completed" and report["gate_profile"] and report["gate_balance"] and report["gate_refinements"] and report["sources_unchanged"] else 2


if __name__=="__main__":sys.exit(main())
