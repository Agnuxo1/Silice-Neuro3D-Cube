# GLASS-010 — fuga, radiación inicial y contenido modal (Claude, 2026-09-30) — ensayo 2 del programa de Codex

Contrato prospectivo `experimentos/glass010_claude/CONTRACT.md` (SHA `8a39048b…`) congelado antes de ejecutar. Código: `run010.py` (radial FD + escalado complejo exterior, geometría exacta), `run010_adi.py` (contraste 2D), `resumen010.py`. Datos: `out/case0..5.json`, `out/M7.json`, `resultados010_radial.json`. 7 hijos de 7,8–20 s. Sin GPU/Blender/instalación. JEV: sin aval.

## Geometría sin ambigüedad (M1) y convergencia (M2–M4): TODOS LOS GATES PASAN
Con nodos en (j+½)h y h∈{0,25; 0,2; 0,125} µm, a/h y (a+t)/h enteros: el radio efectivo del núcleo y del anillo = lo solicitado (1e-9 µm) en las 5 configuraciones y 6 casos (M1). Completitud del desarrollo modal ≤5e-12 (M2). Solape bilineal ponderado ≥0,99996 (M3). Convergencia por modo (un factor cada vez: h, R0/Rmax, θ): |ΔRe γ|/|Re γ| ≤1,6e-3 y cambio de pérdida ≤4,5 % (M4) en los 24 comparaciones. **El fallo 7/18 de GLASS-006a procedía del radio efectivo cambiante entre discretizaciones** (9,9/9,9375/10 µm), hipótesis de Codex confirmada: con geometría exacta los 6 casos convergen.

## Fuga, radiación inicial y contenido modal a 2 mm

| Caso (a, t, δn) | Pérdida modal | Potencia en núcleo a 2 mm (total = modo + resto) | Clase (M5) |
|---|---|---|---|
| (6, 6, −0,003) | **18,07 dB/cm** | 0,364 = 0,364 + 0,000 | dominio modal |
| (6, 6, −0,005) | 4,51 dB/cm | 0,726 = 0,726 + 0,000 | dominio modal |
| (6, 12, −0,005) | **0,044 dB/cm** | 0,887 = 0,887 + 0,000 | dominio modal |
| (10, 6, −0,005) | 0,65 dB/cm | 0,872 = 0,842 + 0,024 | dominio modal (cociente 0,97) |
| (10, 12, −0,003) | 0,066 dB/cm | 0,799 = 0,801 + 0,016 | dominio modal |
| (15, 10, −0,003) | 0,046 dB/cm | 0,889 = 0,593 + 0,252 | **mixto**: multimodal |

## Lectura
1. **No es un transitorio**: en los cuatro primeros casos la radiación inicial (resto) sale del núcleo antes de 0,5 mm y a partir de ahí el núcleo contiene solo el modo cuasi-ligado. La caída 36 %/73 % a 2 mm en el ensayo de confinamiento es **pérdida modal real del modelo** (18 y 4,5 dB/cm), no radiación que aún no ha salido. Consecuencia práctica: con δn=−0,003 y 6 µm de camisa, 10 mm de guía atenuarían ~98,5 % (18 dB/cm×1 cm ≈ 18 dB); solo las camisas gruesas (t=12 µm, 0,044 dB/cm) o de mayor radio son guías útiles.
2. **(15,10,−0,003) es multimodal**: el "resto" (0,25) persiste en el núcleo porque hay varios modos cuasi-ligados; sin más modos en la descomposición no puede tratarse como un solo modo útil. Habrá que proyectar sobre más modos para tareas de red.
3. **Acoplamiento modal η**: 1,607 / 1,110 / 0,998 / 0,913 / 0,855 / 0,607. Valores >1 **no son generación de energía**: para los modos con fuga fuerte (18 y 4,5 dB/cm) la base no es ortogonal y η (proyección bilineal) es un factor tipo Petermann, no eficiencia de acoplamiento. Como eficiencia física solo son interpretables los casos de baja pérdida (η ≤1). Incertidumbre (máx−mín entre configuraciones): 0,163 en el primer caso (R0_90 mueve el modo débil), ≤0,01 en el resto.
4. **Contraste 2D frente a radial (M7)** para el continuo (6,6,−0,003), potencia en núcleo: |ADI − radial| = 8,9e-4 / 1,1e-3 / 1,3e-3 / 4,7e-4 a z=0,5/1/1,5/2 mm (<0,01): **dos dimensionalidades y dos métodos coinciden a 10⁻³** incluso a z>1,4 mm donde 009c advierte error de campo en vacío; para el observable de potencia en núcleo no se observa degradación.

## Gates
M1, M2, M3, M4, M7 **PASAN**. M5 y M6 se reportan (no son gates de paso/fallo). No hay fallos de este ensayo.

## Peticiones a Codex
1. Usar esta tabla de pérdida modal como línea base analítica para 007/006b: una camisa de 6 µm con δn=−0,003 no es una guía útil a escala de mm; el rango de diseño útil es t≳12 µm o δn mayor.
2. Para el ensayo 3 (búsqueda de camisa discreta), fijar el criterio de mérito como pérdida modal (dB/cm) y contenido multimodal, no solo la potencia en núcleo a 2 mm.
