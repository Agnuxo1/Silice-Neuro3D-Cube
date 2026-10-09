"""Prospective SuperLU audit draft; never changes a frozen Stage B study.

Install as scripts/audit_point03_sparse_adi.py, beside point03_sparse_adi.py.
Only syntax and source review are authorized until contract C is frozen.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "resultados/codex"
CONTRACT = ROOT / "Docs/POINT-03-SPARSE-ADI-CONTRACT.md"
HELPER = ROOT / "scripts/point03_sparse_adi.py"
ADI = ROOT / "experimentos/glass009_claude/adi2d.py"
STUDY = ROOT / "resultados/codex/point03_refinement_20261006T220909702270Z/manifest.json"
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
CASES = ("n256_ss64_z125", "n500_ss64_z125")


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid.uuid4().hex[:8]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def reject(value):
        raise ValueError("Nonfinite JSON value: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject)


def write_json(path, data):
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, allow_nan=False)
        handle.write("\n")


def save_npz(path, np, **arrays):
    with Path(path).open("xb") as handle:
        np.savez_compressed(handle, **arrays)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def tracked_snapshot():
    process = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"],
                             capture_output=True, shell=False, timeout=10)
    require(process.returncode == 0, "Git inventory failed: " + process.stderr.decode("utf-8", "replace"))
    result = {}
    for relative in process.stdout.decode("utf-8", "surrogateescape").split("\0"):
        if relative:
            path = ROOT / relative
            require(path.exists(), "Missing tracked file: " + relative)
            if path.is_file() and not path.is_symlink():
                result[relative] = sha(path)
    return result


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def runtime():
    for key in THREADS:
        os.environ[key] = "1"
    import numpy as np
    import scipy
    import psutil
    require(scipy.__version__ == "1.15.1", "Contract C requires SciPy 1.15.1.")
    require(np.__version__ == "2.2.6" and psutil.__version__ == "6.1.1"
            and platform.python_version() == "3.13.7", "Point 01 CPU versions differ.")
    require(Path(sys.prefix).resolve() == (ROOT / ".venv").resolve(), "Use the isolated Point 01 CPU environment.")
    adi = load_module("point03_sparse_original_adi", ADI)
    helper = load_module("point03_sparse_audit_helper", HELPER)
    sparse = helper.make_sparse_stepper(adi.Stepper)
    for name in ("__init__", "_lap", "step"):
        require(getattr(sparse, name) is getattr(adi.Stepper, name), "Original method changed: " + name)
    require("torch" not in sys.modules and "cupy" not in sys.modules, "GPU library imported.")
    return np, scipy, psutil, adi, sparse


def guard(psutil, out, deadline):
    require(time.monotonic() < deadline, "Audit wall-time budget exhausted.")
    require(psutil.virtual_memory().available > 1.5 * 1024**3, "Available RAM must exceed 1.5 GiB.")
    require(shutil.disk_usage(out).free > 2 * 1024**3, "Free disk must exceed 2 GiB.")


def memory_metadata(psutil):
    memory = psutil.Process().memory_info()
    return {"rss_current_bytes": memory.rss, "peak_wset_bytes": getattr(memory, "peak_wset", None),
            "scope": "Windows peak working set if available; RSS is a current sample."}


def verify_manifest(path, expected=None):
    if expected:
        require(sha(path) == expected, "Audit manifest SHA changed.")
    data = read_json(path)
    require(data["schema"] == "silice.point03-sparse.manifest.v1", "Unknown audit manifest.")
    for name, digest in data["frozen_sha256"].items():
        require(sha(name) == digest, "Frozen source or input changed: " + name)
    return data


def dense_matrix(np, dn, sigma, dx, dz, adi, axis):
    """Independent entrywise assembly, without sparse diagonals or factor data."""
    n = dn.shape[0]
    h = dz / 2
    c = 1j / (2 * adi.b0 * dx * dx)
    diagonal = 1 + 2 * h * c - h * (1j * adi.k0 * dn - sigma) / 2
    result = np.zeros((n*n, n*n), dtype=np.complex128)
    for line in range(n):
        for position in range(n):
            index = line*n + position
            iy, ix = (line, position) if axis == "x" else (position, line)
            result[index, index] = diagonal[iy, ix]
            if position:
                result[index, index - 1] = -h*c
            if position + 1 < n:
                result[index, index + 1] = -h*c
    return result


def relative_fields(np, actual, expected):
    require(actual.shape == expected.shape and actual.dtype == expected.dtype == np.dtype("complex128"), "Field shape or dtype mismatch.")
    require(np.all(np.isfinite(actual)) and np.all(np.isfinite(expected)), "Nonfinite field.")
    delta = actual - expected
    l2 = float(np.linalg.norm(delta.ravel()) / np.linalg.norm(expected.ravel()))
    linf = float(np.max(np.abs(delta)) / np.max(np.abs(expected)))
    require(math.isfinite(l2) and math.isfinite(linf), "Invalid field difference.")
    return {"relative_l2": l2, "relative_linf": linf}


def small_worker(args, np, psutil, adi, sparse, started, report):
    rng = np.random.Generator(np.random.PCG64(20261006))
    report["checks"] = []
    report["matrix_checks"] = []
    report["array_artifacts"] = []
    def retain(path, **arrays):
        save_npz(path, np, **arrays)
        report["array_artifacts"].append({"path":str(path),"sha256":sha(path)})
    for n, dx, dz in ((8, .5e-6, 1.25e-6), (11, .256e-6, .625e-6)):
        if n != args.small_n:
            continue
        guard(psutil, args.out_dir, started + 35)
        dn = rng.uniform(-.003, 0, (n, n)).astype(np.float64)
        sigma = rng.uniform(0, 4e4, (n, n)).astype(np.float64)
        field = (rng.standard_normal((n,n)) + 1j*rng.standard_normal((n,n))).astype(np.complex128)
        field /= math.sqrt(float(np.sum(np.abs(field)**2) * dx**2))
        report["small_profile"] = {"N":n,"dx_m":dx,"dz_m":dz,"seed":20261006,
                                   "input_power":adi.power(field,dx)}
        retain(args.out_dir / f"small_n{n}_inputs.npz", dn=dn, sigma=sigma, rhs=field)
        dense = {axis: dense_matrix(np, dn, sigma, dx, dz, adi, axis) for axis in ("x", "y")}
        retain(args.out_dir / f"small_n{n}_dense.npz", dense_x=dense["x"], dense_y=dense["y"])
        original, candidate = adi.Stepper(dn, sigma, dx, dz), sparse(dn, sigma, dx, dz)
        factor_record = {"N":n,"metadata":candidate.sparse_metadata()}
        report.setdefault("factor_metadata",[]).append(factor_record)
        for axis in ("x", "y"):
            factor = getattr(candidate, "f" + axis)
            legacy_factor = getattr(original, "f" + axis)
            matrix = factor["matrix"].toarray()
            require(np.array_equal(matrix, dense[axis]), "Sparse and independent dense operators differ.")
            require(np.count_nonzero(matrix) == 3*n*n-2*n, "Wrong nonzero count.")
            for cut in range(n-1, n*n-1, n):
                require(matrix[cut,cut+1] == matrix[cut+1,cut] == 0, "Coupling across a line cut.")
            report["matrix_checks"].append({"N":n,"axis":axis,"exact_dense_match":True,
                                             "matrix_nnz":int(np.count_nonzero(matrix)),"line_cuts":n-1,
                                             "cross_block_connections":0})
            for label in ("random", "impulse_before_cut", "impulse_after_cut"):
                rhs = field.copy() if axis == "x" else field.T.copy()
                if label != "random":
                    rhs.fill(0)
                    index = n-1 if label == "impulse_before_cut" else n
                    rhs.flat[index] = 1 / dx
                actual = candidate._solve(factor, rhs)
                factor_record["metadata"] = candidate.sparse_metadata()
                expected = original._solve(legacy_factor, rhs)
                retain(args.out_dir / f"small_n{n}_{axis}_{label}.npz",
                       rhs=rhs, sparse_field=actual, original_field=expected)
                difference = relative_fields(np, actual, expected)
                vector, solution = rhs.ravel(), actual.ravel()
                residual = float(np.linalg.norm(dense[axis] @ solution-vector, ord=np.inf)
                                 / (np.linalg.norm(dense[axis],ord=np.inf)*np.linalg.norm(solution,ord=np.inf)
                                    + np.linalg.norm(vector,ord=np.inf)))
                leakage = 0.0
                if label != "random":
                    other = actual.copy()
                    other[index // n, :] = 0
                    leakage = float(np.max(np.abs(other)))
                row = dict(difference, N=n, axis=axis, rhs=label, residual_infinity_normalized=residual,
                           cross_block_leakage=leakage)
                report["checks"].append(row)
                require(residual <= 1e-13 and difference["relative_l2"] <= 1e-12 and leakage == 0,
                        "Small-system solve failed equivalence or block isolation.")
        original_field, sparse_field = field.copy(), field.copy()
        for step in range(1, 65):
            guard(psutil, args.out_dir, started + 35)
            original_field = original.step(original_field)
            sparse_field = candidate.step(sparse_field)
            factor_record["metadata"] = candidate.sparse_metadata()
            if step in (1, 16, 64):
                retain(args.out_dir / f"small_n{n}_steps{step}.npz",
                       sparse_field=sparse_field, original_field=original_field)
                difference = relative_fields(np, sparse_field, original_field)
                power_error = abs(adi.power(sparse_field,dx)-adi.power(original_field,dx))
                report["checks"].append(dict(difference, N=n, steps=step, absolute_power_difference=power_error))
                require(difference["relative_l2"] <= 1e-12 and power_error <= 1e-12,
                        "Complete small-grid ADI steps failed equivalence.")
    for artifact in report["array_artifacts"]:
        require(sha(artifact["path"]) == artifact["sha256"],"Small-case retained arrays changed.")


def reproduction_worker(args, audit, np, psutil, adi, sparse, started, report):
    case = next(c for c in audit["cases"] if c["case_id"] == args.case_id)
    with np.load(case["input_npz_path"], allow_pickle=False) as archive:
        arrays = {key: archive[key] for key in ("A0", "dn", "sigma", "weights")}
    for key, array in arrays.items():
        require(array.shape == (case["N"],case["N"]) and np.all(np.isfinite(array)), "Invalid input array: " + key)
        require(array.dtype == np.dtype("complex128" if key == "A0" else "float64"), "Input dtype differs.")
    require(np.all((arrays["dn"] >= -.003) & (arrays["dn"] <= 0))
            and np.all(arrays["sigma"] >= 0), "Input profile is outside the passive fixed model.")
    require(np.all((arrays["weights"] >= 0) & (arrays["weights"] <= 1)),"Detector weights are nonpassive.")
    dx = case["dx_m"]
    p0 = adi.power(arrays["A0"],dx)
    area = float(np.sum(arrays["weights"])*dx**2)
    require(abs(p0-1) <= 1e-12 and abs(area/(math.pi*(6e-6)**2)-1) <= 1e-12,
            "Stage B initial power or analytic detector area is invalid.")
    field, steps, previous_sha = arrays["A0"].copy(), 0, None
    if args.checkpoint:
        old = read_json(args.checkpoint)
        previous_sha = sha(args.checkpoint)
        require(old["status"] == "checkpoint_completed" and old["case_id"] == args.case_id
                and old["audit_manifest_sha256"] == args.audit_sha
                and old["input_npz_sha256"] == case["input_npz_sha256"], "Parent checkpoint identity changed.")
        require(sha(old["npz_path"]) == old["npz_sha256"], "Parent checkpoint field changed.")
        with np.load(old["npz_path"], allow_pickle=False) as archive:
            field = archive["field"]
        steps = old["steps_done"]
    require(0 <= steps < 1600 and field.dtype == np.dtype("complex128") and np.all(np.isfinite(field)), "Invalid starting field or steps.")
    candidate = sparse(arrays["dn"],arrays["sigma"],case["dx_m"],case["dz_m"])
    first_step = steps
    propagation_started = time.monotonic()
    path = Path(str(args.prefix)+".npz")
    try:
        while steps < min(first_step+200,1600) and time.monotonic() < started+31:
            guard(psutil,args.out_dir,started+35)
            field = candidate.step(field)
            steps += 1
    finally:
        propagation_s = time.monotonic()-propagation_started
        report.update(case_id=args.case_id, steps_start=first_step, steps_done=steps,
                      previous_checkpoint_path=str(args.checkpoint) if args.checkpoint else None,
                      previous_checkpoint_sha256=previous_sha, input_npz_sha256=case["input_npz_sha256"],
                      propagation_s=propagation_s,factor_metadata=candidate.sparse_metadata())
        save_npz(path,np,field=field)
        report.update(npz_path=str(path),npz_sha256=sha(path))
    require(steps > first_step, "No progress within the bounded child.")
    require(field.shape == (case["N"],case["N"]) and field.dtype == np.dtype("complex128")
            and np.all(np.isfinite(field)), "Invalid propagated field; raw checkpoint retained.")
    total = adi.power(field,dx)
    core = float(np.sum(arrays["weights"]*np.abs(field)**2)*dx**2/p0)
    report.update(input_power=p0,output_power=total,core_power_analytic_input=core,core_area_m2=area)
    require(math.isfinite(total) and math.isfinite(core) and 0 <= core <= total/p0+1e-12,
            "Checkpoint violates passive detector invariants.")
    if steps == 1600:
        with np.load(case["reference_npz_path"],allow_pickle=False) as archive:
            reference = archive["field"]
        difference = relative_fields(np,field,reference)
        actual_total, reference_total = adi.power(field,dx), adi.power(reference,dx)
        actual_core = float(np.sum(arrays["weights"]*np.abs(field)**2)*dx**2/p0)
        reference_core = float(np.sum(arrays["weights"]*np.abs(reference)**2)*dx**2/p0)
        report["comparison"] = dict(difference, input_power=p0, sparse_total=actual_total,
                                     reference_total=reference_total, sparse_core=actual_core,
                                     reference_core=reference_core,
                                     absolute_total_difference=abs(actual_total-reference_total),
                                     absolute_core_difference=abs(actual_core-reference_core))
        require(0 <= actual_total <= 1.001 and 0 <= reference_total <= 1.001
                and 0 <= reference_core <= reference_total/p0+1e-12, "Final-power numerical guard failed.")
        require(max(difference.values()) <= 1e-12 and abs(actual_total-reference_total) <= 1e-12
                and abs(actual_core-reference_core) <= 1e-12, "Full Stage B reproduction failed equivalence.")


def private_worker(args):
    started = time.monotonic()
    report = {"schema":"silice.point03-sparse.worker.v1", "status":"failed", "gpu_used":False,
              "audit_manifest_sha256":args.audit_sha}
    try:
        audit = verify_manifest(args.audit_manifest,args.audit_sha)
        require(args.out_dir.resolve() == Path(audit["out_dir"]), "Worker output directory differs.")
        require(args.prefix.resolve().is_relative_to(args.out_dir.resolve()), "Worker prefix escapes audit.")
        np, scipy, psutil, adi, sparse = runtime()
        guard(psutil,args.out_dir,started+35)
        if args.private_small:
            small_worker(args,np,psutil,adi,sparse,started,report)
        else:
            reproduction_worker(args,audit,np,psutil,adi,sparse,started,report)
        verify_manifest(args.audit_manifest,args.audit_sha)
        guard(psutil,args.out_dir,started+35)
        report.update(status="small_completed" if args.private_small else "checkpoint_completed",
                      sources_and_inputs_unchanged=True, memory=memory_metadata(psutil))
    except (Exception,KeyboardInterrupt) as error:
        report.update(error_type=type(error).__name__,error=str(error))
        if hasattr(error,"diagnostic"):
            report["rejected_permutation_diagnostic"] = error.diagnostic
        if hasattr(error,"permutation_arrays"):
            try:
                rejected_path = Path(str(args.prefix)+"_rejected_permutations.npz")
                save_npz(rejected_path,np,**error.permutation_arrays)
                report["rejected_permutation_arrays"] = {
                    "path":str(rejected_path),"sha256":sha(rejected_path),
                    "keys":sorted(error.permutation_arrays)}
            except Exception as retention_error:
                report["permutation_retention_error"] = f"{type(retention_error).__name__}: {retention_error}"
    if "psutil" in locals():
        report.setdefault("memory",memory_metadata(psutil))
    report["elapsed_s"] = time.monotonic()-started
    write_json(Path(str(args.prefix)+".json"),report)
    return 0 if report["status"] != "failed" else 1


def freeze_study(study,out):
    require(study == STUDY.resolve(),"Contract C names a different Stage B study.")
    manifest = read_json(study)
    require(manifest["schema"] == "silice.point03-refinement.manifest.v1", "Unknown Stage B manifest.")
    require(Path(manifest["source_root"]).resolve() == ROOT, "Stage B source checkout differs.")
    frozen = dict(manifest["source_sha256"])
    frozen.update({str(p.resolve()):sha(p) for p in (study,CONTRACT,HELPER,Path(__file__))})
    cases = []
    for name in CASES:
        n = 256 if name.startswith("n256_") else 500
        plan = next(c for c in manifest["case_plan"] if c["case_id"] == name)
        require((plan["N"],plan["profile_samples"],plan["steps_target"],plan["width_m"],plan["dx_m"],plan["dz_m"])
                == (n,64,1600,128e-6,128e-6/n,1.25e-6), "Stage B plan differs from contract C.")
        case_path = study.parent/"cases"/name/"case.json"
        case = read_json(case_path)
        require(case["status"] == "completed" and case["numeric_valid"] is True
                and case["manifest_sha256"] == sha(study) and case["steps_done"] == 1600, "Stage B reference is incomplete.")
        for key in ("input_npz_path","input_npz_sha256"):
            require(case[key] == plan[key], "Reference input differs from Stage B plan.")
        frozen[str(case_path.resolve())] = sha(case_path)
        frozen[case["input_npz_path"]] = case["input_npz_sha256"]
        frozen[case["final_npz_path"]] = case["final_npz_sha256"]
        cases.append(dict(plan,reference_case_path=str(case_path.resolve()),reference_case_sha256=sha(case_path),
                          reference_npz_path=case["final_npz_path"],reference_npz_sha256=case["final_npz_sha256"]))
    return {"schema":"silice.point03-sparse.manifest.v1", "out_dir":str(out), "study_path":str(study),
            "study_sha256":sha(study), "frozen_sha256":frozen, "cases":cases, "total_wall_budget_s":600,
            "seed":20261006, "max_steps_per_child":200, "internal_deadline_s":35,
            "parent_timeout_s":40, "field_tolerance":1e-12, "power_tolerance":1e-12,
            "residual_tolerance":1e-13, "scope":"Solver equivalence only; no convergence or measured speedup claim."}


def execute(args):
    started = time.monotonic()
    out = args.out_dir.resolve()
    report = {"schema":"silice.point03-sparse.execution.v1", "status":"failed", "operational_pass":False,
              "children":[], "case_reports":[], "produced_sha256":{},"study_path":str(args.study.resolve())}
    try:
        before = tracked_snapshot()
        report["tracked_sha256_before"] = before
        audit = freeze_study(args.study.resolve(),out)
        path = out/"audit_manifest.json"
        write_json(path,audit)
        identity = sha(path)
        report["produced_sha256"][str(path)] = identity
        report.update(audit_manifest_path=str(path),audit_manifest_sha256=identity,
                      frozen_sha256_before=audit["frozen_sha256"])
        verify_manifest(path,identity)
        np,scipy,psutil,_,_ = runtime()
        report["environment"] = {"python":sys.version,"numpy":np.__version__,"scipy":scipy.__version__,
                                 "psutil":psutil.__version__,"threads":{k:os.environ[k] for k in THREADS}}
        deadline = started+600

        def child(mode,prefix,case_id=None,checkpoint=None,small_n=None):
            guard(psutil,out,deadline)
            require(deadline-time.monotonic() >= 40, "Insufficient total budget for another child.")
            command = [sys.executable,"-B","-u",str(Path(__file__).resolve()),mode,"--study",str(args.study.resolve()),
                       "--out-dir",str(out),"--audit-manifest",str(path),"--audit-sha",identity,"--prefix",str(prefix)]
            if case_id:
                command += ["--case-id",case_id]
            if checkpoint:
                command += ["--checkpoint",str(checkpoint)]
            if small_n:
                command += ["--small-n",str(small_n)]
            entry = {"command":command,"started_elapsed_s":time.monotonic()-started}
            child_started = time.monotonic()
            try:
                run = subprocess.run(command,cwd=ROOT,shell=False,capture_output=True,text=True,
                                     encoding="utf-8",errors="replace",timeout=40)
                stdout,stderr,code = run.stdout,run.stderr,run.returncode
            except subprocess.TimeoutExpired as error:
                def decoded(value):
                    return value.decode("utf-8","replace") if isinstance(value,bytes) else value or ""
                stdout,stderr,code = decoded(error.stdout),decoded(error.stderr),None
                entry["timed_out"] = True
            except (OSError,KeyboardInterrupt) as error:
                stdout,stderr,code = "",f"{type(error).__name__}: {error}",None
                entry["interrupted_or_launch_error"] = stderr
            entry.update(returncode=code,elapsed_s=time.monotonic()-child_started)
            for label,text in (("stdout",stdout),("stderr",stderr)):
                log = Path(str(prefix)+"."+label+".log")
                with log.open("x",encoding="utf-8",newline="\n") as handle:
                    handle.write(text)
                entry[label+"_path"] = str(log)
                report["produced_sha256"][str(log)] = sha(log)
            report["children"].append(entry)
            require(code == 0,"Bounded child failed; all outputs and logs are retained.")
            verify_manifest(path,identity)
            child_path = Path(str(prefix)+".json")
            result = read_json(child_path)
            report["produced_sha256"][str(child_path)] = sha(child_path)
            require(result["audit_manifest_sha256"] == identity,"Child belongs to another audit.")
            artifacts = list(result.get("array_artifacts",[]))
            if "npz_path" in result:
                artifacts.append({"path":result["npz_path"],"sha256":result["npz_sha256"]})
            for artifact in artifacts:
                require(sha(artifact["path"]) == artifact["sha256"],"Retained child arrays changed.")
                report["produced_sha256"][artifact["path"]] = artifact["sha256"]
            print(json.dumps({"progress":result["status"],"case_id":case_id,"steps_done":result.get("steps_done")}),flush=True)
            return child_path,result

        report["small_reports"] = []
        for n in (8,11):
            small_path,small = child("--private-small",out/f"small_n{n}",small_n=n)
            require(small["status"] == "small_completed","Small-grid validation did not complete.")
            report["small_reports"].append({"N":n,"path":str(small_path),"sha256":sha(small_path)})
        for case in audit["cases"]:
            folder = out/case["case_id"]
            folder.mkdir()
            previous,previous_sha,steps = None,None,0
            while steps < 1600:
                checkpoint,result = child("--private-reproduce",folder/("chunk_"+stamp()),case["case_id"],previous)
                require(result["status"] == "checkpoint_completed" and result["case_id"] == case["case_id"]
                        and result["steps_start"] == steps and steps < result["steps_done"] <= min(steps+200,1600)
                        and result["previous_checkpoint_sha256"] == previous_sha
                        and result["input_npz_sha256"] == case["input_npz_sha256"]
                        and sha(result["npz_path"]) == result["npz_sha256"],"Checkpoint sequence or identity differs.")
                previous,previous_sha,steps = checkpoint,sha(checkpoint),result["steps_done"]
            report["case_reports"].append({"case_id":case["case_id"],"path":str(previous),"sha256":previous_sha,
                                           "comparison":result["comparison"]})
        verify_manifest(path,identity)
        guard(psutil,out,deadline)
        report.update(status="completed",operational_pass=True,memory=memory_metadata(psutil))
    except (Exception,KeyboardInterrupt) as error:
        report.update(status="failed",error_type=type(error).__name__,error=str(error))
    try:
        after = tracked_snapshot()
        report["tracked_sha256_after"] = after
        report["tracked_inputs_unchanged"] = report.get("tracked_sha256_before") == after
        if not report["tracked_inputs_unchanged"]:
            report.update(status="failed",operational_pass=False,integrity_error="Tracked files changed.")
        if "audit" in locals():
            current = {name:sha(name) for name in audit["frozen_sha256"]}
            report["frozen_sha256_after"] = current
            report["frozen_unchanged"] = current == audit["frozen_sha256"]
            if not report["frozen_unchanged"]:
                report.update(status="failed",operational_pass=False,integrity_error="Frozen sources or inputs changed.")
        produced_after = {name:sha(name) for name in report["produced_sha256"]}
        report["produced_sha256_after"] = produced_after
        report["produced_unchanged"] = produced_after == report["produced_sha256"]
        if not report["produced_unchanged"]:
            report.update(status="failed",operational_pass=False,integrity_error="Produced audit evidence changed.")
    except Exception as error:
        report.update(status="failed",operational_pass=False,integrity_error=str(error))
    report["elapsed_s"] = time.monotonic()-started
    if report["elapsed_s"] > 600:
        report.update(status="failed",operational_pass=False,budget_error="Study exceeded 600 s including integrity checks.")
    report["scope"] = "Solver equivalence study; timings are observed costs, not a speedup benchmark. No phase alignment or output renormalization."
    report["equivalence_pass"] = report["operational_pass"]
    write_json(out/"execution.json",report)
    print(json.dumps({"status":report["status"],"report":str(out/"execution.json")}))
    return 0 if report["operational_pass"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study",type=Path,required=True)
    parser.add_argument("--out-dir",type=Path,required=True)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--private-small",action="store_true")
    modes.add_argument("--private-reproduce",action="store_true")
    parser.add_argument("--audit-manifest",type=Path)
    parser.add_argument("--audit-sha")
    parser.add_argument("--prefix",type=Path)
    parser.add_argument("--case-id",choices=CASES)
    parser.add_argument("--checkpoint",type=Path)
    parser.add_argument("--small-n",type=int,choices=(8,11))
    args = parser.parse_args()
    if not args.study.is_file() or not args.study.resolve().is_relative_to(RESULTS.resolve()):
        parser.error("--study must name the retained Stage B manifest under resultados/codex.")
    if not args.out_dir.resolve().is_relative_to(RESULTS.resolve()):
        parser.error("Output must remain under resultados/codex.")
    if args.private_small or args.private_reproduce:
        if not args.audit_manifest or not args.audit_sha or not args.prefix or not args.out_dir.is_dir():
            parser.error("Private workers require an existing audit manifest, identity, prefix, and output.")
        if args.private_reproduce and not args.case_id:
            parser.error("Reproduction worker requires a case identifier.")
        if args.private_small and not args.small_n:
            parser.error("Small-system worker requires its fixed grid identifier.")
        return private_worker(args)
    if args.out_dir.exists():
        parser.error("Output directory must be fresh; this audit never resumes or overwrites.")
    args.out_dir.mkdir(parents=True,exist_ok=False)
    return execute(args)


if __name__ == "__main__":
    raise SystemExit(main())
