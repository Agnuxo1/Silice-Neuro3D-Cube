# P5D: contraste espacial prospectivo del FEM conforme

Este protocolo fija los criterios antes de las potencias P5C. No elimina
ningún fallo anterior ni permite seleccionar otra terna tras observarlas.
Se implementarán y registrarán controlador y auditor antes de utilizar
el resultado reservado. La predicción se guardará y registrará en Git
antes de generar la malla fina y antes de sus campos.

Serie invariable P5A: h local 0,546875 / 0,4375 / 0,35 / 0,28 micrómetros,
razón nominal r=1,25; mallas Gmsh con el mismo generador, semilla, campo
de tamaño, materiales y dominio ±64 micrómetros. Son mallas sistemáticas
no anidadas; el tamaño nominal no garantiza una ley asintótica. Esa ley
es precisamente la hipótesis que debe superar el contraste reservado.
No introducir una malla nueva si el contraste falla en esta ejecución.

Primarias: Padé 32768 pasos de las dos mallas P5C y la trayectoria Padé
32768 de P4I2, reutilizadas por hash. Cada una necesita auditoría temporal
aprobada, con sus matrices y controles geométricos, detector, entrada y
amortiguación. Conservar los dos observables: campo cuadrático integrado
en el círculo físico R=6 micrómetros e intensidad reconstruida linealmente.
No escoger el más favorable.

Antes del resultado reservado, calcular para cada observable:
delta01=P1-P0, delta12=P2-P1 y p=log(delta01/delta12)/log(r).
Prerequisitos simultáneos: deltas finitas, mismo signo y no nulas;
0,5≤p≤6; cada incremento mayor que 20 veces la máxima discrepancia
temporal de potencia registrada en las tres mallas. El intervalo de p
es un filtro amplio contra extrapolaciones patológicas, no un orden
teórico demostrado del FEM para este problema de interfaces.
Si falla un prerrequisito, guardar el resultado negativo y detenerse
antes de generar la malla 0,28.

Predecir P3=P2+delta12/r^p. Guardar potencias, órdenes, predicciones,
fuentes y hashes. No reajustar la predicción después del resultado fino.

Malla reservada: mismo algoritmo P4C, tamaño local 0,28 y fondo 1,12
micrómetros. Conservar límites geométricos originales P4C (incluido error
de área curva ≤1e-5 relativo), conversión de contadores NumPy a int para
el informe y controles detector/entrada/amortiguador P4F/P4G. Registrar
adaptaciones y fuente generada antes de ejecutarlas. Mismos datos físicos.

Propagación fina: Padé6 y Radau5, ambos 65536 pasos de 2 mm, tramos
de 256 pasos. Se elige este refinamiento temporal antes de sus resultados
por el incremento previsto del espectro discreto al reducir h. Padé es
siempre la primaria y Radau el contraste. Exigir los mismos límites
simultáneos: campo relativo ≤1e-4, ambas diferencias de potencia ≤1e-6,
ambas cotas PSD de discrepancia observable ≤1e-5. No alinear la fase ni
renormalizar salidas. Las discrepancias no son errores absolutos probados.

Prueba espacial simultánea para cada observable:

- Nuevo incremento delta23=P3_real-P2 no nulo y con el mismo signo.
- Nuevo p=log(delta12/delta23)/log(r) positivo y en [0,5;6].
- Discrepancia de órdenes |p_nuevo-p_previo|/max(p_nuevo,p_previo) ≤20%.
- Residuo de predicción ≤10% de |delta23|.
- |delta23| >20 veces la máxima discrepancia temporal de potencia.
- Indicador espacial U=1,25*|delta23|/(r^min(p_nuevo,2)-1).
- U más la máxima cota PSD temporal, la discrepancia entre reconstrucciones
  finas y el indicador de cuadratura fina ≤1e-3 y ≤1% de P3_real.

El indicador de cuadratura procede de la cota de operador en norma de
masa del detector multiplicada por la potencia de masa. Son indicadores
condicionados a los contrastes observados, no una cota rigurosa del error
continuo ni un intervalo estadístico del 95%. Informar cada componente.

Comprobar por separado la sensibilidad de potencia a ampliar el dominio,
con protocolo registrado antes de ese nuevo cálculo. Un aprobado espacial
por sí solo no cierra el punto 3. La validación conjunta de frontera,
campo complejo y fase seguirá siendo una tarea posterior distinta.

Cada etapa fina secuencial: un hilo, RAM disponible >3 GiB, disco >2 GiB,
hijos ≤360 s con corte a 370 s. Geometría ≤600 s, detector ≤1800 s,
amortiguador ≤600 s; propagación global ≤36000 s, sin ampliarlo durante
el ensayo. Conservar todos los campos, registros, fallos y fuentes.
Auditoría independiente antes de adoptar cualquier aprobación local.
Alcance: modelo escalar ideal; JEV fallback local por bloqueo heredado.

Referencia metodológica: [NASA, convergencia espacial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html).
La extrapolación requiere un régimen asintótico y no queda justificada
por una diferencia pequeña entre dos mallas. Los métodos específicos
para potenciales discontinuos, como el [DG Trefftz de Gómez y Moiola](https://arxiv.org/abs/2106.04724),
tienen sus propias hipótesis y normas: sus resultados teóricos no se
transfieren automáticamente a esta implementación FEM.
