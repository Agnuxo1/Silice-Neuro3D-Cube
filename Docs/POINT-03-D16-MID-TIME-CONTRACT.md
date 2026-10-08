# D16-M1: control longitudinal de la malla intermedia

Sólo se ejecutará tras recuperar D16-C1 y confirmar localmente su integridad
y precisión temporal. Preparar esta etapa no permite saltar ese requisito.
Todas las fuentes y resultados D16-C1 y K8 permanecen intactos.

Malla ideal existente h0,4375µm, dominio±64µm; masa, camisa, entrada,
detector y amortiguador previamente controlados. K Duffy16 procede de
point03_fem_duffy_mid_20261008; SHA256
d90b53ab2fb53538596b31871050a80cd50cfdc73cf096fb5d5b0e736c88408e.
Su discrepancia contra Duffy24 aprobó el contrato97a33b9 antes de este ensayo.

Mismo modelo escalar y datos físicos de D16-C1. Padé[3/3] y Radau[2/3],
ambos32768pasos de2mm, tramos1024, sin normalizar salidas ni alinear fase.
Mismos límites simultáneos: campo relativo en normaM≤1e-4; dos diferencias
de potencia≤1e-6; dos cotasPSD≤1e-5. Ningún observable puede descartarse.
No se consideran errores absolutos probados frente al continuo.

Un hilo, CPU local. Reserva previa≥6GiB; guard durante/final>3GiB y
disco>2GiB. Hijo≤360s/corte370s; global22000s desde lanzamiento y espera
acumulada≤900s, incluidas interrupciones. No extenderlos durante el ensayo.
Un fallo se preserva; auditoría independiente de todos los tramos antes
de adoptar un aprobado. No reanudar automáticamente ni sobrescribir salidas.

Se generarán copias diferenciadas del trabajador y auditor D16-C1,
con sustituciones explícitas registradas y fuente original verificada por
hash. Sólo cambian archivos de malla, hashK, etiqueta, nombres de fuentes,
requisito de auditoría previa y reserva de memoria. Fórmulas, métodos,
pasos, criterios, límites y formato de campos quedan invariantes.
Se comprobará antes la cadena del trabajador en el sistema manufacturado
de3DOF, con recursos simulados únicamente en ese test de software.

La malla h0,35 necesita después un prerregistro propio antes de nuevos
campos. No combinar primariasK8/K16 ni generar h0,28. El cierre espacial
y del dominio siguen pendientes; tarea1/punto3 abierto. Las tareas2–22
siguen pendientes en el orden del usuario. JEV fallback local por bloqueo
heredado; sin ejecución Blender, GPU o validación física derivada.
