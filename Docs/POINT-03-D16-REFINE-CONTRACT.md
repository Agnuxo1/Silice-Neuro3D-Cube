# D16-C2: refinamiento longitudinal después de un resultado negativo

D16-C1 terminó y sus64tramos fueron recuperados por SHA256/CRC y auditados
localmente. Integridad aprobada; precisión temporal negativa porque la cota
PSD de intensidad1,3491078e-5 supera1e-5. Todos sus datos quedan intactos.

Mismos datos físicos, malla coarse, masa, K Duffy16, camisa, entrada,
detector y amortiguación. Reutilizar exclusivamente Padé32768 completo de
C1: informe P6_32768/part032.json, SHA256
a6b060faaff0d02ea6ee6cb2b7b0331d3962d5815bd97548af95e6d4830877a3.
El Radau32768 anterior se conserva como diagnóstico negativo, sin sustituirlo.

Único cálculo nuevo: Radau[2/3]65536pasos desde la misma entrada inicial,
longitud2mm,64tramos de1024. No continuar sus campos32768 con otro paso,
no recalcular Padé, no alinear fases ni normalizar salidas.

Criterios simultáneos, intactos: Mrel≤1e-4; ambas diferencias de potencia
≤1e-6; ambas cotasPSD≤1e-5. Comparar Padé32768 retenido contra Radau65536.
Son consistencia práctica entre familias, no errores absolutos probados.
Auditor separado recalcula los64tramos nuevos, referencia retenida y dictamen.

CPU local, un hilo. Reserva previa>6GiB; guard original>3GiB/disco>2GiB.
Hijo≤360s/corte370s, global22000s desde nuevo lanzamiento, espera total
≤900s. No extender límites durante la ejecución ni sobrescribir salidas.
No lanzar ninguna malla posterior si este resultado o su auditoría falla.

Fuentes nuevas diferenciadas, generadas a partir del trabajador C1 intacto
por extracción AST y sustitución explícita del método elegido y del paso.
Se registrarán antes de campos nuevos. Las demás fórmulas y verificaciones
del trabajador permanecen invariantes; todo fichero de entrada queda por hash.

M1 previamente preparado queda sin iniciar: su requisito C1temporalPASS
es falso. Si C2 aprueba, registrar una nueva dependencia para la malla
intermedia antes de sus campos; no reescribir ese requisito histórico.
Tarea1/punto3 abierto, sin h0,28 ni tareas2–22. JEV fallback local.
