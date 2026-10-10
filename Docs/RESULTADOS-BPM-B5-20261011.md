# BPM: pérdida del modo guiado (B5, 2026-10-11)

Contrato: `experimentos/bpm_claude/CONTRATO-bpm-r5.md`. Umbral B3 de la ronda 1, sin cambio: pérdida a 1 mm ≤ 1e-5. Modelo escalar paraxial, ventana W = 40 µm, h = 0,2 µm, CAP base, dato inicial LP01 analítico.

| dz (µm) | Pérdida a 1 mm | Fuente |
|---|---|---|
| 1 | 2,460e-4 | `r5_runs/dz1.json` (reproduce la ronda 4) |
| 0,5 | 7,369e-5 | `r5_runs/dz05.json` |
| 0,25 | 3,719e-5 | `r5_runs/log_r5_resto.txt` |
| 0,125 | 2,758e-8 | `r5_runs/log_r5_resto.txt` |
| 0,0625 | 2,675e-8 | `r5_runs/log_r5_dz00625.txt` |

Referencia de primer orden del CAP sobre el modo LP01: 3,167e-8 por mm (`r5_runs/pert.json`).

## Lectura

- **B3 se cumple** para dz ≤ 0,125 µm. Entre dz = 0,125 y dz = 0,0625 µm la pérdida cambia un 3 %, tres órdenes de magnitud por debajo del umbral.
- El valor estable (≈ 2,7e-8 por mm) coincide con la estimación de primer orden del CAP (3,2e-8). Eso es compatible con que la pérdida de dz ≥ 0,25 µm sea un artefacto de la partición temporal del propagador.
- **Límite:** la transición entre dz = 0,25 y dz = 0,125 µm solo tiene un punto por lado. La caída (factor ~1350) no es una ley de potencia limpia, así que el mecanismo exacto no está demostrado.
- **Criterios de convergencia por orden** (D-ORD, D-CONV, D-EXT, D-PERT) fallan al evaluar la sucesión completa de cuatro puntos. No se dan por cumplidos. La evidencia de convergencia es el par dz = 0,125 y 0,0625 µm, con un 3 % de diferencia.

## Consecuencia

- El BPM queda como **parcialmente resuelto**: la pérdida artificial desaparece con dz ≤ 0,125 µm, y en ese régimen B3 se cumple.
- G3 (longitud de transferencia del acoplador) se ejecuta con dz = 0,125 µm, para d = 14 y 16 µm. Sus resultados se publicarán aparte.
