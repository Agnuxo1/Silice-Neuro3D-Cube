# D16-M2: control temporal de la malla intermedia

Contrato nuevo, previo a cualquier campo T96 de esta malla. M1 permanece
sin ejecutar: su requisito C1 no aprobó. M2 requiere la auditoría final
C2-R1 con integridad y precisión temporal aprobadas y conserva todas las
fuentes y resultados anteriores. C2-R1 aprobó el 8 de octubre, 22:49 UTC.

Malla existente h=0,4375 µm, dominio ±64 µm, 47777 grados de libertad
libres. K Duffy16 SHA-256:
`d90b53ab2fb53538596b31871050a80cd50cfdc73cf096fb5d5b0e736c88408e`.
Entrada gaussiana q16, detector de campo q32 e intensidad q32, masa,
camisa y amortiguador q12 controlados previamente. Los siete archivos
numéricos deben verificarse por hashes y la potencia de entrada debe
ser uno dentro de 1e-12 antes de propagar.

Se conserva el modelo escalar, λ=1550 nm, n0=1,444, contraste 0,003,
longitud 2 mm y los mismos operadores físicos de D16. Padé [3/3] con
32768 pasos y Radau [2/3] con 65536 pasos: la pareja contrastada en C2-R1.
Son dos trayectorias nuevas en esta malla, con tramos de 1024 pasos:
32 Padé y 64 Radau, 96 en total. Sin renormalización ni ajuste de fase.

Los cinco requisitos simultáneos permanecen: diferencia relativa del
campo en norma de masa ≤1e-4; ambas diferencias de potencia ≤1e-6;
ambas cotas de discrepancia derivadas de operadores semidefinidos
positivos ≤1e-5. No descartar un detector ni cambiar los umbrales después
de ver los datos. Consistencia entre soluciones discretas, sin afirmar
una cota del error continuo.

CPU local, un hilo. Reserva previa >6 GiB, guardia inicial/final del
trabajador >3 GiB, disco >2 GiB. Cada hijo ≤360 s, corte externo 370 s.
Presupuesto global 22000 s desde el inicio, espera acumulada ≤900 s;
no ampliarlos ni reiniciarlos ante interrupciones. Preservar cualquier
fallo y auditar los campos válidos antes de una recuperación registrada.
No intervenir en procesos de otros proyectos.

Generar copias separadas de M1, verificando las fuentes originales por
hash. Cambian la dependencia a C2-R1, el paso Radau, el número de tramos
y los nombres de fuentes e informes. Las fórmulas, matrices, criterios,
límites y campos complex128 permanecen. Antes de campos ópticos:
control manufacturado de tres grados de libertad y dos tramos de cada
familia contra exponencial densa; rechazo de hash previo incorrecto;
evaluador con controles positivo, error sólo de fase y error de amplitud;
verificación de los siete archivos numéricos. Los recursos simulados se
usan sólo en el control de software, nunca en la ejecución T96.

El auditor independiente recalculará las potencias de los 96 campos,
comprobará cadena, fuentes, tiempos y recursos, y reproducirá los cinco
criterios antes de adoptar el resultado. La primaria espacial sigue
siendo Padé; Radau refinado es su control temporal. No sustituir la
primaria por el método que se acerque más a una extrapolación.

La malla h=0,35 requiere después un protocolo propio con K16 y la misma
pareja temporal; sus campos K8 históricos no se reutilizan como K16.
El estudio espacial y la predicción deben registrarse antes de campos
de la malla reservada h=0,28, aún sin generar. El control de dominio
también sigue pendiente. La tarea 1 permanece abierta; tareas 2–22
todavía sin iniciar. JEV: fallback local identificado por bloqueo heredado.
