cd "$(dirname "$0")"
r(){ timeout 30 python run009c2.py "$@" >>out2/log.txt 2>>out2/err.txt || echo "FAIL/TIMEOUT $*" >> out2/failures.txt; }
for th in 0.02 0.05 0.08; do r $th 128 0.5 2.5 800 800 0; done
r 0 128 0.5 1.25 1600 800 0; r 0 128 0.5 1.25 1600 800 1
for th in 0 0.05; do for c in 0 1 2 3; do r $th 256 0.5 2.5 800 200 $c; done; done
echo done > out2/ALLDONE
