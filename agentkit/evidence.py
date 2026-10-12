"""Immutable evidence receipts, protocols and task-status checks.

This module does not certify optical physics. It checks whether a recorded
claim has the declared prerequisites, criteria and retained evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    """Return an unambiguous UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    """Hash a file without loading large numerical arrays into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: Any) -> bytes:
    """Serialize JSON deterministically and reject non-finite values."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      allow_nan=False, separators=(",", ":")).encode("utf-8")


def write_new_json(path: Path, value: Any) -> None:
    """Write a new durable JSON record and refuse to overwrite evidence."""
    data = canonical(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def inside(root: Path, relative: str) -> Path:
    """Resolve a regular file beneath root, rejecting traversal and symlinks."""
    root = root.resolve()
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts:
        raise ValueError("Evidence paths must be relative and remain inside root")
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlinks are not accepted as evidence")
    current = current.resolve()
    if not current.is_relative_to(root) or not current.is_file():
        raise ValueError("Evidence must be an existing regular file inside root")
    return current


def snapshot(root: Path, relative_paths: list[str]) -> dict[str, Any]:
    """Record exact bytes of a reviewed, explicit list of inputs."""
    if not relative_paths or len(set(relative_paths)) != len(relative_paths):
        raise ValueError("Input paths must be nonempty and unique")
    return {"created_utc": utc_now(), "files": {
        name: {"sha256": sha256_file(inside(root, name)),
               "size": inside(root, name).stat().st_size}
        for name in sorted(relative_paths)}}


def verify_snapshot(root: Path, record: dict[str, Any]) -> None:
    """Reject missing files, changed bytes and malformed snapshots."""
    files = record.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("Snapshot has no input files")
    for name, info in files.items():
        path = inside(root, name)
        if path.stat().st_size != info["size"] or sha256_file(path) != info["sha256"]:
            raise ValueError("Input bytes changed: " + name)


def git_identity(root: Path) -> dict[str, str]:
    """Read the actual checkout identity without changing the repository."""
    def run(arguments: list[str]) -> str:
        result = subprocess.run(["git", "-C", str(root), *arguments],
                                capture_output=True, text=True, check=True)
        return result.stdout.rstrip()
    return {"head": run(["rev-parse", "HEAD"]),
            "branch": run(["branch", "--show-current"]),
            "status": run(["status", "--porcelain=v1", "-z"])}


def freeze(root: Path, protocol_path: str, sources: list[str],
           receipt_path: Path) -> dict[str, Any]:
    """Freeze a protocol and its sources before generating new data."""
    protocol_file = inside(root, protocol_path)
    protocol = json.loads(protocol_file.read_text(encoding="utf-8"))
    required = {"experiment_id", "task_id", "model", "units", "criteria",
                "resource_limits", "heldout_policy", "scope"}
    if not required.issubset(protocol):
        raise ValueError("Protocol is missing required fields")
    if not protocol["criteria"] or not isinstance(protocol["criteria"], list):
        raise ValueError("Protocol must declare explicit acceptance criteria")
    ids = [entry["id"] for entry in protocol["criteria"]]
    if len(set(ids)) != len(ids):
        raise ValueError("Criterion identifiers must be unique")
    for entry in protocol["criteria"]:
        if entry.get("operator") not in ("le", "ge", "eq"):
            raise ValueError("Unsupported criterion operator")
        threshold = entry["threshold"]
        if isinstance(threshold, bool):
            if entry["operator"] != "eq":
                raise ValueError("Boolean criteria must use equality")
        elif not isinstance(threshold, (int, float)) or not math.isfinite(threshold):
            raise ValueError("Criterion threshold must be finite or boolean")
    names = list(dict.fromkeys([protocol_path, *sources]))
    record = {"schema": 1, "kind": "prospective_protocol",
              "protocol_path": protocol_path, "protocol": protocol,
              "inputs": snapshot(root, names), "git": git_identity(root)}
    write_new_json(receipt_path, record)
    return record


def evaluate_receipt(root: Path, freeze_record: dict[str, Any],
                     result: dict[str, Any]) -> dict[str, Any]:
    """Evaluate every frozen criterion; missing and non-finite data fail."""
    if freeze_record.get("kind") != "prospective_protocol":
        raise ValueError("A frozen protocol receipt is required")
    verify_snapshot(root, freeze_record["inputs"])
    protocol = freeze_record["protocol"]
    if result.get("experiment_id") != protocol["experiment_id"]:
        raise ValueError("Result belongs to another experiment")
    if result.get("protocol_sha256") != hashlib.sha256(
            canonical(protocol)).hexdigest():
        raise ValueError("Result does not identify the frozen protocol")
    if result.get("scope") != protocol["scope"]:
        raise ValueError("Result scope differs from the protocol")
    if result.get("status") != "completed":
        raise ValueError("Partial or failed execution cannot pass")
    artifacts = result.get("artifacts", [])
    if not artifacts:
        raise ValueError("A result must retain raw artifacts")
    artifact_snapshot = snapshot(root, artifacts)
    metrics = result.get("metrics", {})
    checks = []
    for criterion in protocol["criteria"]:
        name = criterion["id"]
        value = metrics.get(name)
        threshold = criterion["threshold"]
        valid = (isinstance(value, bool) if isinstance(threshold, bool)
                 else isinstance(value, (int, float)) and
                 not isinstance(value, bool) and math.isfinite(value))
        passed = False
        if valid:
            op = criterion["operator"]
            passed = (value <= threshold if op == "le" else
                      value >= threshold if op == "ge" else value == threshold)
        checks.append({"id": name, "value": value, "threshold": threshold,
                       "operator": criterion["operator"],
                       "evaluated": valid, "passed": bool(passed)})
    return {"schema": 1, "created_utc": utc_now(),
            "experiment_id": protocol["experiment_id"],
            "task_id": protocol["task_id"], "scope": result["scope"],
            "checks": checks, "passed": all(c["passed"] for c in checks),
            "artifacts": artifact_snapshot,
            "note": "Mechanical receipt validation; not independent replication."}


def closure_status(task: dict[str, Any], audit: dict[str, Any],
                   dependency_status: dict[str, str]) -> str:
    """Keep passing numerical records separate from physical/external closure."""
    if task["scope"] != audit["scope"]:
        return "BLOCKED_SCOPE"
    if any(dependency_status.get(dep) != "PASS"
           for dep in task.get("requires", [])):
        return "BLOCKED_DEPENDENCY"
    return "PASS" if audit.get("passed") is True else "FAIL"


def main() -> None:
    """Expose snapshot, freeze and audit as explicit read/write operations."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    snap = commands.add_parser("snapshot")
    snap.add_argument("--paths", nargs="+", required=True)
    snap.add_argument("--out", type=Path, required=True)
    frozen = commands.add_parser("freeze")
    frozen.add_argument("--protocol", required=True)
    frozen.add_argument("--sources", nargs="+", required=True)
    frozen.add_argument("--out", type=Path, required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("--freeze", type=Path, required=True)
    audit.add_argument("--result", type=Path, required=True)
    audit.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "snapshot":
        write_new_json(args.out, snapshot(args.root, args.paths))
    elif args.command == "freeze":
        freeze(args.root, args.protocol, args.sources, args.out)
    else:
        read = lambda p: json.loads(p.read_text(encoding="utf-8"))
        value = evaluate_receipt(args.root, read(args.freeze), read(args.result))
        write_new_json(args.out, value)
        print(json.dumps({"passed": value["passed"]}))
        if not value["passed"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
