cd "$(dirname "$0")"
for th in 0 0.02 0.05 0.08; do for dom in 128 256; do timeout 30 python run009c.py $th $dom 1.0 >>out/log.txt 2>>out/err.txt || echo "FAIL/TIMEOUT $th $dom 1.0" >> out/failures.txt; done; done
timeout 30 python run009c.py 0 128 0.5 >>out/log.txt 2>>out/err.txt || echo "FAIL/TIMEOUT 0 128 0.5" >> out/failures.txt
echo done > out/ALLDONE
