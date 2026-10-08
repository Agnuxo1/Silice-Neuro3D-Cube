# Recuperación controlada de P4I3 tras fallo confirmado de recursos

P4I3 se detuvo a los 4556,720 s. Los tramos 1–74 quedaron completos;
el tramo 75 alcanzó el cálculo del campo, pero falló el control de memoria
al terminar. Su informe no contiene un control final de recursos aprobado.
El padre registró `status=failed`, fuentes sin cambios y el fallo del hijo.
Se conservan íntegros esos informes y campos, incluidos los del tramo 75.
No existe todavía una evaluación temporal final de esta trayectoria.

Registrar controlador y auditor de recuperación antes de cualquier campo
nuevo. Reauditar primero los 74 tramos válidos: hashes, cadena, tipos,
potencia de masa, paso, recursos y fuentes. Recalcular el campo del tramo
fallido sólo desde el tramo 74 válido; no utilizar su salida como entrada.
No repetir los 74 tramos aceptados ni las trayectorias Padé/Radau retenidas.

Continuar exclusivamente los tramos 75–256 en un directorio nuevo,
utilizando el mismo trabajador P4I, sin editarlo. Mismos datos, matrices,
65536 pasos, 256 pasos por tramo y límites numéricos P4I3. La reserva
final RAM>3 GiB y disco>2 GiB sigue siendo obligatoria. Añadir una reserva
previa más conservadora: al menos 6 GiB disponibles antes de cada hijo.
No cerrar ni modificar aplicaciones ajenas para obtener memoria.

Esperar como máximo 1800 s acumulados por esa reserva previa, con
comprobaciones cada 10 s. Si no se dispone de recursos o vuelve a fallar
un hijo, detener esta recuperación y conservar sus registros; sin otro
reinicio automático. Mantener hijos ≤360 s y corte a 370 s.

El presupuesto original de 22000 s no se amplía. Contabilizar desde el
inicio UTC original hasta completar la recuperación, incluyendo el intervalo
de diagnóstico, espera y nueva ejecución. Congelar ese tiempo previo al
inicio de la recuperación y sumar el reloj monótono de su ejecución.
Si se consume el presupuesto, conservar el resultado operativo negativo.

El auditor final debe distinguir 74 tramos reutilizados y 182 nuevos,
reauditar además los 352 campos Padé/Radau anteriores y comprobar los
mismos criterios. La adaptación del auditor P4I3 sólo ajusta la fecha
de registro aplicable a cada tramo y sus contadores; generar y guardar
esa fuente antes de campos nuevos. Verificar por separado el fallo
original, la reserva previa nueva y la identidad de los 74 enlaces.

Ningún dictamen de P4I/P4I2 cambia. P5C sigue sin iniciar y la malla
0,28 sigue sin generar. Antes de un cierre espacial deberá comprobarse
también la sensibilidad a la cuadratura de rigidez en los elementos curvos;
la simetría y el control de constante de P4C no sustituyen ese contraste.
Tarea 1 actual abierta; JEV fallback local por bloqueo heredado.
