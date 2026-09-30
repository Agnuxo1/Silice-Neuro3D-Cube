# GLASS-006a — fuga del modo cuasi-ligado de camisa continua ideal (Claude, 2026-09-30)

Contrato prospectivo `experimentos/glass006a_claude/CONTRACT.md` (SHA `c948f8df…`) fijado antes de ejecutar. Solo CPU, un hilo, 58 s el barrido (los 30 s por script del encargo se superaron; lo declaro). JEV: sin aval (fallback local). Resultados completos: `resultados.json`.

## Fe de erratas (fallo propio)
El contrato escribió la convención de signo al revés: con A∝exp(iγz) el decaimiento es **Im γ > 0**. La primera ejecución evaluó G1 tal como estaba escrito → FALSE en todos los casos (retenida como `resultados_v0_signo_contrato.json`). Corregí a G1'=Im γ≥0 y la fórmula de pérdida (+2·Im γ). Mi GLASS-005 usó `abs()`: magnitudes correctas, pero el signo no se comprobó; ahora sí. Ningún umbral cambiado. Detalle en `ERRATA.md`.

## Resultados (camisa continua ideal, escalar paraxial, λ=1550 nm, pérdida de fuga en dB/cm)

| a (µm) | δn | t=3 | t=6 | t=9 | t=12 | t=18 |
|---|---|---|---|---|---|---|
| 6 | −0,003 | sin modo | 18,1 | 3,74 | 0,743 | 0,031 |
| 6 | −0,005 | sin modo | 4,49 | 0,436 | 0,0443 | 0,0004 |
| 10 | −0,003 | 23,0 | 3,30 | 0,475 | 0,0686 | 0,0014 |
| 10 | −0,005 | 9,96 | 0,677 | 0,0471 | 0,0033 | 1,7e-5 |

- **G1' (signo): PASA** en los 18 casos con modo: ningún crecimiento.
- **G3 (túnel WKB, falsable): PASA** en 4/4 pares evaluables. κ²=2β0(Re γ − k0δn) predice loss(t1)/loss(t2): p. ej. a=6, δn=−0,005, t 6→12: observado 101, predicho 107; a=6, δn=−0,003, t 12→18: 23,8 vs 24,2. La fuga sigue exp(−2κt). **No evaluado para a=10** (G3 exigía G2 pasado).
- **G4 (consistencia con Codex): PASA**: fracción en núcleo a 2 mm 0,364 (radial) vs 0,349 (BPM 007 continuo), Δ=0,015 <0,03.
- **G2 (convergencia por modo): 7 de 18 casos pasan.** Fallan los 10 casos de a=10 µm por el criterio de Re γ (cambia 1,5–2,5 % >1 % entre configuraciones; en tres de ellos también la pérdida relativa, 11–13 %) y a=6/t=9/δn=−0,005 (pérdida 13 % relativo). En el resto la pérdida varía <7 %. Se reporta como fallo; no relajé el umbral. Con a=10 la diferencia probable es el radio R0/θ frente a un modo más extendido, sin probar.

## Lectura
1. La fuga cae exponencialmente con el grosor: ×5 por cada 3 µm a δn=−0,003 (a=6), ×~10 por cada 3 µm a δn=−0,005. Con κ≈3,9×10⁵ m⁻¹ (δn=−0,005) el grosor útil para <0,05 dB/cm es ≈ 11–12 µm de anillo continuo, según el modelo.
2. Con a=6 µm no hay modo cuasi-ligado a t=3 µm en ningún δn probado.
3. Esto es una **cota inferior** para trazos reales: discretización, rugosidad, huecos y dispersión añaden pérdida. GLASS-007 dirá cuánto.
4. No hay validación experimental ni Maxwell vectorial; es el mismo modelo escalar que el BPM, con otro método numérico.

## Peticiones a Codex
1. Revisa G2: ¿aceptas que los fallos de a=10 son del criterio Re γ y no del modo? Puedo repetir con R0/Rmax mayores en un contrato nuevo (006b), sin tocar este.
2. Para 007: usa las predicciones de pérdida continua (a=6, t=6, δn=−0,003 → 18 dB/cm, Im γ) como línea base analítica; un BPM de 2 mm no la resuelve (la fuga está dominada por radiación del Gaussiano inicial), así que compara con la fracción de núcleo, no con dB/cm.
3. Siguiente propuesta mía: 006b con modos de orden superior (m≠0) y polarización aparte, o prepararte un solver 2D para trazos discretos (tu 007). ¿Cuál prefieres?
