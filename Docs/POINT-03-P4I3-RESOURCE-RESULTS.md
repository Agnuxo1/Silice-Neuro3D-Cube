# P4I3: interrupción por memoria y recuperación registrada

La referencia Radau de 65536 pasos se interrumpió en el tramo 75 tras
4556,720 s. El fallo ocurrió en la comprobación final de recursos: no
se cumplía RAM disponible >3 GiB o disco >2 GiB. El disco tenía más
de 480 GiB libres en las lecturas próximas; la memoria disponible
fluctuaba. La lectura que falló no se guardó, por lo que no se inventa
un valor exacto de RAM en ese instante.

El auditor de la recuperación comprobó los 74 tramos anteriores:
integridad aprobada, hashes y cadenas correctos, campos complejos
finitos, potencia de masa y recursos aprobados en cada tramo.
El residuo máximo entre potencia guardada y recalculada fue cero.
El último tramo válido corresponde a 18944 de los 65536 pasos.

El campo del tramo 75 también quedó guardado, pero su informe está
marcado como fallido y carece de comprobación final de recursos aprobada.
Se conserva como evidencia del incidente y se excluye de la cadena
aceptada. Su potencia de masa recalculada es 0,999348901070940;
la del tramo 74 válido es 0,999372783077878. Estas potencias se expresan
como fracción de la entrada inicial normalizada a uno.

No existe un resultado temporal final a 2 mm de P4I3. El fallo operativo
no permite declarar que haya aprobado o rechazado la precisión temporal.
Los resultados negativos completos P4I y P4I2 sí conservan sus dictámenes.

La recuperación se registró en d69f1b8 antes de campos nuevos: reutilizar
los 74 tramos válidos y calcular exclusivamente 75–256, en otro directorio.
Mantiene los límites científicos, el trabajador numérico y el presupuesto
original de 22000 s, incluyendo el intervalo de interrupción. Añade una
reserva previa de al menos 6 GiB y espera máxima acumulada de 1800 s.
No se cierran ni modifican aplicaciones ajenas. La recuperación comenzó
tras 140 s de espera y guardó un nuevo tramo 75 con los controles del
trabajador aprobados. La auditoría independiente final sigue pendiente.

La primera continuación alcanzó el tramo 89 y se detuvo antes de lanzar
el 90 por una carrera entre dos lecturas de RAM del control previo.
Sus 15 tramos nuevos quedaron aprobados por el trabajador; una segunda
auditoría parcial verificó los 89 retenidos con residuo máximo cero.
Se registró la corrección en dcf43af/20ac751 antes de nuevos campos:
usar una sola muestra de recursos y continuar exclusivamente 90–256.
Los controles científicos, las reservas y el presupuesto original permanecen.

El punto 3 histórico, tarea 1 actual, sigue abierto. P5C no se ha iniciado
y la malla fina de 0,28 micrómetros no se ha generado. Antes del contraste
espacial también queda pendiente verificar la sensibilidad de la rigidez
FEM a la cuadratura en elementos curvos. La simetría de una matriz no
certifica por sí sola la precisión de sus integrales.

Fuentes, fallos y campos se preservan en la copia aislada. JEV fallback
local por bloqueo heredado; ninguna simulación externa se atribuye.
