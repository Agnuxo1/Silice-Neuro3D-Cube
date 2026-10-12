"""Smooth signed-field MZM activation and validation-based selection (kit v2).

Finding recorded in guide v2: with the v1 example (unitary_mzm, 8 starts,
1000 iterations, development digits), no start satisfied the v1 gradient
gate; L-BFGS-B stopped on relative loss reduction with max |gradient| of
about 5e-3 to 6e-2. The v1 re-emission uses |cos(.)|, which is not
differentiable where cos = 0, and a positive amplitude discards the sign of
the field. A push-pull MZM fed by a phase-referenced carrier transmits the
signed field amplitude cos(.), which is smooth. These models implement that
convention; their physical validity still requires the hardware check of
T12 point 7 (reference phase, bias stability, measured V_pi).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

from agentkit.evidence import sha256_file, write_new_json
from agentkit.learning import transfer

MODELS_V2 = ("unitary_mzm_signed", "real_mzm_signed")


def model_size_v2(model: str, n: int) -> int:
    """Two full n-by-n transfers."""
    if model not in MODELS_V2:
        raise ValueError("Unknown v2 model")
    return 2 * n * n


def scores_and_directions_v2(parameters, x, model: str, v_pi: float = 1.0,
                             bias: float = 0.0, derivatives: bool = False):
    """Intensity scores and exact parameter directions for signed re-emission."""
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or not np.all(np.isfinite(x)) or not 2 <= x.shape[1] <= 8:
        raise ValueError("Inputs must be finite rows with 2 to 8 features")
    n = x.shape[1]
    p = np.asarray(parameters, dtype=float)
    if p.shape != (model_size_v2(model, n),) or not np.all(np.isfinite(p)):
        raise ValueError("Wrong or non-finite parameters")
    if not math.isfinite(v_pi) or v_pi <= 0 or not math.isfinite(bias):
        raise ValueError("V_pi must be positive and bias finite")
    unitary = model.startswith("unitary")
    first, d_first = transfer(p[:n * n], n, unitary, derivatives)
    second, d_second = transfer(p[n * n:], n, unitary, derivatives)
    z1 = x @ first.T
    i1 = abs(z1) ** 2
    angle = 0.5 * (math.pi * i1 / v_pi + bias)
    amplitude = np.cos(angle)
    slope = -0.5 * math.pi / v_pi * np.sin(angle)
    z2 = amplitude @ second.T
    scores = abs(z2) ** 2
    if not derivatives:
        return scores, None
    directions = []
    for direction in d_first:
        di1 = 2 * np.real(np.conj(z1) * (x @ direction.T))
        directions.append(2 * np.real(np.conj(z2) * ((slope * di1) @ second.T)))
    for direction in d_second:
        directions.append(2 * np.real(np.conj(z2) * (amplitude @ direction.T)))
    return scores, np.asarray(directions)


def objective_v2(parameters, x, y, model: str, v_pi: float = 1.0, bias: float = 0.0):
    """Cross-entropy on intensity logits and its exact gradient."""
    scores, directions = scores_and_directions_v2(parameters, x, model, v_pi, bias, True)
    y = np.asarray(y)
    if y.shape != (len(x),) or y.dtype.kind not in "iu" or y.min() < 0 or y.max() >= scores.shape[1]:
        raise ValueError("Labels must index the output classes")
    normalizer = logsumexp(scores, axis=1)
    loss = float(np.mean(normalizer - scores[np.arange(len(y)), y]))
    weights = np.exp(scores - normalizer[:, None])
    weights[np.arange(len(y)), y] -= 1
    weights /= len(y)
    return loss, np.einsum("nc,knc->k", weights, directions)


def _load_split(path: Path):
    """Load X (finite, 2 to 8 features) and integer labels y of equal length."""
    with np.load(path, allow_pickle=False) as data:
        x, y = data["X"].copy(), data["y"].copy()
    if (x.ndim != 2 or not 2 <= x.shape[1] <= 8 or not np.all(np.isfinite(x))
            or y.shape != (len(x),) or y.dtype.kind not in "iu" or len(x) < 1 or y.min() < 0):
        raise ValueError("Invalid split: " + str(path))
    return x, y


def fit_candidate_v2(train_path: Path, validation_path: Path, model: str, seeds: list[int],
                     maxiter: int, v_pi: float, bias: float,
                     gradient_threshold: float = 1e-5) -> dict:
    """Fit every registered start and keep all diagnostics (same record shape as v1)."""
    if not seeds or len(set(seeds)) != len(seeds) or maxiter < 1:
        raise ValueError("Starts must be unique and iterations positive")
    x, y = _load_split(train_path)
    xv, yv = _load_split(validation_path)
    if xv.shape[1] != x.shape[1]:
        raise ValueError("Training and validation feature dimensions differ")
    records = []
    for seed in seeds:
        start = 0.5 * np.random.default_rng(seed).standard_normal(model_size_v2(model, x.shape[1]))
        result = minimize(objective_v2, start, args=(x, y, model, v_pi, bias), jac=True,
                          method="L-BFGS-B",
                          options={"maxiter": maxiter, "gtol": 1e-8, "ftol": 1e-12})
        loss, gradient = objective_v2(result.x, x, y, model, v_pi, bias)
        norm = float(np.max(abs(gradient)))
        records.append({"seed": seed, "parameters": result.x.tolist(), "training_loss": loss,
                        "gradient_infinity_norm": norm, "optimizer_success": bool(result.success),
                        "optimizer_message": str(result.message), "iterations": int(result.nit),
                        "converged": bool(result.success and norm <= gradient_threshold)})
    converged = [r for r in records if r["converged"]]
    best = min(converged or records, key=lambda item: item["training_loss"])
    parameters = np.asarray(best["parameters"])
    accuracy = lambda a, b: float(np.mean(
        scores_and_directions_v2(parameters, a, model, v_pi, bias)[0].argmax(axis=1) == b))
    validation_scores = scores_and_directions_v2(parameters, xv, model, v_pi, bias)[0]
    validation_loss = float(np.mean(logsumexp(validation_scores, axis=1) -
                                    validation_scores[np.arange(len(yv)), yv]))
    return {"model": model, "dimension": x.shape[1], "v_pi": v_pi, "bias": bias,
            "maxiter": maxiter, "gradient_threshold": gradient_threshold,
            "train_sha256": sha256_file(train_path), "validation_sha256": sha256_file(validation_path),
            "selected_by": ("minimum_training_loss_among_converged_starts" if converged
                            else "minimum_training_loss_no_start_converged"),
            "selected": best, "all_starts": records,
            "converged_starts": sum(r["converged"] for r in records),
            "train_accuracy": accuracy(x, y), "validation_accuracy": accuracy(xv, yv),
            "validation_loss": validation_loss, "test_evaluated": False,
            "scope": "numerical_optoelectronic_model"}


def select_by_validation(candidate_paths: list[Path]) -> dict:
    """Choose among converged configurations by validation loss (test untouched)."""
    entries = []
    for path in candidate_paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        entries.append({"path": str(path), "sha256": sha256_file(path), "model": record["model"],
                        "v_pi": record["v_pi"], "bias": record["bias"],
                        "converged": bool(record["selected"]["converged"]),
                        "validation_loss": record.get("validation_loss"),
                        "validation_accuracy": record["validation_accuracy"]})
    eligible = [e for e in entries if e["converged"] and e["validation_loss"] is not None]
    if not eligible:
        raise ValueError("No converged candidate with a validation loss is available")
    chosen = min(eligible, key=lambda e: (e["validation_loss"], -e["validation_accuracy"]))
    return {"chosen": chosen, "considered": entries,
            "rule": "minimum validation loss among converged candidates; ties by accuracy"}


def evaluate_locked_v2(candidate_path: Path, test_path: Path) -> dict:
    """Evaluate one frozen converged v2 candidate exactly once."""
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    if candidate["model"] not in MODELS_V2 or not candidate["selected"]["converged"]:
        raise ValueError("Requires a converged v2 candidate")
    x, y = _load_split(test_path)
    if x.shape[1] != candidate["dimension"]:
        raise ValueError("Test feature dimension differs from the candidate")
    scores, _ = scores_and_directions_v2(candidate["selected"]["parameters"], x,
                                         candidate["model"], candidate["v_pi"], candidate["bias"])
    predictions = scores.argmax(axis=1)
    return {"candidate_sha256": sha256_file(candidate_path), "test_sha256": sha256_file(test_path),
            "n_test": len(y), "accuracy": float(np.mean(predictions == y)),
            "predictions": predictions.tolist(), "labels": y.tolist(),
            "scope": "numerical_optoelectronic_model"}


def kink_fraction(candidate_path: Path, data_path: Path, epsilon: float = 1e-2) -> dict:
    """For a v1 *_mzm or *_abs candidate, fraction of samples near the nonsmooth point."""
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    model = candidate["model"]
    if not (model.endswith("_mzm") or model.endswith("_abs")):
        raise ValueError("Only v1 models with |.| re-emission have a kink")
    with np.load(data_path, allow_pickle=False) as data:
        x = data["X"].copy()
    n = x.shape[1]
    first, _ = transfer(np.asarray(candidate["selected"]["parameters"])[:n * n], n,
                        model.startswith("unitary"), False)
    i1 = abs(x @ first.T) ** 2
    value = (np.cos(0.5 * (math.pi * i1 / candidate["v_pi"] + candidate["bias"]))
             if model.endswith("_mzm") else np.sqrt(i1))
    near = abs(value) < epsilon
    return {"model": model, "epsilon": epsilon,
            "selected_converged": bool(candidate["selected"]["converged"]),
            "activations_near_kink": int(near.sum()), "activations": int(near.size),
            "fraction_near_kink": float(near.mean()),
            "samples_with_any_near_kink": int(near.any(axis=1).sum()), "samples": len(near),
            "fraction_samples_near_kink": float(near.any(axis=1).mean()),
            "candidate_sha256": sha256_file(candidate_path)}


def main() -> None:
    """fit, select, evaluate or kink diagnostics with new output paths only."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    fit = commands.add_parser("fit")
    fit.add_argument("--train", type=Path, required=True)
    fit.add_argument("--validation", type=Path, required=True)
    fit.add_argument("--model", choices=MODELS_V2, required=True)
    fit.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 9)))
    fit.add_argument("--maxiter", type=int, default=1000)
    fit.add_argument("--v-pi", type=float, default=1.0)
    fit.add_argument("--bias", type=float, default=0.0)
    fit.add_argument("--gradient-threshold", type=float, default=1e-5)
    select = commands.add_parser("select")
    select.add_argument("--candidates", type=Path, nargs="+", required=True)
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--candidate", type=Path, required=True)
    evaluate.add_argument("--test", type=Path, required=True)
    kink = commands.add_parser("kink")
    kink.add_argument("--candidate", type=Path, required=True)
    kink.add_argument("--data", type=Path, required=True)
    kink.add_argument("--epsilon", type=float, default=1e-2)
    for sub in (fit, select, evaluate, kink):
        sub.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Output path must be new")
    if args.command == "fit":
        result = fit_candidate_v2(args.train, args.validation, args.model, args.seeds,
                                  args.maxiter, args.v_pi, args.bias, args.gradient_threshold)
    elif args.command == "select":
        result = select_by_validation(args.candidates)
    elif args.command == "evaluate":
        result = evaluate_locked_v2(args.candidate, args.test)
    else:
        result = kink_fraction(args.candidate, args.data, args.epsilon)
    write_new_json(args.out, result)
    keys = ("model", "converged_starts", "train_accuracy", "validation_accuracy",
            "validation_loss", "accuracy", "fraction_near_kink", "chosen")
    print(json.dumps({k: result[k] for k in keys if k in result}))


if __name__ == "__main__":
    main()
