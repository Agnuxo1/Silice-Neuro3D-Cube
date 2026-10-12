"""Prospective train/validation/test workflow with analytic complex gradients.

The built-in digit dataset is a development control, not pristine independent
evidence for this project. External final data need a provenance review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.linalg import expm, expm_frechet
from scipy.optimize import minimize
from scipy.special import logsumexp

from agentkit.evidence import sha256_file, write_new_json


MODELS = ("unitary", "real", "unitary_abs", "real_abs",
          "unitary_mzm", "real_mzm")


def hermitian_basis(n: int) -> np.ndarray:
    """Build n squared real directions spanning all Hermitian matrices."""
    if type(n) is not int or not 2 <= n <= 8:
        raise ValueError("Learning reference supports dimensions 2 through 8")
    basis = []
    for i in range(n):
        b = np.zeros((n, n), complex)
        b[i, i] = 1
        basis.append(b)
    for i in range(n):
        for j in range(i+1, n):
            b = np.zeros((n, n), complex)
            b[i, j] = b[j, i] = 1
            basis.append(b)
    for i in range(n):
        for j in range(i+1, n):
            b = np.zeros((n, n), complex)
            b[i, j], b[j, i] = 1j, -1j
            basis.append(b)
    return np.asarray(basis)


def transfer(parameters, n: int, unitary: bool, derivatives: bool):
    """Return a real matrix or an exact exponential unitary and its derivatives."""
    p = np.asarray(parameters, dtype=float)
    if p.shape != (n*n,) or not np.all(np.isfinite(p)):
        raise ValueError("Transfer parameter count is invalid")
    if not unitary:
        matrix = p.reshape(n, n)
        basis = np.eye(n*n).reshape(n*n, n, n) if derivatives else None
        return matrix, basis
    basis = hermitian_basis(n)
    h = np.einsum("k,kij->ij", p, basis)
    matrix = expm(1j * h)
    ds = (np.array([expm_frechet(1j*h, 1j*b, compute_expm=False) for b in basis])
          if derivatives else None)
    return matrix, ds


def model_size(model: str, n: int) -> int:
    """Return the full declared parameter count."""
    if model not in MODELS:
        raise ValueError("Unknown model")
    return n*n * (2 if "_" in model else 1)


def scores_and_directions(parameters, x, model: str, v_pi: float = 1.0,
                          bias: float = 0.0, derivatives: bool = False):
    """Evaluate intensity scores and optional analytic parameter directions.

    Two-layer models detect and re-emit a positive real amplitude with zero
    reference phase. This requires optoelectronic hardware; it is not passive.
    The positive MZM amplitude reproduces the legacy square-root intensity
    model, not every physical MZM field convention.
    """
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or not np.all(np.isfinite(x)):
        raise ValueError("Inputs must be finite feature rows")
    n = x.shape[1]
    if not 2 <= n <= 8 or not np.all(np.isfinite(parameters)):
        raise ValueError("Dimension or parameters are invalid")
    if np.asarray(parameters).shape != (model_size(model, n),):
        raise ValueError("Wrong parameter count")
    if not math.isfinite(v_pi) or v_pi <= 0 or not math.isfinite(bias):
        raise ValueError("Activation controls must be finite and V_pi positive")
    is_unitary = model.startswith("unitary")
    first, d_first = transfer(parameters[:n*n], n, is_unitary, derivatives)
    z1 = x @ first.T
    i1 = abs(z1)**2
    if "_" not in model:
        directions = (np.array([2*np.real(np.conj(z1)*(x @ d.T)) for d in d_first])
                      if derivatives else None)
        return i1, directions
    if model.endswith("_abs"):
        amplitude = np.sqrt(i1)
        slope = np.divide(0.5, amplitude, out=np.zeros_like(amplitude),
                          where=amplitude > 1e-14)
    else:
        angle = 0.5 * (math.pi * i1 / v_pi + bias)
        cosine = np.cos(angle)
        amplitude = abs(cosine)
        slope = -0.5 * math.pi / v_pi * np.sin(angle) * np.sign(cosine)
    second, d_second = transfer(parameters[n*n:], n, is_unitary, derivatives)
    z2 = amplitude @ second.T
    scores = abs(z2)**2
    if not derivatives:
        return scores, None
    directions = []
    for direction in d_first:
        di1 = 2 * np.real(np.conj(z1) * (x @ direction.T))
        dz2 = (slope * di1) @ second.T
        directions.append(2 * np.real(np.conj(z2) * dz2))
    for direction in d_second:
        dz2 = amplitude @ direction.T
        directions.append(2 * np.real(np.conj(z2) * dz2))
    return scores, np.asarray(directions)


def objective(parameters, x, y, model: str, v_pi: float = 1.0, bias: float = 0.0):
    """Return cross-entropy and its exact Fréchet-based gradient."""
    scores, directions = scores_and_directions(parameters, x, model, v_pi, bias, True)
    y = np.asarray(y)
    if y.shape != (len(x),) or y.dtype.kind not in "iu" or y.min() < 0 or y.max() >= scores.shape[1]:
        raise ValueError("Labels must index the declared output classes")
    log_normalizer = logsumexp(scores, axis=1)
    loss = float(np.mean(log_normalizer - scores[np.arange(len(y)), y]))
    derivative = np.exp(scores-log_normalizer[:, None])
    derivative[np.arange(len(y)), y] -= 1
    derivative /= len(y)
    gradient = np.einsum("nc,knc->k", derivative, directions)
    return loss, gradient


def accuracy(parameters, x, y, model: str, v_pi: float, bias: float) -> float:
    """Evaluate fixed parameters; no training or selection occurs here."""
    scores, _ = scores_and_directions(parameters, x, model, v_pi, bias)
    return float(np.mean(scores.argmax(axis=1) == y))


def prepare_data(directory: Path, raw_path: Path | None = None, seed: int = 20261012) -> dict:
    """Freeze stratified 60/20/20 partitions and fit preprocessing on train only."""
    if directory.exists():
        raise FileExistsError("Data output directory must be new")
    if raw_path is None:
        from sklearn.datasets import load_digits
        dataset = load_digits()
        mask = np.isin(dataset.target, [0, 1, 2, 3])
        x, labels = dataset.data[mask], dataset.target[mask]
        provenance = "development_public_digits_already_used_in_project"
    else:
        with np.load(raw_path, allow_pickle=False) as data:
            x, labels = data["X"].copy(), data["y"].copy()
        provenance = "external_data_independence_requires_provenance_review"
    if x.ndim != 2 or not np.all(np.isfinite(x)) or labels.shape != (len(x),):
        raise ValueError("Raw data must have finite X feature rows and matching y")
    classes = np.unique(labels)
    if not 2 <= len(classes) <= 8 or x.shape[1] < len(classes):
        raise ValueError("Use 2 through 8 classes and at least that many features")
    y = np.searchsorted(classes, labels)
    rng = np.random.default_rng(seed)
    indices = {"train": [], "validation": [], "test": []}
    for label in range(len(classes)):
        values = np.flatnonzero(y == label)
        if len(values) < 15:
            raise ValueError("Each class requires at least 15 samples")
        values = rng.permutation(values)
        n_train, n_val = int(0.6*len(values)), int(0.2*len(values))
        indices["train"].extend(values[:n_train])
        indices["validation"].extend(values[n_train:n_train+n_val])
        indices["test"].extend(values[n_train+n_val:])
    indices = {name: np.sort(value) for name, value in indices.items()}
    train = x[indices["train"]].astype(float)
    mean, std = train.mean(axis=0), train.std(axis=0)
    std[std < 1e-12] = 1
    standardized = (train-mean)/std
    _, singular, vh = np.linalg.svd(standardized, full_matrices=False)
    components = vh[:len(classes)].copy()
    for component in components:
        if component[np.argmax(abs(component))] < 0:
            component *= -1
    if singular[len(classes)-1] < 1e-12:
        raise ValueError("Training PCA has insufficient effective rank")
    train_features = standardized @ components.T
    feature_scale = train_features.std(axis=0)
    feature_scale[feature_scale < 1e-12] = 1
    directory.mkdir(parents=True)
    for name, values in indices.items():
        features = (((x[values]-mean)/std) @ components.T) / feature_scale
        with (directory/(name+".npz")).open("xb") as output:
            np.savez_compressed(output, X=features, y=y[values], raw_indices=values)
    raw_hash = hashlib.sha256(np.ascontiguousarray(x).tobytes() +
                              np.ascontiguousarray(labels).tobytes()).hexdigest()
    record = {"seed": seed, "provenance": provenance, "raw_array_sha256": raw_hash,
              "raw_file_sha256": None if raw_path is None else sha256_file(raw_path),
              "classes": classes.tolist(), "mean": mean.tolist(), "std": std.tolist(),
              "pca_components": components.tolist(), "feature_scale": feature_scale.tolist(),
              "partition_hashes": {name: sha256_file(directory/(name+".npz")) for name in indices},
              "counts": {name: len(values) for name, values in indices.items()}}
    write_new_json(directory/"manifest.json", record)
    return record


def fit_candidate(train_path: Path, validation_path: Path, model: str,
                  seeds: list[int], maxiter: int, v_pi: float, bias: float,
                  gradient_threshold: float = 1e-5) -> dict:
    """Fit all registered starts and retain convergence diagnostics for every start."""
    if not seeds or len(set(seeds)) != len(seeds) or maxiter < 1:
        raise ValueError("Training starts and iteration count must be positive")
    with np.load(train_path, allow_pickle=False) as data:
        x, y = data["X"].copy(), data["y"].copy()
    with np.load(validation_path, allow_pickle=False) as data:
        xv, yv = data["X"].copy(), data["y"].copy()
    if xv.shape[1] != x.shape[1]:
        raise ValueError("Training and validation feature dimensions differ")
    records = []
    for seed in seeds:
        initial = 0.5 * np.random.default_rng(seed).standard_normal(model_size(model, x.shape[1]))
        result = minimize(objective, initial, args=(x, y, model, v_pi, bias),
                          jac=True, method="L-BFGS-B",
                          options={"maxiter": maxiter, "gtol": 1e-8, "ftol": 1e-12})
        loss, gradient = objective(result.x, x, y, model, v_pi, bias)
        norm = float(np.max(abs(gradient)))
        records.append({"seed": seed, "parameters": result.x.tolist(),
                        "training_loss": loss, "gradient_infinity_norm": norm,
                        "optimizer_success": bool(result.success),
                        "optimizer_message": str(result.message), "iterations": int(result.nit),
                        "converged": bool(result.success and norm <= gradient_threshold)})
    best = min(records, key=lambda item: item["training_loss"])
    parameters = np.asarray(best["parameters"])
    return {"model": model, "dimension": x.shape[1], "v_pi": v_pi, "bias": bias,
            "maxiter": maxiter, "gradient_threshold": gradient_threshold,
            "train_sha256": sha256_file(train_path),
            "validation_sha256": sha256_file(validation_path),
            "selected_by": "minimum_training_loss_across_registered_starts",
            "selected": best, "all_starts": records,
            "train_accuracy": accuracy(parameters, x, y, model, v_pi, bias),
            "validation_accuracy": accuracy(parameters, xv, yv, model, v_pi, bias),
            "test_evaluated": False, "scope": "numerical_optoelectronic_model"}


def evaluate_locked(candidate_path: Path, test_path: Path) -> dict:
    """Evaluate one frozen candidate; no refit or hyperparameter search is allowed."""
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    if not candidate["selected"]["converged"]:
        raise ValueError("Final evaluation requires the selected training run to converge")
    with np.load(test_path, allow_pickle=False) as data:
        x, y = data["X"].copy(), data["y"].copy()
    if x.shape[1] != candidate["dimension"]:
        raise ValueError("Test feature dimension disagrees with the frozen candidate")
    scores, _ = scores_and_directions(candidate["selected"]["parameters"], x,
                                     candidate["model"], candidate["v_pi"], candidate["bias"])
    predictions = scores.argmax(axis=1)
    return {"candidate_sha256": sha256_file(candidate_path),
            "test_sha256": sha256_file(test_path), "n_test": len(y),
            "accuracy": float(np.mean(predictions == y)),
            "predictions": predictions.tolist(), "labels": y.tolist(),
            "scope": "numerical_optoelectronic_model",
            "note": "Independence, one-time test access and experimental hardware remain separate requirements."}


def paired_accuracy(first, second, labels, repeats: int = 2000, seed: int = 20261012) -> dict:
    """Report the observed paired difference separately from bootstrap uncertainty."""
    a, b, y = map(np.asarray, (first, second, labels))
    if a.ndim != 1 or a.shape != b.shape or a.shape != y.shape or len(y) < 2 or repeats < 100:
        raise ValueError("Paired predictions must refer to the same nonempty test samples")
    difference = (a == y).astype(float) - (b == y).astype(float)
    rng = np.random.default_rng(seed)
    draws = np.array([difference[rng.integers(0, len(y), len(y))].mean()
                      for _ in range(repeats)])
    return {"observed_difference": float(difference.mean()),
            "bootstrap_mean": float(draws.mean()),
            "percentile_ci95": np.percentile(draws, [2.5, 97.5]).tolist(),
            "repeats": repeats, "seed": seed}


def main() -> None:
    """Prepare data, train without test access, or evaluate a frozen candidate."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--directory", type=Path, required=True)
    prepare.add_argument("--input", type=Path)
    prepare.add_argument("--seed", type=int, default=20261012)
    fit = commands.add_parser("fit")
    fit.add_argument("--train", type=Path, required=True)
    fit.add_argument("--validation", type=Path, required=True)
    fit.add_argument("--model", choices=MODELS, required=True)
    fit.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 9)))
    fit.add_argument("--maxiter", type=int, default=1000)
    fit.add_argument("--v-pi", type=float, default=1)
    fit.add_argument("--bias", type=float, default=0)
    fit.add_argument("--gradient-threshold", type=float, default=1e-5)
    fit.add_argument("--out", type=Path, required=True)
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--candidate", type=Path, required=True)
    evaluate.add_argument("--test", type=Path, required=True)
    evaluate.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare_data(args.directory, args.input, args.seed)
    elif args.command == "fit":
        if args.out.exists():
            raise FileExistsError("Candidate path must be new")
        result = fit_candidate(args.train, args.validation, args.model, args.seeds,
                               args.maxiter, args.v_pi, args.bias, args.gradient_threshold)
        write_new_json(args.out, result)
    else:
        if args.out.exists():
            raise FileExistsError("Test receipt path must be new")
        result = evaluate_locked(args.candidate, args.test)
        write_new_json(args.out, result)
    summary_keys = ("model", "dimension", "provenance", "counts",
                    "train_accuracy", "validation_accuracy", "accuracy",
                    "test_evaluated", "n_test", "scope")
    print(json.dumps({key: result[key] for key in summary_keys if key in result}))


if __name__ == "__main__":
    main()
