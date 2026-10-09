"""Resumable checkpoint for long CPU runs (support item of the 22-task plan).

A run is a list of named steps. Each finished step stores its result together with a SHA-256 of its
inputs. The file is written atomically (temporary file + os.replace), so an interrupted run resumes at the
first step that is missing or whose inputs changed. Stores data only, never credentials.
Keep checkpoint files on D:, not on C:.

Usage:  python -B tools/resumable_checkpoint.py --selftest
"""
import hashlib
import json
import os
import pathlib
import sys
import tempfile

sys.dont_write_bytecode = True


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


class Checkpoint:
    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.state = {"steps": {}}
        if self.path.exists():
            self.state = json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=self.path.name, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=1)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)

    def done(self, name, inputs):
        rec = self.state["steps"].get(name)
        return rec is not None and rec["inputs_sha256"] == digest(inputs)

    def result(self, name):
        return self.state["steps"][name]["result"]

    def record(self, name, inputs, result):
        self.state["steps"][name] = {"inputs_sha256": digest(inputs), "result": result}
        self._save()


def run(path, steps):
    """steps: list of (name, inputs, fn); fn(inputs) returns a JSON-serialisable result."""
    cp = Checkpoint(path)
    out = {}
    for name, inputs, fn in steps:
        if cp.done(name, inputs):
            out[name] = cp.result(name)
            continue
        res = fn(inputs)
        cp.record(name, inputs, res)
        out[name] = res
    return out


def selftest():
    base = pathlib.Path(__file__).resolve().parent / ".selftest"
    path = base / "run.json"
    calls = {"a": 0, "b": 0, "c": 0}

    def fa(x):
        calls["a"] += 1
        return x * 2

    def fb(x):
        calls["b"] += 1
        if calls["b"] == 1:
            raise RuntimeError("simulated interruption")
        return x + 1

    def fc(x):
        calls["c"] += 1
        return x - 3

    steps = [("a", 5, fa), ("b", 7, fb), ("c", 9, fc)]
    try:
        run(path, steps)
    except RuntimeError:
        pass
    assert calls == {"a": 1, "b": 1, "c": 0}, calls
    out = run(path, steps)  # resume: a is reused, b is computed, c is computed
    assert out == {"a": 10, "b": 8, "c": 6}, out
    assert calls == {"a": 1, "b": 2, "c": 1}, calls
    out = run(path, [("a", 5, fa), ("b", 7, fb), ("c", 10, fc)])  # changed input of c only
    assert out["c"] == 7 and calls == {"a": 1, "b": 2, "c": 2}, (out, calls)
    for f in base.glob("*"):
        f.unlink()
    base.rmdir()
    print("selftest ok:", calls)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        selftest()
    else:
        raise SystemExit("usage: python -B tools/resumable_checkpoint.py --selftest")
