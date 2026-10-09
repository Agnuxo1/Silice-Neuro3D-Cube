# Evaluación T96/Q4 — 7 de octubre de 2026

**Punto 3: ABIERTO: convergencia local aún no aceptada.**

El ensayo E se recuperó completo, sin relanzarlo: ocho simulaciones, 144 checkpoints y 28 800 pasos. Su evaluación científica es negativa. Los archivos originales y los fallos históricos se conservaron.

## Contrastes realizados

| Estudio | Resultado | Evidencia principal |
|---|---|---|
| E original | FAIL | Discrepancia de órdenes 42,956%; predicción N500 fuera de tolerancia; control longitudinal N400 fuera del intervalo registrado |
| F, reconstrucción del detector | Diagnóstico favorable, sin cierre | Predicciones espaciales pasan; el control longitudinal N400 sigue fallando |
| G2, refinamiento ADI | FAIL | Control longitudinal N400/N500 y predicción N640 incumplen; integridad de 233 chunks válida |
| H2, referencia exponencial | FAIL | 76 checkpoints auditados; referencias temporales y nueva predicción N640 contrastadas |

H1 y G1 sufrieron fallos operativos conservados. Sus recuperaciones G2/H2 reutilizaron resultados válidos y repitieron sólo el trabajo necesario, con contratos y límites fijados previamente. H2 reutiliza 48 checkpoints de H1 y añade 28, con particiones de 11/17 tramos en N640.

## Referencia H2: resultados y criterios

| N | dx (µm) | Potencia núcleo / entrada, campo reconstruido | Partición fina |
|---:|---:|---:|---:|
| 256 | 0.5 | 0.332612646565 | 8 |
| 320 | 0.4 | 0.332834679822 | 8 |
| 400 | 0.32 | 0.332917608624 | 8 |
| 500 | 0.256 | 0.332947040298 | 8 |
| 640 | 0.2 | 0.332959782890 | 17 |

| Criterio H2 | Campo | Intensidad |
|---|---:|---:|
| Orden observado | 4.41350306/4.64235222 | 4.41115875/4.64139153 |
| Discrepancia relativa de órdenes | 0.0492959489 | 0.0496042578 |
| Predicción N640 | 0.332958085 | 0.332958063 |
| Potencia N640 | 0.332959783 | 0.332959772 |
| Residual N640 | 1.69808979e-06 | 1.70886666e-06 |
| Límite previo N640 | 1.27425916e-06 | 1.27477793e-06 |
| Predicción aceptada | False | False |

Consistencia de referencias: True; contraste temporal directo ADI: True; cuadratura: True; controles gaussianos: True.

Los indicadores de incertidumbre son condicionales: no son cotas rigurosas ni intervalos con una cobertura probabilística acreditada. Se limitó el exponente del indicador espacial a 2; los órdenes altos del observable no demuestran ese orden para el campo.

## Diagnóstico de dispersión J

Se aplicó a las cinco referencias completas y consistentes. No cambia el dictamen de E/G/H2. La adaptación retuvo un control sintético fallido del indicador seleccionado y añadió una envolvente distinta; sus controles favorables no prueban cobertura universal.
- field: indicador seleccionado en N640 0.000248545546; envolvente 0.000786948476.
- intensity: indicador seleccionado en N640 0.000248213298; envolvente 0.000785968254.

## Contraste de detector K

Los detectores bilineales se verificaron con momentos exactos, 16 celdas de referencia independientes y Gaussianas con fases conocidas. Sus cuatro mallas iniciales pasan. Se congelaron predicciones N640/N626 antes de medir los nuevos funcionales; K640 reutiliza una trayectoria y no constituye una nueva simulación independiente.

| Detector | N640 medido | Residual | Límite previo | Pasa todos los criterios K640 |
|---|---:|---:|---:|---|
| field | 0.332802745 | 7.65878694e-06 | 1.12588279e-05 | True |
| intensity | 0.332864201 | 7.32366774e-06 | 7.35883907e-06 | True |

Resultado K640: True. Una aceptación por K requiere además el nuevo ensayo prospectivo N626; este informe no atribuye ese resultado si no existe evidencia separada.

## Prueba prospectiva independiente N626

Geometría nueva con 48 celdas de referencia; 28 checkpoints auditados; predicciones procedentes exclusivamente de N320/400/500. N640 no se utilizó para reajustarlas.

| Detector | Potencia medida | Predicción previa | Residual | Límite | Pasa |
|---|---:|---:|---:|---:|---|
| field | 0.332802661 | 0.332788155 | 1.45057771e-05 | 1.12503848e-05 | False |
| intensity | 0.332866769 | 0.332852639 | 1.41303153e-05 | 7.61571002e-06 | False |

Diferencia relativa entre referencias: 5.87269258e-10. Resultado del ensayo nuevo: False. E/G/H2 conservan sus resultados propios.
- Concordancia de potencia field: diferencia 3.90550703e-10; límite previo 1e-10; pasa: False.
- Concordancia de potencia intensity: diferencia 3.90625809e-10; límite previo 1e-10; pasa: False.

También fallan ambas concordancias de potencia entre las particiones 11/17. El diagnóstico cúbico posterior revela potencia N626 superior a N640; no se utiliza como aceptación ni demuestra una causa.

## Piloto temporal independiente FDST

Segundo integrador del mismo operador espacial FD: difracción por transformada seno y composición de cuarto orden. Entradas N626 reutilizadas por hash. Los controles con matriz densa y modos conocidos pasaron antes de T96. Los criterios del piloto se congelaron antes de las tres trayectorias ópticas.

| dz (µm) | Error relativo de campo frente R17 | Diferencia de potencia, campo bilineal | Diferencia de potencia, intensidad bilineal |
|---:|---:|---:|---:|
| 0.625 | 0.0059943881 | 0.000182413409 | 0.000181759516 |
| 0.3125 | 3.13209753e-05 | 2.23015057e-06 | 2.22565676e-06 |
| 0.15625 | 5.14488636e-06 | 4.21172111e-07 | 4.2103251e-07 |

Resultado temporal FDST: False; 56 checkpoints auditados. Criterios individuales: {'integrity': True, 'field_fine': True, 'power_fine': True, 'observed_order': False, 'quadrature': True}.

Órdenes observados al dividir dz por dos:
- field: 7.58033954 / 2.60591802.
- power_field: 6.35392686 / 2.40465931.
- power_intensity: 6.35165597 / 2.40222758.

Este piloto sólo contrasta el error temporal. Su resultado no cierra la convergencia espacial, no sustituye los fallos anteriores ni valida Maxwell o la fabricación. La referencia Taylor presenta la discrepancia de potencia registrada en K626; no se afirma exactitud ilimitada.

## Alcance y continuidad

Modelo escalar paraxial ideal: longitud 2 mm, dominio 128 µm, núcleo de radio 6 µm, longitud de onda 1550 nm. Se comparó potencia fraccional del núcleo, sin renormalizar salidas ni alinear fases. La referencia exponencial resuelve el operador espacial discretizado, no el continuo exacto ni Maxwell.

Las particiones de un mismo algoritmo exponencial son controles de consistencia. Particiones relacionadas pueden compartir incrementos internos; no se presentan como dos algoritmos independientes. Campo complejo, fase, frontera, perfiles medidos y fabricación quedan sujetos a los puntos posteriores.

El checkout principal se preservó. La copia aislada retiene fuentes, contratos, predicciones, arrays completos y fallos. El paquete adjunto contiene informes y hashes, no todos los arrays. JEV: fallback local identificado; el bloqueo de seguridad remoto heredado se conservó, sin recomendación remota válida.

## Fuentes primarias consultadas

- [NASA: convergencia espacial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html).
- [SciPy 1.15.1: acción de la exponencial](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.sparse.linalg.expm_multiply.html).
- [Eça–Hoekstra 2014: estimación con dispersión](https://doi.org/10.1016/j.jcp.2014.01.006). Adaptación diagnóstica explícita, sin importar una garantía de cobertura.
- [Vassallo 1997: interfaces y discretización óptica](https://opg.optica.org/josaa/abstract.cfm?uri=josaa-14-12-3273). Sólo resumen del editor.
- [Henning–Peterseim 2017: potenciales abruptos](https://arxiv.org/html/1608.02267). Formulación e hipótesis examinadas; método distinto, sin transferencia automática del teorema.

- [Yoshida 1990, artículo original: composición de órdenes superiores](https://tlakoba.w3.uvm.edu/math6737/for_final_topics/SSM_1990_Yoshida.pdf). Secciones2–4 examinadas; la aplicación con absorción se contrastó numéricamente.
- [SciPy1.15.1: transformada seno multidimensional](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.fft.dstn.html).

## L2: precisión práctica frente a referencias calculadas

L2 utiliza un contrato nuevo, fijado antes de su única trayectoria N400. Reutiliza N626 fino por hash; conserva L1 negativo. No exige ni demuestra orden cuatro, convergencia espacial o exactitud del continuo.

| N | Error relativo de campo | Error de potencia campo / intensidad | Cota respecto a referencia y controles | Todos los criterios L2 |
|---:|---:|---:|---:|---|
| 400 | 6.88801679e-07 | 6.35024986e-08 / 6.35218939e-08 | 1.057151e-06 | True |
| 626 | 5.14488636e-06 | 4.21172111e-07 / 4.2103251e-07 | 7.89385208e-06 | True |

Resultado L2: True. Sus 32 checkpoints nuevos y criterios fueron recalculados por un auditor separado. La cota se refiere a la solución discretizada calculada; la concordancia de referencias es empírica y no certifica su error exacto.

El control sintético de la cota pasó, con una incidencia de versionado conservada: código y contrato se escribieron antes del cálculo, pero el primer commit falló y el commit válido fue posterior. Esa incidencia auxiliar no afecta a los contratos ópticos L1/L2 congelados antes de sus trayectorias.

## M1: prueba nueva N767, con predicción estricta

Criterios bbc891d y pronósticos60684a5 congelados antes de generar la geometría. Área y48celdas independientes pasan. Referencias exponenciales R19/R31 y un cálculo FDST de20480pasos:90checkpoints auditados. Las cuatro primarias se midieron nuevamente desde sus arrays; el auditor recalculó las predicciones sin llamar al evaluador M1.

| Detector | Potencia N767 | Predicción previa | Residuo | Límite previo | Nuevo orden | Pasa M1 |
|---|---:|---:|---:|---:|---:|---|
| field | 0.33284362 | 0.332853321 | 9.70036036e-06 | 4.08747039e-06 | 3.22924299 | False |
| intensity | 0.332886411 | 0.332896475 | 1.00641869e-05 | 2.22102657e-06 | 4.06005591 | False |

Resultado M1: False; condiciones globales: {'reference_field': True, 'reference_bound': True, 'temporal_field': True, 'temporal_bound': True, 'quadrature': True}.
Referencia: campo relativo 3.41195483e-10. Segundo integrador: campo relativo 1.98989125e-06; cota respecto a la referencia 3.05225693e-06.

Los límites nuevos de concordancia de potencia de referencia (1e-8) corresponden al presupuesto práctico de M1. El FAIL original de K626 a1e-10 permanece intacto. Las bandas amplias M0 sólo son diagnósticas y no determinan la aceptación M1.
- field: indicador espacial 0.00011711884, indicador combinado 0.00016008654; condiciones {'holdout': False, 'order': False, 'reference_power': True, 'temporal_power': True, 'uncertainty': True}.
- intensity: indicador espacial 6.36393735e-05, indicador combinado 0.00010660702; condiciones {'holdout': False, 'order': False, 'reference_power': True, 'temporal_power': True, 'uncertainty': True}.

Estos indicadores y el cierre, si se acepta, se limitan a potencia escalar local con entrada, geometría, dominio nominal y longitud fijados. No son cotas rigurosas ni cobertura probabilística; no validan toda la fase/campo/frontera, Maxwell ni fabricación. N767 impar utiliza la misma regla de coordenadas y fantasmas que la serie: la posición discreta de los bordes varía O(dx).
