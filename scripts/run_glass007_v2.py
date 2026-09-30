"""One bounded CPU child per case; retain every output, never overwrite."""
import os
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
import psutil
from silice.bpm import gaussian, metrics, propagate
from silice.coverage import CellGrid, averaged_profile, weighted_core_power

CASES = {
    "continuous": (256, 128e-6, 800, None, 0, False),
    "tracks16": (256, 128e-6, 800, 16, 0, False),
    "tracks32": (256, 128e-6, 800, 32, 0, False),
    "tracks64": (256, 128e-6, 800, 64, 0, False),
    "tracks32_equal_integral": (256, 128e-6, 800, 32, 0, True),
    "tracks32_missing": (256, 128e-6, 800, 32, math.pi/6, False),
    "tracks32_coarse": (192, 128e-6, 800, 32, 0, False),
    "tracks32_wide_coarse": (256, 128e-6*256/192, 800, 32, 0, False),
    "tracks32_dz2": (256, 128e-6, 1000, 32, 0, False),
    "continuous_dz2": (256, 128e-6, 1000, None, 0, False),
    "vacuum": (256, 128e-6, 200, None, 0, False),
    "continuous_dx4": (320, 128e-6, 800, None, 0, False),
    "tracks32_dx4": (320, 128e-6, 800, 32, 0, False),
}
OWN_INPUTS = ["src/silice/bpm.py", "src/silice/tracks.py", "src/silice/coverage.py",
              "scripts/run_glass007_v2.py", "Docs/GLASS-007-V2-CONTRACT.md",
              "resultados/codex/glass007_complete_v1.json"]
PEER_INPUTS = ["experimentos/glass009d_claude/resultados009d.json",
               "experimentos/glass009d_claude/CONTRACT.md",
               "experimentos/glass009d_claude/ERRATA.md",
               "experimentos/glass009_claude/adi2d.py",
               "experimentos/glass009d_claude/run009d.py",
               "experimentos/glass009d_claude/prep_exact.py",
               "experimentos/glass009d_claude/out/exact_T96d.json",
               "experimentos/glass006a_claude/resultados.json",
               "experimentos/glass006a_claude/g4_radial.py"]


def hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in OWN_INPUTS + PEER_INPUTS}


def write_new(path, data):
    encoded = json.dumps(data, indent=2, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(encoded)


def comparison(reference, candidate):
    absolute = abs(candidate-reference)
    relative = absolute/abs(reference) if reference else None
    return dict(absolute=absolute, relative=relative,
                pass_=reference >= 1e-6 and absolute < .005 and relative < .1)


def run_case(name):
    started = time.monotonic()
    deadline = started + 28  # Parent imposes30s including interpreter startup/I/O.
    before = hashes()
    free = psutil.virtual_memory().available
    if free-160*1024**2 < 1024**3:
        raise RuntimeError("CPU budget: need1GiB free AFTER160MiB reserve")
    points, width, steps, count, wedge, equal = CASES[name]
    g = CellGrid(points, width)
    build_start = time.monotonic()
    dn, weights, meta = averaged_profile(g, per_ring=count, missing_wedge_rad=wedge,
                                        match_integral=equal, deadline=deadline)
    if name == "vacuum":
        dn.fill(0)
        meta.update(peak_delta_n=0.0, integral_abs_delta_n_m2=0.0,
                    control_index="uniform_zero; detector retained")
    profile_s = time.monotonic()-build_start
    a = gaussian(g, 6e-6)
    propagation_start = time.monotonic()
    length = .5e-3 if name == "vacuum" else 2e-3
    b, budget = propagate(a, dn, g, steps=steps, length_m=length, deadline=deadline)
    propagation_s = time.monotonic()-propagation_start
    old = metrics(b, g, 6e-6)["core_fraction_remaining"]*budget["output_power"]/budget["input_power"]
    weighted = weighted_core_power(b, weights, g, budget["input_power"])
    after = hashes()
    profile_gate = bool(meta["detector_area_relative_error"] < 1e-10
                    and meta["coverage_area_relative_error"] < 1e-3
                    and meta["fully_core_cells_untouched"] and meta["fully_outside_cells_untouched"]
                    and (not equal or meta["integral_match_relative_error"] < 1e-12))
    result = dict(name=name, status="completed",
                  gpu_used=False, time_utc=datetime.now(timezone.utc).isoformat(),
                  points=points, width_m=width, length_m=length,
                  weighted_core_fraction_input=weighted, old_detector_same_field=old,
                  **budget, **meta, profile_s=profile_s, propagation_s=propagation_s,
                  elapsed_s=time.monotonic()-started, ram_free_before_gib=free/1024**3,
                  rss_mib=psutil.Process().memory_info().rss/1024**2,
                  profile_sha256=hashlib.sha256(dn.tobytes()).hexdigest(),
                  detector_sha256=hashlib.sha256(weights.tobytes()).hexdigest(),
                  hashes_before=before, hashes_after=after, sources_unchanged=before == after,
                  profile_gate=profile_gate, balance_gate=budget["balance_relative"] < 1e-10)
    result["backend"] = "scalar_paraxial_cpu_ssfm_cell_average"
    if name == "vacuum":
        zr = math.pi*1.444*(6e-6)**2/1550e-9
        expected = 1-math.exp(-2/(1+(length/zr)**2))
        result.update(analytic_core_fraction=expected, analytic_absolute_error=abs(weighted-expected),
                      analytic_gate=abs(weighted-expected) < 1e-3)
    return result


def load_reusable(path, name, current):
    case = json.loads(path.read_text(encoding="utf-8"))
    if case.get("status") != "completed" or case.get("name") != name or not case.get("sources_unchanged"):
        raise ValueError("reuse requires an unchanged completed case")
    if case["hashes_before"] != case["hashes_after"]:
        raise ValueError("parent source drift")
    # Metadata/supervisor repair only; scientific coverage/BPM/contract/peer
    # inputs must match EVERY hash from the earlier successful computation.
    for relative, sha in case["hashes_before"].items():
        if relative != "scripts/run_glass007_v2.py" and current.get(relative) != sha:
            raise ValueError("scientific input changed: " + relative)
    legacy = subprocess.check_output(["git", "show", "d7e5e95:scripts/run_glass007_v2.py"], cwd=ROOT)
    if hashlib.sha256(legacy).hexdigest() != case["hashes_before"]["scripts/run_glass007_v2.py"]:
        raise ValueError("unrecognized prior runner version")
    case["report_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    case["report_path"] = path.relative_to(ROOT).as_posix()
    case["reused_without_recomputation"] = True
    return case


def run_all(target, resume_prefix=None):
    start = time.monotonic()
    inputs = hashes()
    paths = {name: target.with_name(target.stem + "__" + name + ".json") for name in CASES}
    if target.exists() or any(path.exists() for path in paths.values()):
        raise FileExistsError("fresh report prefix required; never repeat completed cases silently")
    summary = dict(experiment="GLASS-007-v2", gpu_used=False, hashes_before=inputs,
                   cases=[], children=[], failures=[], gates=[],
                   prior_invalid_artifacts=[], historical_operational_pass=False,
                   peer_Q4_tracks_pass=False, boundary_validated=False,
                   combined_convergence_certified=False)
    if resume_prefix is not None:
        prefix = resume_prefix.resolve()
        if not prefix.is_relative_to(ROOT / "resultados/codex"):
            raise ValueError("resume prefix outside own results")
        for name in CASES:
            old = prefix.with_name(prefix.name + "__" + name + ".json")
            if not old.exists():
                continue
            try:
                case = load_reusable(old, name, inputs)
                summary["cases"].append(case)
            except json.JSONDecodeError:
                summary["prior_invalid_artifacts"].append(dict(path=old.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(old.read_bytes()).hexdigest(), reason="invalid_json_retained"))
    reused = {c["name"] for c in summary["cases"]}
    for name, output in paths.items():
        if name in reused:
            continue
        child_start = time.monotonic()
        result = None
        command = [sys.executable, "-B", str(Path(__file__).resolve()),
                   "--case", name, "--out", str(output)]
        try:
            run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
            child = dict(name=name, rc=run.returncode, elapsed_s=time.monotonic()-child_start,
                         stdout=run.stdout[-1000:], stderr=run.stderr[-1600:])
            if output.exists():
                try:
                    result = json.loads(output.read_text(encoding="utf-8"))
                    result["report_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
                    result["report_path"] = output.relative_to(ROOT).as_posix()
                    summary["cases"].append(result)
                except json.JSONDecodeError:
                    child["artifact_error"] = "invalid_json_retained"
            if run.returncode != 0:
                summary["failures"].append(child)
        except subprocess.TimeoutExpired:
            # subprocess.run kills ONLY the child it created; no peer processes.
            child = dict(name=name, rc="timeout", elapsed_s=time.monotonic()-child_start)
            summary["failures"].append(child)
        summary["children"].append(child)
        print(json.dumps(dict(name=name, rc=child["rc"], elapsed_s=child["elapsed_s"])), flush=True)
        if hashes() != inputs:
            summary["failures"].append(dict(name=name, reason="concurrent_input_mutation"))
            break
        if result is None or result.get("status") != "completed":
            # Stop operationally broken batches; numerical FAIL gates remain
            # reportable across all completed cases without retuning thresholds.
            break
    good = {c["name"]: c for c in summary["cases"] if c["status"] == "completed"}
    peer = json.loads((ROOT / PEER_INPUTS[0]).read_text(encoding="utf-8"))
    if len(good) == len(CASES):
        for label, ref, candidate in [
            ("dx_coarse", "tracks32_coarse", "tracks32"),
            ("domain_equal_dx", "tracks32_coarse", "tracks32_wide_coarse"),
            ("dz_tracks", "tracks32", "tracks32_dz2"),
            ("dz_continuous", "continuous", "continuous_dz2"),
            ("dx_tracks_05_04", "tracks32", "tracks32_dx4"),
            ("dx_continuous_05_04", "continuous", "continuous_dx4")]:
            summary["gates"].append(dict(name=label, reference=ref, candidate=candidate,
                **comparison(good[ref]["weighted_core_fraction_input"], good[candidate]["weighted_core_fraction_input"])))
        for name, key, dx in [("continuous", "Cd", "P_dx0p5"), ("tracks32", "T96d", "P_dx0p5"),
                              ("continuous_dx4", "Cd", "P_dx0p4"), ("tracks32_dx4", "T96d", "P_dx0p4")]:
            diff = abs(good[name]["weighted_core_fraction_input"]-peer[key][dx])
            summary["gates"].append(dict(name="peer_adi_"+name, absolute=diff, pass_=diff < .005))
        radial = json.loads((ROOT / PEER_INPUTS[7]).read_text(encoding="utf-8"))["G4"]["radial"]
        delta = abs(good["continuous"]["weighted_core_fraction_input"]-radial)
        summary["gates"].append(dict(name="radial_continuous", absolute=delta, pass_=delta < .003))
    summary["status"] = "completed" if len(good) == len(CASES) and not summary["failures"] else "incomplete_failures_retained"
    summary["hashes_after"] = hashes()
    summary["sources_unchanged"] = inputs == summary["hashes_after"]
    summary["elapsed_s"] = time.monotonic()-start
    summary["sum_children_s"] = sum(c["elapsed_s"] for c in summary["children"])
    summary["reused_case_count"] = len(reused)
    summary["reused_compute_s"] = sum(c["elapsed_s"] for c in summary["cases"] if c.get("reused_without_recomputation"))
    summary["wall_time_scope"] = "current supervisor only; run1 cost retained separately; run2 aborted before wall-time manifest"
    summary["own_gates_pass"] = (summary["status"] == "completed" and summary["sources_unchanged"]
        and all(c["profile_gate"] and c["balance_gate"] and c.get("analytic_gate", True) for c in good.values())
        and all(g["pass_"] for g in summary["gates"]))
    write_new(target, summary)
    return 0 if summary["own_gates_pass"] else 2


def main():
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--case", choices=CASES)
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--resume-prefix", type=Path)
    args = parser.parse_args()
    target = args.out.resolve()
    if not target.is_relative_to(ROOT / "resultados/codex") or target.exists():
        parser.error("new own output path required")
    if args.all:
        return run_all(target, args.resume_prefix)
    try:
        result = run_case(args.case)
    except Exception as error:
        result = dict(name=args.case, status="failure_retained", error_type=type(error).__name__,
                      error=str(error), gpu_used=False)
    write_new(target, result)
    print(json.dumps({k: result[k] for k in ("name", "status")}), flush=True)
    return 0 if result["status"] == "completed" and result["profile_gate"] and result["balance_gate"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
