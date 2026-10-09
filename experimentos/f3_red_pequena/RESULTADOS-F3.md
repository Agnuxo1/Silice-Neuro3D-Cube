# F3 · red óptica pequeña con tarea congelada: resultados (2026-10-09)

Contrato: [`CONTRATO-F3.md`](CONTRATO-F3.md), publicado antes de entrenar. Código: `run_f3.py`. Datos: `f3_resultados.json`, `f3_aggregate.json`, `diag_m1_optimizer.json`.

**Resultado negativo.** Las hipótesis H1 y H2 no se cumplen. La única que se cumple es H3, que es un techo de referencia y no mide capacidad fotónica.

## Hipótesis (umbrales fijados antes de entrenar)

| Hipótesis | Criterio | Valor medido | Veredicto |
|---|---|---|---|
| **H1** capacidad de la malla | exactitud(M1) en prueba ≥ 0,60 | **0,5905** | **No se cumple** |
| **H2** frente a la línea base | exactitud(M1) − exactitud(M2) > 0 con IC 95 % sin 0 | **−0,257**, IC [−0,282; −0,235] | **No se cumple** (M1 es peor) |
| **H3** techo cuadrático | exactitud(M3) ≥ exactitud(M1) | 0,9915 ≥ 0,5905 | Se cumple |

Tarea congelada: 4 clases, etiqueta = argmax de xᵀQ_k x con Q_k simétricas aleatorias (semillas 20261009 a 20261011). Azar: 0,25. Prueba: 2000 muestras.

| Modelo | Parámetros | Exactitud en prueba | Nota |
|---|---|---|---|
| M1 malla unitaria, lectura |Ux|² | 16 | 0,5905 (mejor de 8 inicios por pérdida de entrenamiento) |
| M2 electrónico, lectura (Ax)² | 16 | 0,8480 | Real, no es una malla pasiva física |
| M3 cuadrática completa | 40 | 0,9915 | No igualada en parámetros; techo de referencia |

## Diagnóstico: ¿es el optimizador o la capacidad?

Se repitió M1 con 32 inicios y 2000 iteraciones máximo (`diag_m1_optimizer.py`, no es un resultado preregistrado). Los 32 inicios convergen (`success` = True, entre 19 y 40 iteraciones). La mejor pérdida de entrenamiento es 1,095 y la exactitud de prueba queda entre 0,581 y 0,591 en todos los inicios. **El límite de H1 no viene del optimizador**: es una capacidad limitada de esta familia para esta tarea.

## Interpretación

- **La unitariedad (malla pasiva y sin pérdidas) limita la expresividad con lectura de intensidad.** M2 tiene el mismo número de parámetros, pero no es unitaria y llega a 0,85. Esta comparación no es un diseño físico: M2 no se puede implementar con una malla pasiva. Sirve para indicar que la restricción unitaria es la que limita aquí.
- **La parte cuadrática sí puede resolver la tarea** (M3 llega a 0,99), pero con 40 parámetros y sin la restricción de ser una malla física.
- **Lo que este resultado no dice:** no excluye mallas con pérdida o ganancia, lectura con más fotodetectores, codificación con fase compleja de las entradas ni arquitecturas de varias capas. Ninguna de estas alternativas se probó aquí.

## Balance energético (paramétrico, sin medidas)

Punto de equilibrio: E_op* = (E_src + 4·E_det) / 20, con 20 operaciones electrónicas por inferencia.

| E_src (J/inferencia) | E_det (J) | E_op* (J/operación) |
|---|---|---|
| 1·10⁻¹² | 1·10⁻¹⁵ | 5,0·10⁻¹⁴ |
| 1·10⁻¹² | 1·10⁻¹⁴ | 5,2·10⁻¹⁴ |
| 1·10⁻¹² | 1·10⁻¹³ | 7,0·10⁻¹⁴ |
| 1·10⁻¹¹ | 1·10⁻¹⁵ | 5,0·10⁻¹³ |
| 1·10⁻¹¹ | 1·10⁻¹⁴ | 5,0·10⁻¹³ |
| 1·10⁻¹¹ | 1·10⁻¹³ | 5,2·10⁻¹³ |

**No se declara ventaja.** Solo una ventaja energética condicionada: la malla óptica sería más barata que la electrónica si la energía real por operación electrónica supera E_op*. Esa comparación requiere valores medidos de la fuente y de los detectores, y de la energía de la operación electrónica en el hardware de referencia. Ninguno está en el repositorio.

## Límites

- Tarea sintética con semillas fijas. No se generaliza a tareas reales.
- Solo lectura de intensidad, sin pérdidas, sin ganancia y sin codificación compleja de entradas.
- M3 no está igualada en parámetros, y M2 no es física.
- Balance energético paramétrico. No mide hardware.
- Sin GPU. Un hilo, con cada modelo en un proceso separado.

## Reproducir

```bash
cd experimentos/f3_red_pequena
python -B run_f3.py m1 && python -B run_f3.py m2 && python -B run_f3.py m3
python -B run_f3.py aggregate
python -B diag_m1_optimizer.py
```
