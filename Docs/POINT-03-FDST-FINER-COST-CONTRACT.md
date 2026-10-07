# Coste sintético de mallas más finas, antes de cualquier nueva óptica

L1 es negativo. L2 continúa y no habilita por sí solo un cierre espacial.
No preparar ni propagar nuevas geometrías T96 durante este control.

Después de terminar L2, medir secuencialmente N767, N959 y N1199: sus
tamaños de DST-I N+1 son 768, 960 y 1200. Se seleccionan por tamaño
y coste transformacional, antes de conocer sus potencias ópticas. Todas
son más finas que N640. La elección no supone mejor precisión del
operador espacial a igual dx.

Para cada N: índice y absorbedor cero, campo producto de modos seno
de índices N-16 y N-18; 100 pasos, dz=2mm/32768. Comparar la solución
con exp(i*lambda_fd*z) conocida. Exigir error relativo <=1e-10,
norma finita, tiempo <=180s. Un hilo, sin GPU ni instalaciones.
El supervisor permite <=190s por hijo y <=600s globales; si un hijo
falla, conservar el resultado y no preparar ninguna óptica de ese N.

Informar segundos/paso y estimaciones de 32768, 65536 y 131072 pasos,
sin afirmar que un tiempo sintético es una garantía para T96. No usar
estos modos lisos para validar el error con el potencial abrupto.
Este registro sólo resuelve viabilidad computacional de refinamientos;
una investigación espacial necesita otro contrato y predicciones nuevas
congeladas antes de preparar o propagar las mallas.

JEV: fallback local identificado por el bloqueo remoto heredado. El
checkout principal y todos los ensayos fallidos permanecen intactos.
