"""Check that the committed closure kit matches the guide byte for byte.

The guide (Docs/GUIA-CIERRE-CIENTIFICO-v2-20261012.md) embeds every kit file
as a fenced block labeled `file=`. Two blocks are committed at different
paths so that Codex-owned tests/ is not changed:
  tests/test_agentkit.py -> agentkit/test_v1.py
  extract_agentkit.py    -> tools/extract_agentkit.py
Exit status 1 if any file is missing or differs; nothing is written.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "Docs" / "GUIA-CIERRE-CIENTIFICO-v2-20261012.md"
RELOCATED = {"tests/test_agentkit.py": "agentkit/test_v1.py",
             "extract_agentkit.py": "tools/extract_agentkit.py"}


def main() -> int:
    text = GUIDE.read_text(encoding="utf-8")
    fence = chr(96) * 3
    pattern = re.compile(r"^" + fence + r"(python|json|text) file=([A-Za-z0-9_./-]+)\r?\n"
                         r"(.*?)^" + fence + r"\s*$", re.MULTILINE | re.DOTALL)
    report, bad = {}, []
    for _, name, source in pattern.findall(text):
        target = ROOT / RELOCATED.get(name, name)
        expected = source.encode("utf-8")
        actual = target.read_bytes() if target.is_file() else None
        same = actual == expected
        report[name] = {"committed_as": target.relative_to(ROOT).as_posix(),
                        "sha256": hashlib.sha256(expected).hexdigest(), "identical": same}
        if not same:
            bad.append(name)
    print(json.dumps({"guide_sha256": hashlib.sha256(GUIDE.read_bytes()).hexdigest(),
                      "files": len(report), "mismatches": bad}, indent=1))
    return 1 if bad or len(report) != 28 else 0


if __name__ == "__main__":
    sys.exit(main())
