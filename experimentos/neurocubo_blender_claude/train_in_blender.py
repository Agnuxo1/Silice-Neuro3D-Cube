"""Train the neuro-cube heater phases inside Blender (background, one thread).

blender -b <nominal_N.blend> -t 1 --python train_in_blender.py -- --task res47 --n 8 --data-dir DATA
        --out-dir RESULTS/training --model-out RESULTS/models/model_res47_N8.json
        --blend-out D:/.../trained_res47_N8.blend --traj-dir D:/.../trajectories --expected-geometry geometry_N8.json

Per iteration (one full-batch L-BFGS-B step = one epoch over the training set) the
current phases are written into the heater objects' `phi` property and a keyframe
is inserted; the training loss is keyframed on the scene. Every start of every
readout gain is trained; selection follows agentkit.learning_v2 (minimum training
loss among converged starts) and then minimum validation cross-entropy across
gains. The test partition is never read here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nc_blender as ncb  # noqa: E402
import numpy as np  # noqa: E402
import scipy  # noqa: E402
import neurocubo_core as nc  # noqa: E402

bpy = ncb.bpy


def load_split(path: Path):
    with np.load(path, allow_pickle=False) as data:
        return data["X"].copy(), data["y"].copy()


def synthetic_split(n: int, classes: int, count: int, seed: int):
    """Random Gaussian blobs for software smoke tests only (no project data)."""
    rng = np.random.default_rng(seed)
    centres = np.random.default_rng(99).standard_normal((classes, n))
    y = rng.integers(0, classes, count)
    return centres[y] + 0.8 * rng.standard_normal((count, n)), y.astype(np.int64)


def write_new_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--smoke", action="store_true", help="synthetic data, software test only")
    parser.add_argument("--gains", type=float, nargs="+", default=[1.0, 4.0, 16.0])
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 9)))
    parser.add_argument("--maxiter", type=int, default=5000)
    parser.add_argument("--gradient-threshold", type=float, default=1e-5)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--model-out", type=Path, required=True)
    parser.add_argument("--blend-out", type=Path, required=True)
    parser.add_argument("--traj-dir", type=Path, required=True)
    parser.add_argument("--expected-geometry", type=Path, required=True)
    args = parser.parse_args(ncb.script_args())
    tag = "%s_N%d" % (args.task, args.n)
    started = time.perf_counter()

    geometry0 = ncb.export_geometry()
    expected = json.loads(args.expected_geometry.read_text(encoding="utf-8"))
    if geometry0["sha256"] != expected["sha256"]:
        raise RuntimeError("Blender objects differ from the committed nominal geometry")
    base_cfg, _ = nc.config_from_geometry(geometry0)
    if base_cfg.n != args.n:
        raise RuntimeError("Geometry size differs from --n")
    if args.smoke:
        x, y = synthetic_split(args.n, len(base_cfg.ports), 120, 1)
        xv, yv = synthetic_split(args.n, len(base_cfg.ports), 40, 2)
        data_hashes = {"synthetic": True}
    else:
        x, y = load_split(args.data_dir / args.task / ("train_N%d.npz" % args.n))
        xv, yv = load_split(args.data_dir / args.task / ("validation_N%d.npz" % args.n))
        data_hashes = {name: hashlib.sha256((args.data_dir / args.task / name).read_bytes()).hexdigest()
                       for name in ("train_N%d.npz" % args.n, "validation_N%d.npz" % args.n)}
    k_count = base_cfg.specs[0].n_mzi
    heaters = ncb.heater_objects([k_count, k_count])
    if len(heaters) != base_cfg.n_params:
        raise RuntimeError("Heater object count differs from the parameter count")
    scene = bpy.context.scene
    scene["nc_training_loss"] = 0.0
    frame = [1]
    timeline, per_gain = [], []
    args.traj_dir.mkdir(parents=True, exist_ok=True)

    for gain in args.gains:
        cfg = nc.optical_config(base_cfg.n, gain, base_cfg.ports, base_cfg.specs, base_cfg.v_pi, base_cfg.bias)
        records = []
        for seed in args.seeds:
            first = frame[0]

            def on_iteration(iteration, params, loss, gnorm):
                ncb.write_params(params, heaters)
                ncb.keyframe_params(heaters, frame[0])
                scene["nc_training_loss"] = float(loss)
                scene.keyframe_insert(data_path='["nc_training_loss"]', frame=frame[0])
                frame[0] += 1

            t0 = time.perf_counter()
            run = nc.fit_start(x, y, cfg, nc.init_params(cfg, seed), args.maxiter,
                               args.gradient_threshold, on_iteration)
            seconds = time.perf_counter() - t0
            run_name = "%s_G%g_seed%d" % (tag, gain, seed)
            np.savez_compressed(args.traj_dir / (run_name + ".npz"), phases=run.pop("trajectory"),
                                loss=run["loss_history"], gradient_inf=run["gradient_history"])
            run["loss_history_len"] = int(len(run.pop("loss_history")))
            run.pop("gradient_history")
            run.update({"seed": seed, "gain": gain, "seconds": seconds, "frames": [first, frame[0] - 1],
                        "validation_cross_entropy": nc.cross_entropy(run["parameters"], xv, yv, cfg),
                        "train_accuracy": nc.accuracy(run["parameters"], x, y, cfg),
                        "validation_accuracy": nc.accuracy(run["parameters"], xv, yv, cfg)})
            timeline.append({"run": run_name, "frames": run["frames"]})
            records.append(run)
            print("NEUROCUBO_RUN", json.dumps({k: run[k] for k in ("gain", "seed", "iterations", "converged",
                                                                    "gradient_infinity_norm", "training_loss",
                                                                    "validation_accuracy", "seconds")}))
        converged = [r for r in records if r["converged"]]
        best = min(converged or records, key=lambda r: r["training_loss"])
        per_gain.append({"gain": gain, "selected_seed": best["seed"], "selected_converged": best["converged"],
                         "converged_starts": len(converged),
                         "selected_by": ("minimum_training_loss_among_converged_starts" if converged
                                         else "minimum_training_loss_no_start_converged"),
                         "validation_cross_entropy": best["validation_cross_entropy"],
                         "validation_accuracy": best["validation_accuracy"], "starts": records})
    eligible = [g for g in per_gain if g["selected_converged"]]
    chosen = min(eligible or per_gain, key=lambda g: (g["validation_cross_entropy"], -g["validation_accuracy"]))
    final = next(r for r in chosen["starts"] if r["seed"] == chosen["selected_seed"])
    ncb.write_params(final["parameters"], heaters)
    ncb.objects_by_role("readout")[0]["gain"] = float(chosen["gain"])
    scene.frame_start, scene.frame_end = 1, max(1, frame[0] - 1)
    model = ncb.export_geometry()
    model["training"] = {"task": args.task, "n": args.n, "gain": chosen["gain"], "seed": final["seed"],
                         "converged": final["converged"], "frames": final["frames"],
                         "smoke": bool(args.smoke)}
    model["sha256"] = nc.geometry_hash(model)
    cfg_final, p_final = nc.config_from_geometry(model)
    if np.max(abs(p_final - np.asarray(final["parameters"]))) > 0:
        raise RuntimeError("Phases read back from objects differ from the trained parameters")
    write_new_json(args.model_out, model)
    with np.load(args.traj_dir / ("%s_G%g_seed%d.npz" % (tag, chosen["gain"], final["seed"]))) as t:
        selected_traj = {k: t[k].copy() for k in t.files}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out_dir / ("trajectory_selected_%s.npz" % tag),
                        phases=selected_traj["phases"].astype(np.float32), loss=selected_traj["loss"],
                        gradient_inf=selected_traj["gradient_inf"])
    ncb.save_blend(args.blend_out)
    record = {"task": args.task, "n": args.n, "scope": nc.SCOPE, "smoke": bool(args.smoke),
              "model_kind": "optical", "geometry_sha256_nominal": geometry0["sha256"],
              "model_sha256": model["sha256"], "data_sha256": data_hashes,
              "gains": args.gains, "seeds": args.seeds, "maxiter": args.maxiter,
              "gradient_threshold": args.gradient_threshold,
              "selection_rule": "per gain: minimum training loss among converged starts (learning_v2); "
                                "across gains: minimum validation cross-entropy among converged selections",
              "chosen_gain": chosen["gain"], "chosen_seed": final["seed"],
              "chosen_converged": final["converged"], "no_converged_selection": not eligible,
              "per_gain": per_gain, "timeline": timeline, "keyframes_total": frame[0] - 1,
              "test_evaluated": False, "seconds_total": time.perf_counter() - started,
              "environment": {"blender": bpy.app.version_string, "python": platform.python_version(),
                              "numpy": np.__version__, "scipy": scipy.__version__,
                              "threads": "blender -t 1; OPENBLAS/OMP/MKL_NUM_THREADS=1 set by the launcher"}}
    write_new_json(args.out_dir / ("candidates_%s.json" % tag), record)
    print("NEUROCUBO_TRAINED", json.dumps({k: record[k] for k in ("task", "n", "chosen_gain", "chosen_seed",
                                                                  "chosen_converged", "keyframes_total",
                                                                  "seconds_total")}))


if __name__ == "__main__":
    main()
