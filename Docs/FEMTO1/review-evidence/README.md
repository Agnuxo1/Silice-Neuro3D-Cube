# Evidencia retenida de la revisión de distancias FEMTO-1

Los dos scripts son el código efímero exacto utilizado en las dos llamadas originales de revisión, guardado después. No se ha repetido el cálculo durante esta retención. `results-record-reconstruction.json` reconstruye los resultados de aquellas salidas y lo identifica explícitamente; no es el resultado de una nueva ejecución. Los hashes de entradas se calcularon al retener la evidencia. El tiempo de 0,7472836999804713 s es el del cálculo original, no el de la retención.

Reejecución opcional, desde PowerShell (un hilo, sin test, sin entrenamiento ni escritura de fuentes):

```powershell
Set-Location -LiteralPath 'D:\PROJECTS\Silice-FEMTO1-20261013'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:NUMEXPR_NUM_THREADS='1'
& 'D:\SiliceAgentkit\.venv-closure\Scripts\python.exe' -B 'D:\PROJECTS\.cognition\femto1\review-evidence\classify_saved_pairs.py'
& 'D:\SiliceAgentkit\.venv-closure\Scripts\python.exe' -B 'D:\PROJECTS\.cognition\femto1\review-evidence\audit_saved_segments.py'
```

Verificar primero que DRC y geometría conservan los hashes del JSON. La primera salida da 314 infracciones entre puntos y 192 banderas conservadoras. La segunda da 2 infracciones de segmentos adicionales y 190 banderas que cumplen la distancia de polilínea. Así se obtiene 316/190. El tiempo de una nueva ejecución será distinto.

La exclusión de 60 µm en extremos comunes, tolerancia de coincidencia 1e-12 m y cutoff de determinante 1e-30 se conservan tal cual. La regla usa desigualdad estricta: distancia menor que umbral. El auditor conserva el filtro original de candidatos por puntos medios y calcula mínimo sobre proyecciones de extremos y punto estacionario interior válido. Esto es distancia de la representación por polilíneas, no una certificación de acoplo/fabricación ni un cambio de los 506 fallos registrados por el DRC.

La revisión original y el informe principal están en `D:/PROJECTS/.cognition/femto1/INDEPENDENT-REVIEW.md`. No se han abierto datos sellados o test_X. Los scripts solamente leen DRC y geometría.
