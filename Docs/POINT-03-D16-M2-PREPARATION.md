# Preparación de D16-M2

Los controles previos aprobaron antes de cualquier propagación T96 de M2:

- Siete archivos numéricos verificados; 47777 grados de libertad libres;
  potencia inicial 1,0000000000000002 y dimensiones consistentes.
- Dos tramos manufacturados por familia, tres grados de libertad,
  comparados con exponencial densa: máximo error 2,7408682e-13 frente
  al límite 1e-10. Hash previo incorrecto rechazado en ambas familias.
- Evaluador: control idéntico aprobado; errores sólo de fase y de
  amplitud rechazados. La igualdad de potencias no basta para aprobar.
- Generación de cinco fuentes diferenciadas, con hashes de las fuentes
  originales y sintaxis comprobados; M1 se conserva sin modificar.

El primer control del trabajador falló por FileNotFoundError: se lanzó
antes de que existiera el informe del evaluador requerido. No propagó
T96 ni generó un campo sintético. Se conservó íntegro en
`point03_d16_mid_refined_worker_dependency_race_20261008` y se repitió
después de terminar la dependencia, usando exactamente el mismo
trabajador. La repetición aprobó. No se eliminó ni sobreescribió el fallo.

Los recursos fueron simulados únicamente en el control manufacturado de
software. La ejecución óptica deberá cumplir los recursos reales del
[contrato M2](POINT-03-D16-MID-REFINED-TIME-CONTRACT.md).
El trabajador probado tiene SHA-256
`bd47274d4526c59f079ae399f086e7bd212c0b917d7b082cf46862a7e3a9ef93`.

Los informes están en `resultados/codex/point03_d16_mid_refined_*`.
Estos controles no constituyen resultados de propagación en la malla
intermedia ni un cierre espacial. La tarea 1 permanece abierta.
