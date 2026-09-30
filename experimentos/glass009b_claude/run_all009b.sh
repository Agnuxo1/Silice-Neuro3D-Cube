cd "$(dirname "$0")"
for c in "K1w 0.5" "K1w 0.4" "Cw 0.5" "T96w 0.5"; do timeout 30 python run009b.py $c >/dev/null 2>>out/err.txt || echo "FAIL/TIMEOUT $c" >> out/failures.txt; done
for c in Cw T96w; do for i in 0 1; do timeout 30 python run009b.py $c 0.4 $i >/dev/null 2>>out/err.txt || echo "FAIL/TIMEOUT $c 0.4 $i" >> out/failures.txt; done; done
echo done > out/ALLDONE
