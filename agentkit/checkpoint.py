"""Atomic numerical checkpoints with input hashes and an explicit hash chain."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import uuid

import numpy as np

from agentkit.evidence import canonical, sha256_file, utc_now


def save_checkpoint(directory: Path, state, step: int, total_steps: int,
                    experiment_hash: str, previous_metadata_hash: str | None) -> Path:
    """Commit a new state; metadata is the final commit marker."""
    if type(step) is not int or type(total_steps) is not int or not 0 <= step <= total_steps:
        raise ValueError("Checkpoint step must lie inside the planned trajectory")
    array = np.asarray(state)
    if array.dtype != np.complex128 or not np.all(np.isfinite(array)):
        raise ValueError("Checkpoint state must be finite complex128")
    if not isinstance(experiment_hash, str) or len(experiment_hash) != 64:
        raise ValueError("Experiment must have a SHA-256 identity")
    directory.mkdir(parents=True, exist_ok=True)
    final = directory / f"step_{step:08d}.json"
    if final.exists():
        raise FileExistsError("A committed checkpoint already exists")
    token = uuid.uuid4().hex
    array_path = directory / f"state_{step:08d}_{token}.npz"
    with array_path.open("xb") as stream:
        np.savez_compressed(stream, state=array)
        stream.flush()
        os.fsync(stream.fileno())
    record = {"schema": 1, "step": step, "total_steps": total_steps,
              "experiment_hash": experiment_hash,
              "previous_metadata_hash": previous_metadata_hash,
              "array_file": array_path.name, "array_sha256": sha256_file(array_path),
              "dtype": str(array.dtype), "shape": list(array.shape),
              "created_utc": utc_now()}
    temp = directory / (final.name + "." + token + ".tmp")
    with temp.open("xb") as stream:
        stream.write(canonical(record) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    # Exclusive hard-link publication prevents overwriting a concurrent writer.
    try:
        os.link(temp, final)
    finally:
        temp.unlink(missing_ok=True)
    return final


def load_latest(directory: Path, experiment_hash: str, total_steps: int):
    """Validate the entire committed chain and return its last retained state."""
    paths = sorted(directory.glob("step_*.json"))
    if not paths:
        return None
    previous_hash = None
    previous_step = -1
    previous_shape = None
    last_state = None
    for path in paths:
        if path.is_symlink():
            raise ValueError("Checkpoint metadata must not be a symlink")
        record = json.loads(path.read_text(encoding="utf-8"))
        step = record["step"]
        if record["experiment_hash"] != experiment_hash or record["total_steps"] != total_steps:
            raise ValueError("Checkpoint configuration changed")
        if step <= previous_step or step > total_steps or (previous_step == -1 and step != 0):
            raise ValueError("Checkpoint chain has invalid step ordering")
        if path.name != f"step_{step:08d}.json":
            raise ValueError("Checkpoint filename and step disagree")
        if record["previous_metadata_hash"] != previous_hash:
            raise ValueError("Checkpoint metadata chain is broken")
        name = record["array_file"]
        if Path(name).name != name or Path(name).is_absolute():
            raise ValueError("Checkpoint array path escapes its directory")
        array_path = directory / name
        if array_path.is_symlink() or sha256_file(array_path) != record["array_sha256"]:
            raise ValueError("Checkpoint array changed")
        with np.load(array_path, allow_pickle=False) as data:
            last_state = data["state"].copy()
        if (last_state.dtype != np.complex128 or
                list(last_state.shape) != record["shape"] or
                record["dtype"] != "complex128" or
                not np.all(np.isfinite(last_state))):
            raise ValueError("Checkpoint state failed validation")
        if previous_shape is not None and tuple(last_state.shape) != previous_shape:
            raise ValueError("Checkpoint state shape changed inside the trajectory")
        previous_shape = tuple(last_state.shape)
        previous_step, previous_hash = step, sha256_file(path)
    return last_state, previous_step, previous_hash
