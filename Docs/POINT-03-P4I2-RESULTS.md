# P4I2: terminado y auditado, con resultado negativo

El ensayo añadió 128 tramos Padé de 256 pasos, sin repetir la referencia
Radau anterior. Terminó en 7910,727 segundos. El auditor independiente
comprobó los 128 campos nuevos y releyó los 224 retenidos: integridad
aprobada y residuo máximo de potencia guardada frente a recalculada cero.

| Criterio registrado | Resultado | Límite | Dictamen |
|---|---:|---:|---|
| Diferencia relativa del campo, norma de masa | 2,070707e-5 | 1e-4 | Aprobado |
| Diferencia de potencia, campo cuadrático | 2,972847e-9 | 1e-6 | Aprobado |
| Diferencia de potencia, intensidad lineal | 1,376515e-7 | 1e-6 | Aprobado |
| Cota PSD del observable, campo cuadrático | 6,930634e-6 | 1e-5 | Aprobado |
| Cota PSD del observable, intensidad lineal | 1,169059e-5 | 1e-5 | Fallido |

Potencia Padé: campo 0,332924114382973; intensidad 0,332698954979332.
Potencia Radau retenida: campo 0,332924117355820;
intensidad 0,332699092630816. No se renormalizó ni alineó la salida.
La cercanía de esas potencias no sustituye el criterio PSD fallido.
Las cotas representan discrepancias entre aproximaciones calculadas;
no prueban por sí solas el error absoluto frente al modelo continuo.

La terminal devolvió código 1 para la orden exterior; el programa
registró `status=completed`, ausencia de error y un dictamen temporal
negativo. Sus 128 hijos acabaron con código cero y fueron auditados.
Se conserva esta diferencia de códigos; no se interpreta como un cálculo
incompleto ni se utiliza para volver a ejecutar la trayectoria válida.

P5C no se inició: su prerrequisito era un aprobado de P4I2. Los protocolos
espaciales y sus 11 controles del evaluador quedan preparados, y la malla
fina de 0,28 micrómetros sigue sin generar. La convergencia T96/Q4
permanece abierta: tarea 1 actual, punto 3 de la documentación histórica.

P4I3, registrado en 21f9ed4 antes de los campos, conserva Padé y añade
únicamente Radau con 65536 pasos. Mantiene los mismos límites y está
pendiente. El refinamiento no atribuye previamente el fallo a una familia.
Su eventual aprobación temporal requerirá todavía el estudio espacial
prospectivo y el control de dominio para cerrar esta tarea.

Todos los fallos anteriores se conservan. Los campos intermedios completos
permanecen localmente; GitHub publica informes, metadatos y terminales
seleccionados. No hay validación experimental ni vectorial derivada de
este control escalar. JEV: fallback local por bloqueo heredado.
