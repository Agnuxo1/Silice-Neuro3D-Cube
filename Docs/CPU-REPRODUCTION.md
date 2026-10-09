# Reproduce the CPU research environment

## Supported, tested target

Two targets are validated for the CPU test suite (51 tests):

- **Windows 10 x64, CPython 3.13.7**: the full path, including the one-command
  bootstrap and the environment verification with 339 tracked hashes. This is
  the original verification host.
- **Linux x86_64 (Ubuntu 24.04), CPython 3.13.7**: the CPU suite only, run by
  GitHub Actions ([workflow](.github/workflows/cpu-tests.yml)). Bootstrap and
  `verify_environment.py` have not been validated on Linux.

This is a CPU-only reproduction path; it neither installs the optional GPU
extra nor runs CUDA.
The general package metadata accepts Python 3.10 and newer, but that is not
a claim that every Python version or platform has been validated.

## One-command setup and verification

From the repository directory, use PowerShell:

```powershell
& 'C:\Python313\python.exe' scripts/bootstrap_cpu.py
```

The script creates the local `.venv`, installs exact wheel versions checked
against `requirements/cpu-win-py313.lock`, installs the local package, and
runs the CPU verification pipeline. It does not change global packages.
It refuses to reuse an unrelated environment. Review the retained summary
and logs under `resultados/codex/env_*` if any stage reports a failure.
The default command downloads the pinned wheels from the explicit PyPI index.
For an existing directory of those exact wheels, use the offline option:

```powershell
& 'C:\Python313\python.exe' scripts/bootstrap_cpu.py --wheelhouse D:\path\to\wheels
```

To repeat verification after setup without reinstalling:

```powershell
& '.\.venv\Scripts\python.exe' scripts/verify_environment.py
```

To run the complete lightweight CPU test suite directly:

```powershell
& '.\.venv\Scripts\python.exe' -B scripts/check.py
```

## Linux (CI-validated path)

The CPU suite runs on Ubuntu 24.04 with the hash-checked Linux lock. From the
repository root:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements/cpu-linux-py313.lock
.venv/bin/python -B scripts/check.py
```

`scripts/check.py` runs the 51 CPU tests, limits the process to one thread and
exits with status 1 on any failure, skip or boundary violation. It does not
write reports unless `--report` is given. The automated run is recorded in
GitHub Actions for each commit on `main`.

## Dependency groups

- Base package: NumPy, used by the CPU numerical modules.
- `research`: SciPy and psutil, used by CMT/radial experiments and supervisors.
- `test`: psutil, needed when tests import resource-aware supervisors.
- `visualization`: Matplotlib and Pillow, for the existing GIF tools.
- `gpu`: PyTorch, for separately authorised GPU work. Installing this extra
  does not grant a resource reservation or validate a CUDA configuration.

The tested CPU lock includes NumPy 2.2.6, SciPy 1.15.1 and psutil 6.1.1,
plus pip 25.3, setuptools 82.0.1 and wheel 0.45.1 for the installation.
The wheel manifest records exact filenames, hashes and dependency metadata.

## What a successful verification means

The package can be installed and imported outside the repository; declared
versions are present and compatible; every current CPU test executes; the
representative CMT and BPM experiments produce complete reports; and the
historical GLASS-007 V2 report passes its own saved-evidence audit.

GLASS-003 V2 deliberately retains its historical convergence failure.
Reproducing that failure is a successful environment check only when the
full output, balance controls, case counts and scientific flags agree.
Q4 for the 96-track GLASS-009d reference also remains a scientific failure.
Neither result is relabelled as converged by this environment verification.

The pipeline uses unique report paths and records file hashes before and
after execution. It never runs peer scripts that overwrite fixed paths.
Historical shell scripts and `ALLDONE` files are not independent proof of
success. CPU children are bounded to one numerical-library thread and
40 seconds each. No physical device or global numerical convergence is
certified by this setup check.

## Primary references

- https://pip.pypa.io/en/stable/topics/repeatable-installs/
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
