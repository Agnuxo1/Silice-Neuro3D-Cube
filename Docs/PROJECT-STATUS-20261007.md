# Actualización factual — 7 de octubre de 2026

Complementa [inventario del 6 de octubre](PROJECT-STATUS.md), conservado
sin cambios. Trabajos en copia aislada, checkout principal preservado.

| Punto | Estado verificable | Evidencia nueva |
|---|---|---|
| 1. Entorno reproducible | Cerrado para la plataforma comprobada | Sin cambiar el alcance de las 51 pruebas históricas |
| 2. Inventario | Cerrado por reconciliación, con esta actualización | Se distinguen resultados, controles y trabajos pendientes |
| 3. T96/Q4 | **Abierto** | E recuperado completo; G2/H2/K626 negativos; K640 favorable; L1 negativo de orden; L2 positivo para precisión longitudinal práctica; M1 completo y auditado negativo |
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
su piloto L1 terminó y conserva el fallo del orden observado. El estudio
L2 terminó en3225,980s y pasó todos los criterios de precisión práctica
en N400/N626;32campos nuevos y18fuentes se auditaron por separado.
Errores máximos de potencia6,36e-8 y4,22e-7 respectivamente, ambos<=1e-6.
No demuestra orden4 ni convergencia espacial; punto3 continúa abierto.

Se congelaron pronósticos diagnósticos N767/959/1199 antes de preparar
sus geometrías, con ajustes de cinco mallas y sensibilidad incluyendo
N626 negativo. Las bandas no bastan para un cierre. Los costes sintéticos
se registraron antes de ejecutar; no constituyen trayectorias T96.

M1 N767 terminó en12064,711s, sin relanzamiento ni fallo operativo.
Contrato `bbc891d`, predicciones `60684a5`, auditor separado `4fbde6e`;
90tramos y20fuentes auditados. Geometría, referencia y precisión temporal
pasan. Predicción y estabilidad de orden FALLAN en ambos detectores:
discrepancias29,93% y41,58% frente al20% registrado. El punto3 sigue
abierto; no iniciar el barrido modal antes de su cierre.

N1: contraste analítico1D registrado después del FAIL M1,18combinaciones,
controles PASS y diagnóstico de órdenes inestables respaldado. No es
convergencia T96 ni identificación causal del fallo. Se necesita controlar
muestreo/dominio del problema real antes de otra afirmación de convergencia.

J: diagnóstico de dispersión aplicado a cinco referencias consistentes,
sin cierre ni cobertura probabilística. Fallo de un control sintético
del indicador seleccionado retenido, envolvente distinta identificada.

La convergencia ensayada es local a potencia del núcleo, T96 ideal,
entrada fijada,2mm/128µm y ecuación escalar. Frontera/campo/fase,
Maxwell, perfiles medidos y fabricación necesitan sus pruebas propias.

Informes: [E](POINT-03-ANALYTIC-PROPAGATION-RESULTS.md),
[G](POINT-03-G-RESULTS.md), [H2/K640](POINT-03-H2-K640-RESULTS.md),
[particiones internas](POINT-03-EXPONENTIAL-PARTITION-RESULTS.md),
[L1](POINT-03-FDST-PILOT-RESULTS.md),
[L2](POINT-03-FDST-ACCURACY-RESULTS.md),
[M1](POINT-03-M1-RESULTS.md), [N1](POINT-03-N1-RESULTS.md).
Arrays, fuentes congeladas, predicciones y fallos se retienen en D:.
JEVfallbacklocal identificado; bloqueo remoto heredado conservado.
