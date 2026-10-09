"""Fail when a change adds blobs above a size limit.

Compares two revisions and lists the files added or modified between them
whose blob is larger than --limit-mb. Git history is never rewritten by this
tool; it only reports. Large evidence should go to a release asset or an
archive with a SHA-256 manifest, not into new commits (see
Docs/ARCHIVO-Y-TAMANO.md).

Standard library only. Usage:
    python tools/repo_size_guard.py --base <rev> --head <rev> [--limit-mb 10]
"""
from __future__ import annotations

import argparse
import subprocess
import sys

ZERO_SHA = "0" * 40


def git(*args: str) -> str:
    """Run git and return stdout, raising on failure."""
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    return result.stdout


def resolve_base(base: str, head: str) -> str:
    """Use the merge-base with origin/main when the base is missing or all zeros."""
    if not base or base == ZERO_SHA:
        return git("merge-base", head, "origin/main").strip()
    return base


def changed_blobs(base: str, head: str) -> list[tuple[int, str]]:
    """Return (size_bytes, path) for each added or modified blob at head."""
    names = git("diff", "--no-renames", "--diff-filter=AM", "--name-only", "-z", base, head)
    paths = [p for p in names.split("\0") if p]
    if not paths:
        return []
    listing = git("ls-tree", "-r", "-l", head, "--", *paths)
    rows = []
    for line in listing.splitlines():
        meta, path = line.split("\t", 1)
        size = meta.split()[3]
        if size != "-":
            rows.append((int(size), path))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", required=True, help="older revision (or empty / all-zero SHA)")
    parser.add_argument("--head", default="HEAD", help="newer revision (default: HEAD)")
    parser.add_argument("--limit-mb", type=float, default=10.0, help="report blobs above this size in MB")
    args = parser.parse_args(argv)

    base = resolve_base(args.base, args.head)
    limit = args.limit_mb * 1_000_000
    rows = changed_blobs(base, args.head)
    over = sorted((r for r in rows if r[0] > limit), reverse=True)
    print(f"range {base[:10]}..{args.head}: {len(rows)} added/modified blobs, "
          f"{len(over)} above {args.limit_mb:g} MB")
    for size, path in over:
        print(f"  {size / 1e6:8.2f} MB  {path}")
    if over:
        print("FAIL: move these to a release asset or archive with a SHA-256 manifest.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
