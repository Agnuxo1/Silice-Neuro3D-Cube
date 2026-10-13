#!/usr/bin/env bash
# Run from repository root. Default is factual status of the retained run.
# bash scripts/femto1/run_pipeline.sh femto1 verify
# Final Blender steps remain closed until DRC and physical evidence pass.
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="scripts/femto1:."
PY=${PY:-D:/SiliceAgentkit/.venv-closure/Scripts/python.exe}
exec "$PY" -B scripts/femto1/run_pipeline.py "${1:-femto1}" "${2:-status}" "${@:3}"
