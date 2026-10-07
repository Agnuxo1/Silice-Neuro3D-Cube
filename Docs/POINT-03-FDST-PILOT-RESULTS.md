# Piloto L1 completo: precisión fina favorable, orden rechazado

Contrato24300fc previo;4341,316s, tres trayectorias nuevas,56checkpoints.
Auditoría independiente: integridad PASS,13fuentes/input inmutables,
56campos rereleídos y dictamen recalculado. Máxima diferencia entre las
dos recomputaciones de potencia cruda1,87628e-14. Punto3 ABIERTO.

| dz (um) | Error relativo de campo | Error potencia campo bilineal | Error potencia intensidad |
|---:|---:|---:|---:|
|0,625|5,9943881e-3|1,8241341e-4|1,8175952e-4|
|0,3125|3,1320975e-5|2,2301506e-6|2,2256568e-6|
|0,15625|5,1448864e-6|4,2117211e-7|4,2103251e-7|

Campo fino<=1e-4 y ambas potencias finas<=1e-6: PASS. Cuadratura,
balance, recursos y finitos: PASS. Órdenes de campo7,5803/2,6059,
potencia campo6,3539/2,4047, intensidad6,3517/2,4022, fuera[3,5;4,5]:
FAIL. El piloto global es FAIL. No cambiar intervalos ni omitir el
paso grueso para convertirlo en una aceptación retrospectiva.

La salida externa del proceso se registró como código1; el manifiesto,
execution y los56hijos confirman trayectorias completas y evaluación
negativa, sin error operativo ni campos pendientes. No hay motivo para
repetirlas. Los controles conocidos recuperan orden4 a pasos menores;
no identifican una causa de T96 ni cambian el resultado L1.

La comparación directa fina cuantifica error contra una referencia del
mismo operador, con la discrepancia R11/R17 de K626 aún declarada. Esto
no establece orden4 para T96 ni convergencia espacial. Una afirmación
distinta de precisión práctica necesita un contrato nuevo y datos de
contraste adicionales, sin sustituir este FAIL ni los de E/G/H/K.
