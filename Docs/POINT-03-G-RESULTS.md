# Punto 3: ensayo G y recuperación G2

## Dictamen

G2 completó las nueve trayectorias previstas. Resultado científico **FAIL**.
No cierra punto3 ni permite iniciar el barrido modal. G1 conserva estado
FAILED operativo; G2 es una recuperación explícita en otra carpeta.

Los criterios espaciales de las cuatro primarias256/320/400/500 pasan:
órdenes4.416937 y4.622569, desacuerdo4.448%, residualN5001.386944e-6
frente2.953806e-6. Los controles temporales y la predicciónN640 fallan.

| Control | Resultado | Criterio previo | Dictamen |
|---|---:|---:|---|
| q400, campo reconstruido |2.752697476|[1.8,2.2]|FAIL|
| q500, campo reconstruido |1.616027256|[1.8,2.2]|FAIL|
| N640, residual campo |1.543968146e-6|<=1.267913190e-6|FAIL|
| N640, residual intensidad |1.554255947e-6|<=1.268407003e-6|FAIL|
| Diferencia detectoresN500 |1.587803333e-8|<=1e-7|PASS|
| Diferencia detectoresN640 |1.093990076e-8|<=1e-7|PASS|

PredicciónN640 campo0.33295837520181587 congelada antes del primer paso;
valor final0.33295991916996165. Para intensidad0.3329583539741138 vs
0.3329599082300609. No se reajustó con campo parcial ni final.
Controles gaussianos, cuadratura y geometríaN640 pasan. Los indicadores
aceptados bloqueados por q fallido siguen nulos; no se presenta GCI aprobado.

## Trayectorias de potencia

Potencias del núcleo relativas a la entrada, detector de campo reconstruido;
z2mm, ancho128um, modelo escalar fijo. Las ocho trayectorias recuperadasE
conservan resultados originales aunque cuatro se reutilizan aquí.

| N | dz (um) | Pcore | Papel |
|---:|---:|---:|---|
|256|0.3125|0.3326128156621074|primaria nueva|
|320|0.3125|0.3328348400220126|primaria nueva|
|400|0.3125|0.3329177019789733|primaria reutilizadaE|
|500|0.3125|0.3329472400380665|primaria reutilizadaE|
|640|0.3125|0.3329599191699617|malla prospectiva nueva|

## Incidente operativo y conservación

G1 se detuvo a2827.081s en hijo6404600→4800:195 pasos y reserva31s
alcanzada. Se conservó campo parcial4795/logs/JSON sin usarlo para continuar.
No apareció un rechazo numérico en el registro de fallo. G2, contrato
3372780/correcciónEOFc682c11 antes de cálculos, reinició desde el checkpoint
completo4600, con hijos100pasos y mismos límites. Recalculó únicamente
los1800 pasos restantes, incluyendo195 fallidos; recuperó ocho casos
terminados y23chunks640. Duración287.814s, sin nuevos fallos de propagación.

La copia del evaluador sólo cambia verificación operativa de100/200pasos.
No cambian fórmulas, Gaussianos, reconstrucción, parámetros ni umbrales.
El preflight conserva el diff exacto y prueba que el worker cambia sólo
longitud del chunk. Una comprobación de formato detectó EOF extra, corregido
y congelado antes de propagar; los commits anteriores se preservan.

[AuditoríaG2](../resultados/codex/point03_reconstructed_20261007_G2/integrity_audit.json)
PASS:233checkpoints completos descomprimidos y potencias recalculadas,
234intentos incluyendo el fallido, identidades/dz/pasos/cadenas/arrays/
permutaciones/hashes/recursos y fecha de predicción comprobados. Los603
outputsoriginalesE quedan intactos. Pasos válidos nuevosG44800;195pasos
operativos repetidos no cuentan como nuevos resultados independientes.

Nota de registro: executionG2 hereda los campos error/diagnostic de G1
aunque status=completed. Son historia del intento recuperado, no otro fallo.
El dictamen se basa en status, assessment y auditoría, y no se edita el JSON
original para eliminar ese texto. El código de retorno visible de la shell
fue no nulo, coherente con rechazo científico; no sustituye esos tres registros.

## Siguiente contraste dentro del punto3

H pre-registradoc04558b comenzó después de completar/auditar G2. Resuelve
el mismo operador espacial sin separación ADI, mediante expm_multiply;
compara particiones y errores temporales directos. G1/G2/E/B mantienen sus
resultados. H no cambia G ni garantiza que la predicción espacial se cumpla.
El punto3 permanece abierto hasta evaluar H y cualquier ensayo necesario.

JEV fallbacklocal identificado, bloqueo remoto heredado preservado.
SinGPU/instalaciones/push, checkout principal preservado. Ningún resultado
es una medición de una guía fabricada ni una validación Maxwell/fase/frontera.
