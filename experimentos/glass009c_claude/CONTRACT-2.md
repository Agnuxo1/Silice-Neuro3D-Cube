# GLASS-009c-2 — contrato prospectivo (Claude, 2026-09-30), ANTES de ejecutar nada de esta fase

Origen: 009c (contrato SHA 1a0d9448…) con dx=1 µm: B1 FALLA (error de campo 1,7–3 % ya ANTES de que el haz llegue al absorbente) y B5 FALLA (dx 0,5 vs 1: 0,021). Con inclinación el error previo a la llegada crece (0,036 a 0,02 rad, 0,10 a 0,05, 0,20 a 0,08): dispersión numérica del esquema (error de velocidad de grupo ~ (k_t·dx)²/6), no frontera. Con dx=0,5 µm y θ=0 el error previo baja a 7,3e-3 y la ventana de confianza (E<2 %) sube a 1,4 mm. Estos resultados se conservan como fallos de 009c.
Fase nueva, datos nuevos, umbrales nuevos (declarados AQUÍ, no ajustados a los datos de 009c salvo por la razón arriba):
 · Todas las corridas con dx=0,5 µm, dz=2,5 µm, 800 pasos, región útil r<40 µm, σmax=4e4, muestreo cada 40 pasos, misma referencia analítica y misma definición de z_arr que 009c.
 · A (nominal 128 µm, N=256): θ ∈ {0,02; 0,05; 0,08} rad.
 · B (diagnóstico del suelo de error): nominal 128 µm, θ=0, dz=1,25 µm, 1600 pasos (2 trozos de 800), para separar error temporal (dz) de espacial (dx).
 · C (dominio ampliado 256 µm, N=512, trozos de 200 pasos): θ ∈ {0; 0,05}.
Gates:
 C1 suelo de discretización: E(z)<2e-2 para todo z<z_arr, todas las corridas A y C.
 C2 ventana de confianza (mayor z con E<2e-2 en todos los instantes hasta él), por (θ, dominio).
 C3 potencia útil: |P_u,num−P_u,an|/P_u,an<1e-2 dentro de la ventana C2.
 C4 el dominio ampliado reduce Emax respecto al nominal del mismo θ (θ=0 y 0,05).
 C5 (diagnóstico, sin gate de paso) cuánto cambia E(z≤0,4 mm) con dz 2,5→1,25.
 C6 regla de entrega: para cada θ se declara "confiable hasta z_max" o "rechazar".
Fallos retenidos; no se ajusta nada tras ver datos. Hijos <30 s; estado de trozos en disco.
