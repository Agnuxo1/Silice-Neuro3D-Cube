# F3-c · tarea independiente con datos reales (dígitos) · contrato prospectivo (2026-10-10)

Publicado antes de entrenar. Tarea 16 del encargo: evaluar la misma familia de modelos con **datos reales públicos**, distintos de la tarea sintética de F3. El conjunto es `sklearn.datasets.load_digits` (incluido en el paquete, sin descarga).

## Datos y preprocesado

- **Clases:** dígitos 0, 1, 2 y 3 (cuatro clases, para que la malla 4×4 tenga cuatro salidas, igual que en F3).
- **Partición:** estratificada 70 % entrenamiento y 30 % prueba, semilla 20261020. La prueba no se usa para ninguna decisión.
- **Reducción:** estandarización y PCA a 4 componentes, ajustados **solo con el entrenamiento** (sin fuga).
- **Entradas:** 4 componentes reales por muestra, igual que las entradas de F3.

## Modelos (igual protocolo que F3)

- **M1** malla unitaria con lectura de intensidad (16 parámetros).
- **M2** pesos reales con lectura de intensidad (16 parámetros).
- **M3** cuadrática completa (40 parámetros, referencia).
- **A** dos mallas unitarias con activación MZM (32 parámetros), como F3-b.
- **B** pesos reales, misma topología que A (32 parámetros).

Entrenamiento: entropía cruzada, L-BFGS-B, 8 inicios con semillas 1 a 8, selección por pérdida de entrenamiento.

## Hipótesis (fijadas aquí)

- **H-D1 (capacidad de la malla).** Exactitud de M1 en prueba ≥ 0,70.
- **H-D2 (referencia electrónica).** Exactitud de B en prueba ≥ 0,90. Si no se cumple, la tarea es demasiado difícil para esta topología y el resultado se interpreta como tal.
- **H-D3 (transferencia de la conclusión de F3).** La diferencia M1 − M2 es menor que −0,05, con intervalo bootstrap emparejado al 95 % (1000 remuestreos) que excluye 0. Es decir, la restricción unitaria pierde frente a pesos reales también en datos reales.

## Qué no afirma

- No es una demostración de reconocimiento de dígitos. Son cuatro clases y cuatro componentes, con una reducción drástica.
- No sustituye la fabricación ni las medidas.
