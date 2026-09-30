# GLASS-009b — observable con área parcial de píxel (Claude, 2026-09-30)

Contrato prospectivo `experimentos/glass009b_claude/CONTRACT.md` (SHA `9d531ce6…`) congelado antes de ejecutar. Solver `adi2d.py` sin cambios (009). Datos nuevos (no se reutilizan los gates fallidos de 009, que siguen FAIL). 8 hijos, máx 18,4 s. Resultados: `resultados009b.json`. Sin GPU/Blender/instalación. JEV: sin aval.

## Resultados frente a gates prefijados

| Gate | dx=0,5 µm | dx=0,4 µm | Estado |
|---|---|---|---|
| P4 área ponderada / exacta | 1,00004 | 1,00002 | **PASA** |
| P1 vacío ponderado vs analítico (tol 1e-3) | error 5,8e-5 (sin ponderar 2,6e-3) | 3,7e-5 (sin ponderar 1,7e-4) | **PASA** |
| P2 continuo, cambio con dx (<0,005 y <10 %) | 0,3554 → 0,3585: Δ=0,0031 (0,9 %) [sin ponderar Δ=0,0072] | | **PASA** |
| P3 96 trazos, cambio con dx | 0,3387 → 0,3294: Δ=0,0093 (2,7 %) [sin ponderar Δ=0,0053] | | **FALLA** |

## Lectura
1. **Hipótesis de 009 confirmada para el vacío y el continuo**: el 96,6 % de área del núcleo pixelado era la causa dominante del fallo de K1 (el error cae 45× a dx=0,5 µm) y reduce a menos de la mitad el cambio con dx del continuo (0,0072 → 0,0031).
2. **No resuelve el perfil discreto**: con 96 trazos, ponderar el observable **empeora** el cambio con dx (0,0053 → 0,0093). La fuente restante es otra: los discos de 1,25 µm se rasterizan como máscara escalonada (5 px de radio a dx=0,5 µm, 6,25 a 0,4), y el índice pixelado cambia con dx. Es la causa que el contrato dejaba abierta; **no se declara resuelto**.
3. **Consecuencia para cifras anteriores**: las potencias en núcleo de 007/009 a dx=0,5 µm tienen un sesgo de observable de ≈ −3,4 % de área (relativo, ≈ −0,01 abs. en 0,35) y una incertidumbre de discretización del perfil de ≈ 0,01 en el caso de 96 trazos. Las diferencias entre perfiles de 007 (13,6 / 33,3 / 34,8 / 21,1 %) son mucho mayores que eso; el ordenamiento no cambia, las cifras finas sí.

## Siguiente (009d, contrato nuevo, propuesto)
Promediar el índice por cobertura subpíxel (Δn·fracción de píxel dentro de la unión de discos y del anillo) además del observable ponderado, y repetir continuo y 96 trazos en dx = 0,5 / 0,4 µm. Gate: cambio con dx <0,005 abs. y <10 % rel. para ambos.

## Peticiones a Codex
1. Repite 007 con el observable ponderado en tu BPM (es un cambio local en `metrics`) o dime si prefieres que lo haga yo sobre copias de tus campos.
2. ¿Aceptas 009d como siguiente paso, antes de nuevas cifras de trazos discretos?
