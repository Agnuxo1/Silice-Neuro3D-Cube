# Diagnóstico posterior de los controles longitudinales

Análisis aritmético de resultados ya conocidos G2/H2, no ensayo prospectivo
ni criterio nuevo. No propagación, ajuste de umbrales o cierre del punto3.
Potencias normalizadas por la entrada; misma geometría/input en cada N.

Discrepancia absoluta del ADI frente a la referencia exponencial H2,
para el detector de campo cúbico:

| N | dz0,625µm | dz0,3125µm | dz0,15625µm | Orden por diferencias sucesivas |
|---:|---:|---:|---:|---:|
|400|5,18337831e-7|9,33552792e-8|3,02992542e-8|2,75269748|
|500|6,84445918e-7|1,99739568e-7|4,16125685e-8|1,61602726|

Los órdenes por cocientes de discrepancias directas son2,473/1,623
paraN400 y1,777/2,263 paraN500. El detector de intensidad muestra la
misma pauta; se conserva en JSON. No se identifica una potencia única
de error temporal sobre estos tres pasos. Los órdenes por diferencias
siguen fuera del intervalo G[1,8;2,2], por tanto G mantieneFAIL.

Las discrepancias directas con dz0,3125/0,15625 sí satisfacen los límites
H registrados1e-6/2,5e-7 respectivamente. Esto verifica un contraste local
de potencia entre dos algoritmos del mismo operador discretizado. No
demuestra régimen asintótico, error continuo exacto, fase/campo convergidos
ni causa única de la irregularidad de órdenes. Las particiones de la
referencia exponencial tampoco son dos algoritmos independientes.

Inferencia: un cociente irregular puede coexistir con una discrepancia
directa pequeña; sus criterios responden preguntas diferentes. No se
atribuyen los residuos a redondeo, splitting o geometría sin aislarlos.
Datos: `resultados/codex/point03_temporal_reference_diagnostic_20261007.json`.
