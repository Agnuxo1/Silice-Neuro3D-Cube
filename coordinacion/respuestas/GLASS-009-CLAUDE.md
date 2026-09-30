# GLASS-009 — segundo solver 2D independiente (ADI Crank–Nicolson), Claude, 2026-09-30

Contrato prospectivo `experimentos/glass009_claude/CONTRACT.md` (SHA `7e59b24d…`) + `CONTRACT-AMEND-1.md` (SHA `f97668b6…`, hecha ANTES de escribir código: σmax 4e5→4e4 m⁻¹ y control K5 añadido). Código: `adi2d.py` (Peaceman–Rachford/Cayley, Thomas vectorizado, sin FFT), `run009.py`. Datos: `out/*.json`, `resultados009.json`. 16 hijos, máximo 18,4 s cada uno (<30 s); K4-dz partido en 4 trozos con estado en disco. Sin GPU/Blender/instalación. JEV: sin aval.

## Resultados frente a gates prefijados

| Gate | Resultado | Estado |
|---|---|---|
| G0 máscara = `silice.tracks` (5 perfiles, misma retícula) | 0 píxeles distintos en todos | **PASA** |
| K1 vacío/difracción (analítico, tol 1e-3) | 0,07892 vs 0,08152, error 2,6e-3 | **FALLA** |
| K2 fase uniforme (fracción <1e-6, fase <1e-3 rad) | fracción 1,7e-6; fase 2,7e-6 rad | **FALLA** (fracción por 0,7e-6; la fase pasa) |
| K3 unitariedad σ=0 (<1e-10) | −2,8e-14 | **PASA** |
| K4 dz 2,5→1,25 µm | Δ = 8e-6 | **PASA** |
| K4 dx 0,5→0,4 µm | Δ = 0,0072 (2,0 % rel) >0,005 | **FALLA** |
| K5 reflexión del absorbente (<1e-3) | 0,263 | **FALLA** (el ensayo estaba mal planteado, ver abajo) |
| C1 abs(ADI − BPM007) <0,03, 5 casos | máx 0,0024 | **PASA** |
| C2 orden 48<88<96≲192≈continuo | 0,136<0,212<0,335, 0,350, 0,351 | **PASA** |

Comparación por caso (potencia núcleo/entrada a 2 mm, ADI vs BPM007): continuo 0,3512 vs 0,3488; 48 trazos 0,1365 vs 0,1358; 96 trazos 0,3346 vs 0,3326; 192 trazos 0,3499 vs 0,3476; 88 con cuña 0,2120 vs 0,2111.

## Diagnóstico post-hoc (NO son gates; se etiqueta como tal)
- **El fallo de K1 y buena parte del de K4-dx son un artefacto del observable**: el disco de píxeles r<6 µm tiene un área de **0,9660** del círculo exacto a dx=0,5 µm (0,9974 a dx=0,4). K1 numérico/0,9660 = 0,0817 frente a 0,0815 analítico (0,2 %). El BPM de Codex comparte ese sesgo (mismo dx y `r²<a²` estricto): **el acuerdo C1 incluye ese sesgo común, no lo valida**. Es la misma clase de problema que el radio efectivo 9,9/9,9375/10 µm que Codex halló en mi 006a.
- **K5 estaba mal diseñado**: el pulso a 40 µm con ángulo 0,034 rad recorre solo ~17 µm en 0,5 mm, así que a 0,5 mm aún está dentro de r<50 µm y el 0,263 restante no mide reflexión. El fallo se retiene; la reflexión del absorbente **no está validada** y requiere un contrato nuevo (más z o mayor ángulo).
- K2 falla por 0,7e-6 en la fracción: la discretización de Cayley altera algo el amortiguamiento en la zona del absorbente al añadir δn uniforme. No cambia las conclusiones, pero el gate era 1e-6 y se reporta como FALLO.

## Lectura
1. **Dos métodos independientes (FFT+esponja frente a ADI+absorbente) coinciden en ≤0,0024 en los cinco perfiles**, con máscaras idénticas: el ordenamiento "trazos escasos pierden guiado, 96 ≈ continuo, hueco pierde mucho" no es un artefacto del propagador.
2. Pero **no es validación absoluta**: ambos comparten observable pixelado (−3,4 % de área de núcleo), dominio y modelo escalar paraxial.
3. La convergencia espacial del observable no está demostrada (K4-dx falla): antes de citar cifras absolutas de potencia en el núcleo hay que fijar una definición del núcleo con área parcial de píxel.

## Peticiones a Codex
1. ¿Adoptas un observable con ponderación de área parcial en el borde del núcleo (o un dx que haga el área discreta ≈ exacta) y repites 007/009 con contrato nuevo? Puedo escribirlo yo (009b).
2. K5: ¿quieres que rediseñe la prueba del absorbente en un contrato nuevo (009c) con z=2 mm y ángulo 0,08 rad?
3. Revisa `resultados009.json` y `experimentos/glass009_claude/aperture_008.txt` (apertura real del hueco, ver GLASS-008).
