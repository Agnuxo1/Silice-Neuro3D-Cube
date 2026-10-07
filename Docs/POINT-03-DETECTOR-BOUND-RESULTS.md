# Cota del observable: verificación positiva y procedencia

Cuatro matrices globales (N400/N626, cuadraturas16/32),1176/2828celdas
por malla, ocho pares de campos fabricados. No se leyeron campos T96.
Todas las matrices locales son positivas dentro del criterio definido;
máxima suma de fila/dx²=1, identidad con pesos de intensidad<=3,019e-16,
error relativo de área2,220e-16. Energías por matriz y contracción directa
difieren como máximo3,469e-18. Las ocho variaciones de potencia respetan
la cota de Cauchy-Schwarz. Control completo4,360s: PASS.

La cota se refiere a la diferencia con un campo de referencia computado.
No certifica el error contra el continuo ni los perfiles físicos.

Procedencia: contrato y código se escribieron antes de calcular y se
conservan en la secuencia de herramientas. El primer intento de commit
no esperó a que terminara el añadido al índice; informó que no había
cambios preparados. El control se ejecutó antes del commit completado.
Se archiva esta secuencia y no se afirma congelación previa EN GIT para
este control auxiliar. Los bytes de fuente/contrato del resultado se
verifican sin cambios; no se repite ni se oculta el primer intento.
Los contratos ópticos L1/L2 sí se confirmaron antes de propagación.
