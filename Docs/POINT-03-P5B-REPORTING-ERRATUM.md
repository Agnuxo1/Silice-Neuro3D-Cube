# P5B: diagnóstico accesorio de distinta dimensión

En el primer adaptador del amortiguador grueso, los controles completos
se calcularon y las matricesD8/D12 se guardaron. Al crear el informe,
el diagnóstico opcional intentó restar una matriz de31549DOF a la
matriz del prototipo74785DOF:ValueError«inconsistent shapes»,exit1.
Esta nota es observación factual del resultado de herramienta; no una
captura de consola reconstruida. Fuente generada y artefactos se conservan.

La recuperación independiente desde las matrices guardadas volvió a
comprobar controles/momentos/simetría/PSD y diferenciaD8/12Mnorm
1,28678e-8m^-1:PASS. No regeneró geometría/matrices ni propagó campos.
Se guarda report_recovered.json, separado de cualquier informe previo.

Antes de adaptar la malla intermedia, el diagnóstico accesorio se marca
no disponible cuando las dimensiones difieren. Los límites y el cálculo
de todos los controles P5B no cambian. Este cambio adicional al adaptador
se declara; no se presenta como transformación original sólo de rutas.
