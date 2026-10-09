# Punto 3: recuperación y evaluación definitiva del ensayo E

Fecha de recuperación: 7 de octubre de 2026. E está completo y cerrado como ensayo negativo. El punto 3 permanece abierto; no se avanzó al barrido modal. E no se relanzó.

## Evidencia recuperada

E terminó el 7 de octubre a las 01:13 UTC (03:13 Europe/Madrid). Conserva las ocho trayectorias, 144 checkpoints y 28800 pasos. Tiempo completo registrado: 1665.463 s. Los campos y métricas finales son válidos bajo E1–E3; el resultado científico es FAIL.

| Malla | dz (um) | Pasos | Potencia del núcleo / entrada | Potencia total / entrada |
|---:|---:|---:|---:|---:|
| 256 | 0.625 | 3200 | 0.332284365695362 | 0.767839755151854 |
| 320 | 0.625 | 3200 | 0.332624488454598 | 0.767617649312944 |
| 400 | 0.625 | 3200 | 0.332809534003563 | 0.767385983553483 |
| 500 | 0.625 | 3200 | 0.332873191359150 | 0.767199737862566 |
| 400 | 1.25 | 1600 | 0.332811505412368 | 0.767391457843859 |
| 500 | 1.25 | 1600 | 0.332874960168753 | 0.767205201530420 |
| 400 | 0.3125 | 6400 | 0.332809109229886 | 0.767384620173981 |
| 500 | 0.3125 | 6400 | 0.332872707399293 | 0.767198370509513 |

## Dictamen con el protocolo original

Órdenes espaciales: 2.727861056 y 4.782065705. Su desacuerdo relativo es 42.956429%, por encima del 20% preregistrado.

Predicción congelada: 0.332910208992994; resultado N500: 0.332873191359150. Residual 3.70176338e-05, frente al límite 6.36573556e-06: 5.815138 veces el límite.

Control longitudinal N400: q=2.214460705, fuera de [1.8,2.2]. N500: q=1.869819471, dentro. La discrepancia pequeña de dz no justifica cambiar la banda. Los radios y el indicador de incertidumbre aceptados que dependen del control fallido permanecen nulos. Los indicadores finales bloqueados no demuestran que el error real supere 1e-3.

El criterio antiguo basado en decrecimiento de diferencias pasa en E, pero sus criterios de orden/predicción más fuertes fallan. El Q4 histórico y el fallo B conservan sus resultados originales. No se usa un GCI aprobado ni se certifica un límite continuo.

## Auditoría de recuperación

[Auditoría](../resultados/codex/point03_recovery_20261007_run2/audit.json): 1653 archivos contrastados con los hashes guardados, 1050 fuentes/evidencias originales, ocho cadenas completas. Se descomprimieron y recalcularon los 144 estados: potencias reproducidas a tolerancia absoluta 1e-12. Sin solver óptico ni nuevos campos.

Incidentes propios retenidos: dos invocaciones del evaluador original no eran compatibles con un intento ya finalizado (restricciones de ubicación e inventario de outputs). No se modificó ese evaluador. El primer auditor de recuperación interpretó incorrectamente el enlace JSON y el contador acumulado de los checkpoints; se corrigió y se obtuvo el PASS citado. Todos los informes fallidos se conservan, sin sustituir datos E.

## Diagnóstico F y continuación

F fue registrado en 2387c7d. Un error de tipo WindowsPath en la comprobación de disco se retuvo antes de medir; corrección 5cd658d. La ejecución posterior completó los controles gaussianos, finitud, positividad y tres cuadraturas para dos reconstrucciones independientes del observable.

| Reconstrucción | Orden 1 | Orden 2 | Residual de predicción | Límite |
|---|---:|---:|---:|---:|
| field | 4.418984647 | 4.610678531 | 1.2935208e-06 | 2.95977829e-06 |
| intensity | 4.416599621 | 4.609687176 | 1.30219298e-06 | 2.957652e-06 |

Diferencia de los dos observables en N500: 1.60044663e-08. Ambos pasan los criterios espaciales como diagnóstico. N400 mantiene q fuera de banda. Esto identifica una sensibilidad a la reconstrucción de intensidad: cobertura geométrica exacta no significa integral exacta del campo. No demuestra que el detector sea la única fuente de error ni convalida E.

El nuevo [contrato G](POINT-03-RECONSTRUCTED-REFINEMENT-CONTRACT.md), commit40f46d0, conserva los umbrales y añade pasos menores y una predicción antes de una nueva propagación N640. Los resultados de G deben revisarse por separado.

## Alcance y fuentes contrastadas

El modelo es escalar/paraxial y usa materiales y trazos ideales. Ningún ensayo aquí certifica frontera/reflexión, campo complejo/fase, polarización/Maxwell, precisión experimental, fabricación o comportamiento de una red física.

- [NASA, convergencia espacial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html), consulta 2026-10-07: Richardson exige revisar consistencia y régimen asintótico; la convergencia de un funcional y la del campo son afirmaciones distintas.
- [Hansen–Henningsson, análisis espacio–tiempo](https://arxiv.org/abs/1512.05931), resumen consultado 2026-10-07: el orden combinado exige condiciones sobre la discretización espacial. Su ejemplo difusivo no valida nuestro índice óptico discontinuo.
- [Eça–Hoekstra, JCP262](https://doi.org/10.1016/j.jcp.2014.01.006), PDF del instituto MARIN recuperado: procedimiento de verificación de solución basado en refinamiento y dispersión. El texto advierte sobre orden observado superior al formal y estimaciones de error demasiado pequeñas (p.108). Por ello los órdenes reconstruidos cercanos a cuatro no se interpretan como un esquema espacial de cuarto orden ni como garantía del error continuo; la malla N640 es una comprobación adicional. No suministra una garantía física para este caso.
- [Hao Wu, potencial discontinuo](https://doi.org/10.1017/S100489790000074X), resumen del editor consultado: el tratamiento de condiciones de salto en la interfaz es una vía documentada para lograr convergencia. Solo se accedió al resumen; no se afirma haber implementado o verificado ese método.

JEV: diagnóstico local v2-doctor=ready; el bloqueo remoto heredado de seguridad se conserva. Las decisiones presentes son fallback local sin aval provenance=jev. No hubo GPU, instalaciones, publicación ni cambios al checkout principal.
