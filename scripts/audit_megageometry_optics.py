"""Small CPU analytic checks, not an RT implementation or capacity benchmark."""
import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "Docs/MEGAGEOMETRY-ANALYTIC-CONTRACT.md"
WAVELENGTH = 1550e-9
INDEX = 1.444


def triangle_hit(origin, direction, triangle):
    """Moller-Trumbore, float64, for nondegenerate interior diagnostic rays."""
    e1, e2 = triangle[1] - triangle[0], triangle[2] - triangle[0]
    cross = np.cross(direction, e2)
    det = float(np.dot(e1, cross))
    if abs(det) < 1e-24:
        raise ValueError("parallel or degenerate diagnostic")
    rel = origin - triangle[0]
    u = float(np.dot(rel, cross) / det)
    q = np.cross(rel, e1)
    v = float(np.dot(direction, q) / det)
    t = float(np.dot(e2, q) / det)
    if not (u > 0 and v > 0 and u + v < 1 and t > 0):
        raise ValueError("not an interior forward hit")
    return t, origin + t * direction


def analytical_checks():
    angle = .37
    rotation = np.array([[np.cos(angle), 0, np.sin(angle)],
                         [0, 1, 0], [-np.sin(angle), 0, np.cos(angle)]])
    transforms = [
        ("identity", np.eye(3), np.zeros(3)),
        ("rotation", rotation, np.zeros(3)),
        ("translation_10mm", np.eye(3), np.array([.01, -.004, .002])),
        ("uniform_scale", np.eye(3) * 1.001, np.zeros(3)),
        ("anisotropic", np.diag([.8, 1.2, 1.01]), np.zeros(3)),
        ("shear", np.array([[1, .2, .1], [0, 1, -.15], [0, 0, 1.02]]), np.zeros(3)),
    ]
    triangle = np.array([[0, 0, 0], [30e-6, 0, 0], [0, 30e-6, 0]])
    direction = np.array([.15, -.1, 1.])
    direction /= np.linalg.norm(direction)
    records = []
    for name, affine, translation in transforms:
        inv = np.linalg.inv(affine)
        world_triangle = triangle @ affine.T + translation
        normal = inv.T @ np.array([0., 0., 1.])
        normal /= np.linalg.norm(normal)
        direct_normal = np.cross(world_triangle[1] - world_triangle[0],
                                 world_triangle[2] - world_triangle[0])
        direct_normal /= np.linalg.norm(direct_normal)
        for x, y in [(5, 5), (10, 5), (5, 10), (9, 9)]:
            target = np.array([x * 1e-6, y * 1e-6, 0])
            origin = target - 4e-6 * direction
            world_origin = affine @ origin + translation
            world_direction = affine @ direction
            world_direction /= np.linalg.norm(world_direction)
            direct_t, direct_hit = triangle_hit(world_origin, world_direction, world_triangle)
            local_origin = inv @ (world_origin - translation)
            # NO normalization: otherwise local t is not the world ray parameter.
            local_direction = inv @ world_direction
            reference_t, reference_hit = triangle_hit(local_origin, local_direction, triangle)
            restored_hit = affine @ reference_hit + translation
            world_length = float(np.linalg.norm(restored_hit - world_origin))
            rest_length = float(np.linalg.norm(reference_hit - local_origin))
            phase_error = 2 * np.pi * INDEX * abs(world_length - rest_length) / WAVELENGTH
            row = dict(transform=name, target_um=[x, y],
                       hit_error_m=float(np.linalg.norm(direct_hit - restored_hit)),
                       t_error_m=abs(direct_t - reference_t),
                       normal_error=float(np.linalg.norm(normal - direct_normal)),
                       world_length_m=world_length, rest_length_m=rest_length,
                       wrong_rest_length_phase_error_rad=float(phase_error))
            row["pass"] = (row["hit_error_m"] <= 1e-12 and row["t_error_m"] <= 1e-12
                           and row["normal_error"] <= 1e-12)
            records.append(row)
    phase_rows = []
    for delta_nm in [0, 1, 10, 200]:
        phase = 2 * np.pi * INDEX * delta_nm * 1e-9 / WAVELENGTH
        intensity = abs((1 - np.exp(1j * phase)) / 2) ** 2
        truth = np.sin(phase / 2) ** 2
        phase_rows.append(dict(delta_length_nm=delta_nm, phase_rad=float(phase),
                               dark_port_power=float(intensity),
                               formula_error=float(abs(intensity - truth)),
                               **{"pass": bool(abs(intensity - truth) <= 1e-12)}))
    opl_budget = WAVELENGTH * .01 / (2 * np.pi)
    length_budget = opl_budget / INDEX
    phase_budget_error = abs(2 * np.pi * INDEX * length_budget / WAVELENGTH - .01)
    alias_detected = any(r["transform"] == "uniform_scale" and
                         r["wrong_rest_length_phase_error_rad"] > .01 for r in records)
    spacing = float(np.spacing(np.float32(.01)))
    return dict(affine_hits=records, two_arm_interference=phase_rows,
                budget=dict(phase_rad=.01, wavelength_vacuum_nm=1550, index=INDEX,
                            optical_path_nm=float(opl_budget * 1e9),
                            physical_length_nm=float(length_budget * 1e9),
                            phase_budget_error=float(phase_budget_error),
                            float32_10mm_spacing_nm=spacing * 1e9,
                            float32_spacing_phase_rad=2*np.pi*INDEX*spacing/WAVELENGTH),
                illustrative_memory_GiB={"500M_16byte_states":500e6*16/2**30,
                                         "500M_32byte_states":500e6*32/2**30,
                                         "500M_8edges_16byte_each":500e6*8*16/2**30},
                illustrative_image_rays=dict(pixels=1920*1080,
                                             max_two_initial_rays_per_frame=1920*1080*2,
                                             at_60fps=1920*1080*2*60,
                                             measured=False),
                gates=dict(affine_24_pass=all(r["pass"] for r in records),
                           interference_4_pass=all(r["pass"] for r in phase_rows),
                           phase_budget_pass=bool(phase_budget_error <= 1e-12),
                           wrong_reference_length_detected=alias_detected))


def capabilities(deadline):
    retained = {}
    for name, command in [
        ("nvidia", ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]),
        ("vulkan", ["vulkaninfo"]),
    ]:
        try:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                retained[name] = dict(error_type="DeadlineExpired", metadata_only=True)
                continue
            result = subprocess.run(command, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=min(20, remaining))
            row = dict(returncode=result.returncode, metadata_only=True)
            if name == "nvidia":
                row["devices"] = result.stdout.strip().splitlines()
            else:
                row["extensions"] = {n: int(v) for n, v in re.findall(
                    r"(VK_(?:NV_cluster_acceleration_structure|NV_partitioned_acceleration_structure|"
                    r"KHR_ray_tracing_pipeline|KHR_acceleration_structure))\s+: extension revision (\d+)",
                    result.stdout)}
            # Do not retain unrelated overlay paths or raw local diagnostics.
            row["stderr_present"] = bool(result.stderr.strip())
            retained[name] = row
        except (OSError, subprocess.TimeoutExpired) as exc:
            retained[name] = dict(error_type=type(exc).__name__, metadata_only=True)
    return retained


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    target = args.out.resolve()
    if not target.is_relative_to(ROOT / "resultados/codex") or target.exists():
        parser.error("new output under resultados/codex required")
    started = time.monotonic()
    checks = analytical_checks()
    metadata = capabilities(started + 28)
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                  scope="CPU analytical diagnostics + read-only driver metadata; NO GPU workload",
                  contract_sha256=hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  checks=checks, capabilities=metadata, elapsed_s=time.monotonic()-started)
    report["operational_pass"] = report["elapsed_s"] < 30
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    ok = all(checks["gates"].values()) and report["operational_pass"]
    print(json.dumps(dict(out=str(target), gates=checks["gates"], elapsed_s=report["elapsed_s"],
                          capabilities=metadata, passed=ok), ensure_ascii=False))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
