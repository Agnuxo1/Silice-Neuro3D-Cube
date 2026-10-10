#!/bin/sh
# GLASS-009c-VACIO. Lotes de corridas en vacio, solo CPU. Un hijo por trozo (<30 s), estado en disco.
# Uso: sh validacion_vacio_lote.sh S1     -> D2 (barrido f,p) + linea de base, dominio 128, dx 0,5 (N=256)
#      sh validacion_vacio_lote.sh S23    -> D4 (dx 0,25, N=512, dominio 128) + D1 ampliado (dominio 256, dx 0,5, N=512)
MODE=$1
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p vacio_out vacio_estados
# chain TH DOM DX FRAC P PER TOTAL: ejecuta los trozos en orden para una configuracion
chain() {
  th=$1; dom=$2; dx=$3; f=$4; p=$5; per=$6; tot=$7
  log="vacio_out/log_th$th-dom$dom-dx$dx-f$f-p$p.txt"
  c=0
  while [ $((c * per)) -lt "$tot" ]; do
    timeout 170 python -B validacion_vacio_run.py "$th" "$dom" "$dx" "$f" "$p" 2.5 "$tot" "$per" "$c" >> "$log" 2>&1 \
      || echo "FALLO th=$th dom=$dom dx=$dx f=$f p=$p trozo=$c" >> vacio_out/fallos.txt
    c=$((c + 1))
  done
}
if [ "$MODE" = "S1" ]; then
  for th in 0 0.02 0.05 0.08; do
    for fp in "0.2 4" "0.2 2" "0.2 6" "0.1 4" "0.3 4"; do
      set -- $fp
      chain "$th" 128 0.5 "$1" "$2" 400 800 &
    done
  done
  wait
  echo done > vacio_out/S1_DONE
fi
if [ "$MODE" = "S23" ]; then
  # N=512: trozos de 160 pasos (~22 s), como mucho 3 hijos a la vez para no saturar la CPU
  rm -f vacio_out/fallos.txt
  chain "0" 128 0.25 0.2 4 160 800 &
  chain "0.02" 128 0.25 0.2 4 160 800 &
  chain "0.05" 128 0.25 0.2 4 160 800 &
  wait
  chain "0.08" 128 0.25 0.2 4 160 800 &
  chain "0.02" 256 0.5 0.2 4 160 800 &
  chain "0.08" 256 0.5 0.2 4 160 800 &
  wait
  echo done > vacio_out/S23_DONE
fi
