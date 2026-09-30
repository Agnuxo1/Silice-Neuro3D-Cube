# GLASS-009d — índice promediado por cobertura subpíxel (Claude, 2026-09-30) — contrato prospectivo, ANTES de ejecutar

Origen: 009b (SHA contrato 9d531ce6…) dejó P3 (96 trazos, cambio con dx) FALLANDO: 0,0093. Causa candidata no probada: el perfil de índice se rasteriza como máscara escalonada que cambia con dx.
Cambio ÚNICO respecto a 009b: el índice de cada píxel = δn × (fracción del píxel dentro de [unión de discos ∩ anillo r∈[a,a+t)]), supersampling 16×16. Observable = ponderado por área de núcleo (como 009b). Solver adi2d.py, λ, geometría, dz=2,5 µm, 800 pasos, σmax=4e4 m⁻¹, dominio 128 µm: sin cambios. Se conserva la integral de |δn| (área modificada exacta en lugar de píxeles enteros).
Casos: continuo y 96 trazos (32/corona), dx∈{0,5; 0,4; 0,625} µm (N=256; 320; 205 → N=round(128/dx)=205 con dominio 128,125 µm: se declara el dominio efectivo N·dx). Un hijo <30 s; dx=0,4 en 2 trozos.
Gates (prefijados): 
 Q1 integral: |Σ|δn|·dx² − δn·área_exacta_unión| / (…) < 1e-3 en cada dx (área exacta = 8,4π/… calculada por trama fina 4096²).
 Q2 continuo: |P(0,4) − P(0,5)| < 0,005 y <10 %.
 Q3 96 trazos: mismos umbrales.
 Q4 tendencia: |P(0,5) − P(0,625)| ≥ |P(0,4) − P(0,5)| en ambos perfiles (convergencia monótona en dx); si no, se reporta como no monótono, sin declarar convergido.
Se reportan también los valores de 009b (índice escalonado) para los mismos dx cuando existan. Fallos retenidos; umbrales fijos; no se toca código de Codex. Sin GPU/Blender.
