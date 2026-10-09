# F3-b · red funcional de dos capas con activación optoelectrónica · contrato prospectivo (2026-10-10)

Publicado antes de entrenar. Tarea 12 del encargo: definir detección, activación, entrenamiento y control de una red funcional. Continúa `CONTRATO-F3.md` y `RESULTADOS-F3.md` (resultado negativo de la malla de una capa). **Es un modelo numérico, no un dispositivo.**

## Definición completa de la red

- **Entrada.** x ∈ ℝ⁴, muestras de la misma tarea congelada (semillas 20261009 a 20261011, mismas etiquetas que F3).
- **Capa 1 (malla unitaria).** U₁ = exp(iH₁), H₁ hermítica 4×4 (16 parámetros reales). Potencias ópticas I₁ = |U₁x|² (4 valores).
- **Detección y activación.** Cada salida se detecta con un fotodetector (corriente proporcional a I₁). La señal controla un modulador de Mach-Zehnder con transmisión T(I) = (1 + cos(πI/V_π + θ_b))/2. La entrada de la capa 2 es a₂ = √T(I₁) (amplitud real). **Esto es una no linealidad optoelectrónica, con electrónica de control: no es una activación totalmente óptica.**
- **Capa 2 (malla unitaria).** U₂ = exp(iH₂), H₂ hermítica 4×4 (16 parámetros). Salida I₂ = |U₂ a₂|².
- **Lectura y decisión.** Logits = I₂ con temperatura fija 1 (argmax para clasificación).
- **Entrenamiento.** Entropía cruzada media en entrenamiento, L-BFGS-B, 8 inicios con semillas fijas. Se elige el inicio con menor pérdida de entrenamiento; nunca por prueba.
- **Control.** θ_b (sesgo del modulador) y V_π son parámetros fijos del modelo: V_π = 1 y θ_b = 0. Se varían solo en el análisis de sensibilidad, sin ajuste sobre prueba.

## Modelos comparados

- **A (fotónico-optoelectrónico).** Topología anterior, 32 parámetros (U₁, U₂), activación T(I) como arriba.
- **B (electrónico, misma topología).** Capas reales W₁ y W₂ (4×4 cada una, 32 parámetros), misma activación T(I) con I = (W x)² y el mismo readout. Es la línea base con igual número de parámetros.
- **C (referencia cuadrática, F3).** 40 parámetros, sin igualar. Techo de referencia ya conocido (99,2 %).

## Hipótesis y umbrales (fijados aquí)

- **H-F1 (funcional).** Exactitud en prueba de A ≥ 0,70. El umbral de F3 era 0,60 para una capa; con una activación, el listón sube.
- **H-F2 (frente a línea base).** Exactitud(A) ≥ Exactitud(B) − 0,02. No se exige ganar, sino no perder más de 2 puntos frente a la electrónica con la misma topología y parámetros.
- **H-F3 (mejora frente a una capa).** Exactitud(A) − 0,5905 > 0, con intervalo bootstrap 95 % (1000 remuestreos) que excluya 0. Es decir, la capa de activación aporta capacidad frente a F3 M1.

## Balance y límites

- No hay medidas ni energía en este contrato (ver `CONTRATO-F3.md`, balance paramétrico).
- La no linealidad usa electrónica de control y un fotodetector: no es una red totalmente óptica.
- No demuestra una red física ni sustituye la fabricación (tarea 13).
