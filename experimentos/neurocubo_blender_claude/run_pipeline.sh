#!/usr/bin/env bash
# Neuro-cube pipeline (CPU, one thread). Usage from the repository root:
#   bash experimentos/neurocubo_blender_claude/run_pipeline.sh real [step]   # after the preregistration commitment
#   bash experimentos/neurocubo_blender_claude/run_pipeline.sh dry  [step]   # software dry run on synthetic data (scratch)
# Steps: checks | train | references | eval | benchmark (default: all, in this order).
set -euo pipefail
MODE=${1:?real or dry}
STEP=${2:-all}
HERE=experimentos/neurocubo_blender_claude
BLENDER=${BLENDER:-D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.exe}
BPY_PYTHON=${BPY_PYTHON:-D:/TOOLS/Blender/blender-4.5.14-windows-x64/4.5/python/bin/python.exe}
PY=${PY:-D:/SiliceAgentkit/.venv-closure/Scripts/python.exe}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0
STATE=D:/PROJECTS/.cognition/neurocubo
if [ "$MODE" = real ]; then
  RES=resultados/agent/neurocubo_20261013
  DATA=$HERE/data
  SEALED=$STATE/sealed
  TASKS="dev03 res47"; SHOW=res47
  TRAIN_ARGS=""; REF_ARGS=""; BENCH_ARGS=""
  OUTSIDE=$STATE/real
else
  RES=$STATE/dry/results
  DATA=$STATE/dry/data
  SEALED=$STATE/dry/sealed
  TASKS="syn"; SHOW=syn
  TRAIN_ARGS="--gains 1 4 --seeds 1 2 --maxiter 30"
  REF_ARGS="--gains 1 4 --seeds 1 2 --maxiter 30"
  BENCH_ARGS="--realizations 2 --recal-maxiter 10 --bootstrap 200"
  OUTSIDE=$STATE/dry/outside
  if [ ! -d "$DATA/syn" ]; then "$PY" -B $HERE/custodian.py seal --task syn --public-dir "$DATA" --sealed-dir "$SEALED"; fi
fi
mkdir -p "$RES" "$OUTSIDE"

# Run Blender, show only our tagged lines, and fail if Blender failed or printed a traceback.
blender_run() {
  local log
  log=$(mktemp)
  "$BLENDER" "$@" > "$log" 2>&1 || { cat "$log"; rm -f "$log"; return 1; }
  grep -E "NEUROCUBO" "$log" || true
  if grep -q "Traceback" "$log"; then cat "$log"; rm -f "$log"; return 1; fi
  rm -f "$log"
}

if [ "$STEP" = all ] || [ "$STEP" = checks ]; then
  blender_run -b --factory-startup -t 1 --python $HERE/build_cube.py -- --check --out-check "$RES/checks/geometry_roundtrip.json"
  "$PY" -B $HERE/test_neurocubo_core.py "$RES/checks/core_tests.json" | tail -3
  for n in 4 8; do
    blender_run -b --factory-startup -t 1 --python $HERE/build_cube.py -- --n $n --ports 0 1 2 3 \
      --out-blend "$OUTSIDE/nominal_N$n.blend"
  done
fi
if [ "$STEP" = all ] || [ "$STEP" = train ]; then
  for task in $TASKS; do for n in 4 8; do
    blender_run -b "$OUTSIDE/nominal_N$n.blend" -t 1 --python $HERE/train_in_blender.py -- --task $task --n $n \
      --data-dir "$DATA" $TRAIN_ARGS --out-dir "$RES/training" --model-out "$RES/models/model_${task}_N$n.json" \
      --blend-out "$OUTSIDE/trained_${task}_N$n.blend" --traj-dir "$OUTSIDE/trajectories" \
      --expected-geometry $HERE/geometry_N$n.json
  done; done
fi
if [ "$STEP" = all ] || [ "$STEP" = references ]; then
  for task in $TASKS; do for n in 4 8; do
    "$PY" -B $HERE/references.py --part sklearn --task $task --n $n --data-dir "$DATA" $REF_ARGS \
      --out "$RES/references/references_${task}_N$n.json"
    # Gain-matched real network: same Python/numpy/scipy stack as the optical training in Blender.
    "$BPY_PYTHON" -s -B $HERE/references.py --part real_matched --task $task --n $n --data-dir "$DATA" $REF_ARGS \
      --out "$RES/references/real_matched_${task}_N$n.json"
  done; done
fi
if [ "$STEP" = all ] || [ "$STEP" = eval ]; then
  for task in $TASKS; do for n in 4 8; do
    blender_run -b "$OUTSIDE/trained_${task}_N$n.blend" -t 1 --python $HERE/blender_eval.py -- --task $task --n $n \
      --data-dir "$DATA" --model "$RES/models/model_${task}_N$n.json" --out "$RES/blender_eval/outputs_${task}_N$n.npz"
  done; done
fi
if [ "$STEP" = all ] || [ "$STEP" = benchmark ]; then
  "$PY" -B $HERE/benchmark.py run --results-dir "$RES" --data-dir "$DATA" --sealed-dir "$SEALED" \
    --protocol $HERE/PROTOCOL-NEUROCUBO.json --tasks $TASKS --show-task $SHOW $BENCH_ARGS
fi
