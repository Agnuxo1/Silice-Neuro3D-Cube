#!/bin/bash
# Full modal sweep: 20 cases x 6 meshes, one process per case and mesh (CONTRATO-BARRIDO-MODAL.md)
cd "$(dirname "$0")"
for a in 6 10; do for dn in -0.003 -0.005; do for t in 3 6 9 12 18; do for N in 500 700 900 1100 1400 1800; do
  python -B barrido_modal.py $a $t $dn $N >> barrido/log.txt 2>&1 || echo "FAILED a=$a t=$t dn=$dn N=$N" >> barrido/log.txt
done; done; done; done
echo ALLDONE >> barrido/log.txt
