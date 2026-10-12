"""Rectangular (Clements-ordered) MZI mesh synthesis with an explicit device convention.

Convention (stated, not universal): a symmetric directional coupler
B = [[cos a, i sin a], [i sin a, cos a]] with a = pi/4 + eps, and
MZI(theta, phi) = B(eps2) @ diag(exp(i theta), 1) @ B(eps1) @ diag(exp(i phi), 1),
both phase shifters on the upper arm of the pair (m, m+1). The ideal MZI is
i exp(i theta/2) [[exp(i phi) sin(theta/2), cos(theta/2)],
                  [exp(i phi) cos(theta/2), -sin(theta/2)]].
Ordering follows Clements et al., Optica 3, 1460 (2016): N(N-1)/2 MZIs in a
rectangular arrangement of depth N, then an output phase screen. Other device
conventions require their own derivation; the reconstruction check below is
the acceptance test, not the formulas.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from agentkit.evidence import write_new_json
from agentkit.numerics import finite_array


def coupler(eps: float = 0.0) -> np.ndarray:
    """Directional coupler with splitting angle pi/4 + eps."""
    a = math.pi / 4 + eps
    return np.array([[math.cos(a), 1j * math.sin(a)], [1j * math.sin(a), math.cos(a)]])


def mzi(theta: float, phi: float, eps1: float = 0.0, eps2: float = 0.0) -> np.ndarray:
    """Return the 2x2 transfer of one MZI in the stated convention."""
    return (coupler(eps2) @ np.diag([np.exp(1j * theta), 1.0]) @ coupler(eps1)
            @ np.diag([np.exp(1j * phi), 1.0]))


def _embed(block: np.ndarray, n: int, m: int) -> np.ndarray:
    full = np.eye(n, dtype=complex)
    full[m:m + 2, m:m + 2] = block
    return full


def _null_right(a: complex, b: complex) -> tuple[float, float]:
    """(theta, phi) with [a, b] @ MZI(theta, phi)^dagger having a zero first entry."""
    theta = 2 * math.atan2(abs(b), abs(a))
    phi = 0.0 if abs(a) == 0 or abs(b) == 0 else float(np.angle(-a / b))
    return theta, phi


def _null_left(a: complex, b: complex) -> tuple[float, float]:
    """(theta, phi) with MZI(theta, phi) @ [a, b]^T having a zero second entry."""
    theta = 2 * math.atan2(abs(a), abs(b))
    phi = 0.0 if abs(a) == 0 or abs(b) == 0 else float(np.angle(b / a))
    return theta, phi


def clements_decompose(unitary, tolerance: float = 1e-10) -> dict:
    """Decompose a unitary into MZIs (propagation order) and output phases."""
    u = finite_array(unitary, ndim=2).astype(complex)
    n = len(u)
    if u.shape != (n, n) or not 2 <= n <= 64:
        raise ValueError("Clements synthesis supports square matrices from 2 to 64")
    if np.linalg.norm(u.conj().T @ u - np.eye(n), 2) > tolerance:
        raise ValueError("Target is not unitary")
    work = u.copy()
    right, left = [], []
    for i in range(1, n):
        if i % 2 == 1:
            for j in range(i):
                row, col = n - 1 - j, i - 1 - j
                theta, phi = _null_right(work[row, col], work[row, col + 1])
                work = work @ _embed(mzi(theta, phi), n, col).conj().T
                right.append((col, theta, phi))
        else:
            for j in range(1, i + 1):
                row, col = n - 1 + j - i, j - 1
                theta, phi = _null_left(work[row - 1, col], work[row, col])
                work = _embed(mzi(theta, phi), n, row - 1) @ work
                left.append((row - 1, theta, phi))
    off = work - np.diag(np.diag(work))
    if np.linalg.norm(off, 2) > 50 * tolerance:
        raise RuntimeError("Nulling sequence did not produce a diagonal matrix")
    diagonal = np.diag(work).copy()
    # U = L_1^dag ... L_k^dag D R_p ... R_1 ; move each L^dag through D.
    moved = []
    for m, theta, phi in reversed(left):
        d1, d2 = diagonal[m], diagonal[m + 1]
        kappa = -np.exp(-1j * theta)
        diagonal[m], diagonal[m + 1] = kappa * np.exp(-1j * phi) * d2, kappa * d2
        moved.append((m, theta, float(np.angle(d1 / d2))))
    sequence = right + moved
    last = [0] * n
    mzis = []
    for m, theta, phi in sequence:
        layer = max(last[m], last[m + 1]) + 1
        last[m] = last[m + 1] = layer
        mzis.append({"modes": [m, m + 1], "theta_rad": float(theta % (2 * math.pi)),
                     "phi_rad": float(phi % (2 * math.pi)), "layer": layer})
    result = {"dimension": n, "convention": "MZI = B P(theta) B P(phi), B symmetric 50:50, upper-arm phases",
              "mzis": mzis, "output_phases_rad": np.angle(diagonal).tolist(),
              "n_mzis": len(mzis), "depth": max(last),
              "scope": "ideal_transfer_algebra", "geometry_validated": False}
    error = float(np.linalg.norm(clements_reconstruct(result) - u, 2))
    if error > 100 * tolerance:
        raise RuntimeError("Clements reconstruction failed")
    result["reconstruction_error"] = error
    return result


def clements_reconstruct(decomposition: dict, splitter_errors=None) -> np.ndarray:
    """Rebuild the transfer; optional per-MZI (eps1, eps2) splitter-angle errors."""
    n = decomposition["dimension"]
    count = len(decomposition["mzis"])
    errors = (np.zeros((count, 2)) if splitter_errors is None
              else finite_array(splitter_errors, ndim=2))
    if errors.shape != (count, 2):
        raise ValueError("splitter_errors must have shape (n_mzis, 2)")
    transfer = np.eye(n, dtype=complex)
    for op, (e1, e2) in zip(decomposition["mzis"], errors):
        block = mzi(op["theta_rad"], op["phi_rad"], float(e1), float(e2))
        transfer = _embed(block, n, op["modes"][0]) @ transfer
    return np.exp(1j * np.asarray(decomposition["output_phases_rad"]))[:, None] * transfer


def fidelity(target, realized) -> float:
    """Global-phase-insensitive fidelity |Tr(U^dagger V)| / N for unitaries."""
    a, b = finite_array(target, ndim=2), finite_array(realized, ndim=2)
    if a.shape != b.shape or a.shape[0] != a.shape[1]:
        raise ValueError("Matrices must be square and equal in shape")
    return float(abs(np.trace(a.conj().T @ b)) / a.shape[0])


def splitter_error_study(unitary, sigma: float, realizations: int, seed: int,
                         correlation: float = 0.0) -> dict:
    """Fidelity distribution under Gaussian splitter errors with a shared component.

    correlation in [0, 1) is the fraction of variance shared by all splitters
    (for example one wafer-level writing bias). Use measured values in T10.
    """
    if not 0 <= correlation < 1 or sigma < 0 or realizations < 1:
        raise ValueError("Invalid error-study parameters")
    decomposition = clements_decompose(unitary)
    rng = np.random.default_rng(seed)
    count = decomposition["n_mzis"]
    values = []
    for _ in range(realizations):
        shared = rng.normal(0, sigma * math.sqrt(correlation))
        local = rng.normal(0, sigma * math.sqrt(1 - correlation), size=(count, 2))
        values.append(fidelity(unitary, clements_reconstruct(decomposition, shared + local)))
    values = np.asarray(values)
    return {"sigma_rad": sigma, "correlation": correlation, "realizations": realizations,
            "seed": seed, "mean_fidelity": float(values.mean()),
            "p05_fidelity": float(np.percentile(values, 5)), "fidelities": values.tolist(),
            "note": "Uncalibrated mesh; in-situ recalibration can recover part of this loss."}


def compile_passive_clements(target) -> dict:
    """T = U diag(s) V^dagger with two rectangular meshes and amplitudes s <= 1."""
    t = finite_array(target, ndim=2).astype(complex)
    if t.shape[0] != t.shape[1]:
        raise ValueError("Passive compilation requires a square target")
    left, singular, right_h = np.linalg.svd(t)
    if singular.max() > 1 + 1e-12:
        raise ValueError("Target requires amplification; declare external gain or input scaling")
    singular = np.minimum(singular, 1.0)
    first, second = clements_decompose(right_h), clements_decompose(left)
    realized = clements_reconstruct(second) @ np.diag(singular) @ clements_reconstruct(first)
    return {"dimension": len(t), "input_mesh": first, "attenuation_amplitudes": singular.tolist(),
            "output_mesh": second, "mesh_depths": [first["depth"], second["depth"]],
            "depth": first["depth"] + second["depth"] + 1,
            "depth_note": "MZI layers of both meshes plus one attenuator column",
            "reconstruction_error": float(np.linalg.norm(realized - t, 2)),
            "scope": "ideal_passive_transfer_algebra", "geometry_validated": False}


def main() -> None:
    """Decompose a complex NPZ `target` (unitary, or contraction with --passive)."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--passive", action="store_true")
    args = parser.parse_args()
    with np.load(args.input, allow_pickle=False) as data:
        target = data["target"]
    result = compile_passive_clements(target) if args.passive else clements_decompose(target)
    write_new_json(args.out, result)
    print(json.dumps({"depth": result["depth"],
                      "reconstruction_error": result["reconstruction_error"]}))


if __name__ == "__main__":
    main()
