"""Run the project's light CPU tests and optionally retain a JSON report."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
import unittest

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"

ROOT = Path(__file__).resolve().parents[1]
# Tests also import the repository's script namespace. Make both roots
# explicit instead of depending on a caller's PYTHONPATH or current directory.
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))


def main(argv: list[str] | None = None) -> int:
    """Execute all discovered CPU tests and record failures without hiding them."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="New JSON path under resultados/codex.")
    args = parser.parse_args(argv)
    target = args.report.resolve() if args.report is not None else None
    if target is not None:
        if not target.is_relative_to(ROOT / "resultados" / "codex"):
            parser.error("the report must be under resultados/codex")
        if target.exists():
            parser.error("the report already exists; historical evidence is never overwritten")
        target.parent.mkdir(parents=True, exist_ok=True)

    started = time.monotonic()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    expected = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    # The CPU suite prepares NumPy operators and tests guards, without
    # importing PyTorch. Treat an unexpected import as a boundary violation.
    torch_imported = "torch" in sys.modules
    successful = (
        result.wasSuccessful()
        and not result.skipped
        and result.testsRun == expected
        and expected > 0
        and not torch_imported
    )
    report = {
        "schema": "silice.cpu-tests.v1",
        "tests_run": result.testsRun,
        "tests_expected": expected,
        "failures": [{"test": str(test), "traceback": detail} for test, detail in result.failures],
        "errors": [{"test": str(test), "traceback": detail} for test, detail in result.errors],
        "skipped": [{"test": str(test), "reason": reason} for test, reason in result.skipped],
        "successful": successful,
        "elapsed_s": time.monotonic() - started,
        "gpu_initialized": False if not torch_imported else None,
        "torch_imported": torch_imported,
        "source_root": str(ROOT),
        "scope": "CPU software tests; no physical-device or global-convergence certification",
    }
    if target is not None:
        with target.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, allow_nan=False)
            handle.write("\n")
    if torch_imported:
        print("CPU boundary violation: the test process imported torch.", file=sys.stderr)
    return 0 if successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
