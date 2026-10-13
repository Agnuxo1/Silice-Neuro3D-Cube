"""Evaluate a frozen neuro-cube inside Blender: phases read from the objects, test features only.

blender -b trained_<task>_N<n>.blend -t 1 --python blender_eval.py -- --task res47 --n 8 --data-dir DATA
        --model RESULTS/models/model_res47_N8.json --out RESULTS/blender_eval/outputs_res47_N8.npz

Writes logits, all output intensities and predictions for the unlabeled test
features, plus timing of the simulated inference on one CPU thread (simulation
cost, not optical latency). Labels are not available here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nc_blender as ncb  # noqa: E402
import numpy as np  # noqa: E402
import neurocubo_core as nc  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=200)
    args = parser.parse_args(ncb.script_args())
    if args.out.exists():
        raise FileExistsError("Output must be new")
    geometry = ncb.export_geometry()
    cfg, params = nc.config_from_geometry(geometry)
    model = json.loads(args.model.read_text(encoding="utf-8"))
    cfg_m, params_m = nc.config_from_geometry(model)
    if not np.array_equal(params, params_m) or cfg.gain != cfg_m.gain or cfg.ports != cfg_m.ports:
        raise RuntimeError("Blender objects differ from the frozen model record")
    path = args.data_dir / args.task / ("test_X_N%d.npz" % args.n)
    with np.load(path, allow_pickle=False) as data:
        x = data["X"].copy()
    logits, intensity, _ = nc.forward(params, x, cfg)
    single = []
    for r in range(args.repeats):
        row = x[r % len(x)][None, :]
        t0 = time.perf_counter()
        nc.forward(params, row, cfg)
        single.append(time.perf_counter() - t0)
    t0 = time.perf_counter()
    for _ in range(20):
        nc.forward(params, x, cfg)
    batch = (time.perf_counter() - t0) / 20
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("xb") as handle:
        np.savez(handle, logits=logits, intensity=intensity, predictions=logits.argmax(axis=1))
    info = {"task": args.task, "n": args.n, "environment": "Blender " + ncb.bpy.app.version_string,
            "numpy": np.__version__, "model_sha256": model["sha256"],
            "geometry_from_objects_sha256": geometry["sha256"],
            "test_features_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "n_test": int(len(x)), "single_sample_seconds_median": float(np.median(single)),
            "single_sample_seconds_p90": float(np.percentile(single, 90)),
            "batch_seconds_per_sample": batch / len(x),
            "note": "CPU simulation time on one thread; not optical latency"}
    with args.out.with_suffix(".json").open("x", encoding="utf-8") as handle:
        json.dump(info, handle, indent=1)
    print("NEUROCUBO_EVAL", json.dumps({"task": args.task, "n": args.n,
                                        "median_us": 1e6 * info["single_sample_seconds_median"]}))


if __name__ == "__main__":
    main()
