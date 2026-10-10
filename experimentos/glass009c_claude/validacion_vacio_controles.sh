#!/bin/sh
# GLASS-009c-VACIO, enmienda 1 (CONTRATO-VACIO.md). Controles, solo CPU. Hijos troceados, estado en disco.
# Uso: sh validacion_vacio_controles.sh CSIN   -> control sin esponja (sigma=0), dominio 128, dx 0,5, theta 0; 0,02; 0,05; 0,08
#      sh validacion_vacio_controles.sh CREF   -> referencia dominio 512 (N=1024), dx 0,5, con esponja de linea base, theta 0,05; 0,08
MODE=$1
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p vacio_out vacio_estados
# chain TH DOM DX FRAC P PER TOTAL: trozos en orden para una configuracion (VACIO_SMAX heredado del entorno del subshell)
chain() {
  th=$1; dom=$2; dx=$3; f=$4; p=$5; per=$6; tot=$7
  log="vacio_out/log_ctrl_${MODE}_th$th-dom$dom-dx$dx-f$f-p$p.txt"
  c=0
  while [ $((c * per)) -lt "$tot" ]; do
    timeout 170 python -B validacion_vacio_run.py "$th" "$dom" "$dx" "$f" "$p" 2.5 "$tot" "$per" "$c" >> "$log" 2>&1 \
      || echo "FALLO control $MODE th=$th dom=$dom trozo=$c" >> vacio_out/fallos_controles.txt
    c=$((c + 1))
  done
}
if [ "$MODE" = "CSIN" ]; then
  for th in 0 0.02 0.05 0.08; do
    ( export VACIO_SMAX=0; chain "$th" 128 0.5 0.2 4 400 800 ) &
  done
  wait
  echo done > vacio_out/CSIN_DONE
fi
if [ "$MODE" = "CREF" ]; then
  for th in 0.05 0.08; do
    chain "$th" 512 0.5 0.2 4 40 800 &
  done
  wait
  echo done > vacio_out/CREF_DONE
fi
