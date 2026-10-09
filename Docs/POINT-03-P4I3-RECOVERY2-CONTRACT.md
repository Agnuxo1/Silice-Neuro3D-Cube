# P4I3: corregir la adquisición de recursos y conservar 89 tramos

La primera recuperación calculó satisfactoriamente 75–89 y se detuvo
antes de lanzar el tramo 90. No existe campo nuevo del tramo 90.
La causa fue una carrera entre dos lecturas de RAM: la condición del
bucle vio ≥6 GiB, pero la segunda lectura del control previo bajó de
ese umbral. Ese controlador y su resultado operativo negativo se
conservan sin editar. No es un fallo de la propagación ni de su precisión.

Registrar esta corrección antes de campos nuevos. Reauditar los 89
tramos aceptados (74 originales y 15 de la primera recuperación),
incluyendo los recursos y hashes. Continuar sólo 90–256 en otro
directorio; no repetir los 89 anteriores ni adoptar el tramo 75 original
con informe de recursos fallido. Mismo trabajador numérico sin editar,
misma entrada y matrices, misma referencia Padé y mismos criterios.

Tomar una única muestra de RAM disponible y disco por intento de reserva.
Si esa RAM es ≥6 GiB y el disco >2 GiB, registrar esa muestra y lanzar
el hijo. Si la RAM es menor, esperar y volver a muestrear. No convertir
una segunda lectura fluctuante en una excepción. El control del propio
trabajador sigue exigiendo RAM>3 GiB al inicio y final, sin relajarlo.

La espera acumulada entre ambas recuperaciones sigue limitada a 1800 s;
la primera consumió 140,005 s. El presupuesto original sigue siendo
22000 s desde el inicio UTC original, incluyendo las interrupciones.
Hijos ≤360 s/corte370 s, un hilo, sin cerrar aplicaciones ajenas.
Un nuevo fallo detendrá este controlador y quedará registrado.

El auditor final reutilizará el algoritmo de auditoría P4I3, ajustando
únicamente la fecha aplicable a 1–74, 75–89 y 90–256 y los contadores:
167 campos nuevos y 441 retenidos. Verificará también la identidad de
los 89 enlaces, las dos interrupciones y las reservas de 6 GiB registradas
para todos los tramos posteriores al 74. Guardar la fuente adaptada
antes de calcular. No alterar ninguna bandera negativa anterior.

P5C sin iniciar, malla0,28 sin generar, cuadratura de rigidez pendiente.
Tarea 1 actual abierta. JEV fallback local por bloqueo heredado.
