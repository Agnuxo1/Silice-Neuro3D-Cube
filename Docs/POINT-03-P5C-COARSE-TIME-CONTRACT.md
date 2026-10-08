# P5C: propagaciones de las dos mallas FEM gruesas

Registrar este protocolo, el controlador y el auditor antes de sus campos.
El ensayo sólo podrá empezar si P4I2 termina y su auditor independiente
aprueba la precisión temporal. Su eventual aprobación no cierra el punto 3.
Los fallos de P4I y de los métodos anteriores permanecen intactos.

Serie ya elegida antes de estas potencias: h local 0,546875 / 0,4375 /
0,35 / 0,28 micrómetros; fondo 4h, transición radial 15–25 micrómetros,
dominio físico cuadrado ±64 micrómetros, misma geometría ideal T96.
Aquí sólo se propagan las dos primeras mallas, en ese orden. Se reutilizan
por hash las matrices, detectores, entradas y amortiguadores P5A/P5B.
P4C/P4I2 proporcionarán el tercer tamaño, sin repetir su trayectoria.
La malla 0,28 queda sin generar y sin propagar.

En cada malla: Padé [3/3] de orden 6 y Radau [2/3] de orden 5, ambos
con 32768 pasos para 2 mm y tramos de 256 pasos. Son los algoritmos
ya contrastados con referencias densas pequeñas; se reutiliza el
trabajador P4I sin editarlo. La potencia principal será la de Padé;
Radau será contraste independiente de precisión temporal, no una
selección del resultado más favorable. Entrada gaussiana continua de
cintura 6 micrómetros proyectada en L2 y normalizada sólo al inicio.
Longitud de onda 1550 nm, índice de referencia 1,444, contraste -0,003
en los trazos, mismo amortiguador por partes P4G/P5B. No alinear fase
ni renormalizar salidas.

Los mismos tres límites simultáneos de P4I/P4I2, para cada malla:

- Diferencia relativa de campo en norma de masa ≤1e-4.
- Diferencia de potencia ≤1e-6 en ambos detectores.
- Cota PSD de discrepancia de cada observable ≤1e-5:
  (sqrt(a*Qa)+sqrt(b*Qb))*sqrt((a-b)*Q(a-b)).

Q es la matriz de integración del campo cuadrático o los pesos positivos
de reconstrucción lineal de intensidad. Se conservan ambos observables.
Estas cotas describen la discrepancia entre las soluciones calculadas;
no certifican su error absoluto frente a la solución continua.

Auditar cada campo complejo, hashes, cadena, recursos, paso físico,
potencia de masa y metadatos. Si una malla falla, detener este estudio
antes de la siguiente y conservar el resultado. No refinar pasos ni
cambiar límites durante esta ejecución. Un eventual nuevo refinamiento
requiere otro protocolo y conserva este fallo.

Un hilo numérico, ejecución secuencial, RAM disponible >3 GiB, disco
libre >2 GiB; cada hijo ≤360 s, corte externo a 370 s; presupuesto global
36000 s para ambas mallas. Todos los tramos y registros se conservan.
Guardar el estado tras cada tramo; sin reinicio ni repetición automática.

Después habrá que registrar el estudio espacial antes de la predicción
y de la malla reservada. Debe contrastar ambas reconstrucciones,
convergencia prospectiva y sensibilidad de potencia al dominio antes
de cerrar el punto 3. No se avanza al barrido modal en este ensayo.
Alcance: modelo escalar ideal. JEV: fallback local por bloqueo heredado,
sin recomendación remota verificada ni laboratorio externo ejecutado.
