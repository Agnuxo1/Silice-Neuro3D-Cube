"""Build the neuro-cube in Blender and export its geometry, or run the geometry round-trip check.

blender -b --factory-startup -t 1 --python build_cube.py -- --n 4 --ports 0 1 2 3 --out-blend X.blend --out-geometry geometry_N4.json
blender -b --factory-startup -t 1 --python build_cube.py -- --check --out-check check.json

The check builds meshes whose heater phases come from agentkit.mzi.clements_decompose
of Haar-random targets, exports the geometry from the Blender objects, rebuilds
the transfer from the exported properties and compares it with the target
(times the declared loss and global propagation phase).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nc_blender as ncb  # noqa: E402
import numpy as np  # noqa: E402
import neurocubo_core as nc  # noqa: E402
from agentkit import mzi as akm  # noqa: E402


def write_new(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=1)


def round_trip_check(sizes=(4, 8), targets_per_size: int = 3, seed: int = 20261013) -> dict:
    rng = np.random.default_rng(seed)
    records = []
    for n in sizes:
        for t in range(targets_per_size):
            targets = [nc.haar_unitary(n, rng) for _ in range(2)]
            decs = [akm.clements_decompose(u) for u in targets]
            design = nc.design_layout(n, 1.0, range(min(n, 4)),
                                      layer_params=[nc.params_from_decomposition(d) for d in decs])
            ncb.clear_scene()
            ncb.build(design)
            geometry = ncb.export_geometry()
            errors, agentkit_errors = [], []
            for li, layer in enumerate(geometry["layers"]):
                spec, p = nc.spec_from_geometry_layer(layer)
                transfer, _ = nc.mesh_transfer(p, spec)
                expected = spec.eta * np.exp(1j * spec.common_phase) * targets[li]
                errors.append(float(np.linalg.norm(transfer - expected, 2)))
                via_kit = spec.eta * np.exp(1j * spec.common_phase) * akm.clements_reconstruct(decs[li])
                agentkit_errors.append(float(np.linalg.norm(transfer - via_kit, 2)))
            records.append({"n": n, "target": t, "spectral_error_vs_target": errors,
                            "spectral_error_vs_clements_reconstruct": agentkit_errors,
                            "max_abs_coupler_eps": float(max(np.max(abs(nc.spec_from_geometry_layer(l)[0].eps))
                                                             for l in geometry["layers"])),
                            "geometry_sha256": geometry["sha256"]})
    worst = max(max(r["spectral_error_vs_target"] + r["spectral_error_vs_clements_reconstruct"])
                for r in records)
    return {"check": "geometry_round_trip_blender", "seed": seed, "records": records,
            "geometry_reconstruction_error_max": worst, "threshold": 1e-10, "passed": worst < 1e-10}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int)
    parser.add_argument("--ports", type=int, nargs="+")
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--out-blend", type=Path)
    parser.add_argument("--out-geometry", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out-check", type=Path)
    args = parser.parse_args(ncb.script_args())
    start = time.perf_counter()
    if args.check:
        result = round_trip_check()
        result["seconds"] = time.perf_counter() - start
        write_new(args.out_check, result)
        print("NEUROCUBO_CHECK", json.dumps({"max": result["geometry_reconstruction_error_max"],
                                             "passed": result["passed"]}))
        return
    design = nc.design_layout(args.n, args.gain, args.ports)
    ncb.clear_scene()
    ncb.build(design)
    geometry = ncb.export_geometry()
    if args.out_geometry:
        write_new(args.out_geometry, geometry)
    if args.out_blend:
        ncb.save_blend(args.out_blend)
    print("NEUROCUBO_BUILD", json.dumps({"n": args.n, "sha256": geometry["sha256"],
                                         "side_m": geometry["cube"]["side_m"],
                                         "objects": len(ncb.bpy.data.objects)}))


if __name__ == "__main__":
    main()
