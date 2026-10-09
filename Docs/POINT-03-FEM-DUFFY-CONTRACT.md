# Cuadratura de rigidez por bloques con Gauss–Duffy

Registrar antes de las matrices nuevas. El control precedente aprobó
identidades de ensamblaje, pero no certificó el orden 8 en prototipo ni
malla intermedia. El par 12–16 sí pasó en h0,35 (cotas de potencia
6,13e-6/5,41e-6), pero falló en h0,4375 (4,63e-4/4,10e-4).
Una cota conservadora insuficiente no demuestra un error real igual
a esa cota; no se atribuyen a este mecanismo los fallos históricos.

Nuevo control: regla positiva tensorial Gauss–Legendre de 12, 16 y 24
puntos por eje, transformada al triángulo por x=s, y=(1-s)*t,
jacobiano de referencia 1-s. s,t pertenecen a [0,1]. Comprobar momentos
monomiales de grado total hasta 10 frente a i!*j!/(i+j+2)! y suma de
pesos 1/2, con error absoluto ≤1e-13. No confundir puntos por eje con
el grado de las reglas triangulares anteriores.

Usar las mismas tres mallas guardadas, sin generar geometría ni campos.
Ensamblar la rigidez en bloques de 256 triángulos, manteniendo el mapa
global de grados de libertad. Los bloques son sólo una estrategia de
memoria; no cambian la regla ni el integrando. Verificar que la suma
por bloques con orden triangular 8 reproduce la matriz histórica dentro
de 1e-13 relativo. Conservar controles de simetría, constante, energías
lineales físicas x,y y producto cruzado del protocolo anterior.

Conservar la diagonal D con M≥D y la misma cota de operador mediante
sumas absolutas por fila. Para pares Duffy12–24 y Duffy16–24 exigir
eta=z*cota≤1e-6 y ambas cotas conservadoras 2*L*eta≤1e-5 a z=2mm.
Guardar todos los resultados, también los negativos. No son cotas del
error frente a la integral exacta: comparan las matrices calculadas.
La selección de una regla común de producción se registrará aparte
antes de propagaciones nuevas, sin modificar los datos previos.

Un hilo, máximo1800s por malla, RAM disponible inicial≥3,5GiB y final
>3GiB, disco>2GiB. El umbral inicial menor que el control anterior se
justifica por el ensamblaje en bloques; no relaja criterios numéricos.
Guardar matrices, entradas, fuentes/hashes, recursos, tiempo y fallos.
No ejecutar simultáneamente ninguna propagación ni generar h0,28.
P4I3 queda operativo negativo/incompleto tras sus fallos; sus100 campos
válidos y todos los anteriores se preservan. Tarea1 abierta. JEV local.
