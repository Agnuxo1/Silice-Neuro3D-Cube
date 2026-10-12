"""Exact triangular unitary synthesis and passive SVD transfer compilation.

This produces mathematical optical components. Converting them to laser
paths requires an independently calibrated physical component library.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from agentkit.evidence import write_new_json
from agentkit.numerics import finite_array


def complex_pairs(matrix) -> list:
    """Encode complex matrices as portable real/imaginary pairs."""
    a = finite_array(matrix)
    return np.stack([a.real, a.imag], axis=-1).tolist()


def from_pairs(value) -> np.ndarray:
    """Decode the explicit last-axis real/imaginary representation."""
    a = finite_array(value)
    if a.shape[-1] != 2:
        raise ValueError("Complex representation must end in two coordinates")
    return a[..., 0] + 1j * a[..., 1]


def decompose_unitary(unitary, tolerance: float = 1e-10) -> dict:
    """Eliminate lower entries with complex Givens rotations and retain all phases."""
    u = finite_array(unitary, ndim=2).astype(complex)
    n = len(u)
    if u.shape != (n, n) or not 1 <= n <= 64:
        raise ValueError("Unitary compiler supports square matrices up to 64")
    if np.linalg.norm(u.conj().T @ u - np.eye(n), 2) > tolerance:
        raise ValueError("Target is not unitary")
    current = u.copy()
    eliminations = []
    for column in range(n - 1):
        for bottom in range(n - 1, column, -1):
            top = bottom - 1
            a, b = current[top, column], current[bottom, column]
            radius = np.hypot(abs(a), abs(b))
            if radius <= np.finfo(float).tiny:
                continue
            rotation = np.array([[np.conj(a)/radius, np.conj(b)/radius],
                                 [-b/radius, a/radius]], dtype=complex)
            current[[top, bottom], :] = rotation @ current[[top, bottom], :]
            eliminations.append((top, bottom, rotation))
    off_diagonal = current - np.diag(np.diag(current))
    if np.linalg.norm(off_diagonal, 2) > 20 * tolerance:
        raise RuntimeError("Triangular unitary reduction did not become diagonal")
    diagonal = np.diag(current)
    operations = [{"kind": "phase", "phases_rad": np.angle(diagonal).tolist()}]
    for top, bottom, rotation in reversed(eliminations):
        block = rotation.conj().T
        operations.append({"kind": "two_mode_unitary", "ports": [top, bottom],
                           "matrix_pairs": complex_pairs(block),
                           "mixing_angle_rad": float(np.arctan2(abs(block[0, 1]), abs(block[0, 0])))})
    compiled = {"dimension": n, "operations": operations,
                "geometry_validated": False, "scope": "ideal_transfer_algebra"}
    reconstructed = reconstruct(compiled)
    error = float(np.linalg.norm(reconstructed - u, 2))
    if error > 50 * tolerance:
        raise RuntimeError("Compiled coherent transfer failed reconstruction")
    compiled["reconstruction_error"] = error
    return compiled


def reconstruct(compiled: dict) -> np.ndarray:
    """Apply the recorded operations in propagation order."""
    n = compiled["dimension"]
    transfer = np.eye(n, dtype=complex)
    for operation in compiled["operations"]:
        kind = operation["kind"]
        if kind == "phase":
            transfer = np.exp(1j * np.asarray(operation["phases_rad"]))[:, None] * transfer
        elif kind == "attenuation":
            values = finite_array(operation["amplitudes"], ndim=1)
            if values.shape != (n,) or np.min(values) < 0 or np.max(values) > 1 + 1e-12:
                raise ValueError("Passive attenuation amplitudes must lie in [0,1]")
            transfer = values[:, None] * transfer
        elif kind == "two_mode_unitary":
            ports = operation["ports"]
            block = from_pairs(operation["matrix_pairs"])
            transfer[ports, :] = block @ transfer[ports, :]
        else:
            raise ValueError("Unknown optical operation")
    return transfer


def compile_passive(target) -> dict:
    """Compile a contraction as right unitary, amplitudes and left unitary."""
    t = finite_array(target, ndim=2).astype(complex)
    if t.shape[0] != t.shape[1] or len(t) > 64:
        raise ValueError("Passive compilation requires a square target up to 64")
    left, singular, right_h = np.linalg.svd(t)
    if singular.max() > 1 + 1e-12:
        raise ValueError("Target requires amplification; declare external gain or input scaling")
    # Clip only rounding at the passive threshold, never a substantive gain.
    singular = np.minimum(singular, 1.0)
    right = decompose_unitary(right_h)
    left_compiled = decompose_unitary(left)
    compiled = {"dimension": len(t), "scope": "ideal_passive_transfer_algebra",
                "geometry_validated": False,
                "operations": [*right["operations"],
                               {"kind": "attenuation", "amplitudes": singular.tolist()},
                               *left_compiled["operations"]]}
    compiled["reconstruction_error"] = float(np.linalg.norm(reconstruct(compiled) - t, 2))
    return compiled


def fixed_coupling_lengths(compiled: dict, kappa_per_m: float) -> list[dict]:
    """Map mixing magnitudes to lengths only; phase/layout calibration remains explicit."""
    if not math.isfinite(kappa_per_m) or kappa_per_m <= 0:
        raise ValueError("Calibrated coupling coefficient must be positive")
    return [{"ports": op["ports"], "mixing_angle_rad": op["mixing_angle_rad"],
             "length_m": op["mixing_angle_rad"] / kappa_per_m,
             "phase_mapping_validated": False}
            for op in compiled["operations"] if op["kind"] == "two_mode_unitary"]


def main() -> None:
    """Compile a supplied complex NPZ target and retain an exclusive report."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--kappa-per-m", type=float)
    args = parser.parse_args()
    with np.load(args.input, allow_pickle=False) as data:
        compiled = compile_passive(data["target"])
    if args.kappa_per_m is not None:
        compiled["mixing_lengths"] = fixed_coupling_lengths(compiled, args.kappa_per_m)
    write_new_json(args.out, compiled)
    print(json.dumps({"error": compiled["reconstruction_error"],
                      "geometry_validated": compiled["geometry_validated"]}))


if __name__ == "__main__":
    main()
