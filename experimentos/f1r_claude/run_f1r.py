"""F1R: registered replacement of the lost F1 run (D16 fine mesh, h = 0.35 um).

The numerical worker is Codex's original scripts/run_point03_d16_fine_time.py,
unchanged and SHA-checked. Only the orchestration of the original run() and
the original audit() are derived here by exact text substitutions, each of
which must occur exactly once (see SUBSTITUTIONS). Everything else (steps,
chunks, solvers, criteria, child budget 360 s, global budget 32000 s, wait
budget 900 s) is the registered F1 contract (Docs/POINT-03-D16-FINE-TIME-CONTRACT.md).

Usage:
  python -B run_f1r.py run   --root <extracted F1 package root> --out <root>/resultados/agent/f1r_20261013
  python -B run_f1r.py audit --root <root> --out <same folder>
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import sys
import textwrap

PACKAGE_SHA256 = "d79a777e2d5d1d955205c039aef95faae9c54efd38ca40fc3815828ad616368f"
WORKER_SHA256 = None  # read from the package's own worker-controls report at run time
NEW_DEADLINE = datetime(2026, 10, 16, 0, 0, tzinfo=timezone.utc)

RUN_SUBSTITUTIONS = [
    ("out.is_relative_to(ROOT/'resultados/codex')", "out.is_relative_to(ROOT/'resultados/agent')"),
    ("reservation['available_ram_bytes'] > 6*1024**3", "reservation['available_ram_bytes'] > 3*1024**3"),
]
AUDIT_SUBSTITUTIONS = [
    ("datetime(2026, 10, 9, 13, 45, tzinfo=timezone.utc)", "datetime(2026, 10, 16, 0, 0, tzinfo=timezone.utc)"),
    ("event['reservation']['available_ram_bytes'] > 6*1024**3", "event['reservation']['available_ram_bytes'] > 3*1024**3"),
]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def derive(module, function_name: str, substitutions):
    source = textwrap.dedent(inspect.getsource(getattr(module, function_name)))
    for old, new in substitutions:
        assert source.count(old) == 1, "substitution must occur exactly once: " + old
        source = source.replace(old, new)
    namespace = module.__dict__
    exec(compile(source, module.__file__ + ":" + function_name + "[F1R]", "exec"), namespace)
    return namespace[function_name], source


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("run", "audit"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    scripts = root / "scripts"
    sys.path.insert(0, str(scripts))
    worker_path = scripts / "run_point03_d16_fine_time.py"
    controls = json.loads((root / "resultados/codex/point03_d16_fine_worker_controls_20261009/report.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(worker_path.read_bytes()).hexdigest() == controls["tested_worker_sha256"], "worker changed"
    if args.mode == "run":
        f1 = load(worker_path, "run_point03_d16_fine_time")
        f1.DEADLINE = NEW_DEADLINE
        run, _ = derive(f1, "run", RUN_SUBSTITUTIONS)
        return run(args.out.resolve())
    auditor = load(scripts / "audit_point03_d16_fine_time.py", "audit_point03_d16_fine_time")
    audit, _ = derive(auditor, "audit", AUDIT_SUBSTITUTIONS)
    out = args.out.resolve()
    result = audit(out)
    result["f1r_substitutions"] = {"run": RUN_SUBSTITUTIONS, "audit": AUDIT_SUBSTITUTIONS}
    with (out / "integrity_audit.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, default=str)
    print(json.dumps({k: result[k] for k in ("integrity_pass", "temporal_precision_pass",
                                             "relative_field_difference", "power_differences",
                                             "PSD_observable_bounds")}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
