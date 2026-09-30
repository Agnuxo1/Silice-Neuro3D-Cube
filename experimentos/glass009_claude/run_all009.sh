cd "$(dirname "$0")"
for c in G0 K1 K2 K3 K5 cont t48 t96 t192 t88; do timeout 30 python run009.py $c >/dev/null 2>out/err_$c.txt || echo "FAIL/TIMEOUT $c" >> out/failures.txt; done
for i in 0 1 2 3; do timeout 30 python run009.py K4dz $i >/dev/null 2>out/err_K4dz$i.txt || echo "FAIL/TIMEOUT K4dz $i" >> out/failures.txt; done
for i in 0 1; do timeout 30 python run009.py K4dx $i >/dev/null 2>out/err_K4dx$i.txt || echo "FAIL/TIMEOUT K4dx $i" >> out/failures.txt; done
echo done > out/ALLDONE
