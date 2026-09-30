"""Read-only peer audit; report empirical noise tails, not fabrication yield."""
import os
for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ[name]="1"
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from datetime import datetime,timezone
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PEER=ROOT/"experimentos/glass_min1"


def closed_mesh(theta,phi,dkl=None,dph_in=None,dph_mid=None,loss_db=0):
    dkl=np.zeros(4) if dkl is None else np.asarray(dkl)
    dph_in=np.zeros(4) if dph_in is None else np.asarray(dph_in)
    dph_mid=np.zeros(4) if dph_mid is None else np.asarray(dph_mid)
    s1=np.eye(4,dtype=complex);s2=np.eye(4,dtype=complex)
    for matrix,pairs,angles in [(s1,[(0,2),(1,3)],np.pi/4+dkl[:2]),
                               (s2,[(0,1),(2,3)],np.pi/4+dkl[2:])]:
        for (i,j),angle in zip(pairs,angles):
            matrix[i,i]=matrix[j,j]=np.cos(angle)
            matrix[i,j]=matrix[j,i]=-1j*np.sin(angle)
    return s2@np.diag(np.exp(1j*(phi+dph_mid)))@s1@np.diag(np.exp(1j*(theta+dph_in)))*10**(-loss_db/20)


def load_readonly(name):
    spec=importlib.util.spec_from_file_location("glass004_peer_"+name,PEER/(name+".py"))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args();target=args.out.resolve()
    if not target.is_relative_to(ROOT/"resultados/codex") or target.exists():
        parser.error("new output under resultados/codex only, no overwrite")
    started=time.monotonic();deadline=started+40
    names=["sim_cmt.py","oracle.py","montecarlo.py","phases.npy","resultados.txt"]
    def hashes():return {n:hashlib.sha256((PEER/n).read_bytes()).hexdigest() for n in names}
    before=hashes()
    cmt=load_readonly("sim_cmt");oracle=load_readonly("oracle")
    phases=np.load(PEER/"phases.npy",allow_pickle=False)
    if phases.shape!=(8,) or not np.isfinite(phases).all():raise ValueError("invalid phases")
    theta,phi=phases[:4],phases[4:]
    # Explicit analytical DFT: no calls to the peer's dft4.
    dft=np.array([[1,1,1,1],[1,-1j,-1,1j],[1,-1,1,-1],[1,1j,-1,-1j]],complex)/2
    expected=dft[[0,2,1,3],:]
    inputs=oracle.test_states(n=32,seed=0)
    truth=np.abs(inputs@expected.T)**2
    bright=truth>0.05;dark=~bright
    def errors(u):
        intensity=np.abs(inputs@u.T)**2
        return float(np.mean(np.abs(intensity-truth)[bright]/truth[bright])),float(np.max(np.abs(intensity-truth)[dark]))
    u=closed_mesh(theta,phi)
    peer=cmt.mesh(theta,phi)
    cmt_error=float(np.max(np.abs(u-peer)))
    nominal,dark_nominal=errors(u)
    # Row-dependent phase is unobservable by output intensity detectors but
    # matters to a later coherent stage; expose rather than silently align it.
    phase_alignment=np.sum(u*np.conj(expected),axis=1)
    row_phases=np.angle(phase_alignment)
    raw_field_error=float(np.max(np.abs(u-expected)))
    row_aligned_error=float(np.max(np.abs(u-np.exp(1j*row_phases)[:,None]*expected)))
    noise=[]
    for kind,sigma in [("phase",0.05),("phase",0.10),("coupling",0.03),("coupling",0.05)]:
        rng=np.random.default_rng(7)
        bright_errors=[];dark_errors=[]
        for _ in range(400):
            if time.monotonic()>deadline:raise TimeoutError("audit CPU deadline")
            kwargs=dict(dph_in=rng.normal(0,sigma,4),dph_mid=rng.normal(0,sigma,4)) if kind=="phase" else dict(dkl=rng.normal(0,sigma,4))
            rel,absdark=errors(closed_mesh(theta,phi,**kwargs))
            bright_errors.append(rel);dark_errors.append(absdark)
        noise.append(dict(kind=kind,sigma_rad=sigma,pieces=400,
            mean=float(np.mean(bright_errors)),p95=float(np.percentile(bright_errors,95)),
            fraction_over_10pct=float(np.mean(np.array(bright_errors)>0.10)),
            p95_dark_absolute=float(np.percentile(dark_errors,95))))
    negatives=dict(phase_pi=errors(closed_mesh(theta,phi+np.array([0,np.pi,0,0])))[0],
                   coupler_off=errors(closed_mesh(theta,phi,dkl=[-np.pi/4,0,0,0]))[0])
    loss=closed_mesh(theta,phi,loss_db=1)
    loss_power=float(np.mean(np.sum(np.abs(inputs@loss.T)**2,axis=1)))
    after=hashes()
    report=dict(experiment="GLASS-004-v1",time_utc=datetime.now(timezone.utc).isoformat(),
        backend="independent_closed_couplers_cpu",gpu_used=False,elapsed_s=time.monotonic()-started,
        source_hashes_before=before,source_hashes_after=after,peer_unchanged=before==after,
        port_order=[0,2,1,3],nominal_bright_relative=nominal,nominal_dark_absolute=dark_nominal,
        independent_vs_cmt_max_field=cmt_error,raw_dft_field_error=raw_field_error,
        row_phase_rad=row_phases.tolist(),row_phase_aligned_field_error=row_aligned_error,
        noise=noise,controls=negatives,loss_power=loss_power,
        loss_expected=10**(-0.1),gate_nominal=nominal<1e-4 and cmt_error<1e-12,
        gate_controls=all(v>0.1 for v in negatives.values()),
        caveats=["noise is hypothetical, not manufactured sample yield",
                 "bright metric excludes dark ports; both recorded",
                 "row phase alignment diagnostic only, not physical calibration"],
        audit_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    target.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in ["peer_unchanged","nominal_bright_relative",
        "independent_vs_cmt_max_field","raw_dft_field_error","row_phase_aligned_field_error",
        "noise","gate_nominal","gate_controls","elapsed_s"]}))
    return 0 if report["peer_unchanged"] and report["gate_nominal"] and report["gate_controls"] else 2


if __name__=="__main__":sys.exit(main())
