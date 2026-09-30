cd "$(dirname "$0")"
k=T96d
for dxv in 0.5 0.625; do timeout 30 python run009d.py $k $dxv >/dev/null 2>>out/err.txt || echo "FAIL/TIMEOUT run2 $k $dxv" >> out/failures.txt; done
for i in 0 1; do timeout 30 python run009d.py $k 0.4 $i >/dev/null 2>>out/err.txt || echo "FAIL/TIMEOUT run2 $k 0.4 $i" >> out/failures.txt; done
echo done > out/ALLDONE2
