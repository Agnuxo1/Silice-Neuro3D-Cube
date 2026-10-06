# Point 01 — CPU environment reproduction contract

Date: 2026-10-06. Base: a15025159cf8c67477e8b1020e1cc368586a2cda.
The user requested sequential completion of the attached research roadmap.
This contract is fixed before the isolated-environment verification run.

## Scope and authority

Point 01 covers dependency declaration, an isolated installation, and a
representative CPU verification suite. Installing the declared dependencies
inside a new project virtual environment is part of the requested work.
No global packages are changed. No GPU or Blender execution is included.
The earlier GPU time window has expired; this CPU contract does not renew it.
JEV advice is unavailable under the existing block; local analysis is explicit.
Physical modelling and historical acceptance thresholds remain unchanged.

## Reference environment

Observed host: Windows 10 x64; CPython 3.13.7.
Observed versions: NumPy 2.2.6, SciPy 1.15.1, psutil 6.1.1,
setuptools 82.0.1, pip 25.3, wheel 0.45.1.
The original environment ran all 51 current CPU tests successfully.
The initial PowerShell stderr-redirection failure is retained separately;
it is an orchestration error and is not a scientific test result.
An explicit Python subprocess supervisor avoids that shell ambiguity.

## Frozen acceptance criteria

E1. Install into a new virtual environment without system site packages.
Use the six exact package versions above and SHA-256 checked wheel hashes.
Declare scientific, test, visualisation and optional GPU dependencies by use.
Do not claim that this Windows/Python lock validates other platforms.

E2. Install the local silice package non-editably. Import it from outside
the repository with isolated Python; its file must be inside the environment.
Run pip check successfully and record actual installed package versions.

E3. Run every currently discovered CPU test: at least 51 tests, zero errors,
zero failures and zero skips. Record discovery and execution counts. Do not
import torch in this test process or initialise a GPU through another API.

E4. Re-run the GLASS-004 CMT audit into a new report. Preserve its original
nominal/control/peer-integrity gates and retain its intensity/field caveats.

E5. Re-run GLASS-003 V2 into a new complete 15-case report. Its historical
general convergence failure is an expected scientific result, not a setup
failure. Require the original balance checks and matching result flags;
a return code alone is insufficient to classify a completed experiment.

E6. Run the existing GLASS-007 V2 saved-report auditor. Require 13 cases,
four reused reports, nine later children and its own saved gates. Preserve
Q4 failure for the 96-track reference and the boundary/convergence limits.
This is a historical-report audit, not a new wave propagation experiment.

E7. Before and after verification, hash all tracked source and historical
result files. They must be unchanged by verification. New reports and logs
have unique paths. Record commands, return codes, timing, host, Python,
package versions, numerical library configuration and thread settings.

E8. Limit each numerical child to 40 seconds and one numerical-library
thread. Installation and metadata processes have separate bounded timeouts.
Always retain a summary, including failed or incomplete stages.

## Interpretation and review

Passing E1–E8 closes only Point 01 on the tested platform. It does not
certify physical fabrication, full convergence, Maxwell accuracy or GPU
performance. Any failure remains reported until diagnosed and rerun under
a recorded implementation correction; scientific thresholds are not relaxed.
An independent code-and-evidence review precedes closure of this point.

## Primary documentation

- https://pip.pypa.io/en/stable/topics/repeatable-installs/
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
