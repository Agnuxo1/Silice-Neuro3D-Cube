#!/bin/bash
# 4 geometries x 4 families, 4 parallel jobs (CONTRATO-VECTORIAL-GEOMETRIA.md)
cd "$(dirname "$0")"
printf "%s\n" "-0.005 6 HE11" "-0.005 6 TE01" "-0.005 6 TM01" "-0.005 6 HE21" "-0.005 12 HE11" "-0.005 12 TE01" "-0.005 12 TM01" "-0.005 12 HE21" "-0.003 6 HE11" "-0.003 6 TE01" "-0.003 6 TM01" "-0.003 6 HE21" "-0.003 12 HE11" "-0.003 12 TE01" "-0.003 12 TM01" "-0.003 12 HE21" | xargs -P 4 -L 1 python -B trinchera_job.py > trinchera_jobs.log 2>&1
echo ALLDONE >> trinchera_jobs.log
