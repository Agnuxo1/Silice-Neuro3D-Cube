# Tarea 10 · presupuesto de error de fase con correlación y deriva · resultados (2026-10-10)

Contrato: [`CONTRATO-FASE.md`](CONTRATO-FASE.md) (publicado antes de calcular; el modelo se corrigió dos veces antes de los resultados, y las correcciones están en el historial del archivo `fase_mc.py`). Código: `fase_mc.py`. Datos: `fase_resultados.json`.

**Este es un modelo de presupuesto de error, no una medida.** No hay deriva térmica real, ni calibración, ni instrumento.

## Modelo

Malla rectangular 4×4 de 6 MZI con 16 fases (malla genérica de unitarias), ajustada a una DFT₄ con error de transferencia de 6.4e-16. Errores de fase independientes (ℓ = 0), correlados con ℓ = 1 y 3 elementos, y deriva lineal s. Monte Carlo de 3000 muestras por caso.

**Nota de modelo.** Con dos etapas de acopladores en mariposa, cada entrada llega a cada salida por un único camino: las intensidades no dependen de las fases y el presupuesto sería nulo. Esa estructura no sirve para este análisis, y el resultado se descartó. La malla rectangular tiene caminos múltiples y por eso interfiere.

## Tabla (error de transferencia ε = ‖U − U_t‖_F/‖U_t‖_F y error de intensidad máximo)

| σ (rad) | ℓ | s (rad) | ε media | ε p95 | error intensidad medio | error intensidad p95 |
|---|---|---|---|---|---|---|
| 0.02 | 0 | 0.00 | 0.0386 | 0.0572 | 0.0622 | 0.1002 |
| 0.02 | 0 | 0.01 | 0.0432 | 0.0642 | 0.0697 | 0.1100 |
| 0.02 | 1 | 0.00 | 0.0417 | 0.0691 | 0.0612 | 0.0987 |
| 0.02 | 1 | 0.01 | 0.0460 | 0.0742 | 0.0689 | 0.1100 |
| 0.02 | 3 | 0.00 | 0.0484 | 0.0972 | 0.0561 | 0.0937 |
| 0.02 | 3 | 0.01 | 0.0523 | 0.1002 | 0.0647 | 0.1063 |
| 0.05 | 0 | 0.00 | 0.0965 | 0.1427 | 0.1552 | 0.2482 |
| 0.05 | 0 | 0.01 | 0.0984 | 0.1458 | 0.1582 | 0.2529 |
| 0.05 | 1 | 0.00 | 0.1041 | 0.1722 | 0.1528 | 0.2456 |
| 0.05 | 1 | 0.01 | 0.1059 | 0.1750 | 0.1559 | 0.2503 |
| 0.05 | 3 | 0.00 | 0.1207 | 0.2420 | 0.1402 | 0.2346 |
| 0.05 | 3 | 0.01 | 0.1223 | 0.2437 | 0.1438 | 0.2383 |
| 0.10 | 0 | 0.00 | 0.1922 | 0.2839 | 0.3089 | 0.4943 |
| 0.10 | 0 | 0.01 | 0.1931 | 0.2862 | 0.3101 | 0.4939 |
| 0.10 | 1 | 0.00 | 0.2073 | 0.3412 | 0.3042 | 0.4899 |
| 0.10 | 1 | 0.01 | 0.2082 | 0.3414 | 0.3058 | 0.4890 |
| 0.10 | 3 | 0.00 | 0.2398 | 0.4782 | 0.2799 | 0.4710 |
| 0.10 | 3 | 0.01 | 0.2406 | 0.4790 | 0.2814 | 0.4741 |

## Criterios

| Criterio | Valor | Veredicto |
|---|---|---|
| H10a convergencia del Monte Carlo (3000 frente a 6000 muestras, σ = 0,10) | diferencia relativa en la media 0.77 % (< 5 %) | **Cumple** |
| H10b efecto de la correlación en el p95 (ℓ = 3 frente a ℓ = 0, σ = 0,10) | cociente 1.684 (intervalo 0,8–1,25) | **No cumple** |
| H10c efecto de la deriva (s = 0,01 frente a 0, σ = 0,02) | cociente de medias 1.118 (< 1,5) | **Cumple** |

## Lectura

- **La correlación no cambia la media, pero infla la cola.** A σ = 0,10 la media de ε sube solo un 25 %, y el p95 sube un 68 %. Un presupuesto basado solo en desviaciones independientes subestima la cola.
- **La deriva de 0,01 rad es pequeña frente a σ = 0,02.** Con σ = 0,02, la media sube un 12 %. Con deriva mayor o con deriva correlada, el efecto puede crecer. No se ha probado.
- **Escala.** Con σ = 0,10 rad (≈ 6°), el error de intensidad medio es 31 % y el p95 49 %. Eso es mucho mayor que el ≈ 11 % de GLASS-004, pero **no son comparables**: GLASS-004 usa otra malla y otra métrica.

## Lo que falta para cerrar la tarea 10

- Medir fases reales en un chip (calibración, deriva térmica, correlación espacial medida). Eso requiere laboratorio (tarea 14).
- Un presupuesto con errores de fabricación correlados entre elementos vecinos, calibrado con datos.
