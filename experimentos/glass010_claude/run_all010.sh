cd "$(dirname "$0")"
for i in 0 1 2 3 4 5; do timeout 30 python run010.py $i >>out/log.txt 2>>out/err.txt || echo "FAIL/TIMEOUT case $i" >> out/failures.txt; done
echo done > out/ALLDONE
