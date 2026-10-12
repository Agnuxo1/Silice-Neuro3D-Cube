"""T25: 3D versus planar mesh scaling (depth, crossings, path loss, error accumulation).

Model study, no measurement. Four parts, all deterministic with fixed seeds:
1. Depth of the triangular (agentkit.mesh) and rectangular Clements (agentkit.mzi)
   syntheses, measured on random unitaries for N = 3..16, against the
   dimension-count lower bound N - 1 (guide v2 section 39).
2. Crossings of an explicit planar layout of the radix-2 butterfly
   (FFT-type) network: before each stage of stride d, adjacent swaps bring
   partners together and the inverse swaps restore the order; every swap is
   one waveguide crossing. Total and worst-path counts are computed exactly
   and checked against a closed form and a brute-force path enumeration.
   This layout is an upper-bound construction; minimality is not claimed.
3. Path-loss comparison for the unitary DFT realized as (A) planar Clements
   (no crossings, depth N), (B) planar butterfly (depth log2 N, crossings),
   (C) 3D butterfly (depth log2 N, no crossings, a vertical-transition cost
   per stage). Losses are parameter grids, not measured values.
4. Error accumulation: fidelity of the DFT under Gaussian splitter-angle
   errors (shared plus local) for Clements versus butterfly realizations.

Usage (from the repository root):
  python -B experimentos/t25_escalado_claude/run_t25.py --outdir resultados/agent/t25_scaling_20261012
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentkit.evidence import write_new_json  # noqa: E402
from agentkit.mesh import decompose_unitary, reconstruct  # noqa: E402
from agentkit.mzi import clements_decompose, clements_reconstruct, coupler, fidelity  # noqa: E402

U_DB = 0.2          # planning value: repeatability of an insertion-loss difference (ASSUMPTION)
SIGMA_RAD = 0.02    # splitter-angle error, model value used in guide v2 section 43
REALIZATIONS = 200
CORRELATIONS = (0.0, 0.8)


def random_unitary(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    q, r = np.linalg.qr(rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n)))
    return q * (np.diag(r) / abs(np.diag(r)))


def triangular_depth(compiled: dict, n: int) -> int:
    last = [0] * n
    for op in compiled["operations"]:
        if op["kind"] == "two_mode_unitary":
            a, b = op["ports"]
            last[a] = last[b] = max(last[a], last[b]) + 1
    return max(last)


def part_depth() -> dict:
    rows, max_error = [], 0.0
    for n in range(3, 17):
        u = random_unitary(n, 1000 + n)
        tri = decompose_unitary(u)
        cle = clements_decompose(u)
        err_t = float(np.linalg.norm(reconstruct(tri) - u, 2))
        err_c = float(cle["reconstruction_error"])
        max_error = max(max_error, err_t, err_c)
        rows.append({"n": n, "lower_bound": n - 1, "triangular_depth": triangular_depth(tri, n),
                     "clements_depth": cle["depth"], "n_mzis": cle["n_mzis"],
                     "triangular_error": err_t, "clements_error": err_c})
    return {"rows": rows, "max_reconstruction_error": max_error,
            "clements_depth_equals_n": all(r["clements_depth"] == r["n"] for r in rows),
            "triangular_depth_equals_2n_minus_3": all(r["triangular_depth"] == 2 * r["n"] - 3 for r in rows),
            "depth_lower_bound_respected": all(min(r["clements_depth"], r["triangular_depth"]) >= r["lower_bound"]
                                               for r in rows)}


def stage_swaps(n: int, d: int) -> np.ndarray:
    """Adjacent swaps per guide label to interleave partners (i, i + d) in each block of 2d."""
    order = list(range(n))
    target = {}
    for start in range(0, n, 2 * d):
        for j in range(d):
            target[start + j] = start + 2 * j
            target[start + d + j] = start + 2 * j + 1
    swaps = np.zeros(n, dtype=int)
    changed = True
    while changed:  # bubble sort by target position; each adjacent exchange is one crossing
        changed = False
        for p in range(n - 1):
            a, b = order[p], order[p + 1]
            if target[a] > target[b]:
                order[p], order[p + 1] = b, a
                swaps[a] += 1
                swaps[b] += 1
                changed = True
    return swaps


def worst_path(n: int, per_stage: list[np.ndarray]) -> int:
    """Max crossings on a light path; at each coupler the path may switch to the partner."""
    best = np.zeros(n, dtype=int)
    for s, swaps in enumerate(per_stage):
        d = 2 ** s
        new = np.full(n, -1, dtype=int)
        for label in range(n):
            partner = label ^ d
            # enter at `label` (forward swaps), leave at `out` (inverse swaps of `out`)
            for out in (label, partner):
                new[out] = max(new[out], best[label] + swaps[label] + swaps[out])
        best = new
    return int(best.max())


def worst_path_bruteforce(n: int, per_stage: list[np.ndarray]) -> int:
    k = int(math.log2(n))
    top = 0
    for start in range(n):
        for switches in itertools.product((0, 1), repeat=k):
            label, total = start, 0
            for s, flip in enumerate(switches):
                out = label ^ (2 ** s) if flip else label
                total += per_stage[s][label] + per_stage[s][out]
                label = out
            top = max(top, total)
    return top


def part_crossings() -> dict:
    rows, closed_ok, brute_ok = [], True, True
    for k in range(2, 9):
        n = 2 ** k
        per_stage = [stage_swaps(n, 2 ** s) for s in range(k)]
        total = int(sum(int(s.sum()) // 2 for s in per_stage)) * 2  # forward plus inverse swaps
        closed = n * (n - 1 - k) // 2
        closed_ok &= total == closed
        worst = worst_path(n, per_stage)
        brute = worst_path_bruteforce(n, per_stage) if n <= 32 else None
        if brute is not None:
            brute_ok &= brute == worst
        rows.append({"n": n, "stages": k, "couplers": n * k // 2, "crossings_total": total,
                     "crossings_closed_form": closed, "worst_path_crossings": worst,
                     "worst_path_bruteforce": brute,
                     "breakeven_crossing_loss_db": 2 * U_DB / worst if worst else None})
    return {"layout": "adjacent-swap interleave before each stage and inverse swaps after it",
            "rows": rows, "crossing_total_matches_closed_form": bool(closed_ok),
            "worst_path_dp_matches_bruteforce": bool(brute_ok),
            "closed_form": "total crossings = N (N - 1 - log2 N) / 2",
            "breakeven_definition": "crossing loss at which the worst-path difference equals 2 U, U = %.2f dB (planning ASSUMPTION)" % U_DB}


def dft(n: int) -> np.ndarray:
    idx = np.arange(n)
    return np.exp(-2j * np.pi * np.outer(idx, idx) / n) / math.sqrt(n)


def butterfly_dft(n: int, eps: np.ndarray | None = None) -> np.ndarray:
    """Radix-2 DIT FFT as coupler stages: H = P B P with P = diag(1, -i), B a 50:50 coupler.

    eps[s, b] is the splitter-angle error of butterfly b in stage s (radians).
    Input bit reversal is a fixed relabeling of input ports (no device).
    """
    k = int(math.log2(n))
    rev = [int(format(i, "0%db" % k)[::-1], 2) for i in range(n)]
    matrix = np.eye(n, dtype=complex)[rev]
    p = np.diag([1.0, -1j])
    for s in range(k):
        half = 2 ** s
        stage = np.zeros((n, n), dtype=complex)
        b = 0
        for start in range(0, n, 2 * half):
            for j in range(half):
                top, bottom = start + j, start + j + half
                w = np.exp(-2j * np.pi * j / (2 * half))
                e = 0.0 if eps is None else float(eps[s, b])
                block = p @ coupler(e) @ p @ np.diag([1.0, w])
                stage[np.ix_([top, bottom], [top, bottom])] = block
                b += 1
        matrix = stage @ matrix
    return matrix


def part_errors() -> dict:
    rows = []
    for n in (4, 8, 16):
        target = dft(n)
        cle = clements_decompose(target)
        k = int(math.log2(n))
        for corr in CORRELATIONS:
            rng = np.random.default_rng(20261012 + n + int(100 * corr))
            fc, fb = [], []
            for _ in range(REALIZATIONS):
                shared = rng.normal(0, SIGMA_RAD * math.sqrt(corr))
                local_c = rng.normal(0, SIGMA_RAD * math.sqrt(1 - corr), size=(cle["n_mzis"], 2))
                fc.append(fidelity(target, clements_reconstruct(cle, shared + local_c)))
                local_b = rng.normal(0, SIGMA_RAD * math.sqrt(1 - corr), size=(k, n // 2))
                fb.append(fidelity(target, butterfly_dft(n, shared + local_b)))
            rows.append({"n": n, "correlation": corr, "sigma_rad": SIGMA_RAD,
                         "realizations": REALIZATIONS,
                         "clements_couplers": 2 * cle["n_mzis"], "butterfly_couplers": k * n // 2,
                         "clements_mean_fidelity": float(np.mean(fc)),
                         "clements_p05_fidelity": float(np.percentile(fc, 5)),
                         "butterfly_mean_fidelity": float(np.mean(fb)),
                         "butterfly_p05_fidelity": float(np.percentile(fb, 5))})
    return {"rows": rows, "fidelity": "|Tr(U^dagger V)| / N (global phase insensitive)",
            "note": "Uncalibrated; same error model and seeds per (N, correlation) for both architectures."}


def part_path_loss(crossings: dict) -> dict:
    stage_grid = (0.05, 0.1, 0.2, 0.5)      # dB per MZI or butterfly stage (grid, not measured)
    cross_grid = (0.01, 0.02, 0.05, 0.1, 0.2, 0.5)  # dB per crossing (grid, not measured)
    vertical_grid = (0.0, 0.05, 0.1)       # dB per stage for a 3D vertical transition (grid)
    worst = {r["n"]: r["worst_path_crossings"] for r in crossings["rows"]}
    rows = []
    for n in (4, 8, 16, 32, 64):
        k = int(math.log2(n))
        for a, x, v in itertools.product(stage_grid, cross_grid, vertical_grid):
            clements = n * a
            planar_bfly = k * a + worst[n] * x
            bfly3d = k * (a + v)
            rows.append({"n": n, "stage_loss_db": a, "crossing_loss_db": x, "vertical_loss_db": v,
                         "clements_planar_db": clements, "butterfly_planar_db": planar_bfly,
                         "butterfly_3d_db": bfly3d,
                         "gain_3d_vs_planar_butterfly_db": planar_bfly - bfly3d,
                         "gain_3d_vs_planar_clements_db": clements - bfly3d})
    return {"rows": rows, "model": "worst-path insertion loss = stages x stage loss + crossings x crossing loss (+ stages x vertical loss in 3D); crosstalk not modeled"}


def figure(outdir: Path, depth: dict, crossings: dict, errors: dict) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    paths = [outdir / "fig_t25_scaling.png", outdir / "fig_t25_scaling.pdf"]
    if any(p.exists() for p in paths):
        raise FileExistsError("Figure paths must be new")
    with plt.rc_context({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "savefig.facecolor": "white"}):
        fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4), layout="constrained")
        n = [r["n"] for r in depth["rows"]]
        axes[0].plot(n, [r["triangular_depth"] for r in depth["rows"]], "o-", color="#B5651D", label="Triangular (2N-3)")
        axes[0].plot(n, [r["clements_depth"] for r in depth["rows"]], "s-", color="#146C94", label="Clements (N)")
        axes[0].plot(n, [r["lower_bound"] for r in depth["rows"]], "--", color="0.4", label="Lower bound N-1")
        axes[0].set_xlabel("Modes N")
        axes[0].set_ylabel("Mesh depth (MZI layers)")
        axes[0].set_title("(a) Universal meshes")
        axes[0].legend(frameon=False)
        nc = [r["n"] for r in crossings["rows"]]
        axes[1].loglog(nc, [r["worst_path_crossings"] for r in crossings["rows"]], "o-", color="#7A3E9D", label="Worst path")
        axes[1].loglog(nc, [r["crossings_total"] for r in crossings["rows"]], "s-", color="0.3", label="Total")
        axes[1].set_xlabel("Modes N")
        axes[1].set_ylabel("Waveguide crossings")
        axes[1].set_title("(b) Planar butterfly layout")
        axes[1].legend(frameon=False)
        for corr, style in zip(CORRELATIONS, ("-", "--")):
            rows = [r for r in errors["rows"] if r["correlation"] == corr]
            ne = [r["n"] for r in rows]
            axes[2].plot(ne, [1 - r["clements_p05_fidelity"] for r in rows], "s" + style, color="#146C94",
                         label="Clements, corr %.1f" % corr)
            axes[2].plot(ne, [1 - r["butterfly_p05_fidelity"] for r in rows], "o" + style, color="#C0392B",
                         label="Butterfly, corr %.1f" % corr)
        axes[2].set_yscale("log")
        axes[2].set_xlabel("Modes N (DFT)")
        axes[2].set_ylabel("1 - fidelity, 5th percentile")
        axes[2].set_title("(c) Splitter errors, sigma 0.02 rad")
        axes[2].legend(frameon=False, fontsize=7)
        fig.supxlabel("Model study (T25); no measured device. Crossing layout is an upper-bound construction.", fontsize=7)
        fig.savefig(paths[0], dpi=300)
        fig.savefig(paths[1])
        plt.close(fig)
    return [p.relative_to(ROOT).as_posix() for p in paths]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    outdir = args.outdir if args.outdir.is_absolute() else ROOT / args.outdir
    target = outdir / "results.json"
    if target.exists():
        raise FileExistsError("Output must be new")
    outdir.mkdir(parents=True, exist_ok=True)
    depth = part_depth()
    crossings = part_crossings()
    fft_error = max(float(np.linalg.norm(butterfly_dft(n) - dft(n), 2)) for n in (2, 4, 8, 16, 32, 64))
    errors = part_errors()
    losses = part_path_loss(crossings)
    figures = figure(outdir, depth, crossings, errors)
    metrics = {"clements_depth_equals_n": depth["clements_depth_equals_n"],
               "triangular_depth_equals_2n_minus_3": depth["triangular_depth_equals_2n_minus_3"],
               "max_reconstruction_error": depth["max_reconstruction_error"],
               "crossing_total_matches_closed_form": crossings["crossing_total_matches_closed_form"],
               "worst_path_dp_matches_bruteforce": crossings["worst_path_dp_matches_bruteforce"],
               "fft_factorization_error": fft_error,
               "depth_lower_bound_respected": depth["depth_lower_bound_respected"]}
    write_new_json(target, {"scope": "numerical_model", "u_db_assumption": U_DB,
                            "depth": depth, "crossings": crossings, "fft_factorization_error": fft_error,
                            "errors": errors, "path_loss": losses, "figures": figures,
                            "metrics": metrics})
    print(json.dumps(metrics, indent=1))
    print(json.dumps([{k: r[k] for k in ("n", "crossings_total", "worst_path_crossings",
                                         "breakeven_crossing_loss_db")} for r in crossings["rows"]]))


if __name__ == "__main__":
    main()
