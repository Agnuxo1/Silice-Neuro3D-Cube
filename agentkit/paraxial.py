"""Independent bounded FFT split-step reference with resumable trajectories.

All distances are SI metres. The equation is a scalar, monochromatic,
weak-index paraxial model with periodic transverse boundaries. A sponge
is numerical absorption; it is not measured material loss or a PML proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import numpy as np

from agentkit.checkpoint import load_latest, save_checkpoint
from agentkit.evidence import canonical, sha256_file, write_new_json
from agentkit.numerics import phase_metrics


def grid(points: int, width_m: float):
    """Construct a centered periodic square grid with explicit spacing."""
    if type(points) is not int or not 16 <= points <= 512:
        raise ValueError("Bounded grid requires 16 through 512 points per axis")
    if not math.isfinite(width_m) or width_m <= 0:
        raise ValueError("Grid width must be positive")
    dx = width_m / points
    axis = (np.arange(points) - points // 2) * dx
    return np.meshgrid(axis, axis, indexing="xy"), dx


def disk_area_weights(points: int, width_m: float, radius_m: float,
                      subdivisions: int = 8) -> np.ndarray:
    """Compute a subpixel circle-area indicator; it is not an exact geometry bound."""
    if type(subdivisions) is not int or not 1 <= subdivisions <= 32:
        raise ValueError("Subpixel quadrature requires 1 through 32 subdivisions")
    (x, y), dx = grid(points, width_m)
    if not math.isfinite(radius_m) or not 0 < radius_m < width_m / 2:
        raise ValueError("Circle radius must fit inside the domain")
    weights = np.zeros_like(x)
    offsets = ((np.arange(subdivisions) + 0.5) / subdivisions - 0.5) * dx
    for ox in offsets:
        for oy in offsets:
            weights += ((x + ox)**2 + (y + oy)**2 <= radius_m**2)
    return weights * dx**2 / subdivisions**2


def split_step(field, profile, width_m: float, wavelength_m: float,
               n_reference: float, dz_m: float, sponge_rate=None) -> np.ndarray:
    """Execute one symmetric split step with nonnegative optional damping."""
    u, dn = np.asarray(field, dtype=np.complex128), np.asarray(profile)
    if u.ndim != 2 or u.shape[0] != u.shape[1] or dn.shape != u.shape:
        raise ValueError("Field and profile must be matching square arrays")
    (_, _), dx = grid(len(u), width_m)
    values = (wavelength_m, n_reference, dz_m)
    if not all(math.isfinite(v) and v > 0 for v in values):
        raise ValueError("Wavelength, reference index and step must be positive")
    if np.iscomplexobj(dn) or not np.all(np.isfinite(dn)) or not np.all(np.isfinite(u)):
        raise ValueError("Profile must be real and the field must be finite")
    if np.max(abs(dn)) > 0.01 or np.min(n_reference + dn) <= 0:
        raise ValueError("Profile is outside the declared weak-index regime")
    sigma = np.zeros_like(dn, dtype=float) if sponge_rate is None else np.asarray(sponge_rate)
    if sigma.shape != u.shape or np.iscomplexobj(sigma) or not np.all(np.isfinite(sigma)) or sigma.min() < 0:
        raise ValueError("Sponge rates must be finite, real and nonnegative")
    k0 = 2 * math.pi / wavelength_m
    freq = 2 * math.pi * np.fft.fftfreq(len(u), d=dx)
    kx, ky = np.meshgrid(freq, freq, indexing="xy")
    half = np.exp((1j * k0 * dn - sigma) * dz_m / 2)
    kernel = np.exp(-1j * (kx*kx + ky*ky) * dz_m / (2 * k0 * n_reference))
    return half * np.fft.ifft2(np.fft.fft2(half * u) * kernel)


def run_resumable(input_path: Path, config: dict, directory: Path,
                  chunk_steps: int = 100, max_seconds: float = 40.0) -> dict:
    """Resume only the exact frozen input/configuration/source identity.

    A partial return is an operational status. It does not pass any optical
    acceptance criterion and does not extend an external resource window.
    """
    if type(chunk_steps) is not int or chunk_steps < 1 or not math.isfinite(max_seconds) or max_seconds <= 0:
        raise ValueError("Chunk and invocation limits must be positive")
    required = ("width_m", "wavelength_m", "n_reference", "length_m", "steps")
    if any(key not in config for key in required):
        raise ValueError("Missing simulation parameter")
    steps = config["steps"]
    if type(steps) is not int or not 1 <= steps <= 10000000:
        raise ValueError("Step count must be a positive bounded integer")
    if not math.isfinite(config["length_m"]) or config["length_m"] <= 0:
        raise ValueError("Length must be positive")
    identity = {"config": config, "input_sha256": sha256_file(input_path),
                "numpy_version": np.__version__,
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "source_sha256": sha256_file(Path(__file__)),
                "checkpoint_source_sha256": sha256_file(Path(__file__).with_name("checkpoint.py")),
                "evidence_source_sha256": sha256_file(Path(__file__).with_name("evidence.py"))}
    experiment_hash = hashlib.sha256(canonical(identity)).hexdigest()
    with np.load(input_path, allow_pickle=False) as source:
        field = source["field"].astype(np.complex128, copy=True)
        profile = source["delta_n"].copy()
        sponge = source["sponge_rate"].copy() if "sponge_rate" in source else np.zeros_like(profile)
    # Validate all shapes and scalar parameters before publishing the first state.
    split_step(field, profile, config["width_m"], config["wavelength_m"],
               config["n_reference"], config["length_m"] / steps, sponge)
    retained = load_latest(directory, experiment_hash, steps)
    if retained is None:
        marker = save_checkpoint(directory, field, 0, steps, experiment_hash, None)
        step, previous_hash = 0, sha256_file(marker)
    else:
        restored, step, previous_hash = retained
        if restored.shape != field.shape:
            raise ValueError("Retained state shape differs from the frozen input")
        field = restored
    start = time.monotonic()
    completed_at_entry = step
    while step < steps and time.monotonic() - start < max_seconds:
        end = min(steps, step + chunk_steps)
        while step < end:
            field = split_step(field, profile, config["width_m"], config["wavelength_m"],
                               config["n_reference"], config["length_m"] / steps, sponge)
            step += 1
        marker = save_checkpoint(directory, field, step, steps, experiment_hash, previous_hash)
        previous_hash = sha256_file(marker)
    return {"status": "completed" if step == steps else "partial",
            "steps_completed": step, "steps_at_entry": completed_at_entry,
            "total_steps": steps, "experiment_hash": experiment_hash,
            "invocation_seconds": time.monotonic() - start,
            "note": "Chunk-level cooperative limit; use the supervisor for a hard deadline."}


def compare_fields(first: Path, second: Path, width_m: float) -> dict:
    """Compare matching final arrays without phase fitting or rescaling."""
    with np.load(first, allow_pickle=False) as f:
        u = f["state"] if "state" in f else f["field"]
    with np.load(second, allow_pickle=False) as f:
        v = f["state"] if "state" in f else f["field"]
    if u.shape != v.shape or u.ndim != 2 or u.shape[0] != u.shape[1]:
        raise ValueError("Comparison requires the same physical sampling grid")
    (_, _), dx = grid(len(u), width_m)
    return phase_metrics(u.ravel(), v.ravel(), np.full(u.size, dx*dx))


def main() -> None:
    """Run an explicit frozen NPZ/configuration pair or compare retained fields."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--input", type=Path, required=True)
    run.add_argument("--config", type=Path, required=True)
    run.add_argument("--directory", type=Path, required=True)
    run.add_argument("--chunk-steps", type=int, default=100)
    run.add_argument("--max-seconds", type=float, default=40)
    run.add_argument("--receipt", type=Path, required=True)
    compare = commands.add_parser("compare")
    compare.add_argument("--first", type=Path, required=True)
    compare.add_argument("--second", type=Path, required=True)
    compare.add_argument("--width-m", type=float, required=True)
    compare.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "run":
        if args.receipt.exists():
            raise FileExistsError("Invocation receipt must use a new path")
        config = json.loads(args.config.read_text(encoding="utf-8"))
        result = run_resumable(args.input, config, args.directory,
                               args.chunk_steps, args.max_seconds)
        write_new_json(args.receipt, result)
    else:
        result = compare_fields(args.first, args.second, args.width_m)
        write_new_json(args.out, result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
