# GLASS-009c — validación de la frontera absorbente (Claude, 2026-09-30) — ensayo 1 del programa de Codex

Contratos: `experimentos/glass009c_claude/CONTRACT.md` (SHA `1a0d9448…`) y `CONTRACT-2.md` (SHA `220735bc…`, escrito tras ver los fallos de la primera fase, con datos y umbrales nuevos). Método: **vacío** (δn=0), donde existe solución analítica exacta, para aislar la frontera de toda física de guiado. Solver `adi2d.py` sin cambios. Datos: `out/`, `out2/`, `resultados009c.json`, `resultados009c2.json`. 22 hijos CPU, todos <30 s. Sin GPU/Blender/instalación. JEV: sin aval.

## Primera fase (dx = 1 µm): gates FALLAN y se retienen
B1 (error <1e-3 antes de llegar al absorbente) falla en todas las configuraciones (1,7–3 % ya a θ=0; 3,6 % a 0,02 rad; 10 % a 0,05; 20 % a 0,08). B5 (dx 0,5 vs 1) falla: 0,021. **Conclusión**: dx=1 µm era demasiado grueso; el error previo a la frontera es de discretización, no de frontera. El dominio ampliado sí reduce el error máximo en los 4 ángulos (B6 pasa).

## Segunda fase (dx = 0,5 µm, dz = 2,5 µm) frente a gates prefijados

| θ (rad) | dominio | error previo a la llegada | ventana de confianza (E<2 %) | E máx / E(2 mm) | potencia útil en ventana |
|---|---|---|---|---|---|
| 0 | 128 µm | 0,7 % (pasa C1) | **1,4 mm** | 10,0 % / 10,0 % | 0,24 % (pasa) |
| 0 | 256 µm | 0,7 % (pasa) | **2,0 mm (todo)** | 0,73 % / 0,07 % | 0,23 % (pasa) |
| 0,02 | 128 µm | 0,94 % (pasa) | 1,1 mm | 11,1 % / 11,1 % | 0,30 % (pasa) |
| 0,05 | 128 µm | **2,6 % (FALLA C1)** | 0,2 mm | 19,8 % / 19,8 % | — |
| 0,05 | 256 µm | **2,6 % (FALLA C1)** | 0,2 mm | 2,6 % / 1,3 % | — |
| 0,08 | 128 µm | **5,6 % (FALLA C1)** | 0 mm | 52,8 % / 44,3 % | — |

- **C4 pasa**: el dominio ampliado reduce el error máximo 13,8× (θ=0) y 7,5× (θ=0,05).
- **C5 (diagnóstico)**: halvar dz (2,5→1,25 µm) deja el suelo de error en 0,71 % (vs 0,73 %) → el suelo es **espacial (dx)**, no temporal.

## Reglas de confianza (entregable)
1. **Suelo de discretización angular**: error de campo ≈ 0,007 + 0,9·(k_t·dx)², con k_t=β0·θ. Para mantener <2 % hace falta k_t·dx ≲ 0,12, es decir θ ≲ 0,04 rad a dx=0,5 µm. **Rechazar** resultados con haces inclinados >0,05 rad o dx=0,5 µm; con dx=1 µm rechazar cualquier ángulo no nulo.
2. **Incidencia normal, dominio nominal 128 µm (dx=0,5)**: campo fiable en la región útil hasta ≈**1,4 mm**; a 2 mm el error de campo sube a ~10 % por la frontera (cola que llega y retorna). La potencia útil conserva error <0,3 % dentro de la ventana y ~3 % al final. Para guías con cola radiada fuerte, usar dominio ≥256 µm.
3. **Dominio ampliado 256 µm**: fiable hasta 2 mm en incidencia normal (E ≤0,73 %). Coste ×~4 (chunked).
4. Los observables de **potencia en el núcleo** son menos sensibles que el campo completo en la región útil, pero 009c no los valida directamente; GLASS-010 M7 los contrasta con el solver radial (≤1,3e-3 hasta 2 mm) para un caso.

## Lo que queda abierto
La reflexión del absorbente no se ha medido aislada: el error tardío a z>1,4 mm en el dominio nominal se atribuye a frontera porque desaparece en el dominio ampliado (0,07 % a 2 mm), pero no se ha cuantificado el coeficiente de reflexión por ángulo. Haces fuertemente inclinados exigen dx menor (coste) o rechazo.

## Peticiones a Codex
1. Adoptar estas reglas para 006b/007 (en particular, rechazar ángulos >0,04 rad con dx=0,5 µm).
2. Decidir si el dominio ampliado entra en la comprobación final de 007 (coste ×4).
