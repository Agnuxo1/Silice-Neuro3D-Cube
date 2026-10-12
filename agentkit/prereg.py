"""Git-anchored prospective commitments and a stricter receipt audit (kit v2).

Closes gaps of agentkit.evidence (v1):
1. evaluate_receipt trusts the protocol dictionary stored in the receipt, so
   editing that dictionary relaxes criteria without touching the protocol file.
   Here the protocol is always re-read from the committed git object.
2. freeze does not require the protocol or sources to be committed, clean or
   published. Here they must be tracked and unmodified, planned artifacts are
   mandatory, and publication can be re-verified at audit time, optionally
   against the server with `git ls-remote`.
3. The audit scans git history for other protocols with the same
   experiment_id at the same path, and for planned artifacts committed outside
   the descendants of the commitment commit.

Residual limits, stated rather than hidden: a commitment record is a local
file; a protocol committed after data were produced (and never committed
before in another form) cannot be detected from the repository alone. Only
an external timestamp (archive DOI, preregistration service) plus data
custody closes that gap. This module never pushes, publishes or contacts
anyone; `--query-server` only reads the remote's refs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

from agentkit.evidence import (canonical, evaluate_receipt, inside, snapshot,
                               utc_now, write_new_json)


REQUIRED = {"experiment_id", "task_id", "model", "units", "criteria",
            "resource_limits", "heldout_policy", "scope", "planned_artifacts"}


def _git(root: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run git without a shell; decode output as UTF-8 on every platform."""
    return subprocess.run(["git", "-C", str(root), *arguments], capture_output=True,
                          text=True, encoding="utf-8", errors="strict", check=check)


def _git_bytes(root: Path, *arguments: str) -> bytes:
    """Run git and return raw bytes (used for committed file content)."""
    return subprocess.run(["git", "-C", str(root), *arguments], capture_output=True,
                          check=True).stdout


def _norm(name: str) -> str:
    """Repository-relative POSIX path, so Windows separators resolve in git."""
    posix = str(name).replace("\\", "/")
    if not posix or posix.startswith("/") or ":" in posix.split("/")[0]:
        raise ValueError("Paths must be relative to the repository root: " + str(name))
    return posix


def _committed_blob(root: Path, commit: str, relative: str) -> str | None:
    """Return the blob id of a path in a commit, or None if absent."""
    result = _git(root, "rev-parse", "--verify", "--quiet", f"{commit}:{relative}", check=False)
    return result.stdout.strip() or None


def _working_blob(root: Path, relative: str) -> str:
    """Hash the working file with git's own filters (CRLF-normalization aware)."""
    return _git(root, "hash-object", "--", relative).stdout.strip()


def _load_committed_json(root: Path, commit: str, relative: str) -> dict:
    return json.loads(_git_bytes(root, "show", f"{commit}:{relative}").decode("utf-8"))


def _validate_protocol(protocol: dict) -> None:
    """Structural rules: the v1 rules plus mandatory planned artifacts."""
    if not REQUIRED.issubset(protocol):
        raise ValueError("Protocol is missing required fields: " +
                         ", ".join(sorted(REQUIRED - set(protocol))))
    criteria = protocol["criteria"]
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("Protocol must declare explicit acceptance criteria")
    ids = [entry["id"] for entry in criteria]
    if len(set(ids)) != len(ids):
        raise ValueError("Criterion identifiers must be unique")
    for entry in criteria:
        if entry.get("operator") not in ("le", "ge", "eq"):
            raise ValueError("Unsupported criterion operator")
        threshold = entry.get("threshold")
        if isinstance(threshold, bool):
            if entry["operator"] != "eq":
                raise ValueError("Boolean criteria must use equality")
        elif not isinstance(threshold, (int, float)) or not math.isfinite(threshold):
            raise ValueError("Criterion threshold must be finite or boolean")
    planned = protocol["planned_artifacts"]
    if (not isinstance(planned, list) or not planned
            or not all(isinstance(p, str) and p for p in planned)
            or len({_norm(p) for p in planned}) != len(planned)):
        raise ValueError("planned_artifacts must be a nonempty list of unique relative paths")


def remote_contains(root: Path, commit: str, remote_ref: str, query_server: bool) -> bool | None:
    """Whether `commit` is contained in `remote_ref` ("remote/branch").

    Without query_server the local remote-tracking ref is used, which a user
    can create without pushing. With query_server the branch head is read
    from the server; None means the head is not available locally (fetch).
    """
    if not query_server:
        return _git(root, "merge-base", "--is-ancestor", commit, remote_ref,
                    check=False).returncode == 0
    remote, _, branch = remote_ref.partition("/")
    if not branch:
        raise ValueError("remote_ref must look like remote/branch")
    listed = _git(root, "ls-remote", "--heads", remote, "refs/heads/" + branch, check=False)
    if listed.returncode or not listed.stdout.strip():
        return False
    head = listed.stdout.split()[0]
    if _git(root, "cat-file", "-e", head + "^{commit}", check=False).returncode:
        return None
    return _git(root, "merge-base", "--is-ancestor", commit, head, check=False).returncode == 0


def commit_protocol(root: Path, protocol_path: str, sources: list[str], out: Path,
                    remote_ref: str | None = None, allow_unpublished: bool = False,
                    query_server: bool = False) -> dict:
    """Record a protocol committed (and optionally published) before any new data."""
    root = root.resolve()
    protocol_path = _norm(protocol_path)
    names = list(dict.fromkeys([protocol_path, *[_norm(s) for s in sources]]))
    for name in names:
        inside(root, name)
        if _git(root, "ls-files", "--error-unmatch", "--", name, check=False).returncode:
            raise ValueError("Path is not tracked by git: " + name)
    head = _git(root, "rev-parse", "HEAD").stdout.strip()
    blobs = {}
    for name in names:
        committed = _committed_blob(root, head, name)
        if committed is None or committed != _working_blob(root, name):
            raise ValueError("Path has uncommitted changes: " + name)
        blobs[name] = committed
    protocol = _load_committed_json(root, head, protocol_path)
    _validate_protocol(protocol)
    for planned in protocol["planned_artifacts"]:
        planned = _norm(planned)
        if (root / planned).exists() or _committed_blob(root, head, planned) is not None:
            raise ValueError("A planned artifact already exists before the commitment: " + planned)
    published = None
    if remote_ref is not None:
        published = remote_contains(root, head, remote_ref, query_server)
        if not published and not allow_unpublished:
            raise ValueError("Commitment commit is not verifiably contained in " + remote_ref)
    record = {"schema": 2, "kind": "git_anchored_protocol",
              "created_utc": utc_now(), "protocol_path": protocol_path,
              "protocol_sha256": hashlib.sha256(canonical(protocol)).hexdigest(),
              "commit": head,
              "commit_time_iso": _git(root, "show", "-s", "--format=%cI", head).stdout.strip(),
              "git_blobs": blobs, "remote_ref": remote_ref,
              "published_at_commitment": published,
              "published_check": "server" if query_server else "local_tracking_ref",
              "inputs": snapshot(root, names),
              "note": ("Commit the record itself and publish it before producing data; "
                       "a commit date can be forged and only an external timestamp is strong.")}
    write_new_json(out, record)
    return record


def committed_protocol(root: Path, record: dict) -> dict:
    """Return the protocol exactly as committed, after verifying the anchor."""
    root = root.resolve()
    if record.get("kind") != "git_anchored_protocol":
        raise ValueError("A git-anchored commitment is required")
    commit = record["commit"]
    if _git(root, "cat-file", "-e", commit + "^{commit}", check=False).returncode:
        raise ValueError("Committed protocol commit is not present in this repository")
    for name, blob in record["git_blobs"].items():
        if _committed_blob(root, commit, name) != blob:
            raise ValueError("Committed object differs from the commitment: " + name)
    protocol = _load_committed_json(root, commit, record["protocol_path"])
    if hashlib.sha256(canonical(protocol)).hexdigest() != record["protocol_sha256"]:
        raise ValueError("Commitment protocol hash does not match the committed protocol")
    _validate_protocol(protocol)
    return protocol


def history_conflicts(root: Path, record: dict, protocol: dict) -> list[dict]:
    """Other committed versions of the protocol path with the same experiment_id."""
    path = record["protocol_path"]
    conflicts = []
    for commit in _git(root, "rev-list", "--all", "--", path).stdout.split():
        blob = _committed_blob(root, commit, path)
        if blob is None or blob == record["git_blobs"][path]:
            continue
        try:
            other = _load_committed_json(root, commit, path)
        except (ValueError, UnicodeDecodeError):
            continue
        if other.get("experiment_id") == protocol["experiment_id"]:
            conflicts.append({"commit": commit,
                              "protocol_sha256": hashlib.sha256(canonical(other)).hexdigest()})
    return conflicts


def _first_added(root: Path, path: str) -> str | None:
    commits = _git(root, "log", "--all", "--diff-filter=A", "--format=%H", "--", path).stdout.split()
    return commits[-1] if commits else None


def audit_v2(root: Path, record: dict, result: dict, query_server: bool = False,
             require_published: bool = False) -> dict:
    """Evaluate a result against the committed protocol, never the record's copy."""
    root = root.resolve()
    protocol = committed_protocol(root, record)
    names = list(record["git_blobs"])
    for name in names:
        if _working_blob(root, name) != record["git_blobs"][name]:
            raise ValueError("Committed input changed after the commitment: " + name)
    # Inputs were verified through git blob ids (portable across CRLF/LF
    # checkouts); evaluate against a fresh byte snapshot of the same files.
    receipt = evaluate_receipt(root, {"kind": "prospective_protocol", "protocol": protocol,
                                      "inputs": snapshot(root, names)}, result)
    commit = record["commit"]
    artifacts = [_norm(a) for a in result["artifacts"]]
    planned = [_norm(p) for p in protocol["planned_artifacts"]]
    preexisting = [a for a in artifacts if _committed_blob(root, commit, a) is not None]
    unplanned = [a for a in artifacts if a not in planned]
    outside = []
    for artifact in artifacts:
        first = _first_added(root, artifact)
        if first is not None and _git(root, "merge-base", "--is-ancestor", commit, first,
                                      check=False).returncode:
            outside.append({"artifact": artifact, "first_added_in": first})
    conflicts = history_conflicts(root, record, protocol)
    published = None
    if record.get("remote_ref"):
        published = remote_contains(root, commit, record["remote_ref"], query_server)
    failures = {"artifacts_present_at_commitment": preexisting,
                "unplanned_artifacts": unplanned,
                "artifacts_added_outside_commitment_descendants": outside,
                "other_protocol_versions_same_experiment": conflicts}
    published_ok = bool(published) if require_published else True
    receipt.update({"schema": 2, "commitment_commit": commit,
                    "published_verified_at_audit": published,
                    "published_check": "server" if query_server else "local_tracking_ref",
                    **failures,
                    "criteria_passed": receipt["passed"],
                    "passed": bool(receipt["passed"] and published_ok
                                   and not any(failures.values())),
                    "residual_limits": ("A protocol first committed after the data were "
                                        "produced is not detectable here; use an external "
                                        "timestamp and data custody for confirmatory claims."),
                    "note": "Mechanical audit; independent recomputation and review remain required."})
    return receipt


def main() -> None:
    """Commit-check, verify or audit with explicit paths; outputs are never overwritten."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    commit = commands.add_parser("commit")
    commit.add_argument("--protocol", required=True)
    commit.add_argument("--sources", nargs="+", required=True)
    commit.add_argument("--out", type=Path, required=True)
    commit.add_argument("--remote-ref")
    commit.add_argument("--allow-unpublished", action="store_true")
    commit.add_argument("--query-server", action="store_true")
    verify = commands.add_parser("verify")
    verify.add_argument("--commitment", type=Path, required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("--commitment", type=Path, required=True)
    audit.add_argument("--result", type=Path, required=True)
    audit.add_argument("--out", type=Path, required=True)
    audit.add_argument("--query-server", action="store_true")
    audit.add_argument("--require-published", action="store_true")
    args = parser.parse_args()
    read = lambda path: json.loads(path.read_text(encoding="utf-8"))
    if args.command == "commit":
        record = commit_protocol(args.root, args.protocol, args.sources, args.out,
                                 args.remote_ref, args.allow_unpublished, args.query_server)
        print(json.dumps({"commit": record["commit"],
                          "published_at_commitment": record["published_at_commitment"]}))
    elif args.command == "verify":
        record = read(args.commitment)
        protocol = committed_protocol(args.root, record)
        print(json.dumps({"verified": True,
                          "other_protocol_versions_same_experiment":
                              history_conflicts(args.root.resolve(), record, protocol)}))
    else:
        receipt = audit_v2(args.root, read(args.commitment), read(args.result),
                           args.query_server, args.require_published)
        write_new_json(args.out, receipt)
        print(json.dumps({"passed": receipt["passed"]}))
        if not receipt["passed"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
