"""T27 / H-C model: in-situ recalibration of a Clements mesh with splitter errors.

Model study, no hardware. A Clements mesh (agentkit.mzi convention) has
Gaussian splitter-angle errors with a shared component (wafer-level bias)
and a local component. Strategy A programs the ideal phases computed for an
error-free mesh. Strategy B ("in situ") re-optimizes every phase on the
erroneous device, using its transfer matrix as a hardware-in-the-loop
measurement (exact access), starting from the ideal phases. Strategy C
optimizes on a model whose splitter errors were characterized with error and
applies those phases to the true device. Optionally the calibrated phases are
quantized to an 8-bit DAC over 2*pi. Infidelity = 1 - |Tr(U^dagger V)| / N.

Usage (from the repository root):
  python -B experimentos/t27_calibracion_claude/run_t27.py --outdir resultados/agent/t27_calibration_20261012
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentkit.evidence import write_new_json  # noqa: E402
from agentkit.mzi import clements_decompose, coupler  # noqa: E402
from agentkit.stats import upper_tolerance_bound  # noqa: E402

PRIMARY = {"n": 8, "sigma_rad": 0.02, "correlation": 0.8}
SECONDARY = [{"n": n, "sigma_rad": s, "correlation": c}
             for n in (4, 8) for s in (0.02, 0.05) for c in (0.0, 0.8)]
REALIZATIONS = 60          # >= 59 for a distribution-free 95/95 upper bound
MAXITER = 1000
ESTIMATION_FRACTION = 0.1  # std of the splitter-error characterization, as a fraction of sigma (variant)
DAC_BITS = 8


def haar(n: int, rng) -> np.ndarray:
    q, r = np.linalg.qr(rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n)))
    return q * (np.diag(r) / abs(np.diag(r)))


class Device:
    """Clements mesh with fixed splitter errors; parameters = (theta, phi) per MZI + output phases."""

    def __init__(self, layout: dict, errors: np.ndarray):
        self.n = layout["dimension"]
        self.modes = [op["modes"][0] for op in layout["mzis"]]
        self.c1 = [coupler(float(e1)) for e1, _ in errors]
        self.c2 = [coupler(float(e2)) for _, e2 in errors]
        self.k = len(self.modes)

    def blocks(self, p):
        th, ph = p[:self.k], p[self.k:2 * self.k]
        out = []
        for j in range(self.k):
            pt = np.diag([np.exp(1j * th[j]), 1.0])
            pp = np.diag([np.exp(1j * ph[j]), 1.0])
            out.append((self.c2[j] @ pt @ self.c1[j] @ pp,
                        self.c2[j] @ np.diag([1j * np.exp(1j * th[j]), 0]) @ self.c1[j] @ pp,
                        self.c2[j] @ pt @ self.c1[j] @ np.diag([1j * np.exp(1j * ph[j]), 0])))
        return out

    def transfer(self, p) -> np.ndarray:
        t = np.eye(self.n, dtype=complex)
        for (m, _, _), row in zip(self.blocks(p), self.modes):
            t[[row, row + 1], :] = m @ t[[row, row + 1], :]
        return np.exp(1j * p[2 * self.k:])[:, None] * t

    def infidelity_and_grad(self, p, target):
        """1 - |Tr(U^H V)|/N and its exact gradient with respect to all phases."""
        n, k = self.n, self.k
        blocks = self.blocks(p)
        prefix = [np.eye(n, dtype=complex)]
        for (m, _, _), row in zip(blocks, self.modes):
            nxt = prefix[-1].copy()
            nxt[[row, row + 1], :] = m @ nxt[[row, row + 1], :]
            prefix.append(nxt)
        d = np.exp(1j * p[2 * k:])
        uh = target.conj().T
        g = np.sum(d * np.diag(prefix[-1] @ uh))
        mag = abs(g)
        if mag == 0:
            return 1.0, np.zeros_like(p)
        weight = np.conj(g) / mag
        grad = np.zeros_like(p)
        # A_j = prefix_{j} U^H D S_j, where S_j is the product of blocks after j.
        suffix = np.eye(n, dtype=complex)
        dsuffix = np.diag(d) @ suffix
        for j in range(k - 1, -1, -1):
            m, dth, dph = blocks[j]
            row = self.modes[j]
            a = prefix[j] @ uh @ dsuffix  # Tr(A E) with E embedded at (row, row+1)
            sub = a[np.ix_([row, row + 1], [row, row + 1])]
            grad[j] = -np.real(weight * np.sum(sub.T * dth)) / n
            grad[k + j] = -np.real(weight * np.sum(sub.T * dph)) / n
            emb = np.eye(n, dtype=complex)
            emb[np.ix_([row, row + 1], [row, row + 1])] = m
            dsuffix = dsuffix @ emb
        tu = np.diag(prefix[-1] @ uh)
        grad[2 * k:] = -np.real(weight * 1j * d * tu) / n
        return 1.0 - mag / n, grad


def ideal_parameters(layout: dict) -> np.ndarray:
    th = [op["theta_rad"] for op in layout["mzis"]]
    ph = [op["phi_rad"] for op in layout["mzis"]]
    return np.array([*th, *ph, *layout["output_phases_rad"]], dtype=float)


def infidelity(target, realized) -> float:
    return 1.0 - abs(np.trace(target.conj().T @ realized)) / len(target)


def run_setting(setting: dict, seed_base: int) -> dict:
    n, sigma, corr = setting["n"], setting["sigma_rad"], setting["correlation"]
    rows = []
    for r in range(REALIZATIONS):
        rng = np.random.default_rng(seed_base + 1000 * n + int(1000 * sigma) + int(10 * corr) * 7 + r * 13)
        target = haar(n, rng)
        layout = clements_decompose(target)
        shared = rng.normal(0, sigma * math.sqrt(corr))
        errors = shared + rng.normal(0, sigma * math.sqrt(1 - corr), size=(layout["n_mzis"], 2))
        device = Device(layout, errors)
        p0 = ideal_parameters(layout)
        before = infidelity(target, device.transfer(p0))
        fit = minimize(device.infidelity_and_grad, p0, args=(target,), jac=True, method="L-BFGS-B",
                       options={"maxiter": MAXITER, "gtol": 1e-12, "ftol": 1e-15})
        after = infidelity(target, device.transfer(fit.x))
        step = 2 * math.pi / 2 ** DAC_BITS
        quantized = infidelity(target, device.transfer(np.round(fit.x / step) * step))
        # Model-based variant: splitter errors are characterized with error (std ESTIMATION_FRACTION
        # x sigma), phases are optimized on that estimated model and applied to the true device.
        estimate = errors + rng.normal(0, ESTIMATION_FRACTION * sigma, size=errors.shape)
        model = Device(layout, estimate)
        fit_model = minimize(model.infidelity_and_grad, p0, args=(target,), jac=True, method="L-BFGS-B",
                             options={"maxiter": MAXITER, "gtol": 1e-12, "ftol": 1e-15})
        after_estimated = infidelity(target, device.transfer(fit_model.x))
        rows.append({"realization": r, "before": before, "after": after, "after_8bit": quantized,
                     "after_model_estimated_errors": after_estimated, "iterations": int(fit.nit),
                     "optimizer_message": str(fit.message)})
    arr = {key: np.array([row[key] for row in rows]) for key in ("before", "after", "after_8bit", "after_model_estimated_errors")}
    ratio = arr["before"] / np.maximum(arr["after"], 1e-16)
    summary = {key: {"median": float(np.median(v)), "max": float(np.max(v)),
                     "wilks_95_95_upper": upper_tolerance_bound(v, 0.95, 0.95)["bound"]}
               for key, v in arr.items()}
    return {**setting, "realizations": REALIZATIONS, "summary": summary,
            "median_improvement_factor": float(np.median(ratio)), "rows": rows}


def gradient_check() -> float:
    rng = np.random.default_rng(7)
    target = haar(5, rng)
    layout = clements_decompose(target)
    device = Device(layout, rng.normal(0, 0.03, size=(layout["n_mzis"], 2)))
    p = ideal_parameters(layout) + rng.normal(0, 0.1, size=2 * layout["n_mzis"] + 5)
    _, grad = device.infidelity_and_grad(p, target)
    numeric = np.zeros_like(p)
    for i in range(len(p)):
        e = np.zeros_like(p)
        e[i] = 1e-6
        numeric[i] = (device.infidelity_and_grad(p + e, target)[0] - device.infidelity_and_grad(p - e, target)[0]) / 2e-6
    return float(np.max(abs(grad - numeric)) / max(np.max(abs(numeric)), 1e-300))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    outdir = args.outdir if args.outdir.is_absolute() else ROOT / args.outdir
    target = outdir / "results.json"
    if target.exists():
        raise FileExistsError("Output must be new")
    outdir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    check = gradient_check()
    primary = run_setting(PRIMARY, 20261012)
    secondary = [run_setting(s, 20261013) for s in SECONDARY]
    metrics = {"gradient_check_relative_error": check,
               "wilks_95_95_after_primary": primary["summary"]["after"]["wilks_95_95_upper"],
               "median_improvement_factor_primary": primary["median_improvement_factor"]}
    write_new_json(target, {"scope": "numerical_model", "primary": primary, "secondary": secondary,
                            "settings": {"realizations": REALIZATIONS, "maxiter": MAXITER,
                                         "estimation_fraction": ESTIMATION_FRACTION, "dac_bits": DAC_BITS},
                            "elapsed_s": time.monotonic() - started, "metrics": metrics})
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
