# GLASS-006a · G2 a 10 µm: diagnóstico y convergencia en malla · resultados (2026-10-09)

Contratos: [`CONTRACT-G2-DIAG.md`](CONTRACT-G2-DIAG.md) y [`CONTRACT-N-CONV.md`](CONTRACT-N-CONV.md) (enmiendas E2 y E3, registradas antes de cada cálculo). Veredicto histórico, **sin modificar**: `resultados.json`, G2 con 7/18 PASS y 11/18 FAIL.

## 1 · Diagnóstico, un factor cada vez (10 casos, a = 10 µm)

- **Reproducción (P1).** Las configuraciones nominal y B reproducen los valores guardados con error 0,0 en los diez casos.
- **Efecto de cada factor sobre Re γ**, respecto de la configuración nominal (N = 500, R0 = 70 µm, Rmax = 150 µm, θ = 0,6):

| Factor | Cambio en Re γ |
|---|---|
| Malla N 500 → 700 | 2,4 % a 2,7 % |
| Dominio R0 = 90, Rmax = 200 | 1,6 % a 3,2 % |
| θ 0,6 → 0,8 | ≤ 3·10⁻⁴ % |

- **Atribución (P2, conjunto de factores que alcanzan el 50 % del cambio nominal → B):** dominio y malla N en los diez casos.
- La configuración B compensa parcialmente los dos efectos. Por eso la comparación nominal con B subestimaba el error de discretización.

## 2 · Convergencia en N (500, 700, 900, 1100, 1400, 1800)

- **Modo estable.** La fracción de potencia en el núcleo se mantiene en 0,95 (δn = −0,005) y 0,85 (δn = −0,003).
- **Re γ no es monótona en N.** Los diez casos muestran dos cambios de signo en la secuencia (P4 cumplida). Ejemplo, t = 6 µm, δn = −0,005: −3409 → −3317 → −3357 → −3382 → −3377 → −3357 m⁻¹.
- **Par (1400, 1800), criterio G2 sin cambios (P3 cumplida).** Cambio relativo en Re γ de 0,54 % a 0,58 %, y en pérdida de 0,7 % a 2,1 %. G2 se cumple en 10 de 10 casos.
- **Predicción P1 no cumplida con precisión.** Se predijo ≈ 0,5 % para el par 900–1100 bajo orden 2; el valor observado fue 0,71 % a 0,76 %. El orden de convergencia no es uniforme: en los pasos gruesos es ≈ 1,9, pero en el último paso es ≈ 0,5 a 1,0.

## 3 · Dominio en malla fina (E3, P5)

Con N = 1400, el dominio B cambia Re γ entre 0,55 % y 0,78 % respecto del nominal. P5 se cumple en 10 de 10 casos.

**Incertidumbre práctica** de Re γ para a = 10 µm con N ≥ 1400: **±0,8 %**, combinando malla y dominio.

## 4 · Caso a = 6 µm, t = 9 µm, δn = −0,005

La convergencia es monótona: Re γ pasa de −7314,5 a −7325,3 m⁻¹, y la pérdida de 0,436 a 0,443 dB/cm. En el par (1400, 1800): Re 0,008 %, pérdida 0,14 %. **G2 se cumple.** El fallo original de pérdida (13 %) era una discrepancia entre configuraciones de malla gruesa.

## Interpretación

- Los fallos de G2 a 10 µm en la configuración original (N ≤ 800) provienen de la discretización. Las mallas gruesas se desvían entre 2 % y 3 % en Re γ, por encima del criterio del 1 %.
- Con N ≥ 1400 y dominio nominal o B, Re γ de a = 10 µm coincide dentro de ±0,8 %.
- **Esto no convierte los FAIL históricos en PASS.** Es evidencia nueva, con contrato propio y veredicto propio. El registro original se conserva.

## Lo que no demuestra

- **No hay convergencia asintótica.** La secuencia oscila y no se ha extrapolado a N → ∞.
- **Causa de la no monotonía no diagnosticada.** Puede venir del mapeo de malla θ o del tratamiento de la capa exterior (ECS). No se ha determinado.
- **Otros dominios y otros θ en malla fina** no se han probado, salvo el dominio B.
- **Trazos discretos (GLASS-007) no están cubiertos.** Este análisis trata la camisa continua de GLASS-006a.
- **Q4 de la convergencia de trazos (POINT-03) sigue abierta.** Depende del cálculo F1, que no tiene estado verificado.

## Ficheros

- `diag_g2_radius10.py` y `diag_g2_radius10.json`: diagnóstico de un factor.
- `conv_n_a10.py` y `conv_n_a10.json`: convergencia en N = 500–1100.
- `conv_extend.py` y `conv_n_a10_ext.json`: extensión a N = 1400 y 1800.
- `conv_domain_fine.json`: comparación de dominio en N = 1400.
- `conv_a6_t9.json`: caso a = 6 µm.

Coste: N = 1800 ≈ 12 s por caso. Todo en un hilo, sin GPU.
