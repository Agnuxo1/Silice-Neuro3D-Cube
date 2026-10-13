"""Data custodian for the neuro-cube benchmark: frozen partitions and sealed test labels.

`seal` builds stratified 60/20/20 partitions, fits standardization and PCA on the
training partition only, writes public train/validation files (with labels) and
test features WITHOUT labels into the repository, and stores the test labels
outside the repository (D:) with a salted SHA-256 commitment in the public
manifest. `reveal` releases the labels once, only after a predictions file
exists; it records that file's hash and refuses a second reveal.

Tasks: dev03 = sklearn digits 0-3 (development control, already used in this
project); res47 = sklearn digits 4-7 (classes never used in the project).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

TASKS = {"dev03": ([0, 1, 2, 3], "development_control_digits_0_3_already_used_in_project"),
         "res47": ([4, 5, 6, 7], "reserved_digits_4_7_never_used_in_project"),
         "syn": ([0, 1, 2, 3], "synthetic_8x8_prototypes_for_software_dry_runs_only")}


def synthetic_digits(seed: int = 5):
    """Four noisy random 8x8 prototypes (dry runs only; never a result)."""
    rng = np.random.default_rng(seed)
    prototypes = rng.uniform(0, 16, (4, 64))
    target = np.repeat(np.arange(4), 180)
    images = np.clip(prototypes[target] + rng.normal(0, 5, (len(target), 64)), 0, 16)
    return images, target


def load_images(task: str, raw_indices, public_dir: Path | None = None) -> np.ndarray:
    """8x8 images for the response panel."""
    if task == "syn":
        return synthetic_digits()[0][np.asarray(raw_indices)].reshape(-1, 8, 8)
    from sklearn.datasets import load_digits
    return load_digits().images[np.asarray(raw_indices)]
FEATURES = (4, 8)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_new(path: Path, text: str) -> None:
    with path.open("x", encoding="utf-8") as handle:
        handle.write(text)


def _save(path: Path, **arrays) -> None:
    with path.open("xb") as handle:
        np.savez_compressed(handle, **arrays)


def label_commitment(salt: str, labels: np.ndarray, indices: np.ndarray) -> str:
    payload = (salt.encode() + np.ascontiguousarray(labels.astype(np.int64)).tobytes()
               + np.ascontiguousarray(indices.astype(np.int64)).tobytes())
    return hashlib.sha256(payload).hexdigest()


def seal(task: str, seed: int, public_dir: Path, sealed_dir: Path) -> dict:
    classes, provenance = TASKS[task]
    out, vault = public_dir / task, sealed_dir / task
    if out.exists() or vault.exists():
        raise FileExistsError("Partition directories must be new")
    if task == "syn":
        images, target = synthetic_digits()
    else:
        from sklearn.datasets import load_digits
        data = load_digits()
        images, target = data.data, data.target
    mask = np.isin(target, classes)
    raw_index = np.flatnonzero(mask)
    x_all, labels = images[mask].astype(float), target[mask]
    y_all = np.searchsorted(classes, labels)
    rng = np.random.default_rng(seed)
    parts = {"train": [], "validation": [], "test": []}
    for label in range(len(classes)):
        members = rng.permutation(np.flatnonzero(y_all == label))
        n_train, n_val = int(0.6 * len(members)), int(0.2 * len(members))
        parts["train"].extend(members[:n_train])
        parts["validation"].extend(members[n_train:n_train + n_val])
        parts["test"].extend(members[n_train + n_val:])
    parts = {k: np.sort(np.asarray(v)) for k, v in parts.items()}
    train = x_all[parts["train"]]
    mean, std = train.mean(axis=0), train.std(axis=0)
    std[std < 1e-12] = 1.0
    standardized = (train - mean) / std
    _, singular, vh = np.linalg.svd(standardized, full_matrices=False)
    components = vh[:max(FEATURES)].copy()
    for component in components:
        if component[np.argmax(abs(component))] < 0:
            component *= -1
    out.mkdir(parents=True)
    vault.mkdir(parents=True)
    record = {"task": task, "classes": classes, "provenance": provenance, "seed": seed,
              "source": "sklearn.datasets.load_digits (UCI optdigits test set, 8x8 images)",
              "counts": {k: int(len(v)) for k, v in parts.items()},
              "preprocessing": "standardize (train mean/std) -> PCA (train SVD, sign fixed) -> "
                               "divide by train std of each component; fitted on train only",
              "pca_singular_values": singular[:max(FEATURES)].tolist(), "files": {}}
    for n in FEATURES:
        comp = components[:n]
        scale = (standardized @ comp.T).std(axis=0)
        scale[scale < 1e-12] = 1.0
        feats = lambda idx: (((x_all[idx] - mean) / std) @ comp.T) / scale
        for name in ("train", "validation"):
            path = out / ("%s_N%d.npz" % (name, n))
            _save(path, X=feats(parts[name]), y=y_all[parts[name]].astype(np.int64),
                  raw_indices=raw_index[parts[name]])
            record["files"][path.name] = _sha(path)
        path = out / ("test_X_N%d.npz" % n)
        _save(path, X=feats(parts["test"]), raw_indices=raw_index[parts["test"]])
        record["files"][path.name] = _sha(path)
        record["feature_scale_N%d" % n] = scale.tolist()
    salt = secrets.token_hex(32)
    test_labels = y_all[parts["test"]].astype(np.int64)
    test_raw = raw_index[parts["test"]]
    _save(vault / "test_labels.npz", y=test_labels, raw_indices=test_raw)
    (vault / "salt.json").write_text(json.dumps({"salt": salt}), encoding="utf-8")
    record["test_label_commitment_sha256"] = label_commitment(salt, test_labels, test_raw)
    record["commitment_rule"] = "sha256(salt_utf8 || int64 labels || int64 raw indices)"
    record["sealed_at_utc"] = _now()
    record["preprocessing_state"] = {"mean": mean.tolist(), "std": std.tolist(),
                                     "components": components.tolist()}
    _write_new(out / "manifest.json", json.dumps(record, indent=1))
    return {k: record[k] for k in ("task", "counts", "test_label_commitment_sha256")}


def reveal(task: str, public_dir: Path, sealed_dir: Path, predictions: Path, out_dir: Path) -> dict:
    """Release the sealed labels once, after the frozen predictions exist."""
    vault = sealed_dir / task
    receipt_path = vault / "reveal_receipt.json"
    if receipt_path.exists():
        raise RuntimeError("Labels for %s were already revealed: %s" % (task, receipt_path))
    if not predictions.is_file():
        raise FileNotFoundError("Frozen predictions must exist before the reveal")
    manifest = json.loads((public_dir / task / "manifest.json").read_text(encoding="utf-8"))
    salt = json.loads((vault / "salt.json").read_text(encoding="utf-8"))["salt"]
    with np.load(vault / "test_labels.npz", allow_pickle=False) as data:
        labels, raw = data["y"].copy(), data["raw_indices"].copy()
    if label_commitment(salt, labels, raw) != manifest["test_label_commitment_sha256"]:
        raise RuntimeError("Sealed labels do not match the public commitment")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / ("revealed_test_labels_%s.npz" % task)
    shutil.copyfile(vault / "test_labels.npz", target)
    receipt = {"task": task, "revealed_at_utc": _now(), "predictions_file": str(predictions),
               "predictions_sha256": _sha(predictions), "labels_file": target.name,
               "labels_sha256": _sha(target), "salt": salt,
               "commitment_sha256": manifest["test_label_commitment_sha256"], "commitment_verified": True}
    _write_new(receipt_path, json.dumps(receipt, indent=1))
    _write_new(out_dir / ("reveal_receipt_%s.json" % task), json.dumps(receipt, indent=1))
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("seal")
    s.add_argument("--task", choices=sorted(TASKS), required=True)
    s.add_argument("--seed", type=int, default=20261013)
    r = sub.add_parser("reveal")
    r.add_argument("--task", choices=sorted(TASKS), required=True)
    r.add_argument("--predictions", type=Path, required=True)
    r.add_argument("--out-dir", type=Path, required=True)
    for p in (s, r):
        p.add_argument("--public-dir", type=Path, required=True)
        p.add_argument("--sealed-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "seal":
        print(json.dumps(seal(args.task, args.seed, args.public_dir, args.sealed_dir)))
    else:
        receipt = reveal(args.task, args.public_dir, args.sealed_dir, args.predictions, args.out_dir)
        print(json.dumps({k: receipt[k] for k in ("task", "predictions_sha256", "commitment_verified")}))


if __name__ == "__main__":
    main()
