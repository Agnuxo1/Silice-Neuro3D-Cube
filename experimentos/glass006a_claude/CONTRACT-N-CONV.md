# GLASS-006a · convergencia en N para a = 10 µm · contrato prospectivo (2026-10-09)

Publicado antes de calcular. Continúa el diagnóstico de `CONTRACT-G2-DIAG.md` (ver `diag_g2_radius10.json`) y no modifica resultados anteriores.

## Hallazgo previo (diagnóstico, ya ejecutado)

En los diez casos a = 10 µm, la malla sola (N 500 → 700, dominio fijo) cambia Re γ entre 2,4 % y 2,7 %, más que el cambio combinado nominal → B (1,5 % a 2,5 %). Los dos efectos se compensan en parte. Así, la comparación nominal con B subestimaba el error de discretización. El dominio solo cambia Re γ entre 1,6 % y 3,2 %. θ no influye.

## Pregunta

¿Converge Re γ al refinar N con el dominio nominal (R0 = 70 µm, Rmax = 150 µm, θ = 0,6)? ¿Cumple G2 entre las dos mallas más finas?

## Diseño

- Casos: los diez de a = 10 µm (t ∈ {3, 6, 9, 12, 18} µm, δn ∈ {−0,003, −0,005}).
- Mallas: N ∈ {500, 700, 900, 1100}. Dominio y θ fijos en valores nominales.
- Selección de modo: la misma que `run006a.py` (|Im γ| < 3000 m⁻¹, potencia en el núcleo > 0,3, mayor Re γ).

## Criterios (sin cambios respecto de G2)

- Pérdida: cambio relativo < 10 % **o** absoluto < 0,005 dB/cm.
- Re γ: cambio relativo < 1 %.
- G2 se evalúa entre las dos mallas más finas (900 y 1100). Se publican también todos los pares sucesivos.

## Predicción fijada antes

- **P1.** Si el error de discretización decrece como 1/N² (orden 2), el cambio de Re γ entre N = 900 y N = 1100 sale de los datos de 500 → 700 y es ≈ 0,5 %. Entonces Re γ cumple G2 en ese par.
- **P2.** Si el cambio entre 900 y 1100 es ≥ 1 %, el orden de convergencia es menor que 2 y G2 **no** se cumple con N ≤ 1100. Se declara así, sin relajar el criterio.

## Reglas

- Un proceso por caso, por debajo de 30 s en un hilo.
- No se reajusta ningún umbral. Los fallos se publican.
- Este contrato no cierra Q4 ni reemplaza el veredicto original de GLASS-006a. Solo informa sobre la convergencia de los modos de a = 10 µm.
