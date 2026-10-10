#!/usr/bin/env bash
# GLASS-009c-VACIO D5: lote de corridas en CPU. Un hilo por proceso, python -B, temporales en D:.
# Argumentos de cada trabajo: W0_um THETA DOM_um DX_um FRAC P DZ_um TOTAL EVERY TAG
set -u
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export TMPDIR=/d/PROJECTS/.cognition/tmp_glass009c_d5 TEMP=/d/PROJECTS/.cognition/tmp_glass009c_d5 TMP=/d/PROJECTS/.cognition/tmp_glass009c_d5
mkdir -p "$TMPDIR"
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE" || exit 1
JOBS="$HERE/validacion_vacio_D5_trabajos.txt"
cat > "$JOBS" <<'EOF'
6 0 256 0.5 0.2 4 2.5 800 40 W6_d256_base
8 0 256 0.5 0.2 4 2.5 800 40 W8_d256_base
12 0 256 0.5 0.2 4 2.5 800 40 W12_d256_base
6 0 128 0.5 0.2 4 2.5 800 40 K0a_repro_w6_d128_base
12 0 256 0.25 0.2 4 2.5 800 40 G12a_w12_d256_dx025
12 0 256 0.5 0.2 4 1.25 1600 80 G12b_w12_d256_dz125
EOF
# Cuatro procesos a la vez; cada uno tiene pico de memoria bien por debajo de 2 GB (N<=1024).
xargs -P 4 -L 1 python -B validacion_vacio_D5_run.py < "$JOBS"
echo "LOTE_D5_DONE rc=$?"
