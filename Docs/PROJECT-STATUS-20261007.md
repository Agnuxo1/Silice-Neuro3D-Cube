# Actualización factual — 7 de octubre de 2026

Complementa [inventario del 6 de octubre](PROJECT-STATUS.md), conservado
sin cambios. Trabajos en copia aislada, checkout principal preservado.

| Punto | Estado verificable | Evidencia nueva |
|---|---|---|
| 1. Entorno reproducible | Cerrado para la plataforma comprobada | Sin cambiar el alcance de las 51 pruebas históricas |
| 2. Inventario | Cerrado por reconciliación, con esta actualización | Se distinguen resultados, controles y trabajos pendientes |
| 3. T96/Q4 | **Abierto** | E recuperado completo; G2/H2 negativos; K640 favorable; K626 completo y negativo; contraste FDST registrado |
| Barrido modal y siguientes | Pendientes | Se mantiene el orden; no iniciados durante el punto 3 |

E: ocho simulaciones y controles longitudinales recuperados sin relanzar;
144 checkpoints y28800pasos auditados, FAIL de predicción/orden/control.
G2: recuperación limitada a los pasos pendientes tras fallo operativo G1;
integridad233chunks PASS, criterios de predicción y longitudinales FAIL.
H2:48checkpoints retenidos de H1 y28nuevos,76auditados PASS; predicción
N640FAIL por factor1,333. Controles temporal/referencia/detector pasan.
No reinterpretar controles favorables como aprobación de la predicción.

K: reconstrucciones bilineales verificadas antes de medir nuevos
observables; predicciones640/626 congeladas. K640 pasa ambos métodos;
la intensidad queda próxima a su límite. K626 terminó con integridad
PASS y resultados negativos en ambas predicciones y ambas concordancias
de potencia. Punto3 abierto. El nuevo kernelFDST pasa controles conocidos;
su piloto temporal está registrado y no permite cerrar convergencia espacial.

J: diagnóstico de dispersión aplicado a cinco referencias consistentes,
sin cierre ni cobertura probabilística. Fallo de un control sintético
del indicador seleccionado retenido, envolvente distinta identificada.

La convergencia ensayada es local a potencia del núcleo, T96 ideal,
entrada fijada,2mm/128µm y ecuación escalar. Frontera/campo/fase,
Maxwell, perfiles medidos y fabricación necesitan sus pruebas propias.

Informes: [E](POINT-03-ANALYTIC-PROPAGATION-RESULTS.md),
[G](POINT-03-G-RESULTS.md), [H2/K640](POINT-03-H2-K640-RESULTS.md),
[particiones internas](POINT-03-EXPONENTIAL-PARTITION-RESULTS.md).
Arrays, fuentes congeladas, predicciones y fallos se retienen en D:.
JEVfallbacklocal identificado; bloqueo remoto heredado conservado.
