# F3-c · tarea con datos reales (dígitos 0–3) · resultados (2026-10-10)

Contrato: [`CONTRATO-DIGITS.md`](CONTRATO-DIGITS.md), publicado antes de entrenar. Código: `run_digits.py`. Datos: `digits_resultados/`, `digits_aggregate.json`. Conjunto: `sklearn.datasets.load_digits`, dígitos 0–3, 4 componentes PCA ajustadas solo con entrenamiento, partición 70/30 estratificada.

## Hipótesis preregistradas

| Hipótesis | Criterio | Valor | Veredicto |
|---|---|---|---|
| H-D1 capacidad de M1 (malla unitaria) | ≥ 0,70 | 0.7685 | **Cumple** |
| H-D2 referencia electrónica B | ≥ 0,90 | 0.4074 | **No cumple** (ver diagnóstico) |
| H-D3 M1 pierde frente a pesos reales (M2) | M1 − M2 < −0,05 con IC95 excluyendo 0 | -0.0700, IC95 [-0.1157; -0.0278] | **Cumple** |

## Todos los modelos (protocolo preregistrado)

| Modelo | Parámetros | Exactitud train | Exactitud prueba |
|---|---|---|---|
| M1 malla unitaria, intensidad | 16 | 0.792 | 0.7685 |
| M2 pesos reales, intensidad | 16 | 0.851 | 0.8380 |
| M3 cuadrática completa | 40 | 0.871 | 0.8565 |
| A malla–activación–malla | 32 | 0.375 | 0.2963 |
| B pesos reales, misma topología | 32 | 0.500 | 0.4074 |

## Diagnóstico de H-D2 (exploratorio, **no preregistrado**)

Las componentes PCA tienen desviación típica 1,9–3,3 (máximo ≈ 7,5), y la activación usa V_π = 1 fijo. Con esa escala, la activación queda en un régimen muy oscilatorio, y el entrenamiento de A y B falla (B = 0.41, casi al azar). Como comprobación, se dividieron las componentes por su desviación típica de entrenamiento, sin cambiar nada más:

| Modelo | Prueba (normalizado, exploratorio) |
|---|---|
| A | 0.5787 |
| B | 0.8889 |

Con entradas normalizadas, la red electrónica llega a 88.9 %, a un punto de H-D2. **Esta cifra no sustituye el veredicto preregistrado**; sirve para atribuir el fallo a la escala de entrada y a V_π fijo, no a la topología. La sensibilidad a la escala es en sí un resultado: la activación optoelectrónica necesita diseño de entradas y de V_π.

## Lectura

- **La restricción unitaria se confirma en datos reales.** M1 pierde frente a pesos reales (H-D3) con un margen que excluye cero.
- **La activación optoelectrónica es sensible a la escala.** Con entradas no normalizadas, la red de dos capas no entrena; con entradas normalizadas, la referencia electrónica casi cumple y la versión óptica sigue muy por debajo.
- **Esta tarea es independiente de F3 (datos reales, no sintéticos)**, pero sigue siendo de 4 clases y 4 componentes. No es reconocimiento de dígitos.

## Límites

- Preprocesado de escala fija, preregistrado. El diagnóstico normalizado es posterior y exploratorio.
- Sin medidas ni energía. Modelo numérico.
