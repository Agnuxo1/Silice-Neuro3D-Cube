# F3 · red óptica pequeña con tarea congelada y línea base electrónica · contrato prospectivo (2026-10-09)

Publicado antes de entrenar nada. Es un estudio numérico con datos sintéticos. **No es una red física**: no hay fabricación, ni fuentes, ni detectores reales, ni medidas.

## Pregunta

¿Puede una malla lineal unitaria 4×4 con lectura de intensidad resolver una tarea cuadrática congelada con una precisión que supere a una línea base electrónica con el mismo número de parámetros? ¿Cuál es el balance energético bajo supuestos explícitos?

## Tarea congelada

- Entradas: x ∈ ℝ⁴, muestras de N(0, I₄), semilla de entrenamiento 20261009 (2000 muestras) y semilla de prueba 20261010 (2000 muestras). Los conjuntos de prueba no se usan para elegir nada.
- Etiquetas: y = argmax_k xᵀQ_k x, con cuatro matrices simétricas Q_k generadas con semilla 20261011. Las etiquetas son reproducibles, no dependen de ningún modelo.
- Azar: exactitud 0,25.

## Modelos

- **M1 (fotónico, malla unitaria).** U = exp(iH), con H hermítica 4×4 (16 parámetros reales). Salida y_k = |(Ux)_k|². Lectura de intensidad, sin no linealidad adicional.
- **M2 (electrónico, mismo readout).** y_k = (Ax)_k², con A real 4×4 (16 parámetros). Es la línea base con el mismo tipo de lectura y el mismo número de parámetros.
- **M3 (referencia cuadrática completa).** y_k = xᵀP_k x, con P_k simétricas (40 parámetros). No está igualada en parámetros; sirve de techo de referencia.

Logits = y con temperatura fija 1 en los tres modelos.

## Entrenamiento

- Pérdida: entropía cruzada media sobre el conjunto de entrenamiento.
- Optimizador: L-BFGS-B, 8 inicios con semillas fijas (1 a 8). Se elige el inicio con menor pérdida de entrenamiento, nunca por prueba.

## Hipótesis y umbrales (fijados aquí)

- **H1 (capacidad).** Exactitud de M1 en prueba ≥ 0,60.
- **H2 (readout frente a línea base).** Exactitud(M1) − Exactitud(M2) > 0, con intervalo de confianza bootstrap al 95 % (1000 remuestreos) que excluya 0.
- **H3 (techo).** Exactitud(M3) ≥ Exactitud(M1).

## Balance energético (sin medidas)

Modelo paramétrico con operaciones por inferencia: la línea base hace 16 multiplicaciones-acumulaciones y 4 elevaciones al cuadrado (20 operaciones). La malla óptica consume una energía de fuente por inferencia y 4 detecciones. El punto de equilibrio es la energía por operación electrónica E_op* a partir de la cual la línea base gastaría más que la malla. **No se declara ventaja**: los valores de referencia son supuestos, y el informe muestra el equilibrio como función de esos supuestos.

## Lo que este contrato no afirma

- No demuestra una red neuronal óptica. La malla es lineal en campo; la lectura cuadrática es la única no linealidad, y está fuera de la parte pasiva.
- No mide energía. No compara con hardware real.
- Los resultados dependen de la tarea sintética elegida; no se generalizan a tareas reales.
