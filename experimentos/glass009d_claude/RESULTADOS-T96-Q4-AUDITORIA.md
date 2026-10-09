# T96/Q4 · auditoría independiente: malla reservada y dominio · resultados (2026-10-10)

Contratos: [`CONTRATO-Q4-RESERVA-028.md`](CONTRATO-Q4-RESERVA-028.md) y [`CONTRATO-DOMINIO-192.md`](CONTRATO-DOMINIO-192.md), publicados antes de calcular. Solver: `adi2d.py` (GLASS-009), geometría de 96 trazos (32 por corona), λ = 1550 nm, dz = 2,5 µm, 800 pasos. Ejecución por trozos de 200 pasos, comprobada exacta frente a la ejecución original (dx = 0,4: diferencia 0,00).

Este estudio corresponde al caso de 96 trazos de GLASS-009d (malla 2D). **No es el T96 de POINT-03 (solver D16 y F1), que es de Codex y no se recupera.**

## 1 · Serie en dx (potencia en núcleo, peso de área)

| dx (µm) | P | Nota |
|---|---|---|
| 0,625 | 0,33263167 | malla original |
| 0,500 | 0,33223676 | malla original |
| 0,400 | 0,33267435 | malla original (2 trozos) |
| **0,280** | **0,33298713** | **malla reservada, prospectiva** |

## 2 · Criterios

| Criterio | Umbral | Valor | Veredicto |
|---|---|---|---|
| Q1 integral de δn (dx = 0,28) | < 10⁻³ | 1,5·10⁻⁴ | Cumple |
| Q2/Q3 |P(0,28) − P(0,4)| | < 0,005 y < 10 % | 3,1·10⁻⁴ (9,4·10⁻⁴ relativo) | Cumple |
| **Q4 histórico** (monotonía en el par 0,625 / 0,5 frente a 0,4 / 0,5) | — | 3,95·10⁻⁴ < 4,38·10⁻⁴ | **No cumple** (sin cambios) |
| **Q5 nuevo** (dispersión relativa de {0,5; 0,4; 0,28}) | < 0,5 % | 0,23 % | Cumple |
| P-R1 (banda [0,331799; 0,333112]) | dentro de la banda | 0,332987 | Cumple |
| P-R2 (no crece la desviación de 0,4) | ≤ 4,4·10⁻⁴ | 3,1·10⁻⁴ | Cumple |

**Lectura de Q4.** Los tres puntos finos (0,5 → 0,4 → 0,28) son monótonos, con incrementos de +4,38·10⁻⁴ y +3,13·10⁻⁴ (cociente 0,71). El incumplimiento de Q4 viene del punto de 0,625, que sale de la tendencia. El criterio de monotonía se conserva sin cambios, y su fallo se registra como tal.

Una extrapolación geométrica con ese cociente daría P∞ ≈ 0,33377. **Es una hipótesis con dos incrementos, no un resultado**: el orden de convergencia no está determinado con tres mallas finas.

## 3 · Dominio (contrato D1)

| Dominio | dx | P | |ΔP|/P |
|---|---|---|---|
| 128 µm (N = 256) | 0,5 | 0,33223676 | referencia |
| 192 µm (N = 384) | 0,5 | 0,33170887 | **0,159 %** |

Criterio D1 (< 0,2 %): **cumple**. Predicción P-D1 (el dominio de 128 µm es suficiente): **se confirma** dentro del umbral. El efecto del dominio es del mismo orden que la dispersión de malla (0,13–0,23 %). Por eso la incertidumbre conjunta de P para 96 trazos en este modelo es de **±0,3 %** aproximadamente.

## 4 · Conclusión de esta auditoría

- **T96/Q4 del modelo 2D (GLASS-009d):** la potencia en núcleo está estable dentro de 0,23 % en dx entre 0,5 y 0,28 µm, y el dominio cambia el resultado en 0,16 % al pasar de 128 a 192 µm. El criterio histórico de monotonía sigue fallando por el punto de 0,625 µm, y así se registra.
- **No se cierra Q4 como criterio histórico**, porque su condición de monotonía no se cumple. Sí se documenta una convergencia dentro de tolerancia declarada (Q5), con su incertidumbre.
- **POINT-03 T96/Q4** (solver D16, F1 y malla reservada de 0,28 µm en el modelo de Codex) **no está cerrado** y depende de Codex y de la recuperación de F1.

## 5 · Ficheros

- `run009d_reserva.py`, `out/T96d_dx3_c{0..3}.json`, `resultados_q4_reserva_028.json`.
- `run009d_dominio.py`, `out/T96d_dx5_dom192.json`, `resultados_dominio_192.json`.
