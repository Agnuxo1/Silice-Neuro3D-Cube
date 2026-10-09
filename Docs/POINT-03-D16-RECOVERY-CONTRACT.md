# C2-R1: recuperación operativa tras fallo confirmado

C2 terminó statusfailed al superar la espera acumulada900s. No calculó
tramo16. Sus15campos completos fueron auditados independientemente:
integridad aprobada, máximo residuo de potencia0, longitud0,46875mm.
Informe final original y todos sus datos/fuentes se conservan intactos.

Recuperar exclusivamente tramos16–64 de Radau65536. Mismo trabajador
def715416c077fa120755e671199491a3a454a8c369645e5c45e3b2d9103e2d3,
manifest numérico original, operador, entrada y paso. Reutilizar campo15
y su cadena por hashes, sin recalcular los15anteriores ni Padé.
Prefijos de campos continúan en carpetaR5_65536; informes de recuperación,
manifiesto, evaluación y auditoría se guardan en una carpeta diferenciada.
El original statusfailed no se sustituye por completed.

Reserva nueva>4,5GiB, guard numérico original>3GiB/disco>2GiB, un hilo.
Fundamento operativo observado: trabajador propio con pico de conjunto
residente0,43864GiB y lanzador0,00324GiB. Es observación de un caso, no
garantía universal; cada hijo conserva sus controles y puede fallar.
Sin espera adicional: si falta la reserva, detener la recuperación.
Hijo≤360s/corte370s. GlobalORIGINAL22000s desde21:08:45,812102UTC
del8deoctubre, incluyendo el fallo, preparación e interrupciones. No resetear
ni extender ese presupuesto. No detener procesos de otros proyectos.

Mismos criterios: campoMrel≤1e-4, ambas diferencias de potencia≤1e-6 y
ambas cotasPSD≤1e-5. Requisito de fuente/integridad antes de cada nuevo
campo y auditoría independiente de los64tramos y referenciaPadé retenida.
Auditor distinguirá reserva6GiB de los15originales y4,5GiB de los nuevos,
misma física y mismo guard final. No adoptar un aprobado sin esa auditoría.

M1 intermedia sigue sin ejecutar y su requisito C1temporalPASS siguefalso.
Si recuperaciónC2 aprueba, registrar nueva dependencia para la siguiente
malla antes de sus campos. Tarea1/punto3 abierto; no tareas2–22/h0,28.
JEV fallback local por bloqueo heredado. Sin validación física derivada.
