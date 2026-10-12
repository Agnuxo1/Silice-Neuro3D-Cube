"""Extract the complete agent kit embedded in the companion Markdown guide.

Only labeled files are extracted. Existing different files, traversal,
symlinks and unexpected file types are rejected before anything is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


def extract(guide: Path, destination: Path) -> dict:
    """Create the labeled source files after validating the whole batch."""
    text = guide.read_text(encoding="utf-8")
    fence = chr(96) * 3
    pattern = re.compile(
        r"^" + fence + r"(python|json|text) file=([A-Za-z0-9_./-]+)\r?\n"
        r"(.*?)^" + fence + r"\s*$", re.MULTILINE | re.DOTALL)
    root = destination.resolve()
    entries = []
    seen = set()
    for match in pattern.finditer(text):
        language, name, source = match.groups()
        rel = Path(name)
        if name in seen or rel.is_absolute() or ".." in rel.parts:
            raise ValueError("Duplicate or unsafe source path")
        seen.add(name)
        if not (name == "extract_agentkit.py" or name.startswith("agentkit/")
                or name == "tests/test_agentkit.py"):
            raise ValueError("Path is outside the declared kit")
        expected = {"python": ".py", "json": ".json", "text": ".txt"}[language]
        if rel.suffix != expected:
            raise ValueError("Source language and extension disagree")
        path = root / rel
        current = root
        for part in rel.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError("Source destination must not be a symlink")
        data = source.encode("utf-8")
        if path.exists() and (not path.is_file() or path.read_bytes() != data):
            raise FileExistsError("Refusing to overwrite different file: " + name)
        entries.append((name, path, data))
    if len(entries) < 10:
        raise ValueError("Guide is incomplete or its labeled code blocks are missing")
    for name, path, data in entries:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with path.open("xb") as output:
                output.write(data)
    manifest = {"guide_sha256": hashlib.sha256(guide.read_bytes()).hexdigest(),
                "files": {name: hashlib.sha256(data).hexdigest()
                          for name, _, data in entries}}
    print(json.dumps(manifest, indent=2))
    return manifest


def main() -> None:
    """Extract into the already reviewed isolated checkout."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--guide", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    extract(args.guide, args.destination)


if __name__ == "__main__":
    main()
