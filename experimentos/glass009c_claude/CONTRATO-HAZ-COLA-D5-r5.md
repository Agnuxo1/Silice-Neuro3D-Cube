# GLASS-009c · D5 · validación de vacío con haces de cola espectral controlada (ronda 5, r5) · contrato prospectivo

Redactado: 2026-10-10, ≈10:23 UTC, ANTES de ejecutar ninguna corrida D5. Hora límite de entrega: 12:45 UTC.
Carpeta: `experimentos/glass009c_claude/`. Archivos nuevos: este contrato, `validacion_vacio_D5_run.py`, `validacion_vacio_D5_lote.sh`, `validacion_vacio_D5_analisis.py`, `D5_out/`, `resultados009c_D5.json`. No se modifica ningún archivo existente. Solo se leen `D3_out/*.json`, `resultados009c_D4.json` y `../glass009_claude/adi2d.py`. No se escribe ningún informe `.md`.

Todo es un modelo numérico (paraxial, δn = 0, θ = 0, sin medida). No hay dispositivo. El analítico es la predicción sin frontera; el numérico es el modelo discreto del solver de 009c.

## Pregunta
¿Existe un ancho de haz inicial w0 ∈ {6; 8; 12} µm con el que la métrica de retorno M cumpla K1 (M < 1e-4) en la ventana común, con el mismo absorbente de referencia (base: f = 0,2, p = 4) y dominio 256 µm?

Motivo: D4 atribuye el retorno casi por completo al ancho w0 (η² = 0,999996) y no al absorbente ni al dominio. Con w0 = 2 µm, M = 2,0597e-2; con w0 = 4 µm, M = 4,3842e-3 (ambos 256 µm, base, ventana común). Ninguna de las 8 celdas de D4 cumple K1.

## Punto de partida (se cita, no se reabre)
- K1 = 1e-4 (−40 dB), sin cambio. Ronda 1 (`CONTRATO-VACIO.md`, `RESULTADOS-009C-VACIO.md`).
- Ventana común W = {0,2 ≤ z ≤ 2,0 mm}, 19 muestras cada 0,1 mm (`CONTRATO-VENTANA-COMUN-D4-r4.md`).
- Tolerancias K0 de D3 y D4 (1e-9 y 1e-12): se mantienen.
- Bandas de malla heredadas de 009c (K4 de D4): q ∈ [2,5; 6] → discretización (orden ~2); q ∈ [0,67; 1,5] → independiente de la malla; otro → indeterminado.
- Criterio de atribución de D4 (η² de ANOVA): se cita como descriptivo; D5 no hace ANOVA.

## Cambio de protocolo (declarado como tal)
- **Haz de entrada:** w0 ∈ {6; 8; 12} µm, en lugar de {2; 4} µm de 009c, D3 y D4. Cualquier celda que cumpla K1 se publica como **cambio de protocolo de haz**. No se publica como validación del absorbente con el criterio original.
- Se mantienen: dominio 256 µm, ventana común W de D4, absorbente base (f = 0,2, p = 4), K1 = 1e-4.
- El absorbente no cambia en D5: no se prueba f = 0,3 ni p ≠ 4 a 256 µm.

## Diseño
**Corridas principales (3, nuevas):** w0 ∈ {6; 8; 12} µm; θ = 0; dominio 256 µm (N = 512); dx = 0,5 µm; dz = 2,5 µm; 800 pasos (z = 2 mm); muestreo cada 40 pasos (21 instantes; 19 en W). Absorbente base: σmax = 4e4 m⁻¹, f = 0,2, p = 4. λ = 1550 nm, n0 = 1,444, b0 = k0·n0. Solver `adi2d.py` de `../glass009_claude` sin cambios.

**Referencias ya calculadas (solo lectura, no se recalculan):**
- w0 = 2 y 4 µm, 256 µm, base: `D3_out/w2_d256_base.json`, `D3_out/w4_d256_base.json`. Dan la curva M(w0) en 256 µm.
- w0 = 6 µm, 128 µm, base: `D3_out/V1_w6_d128_base.json`. Descriptivo del efecto del dominio.

**Control de reproducción (K0a):** w0 = 6 µm, 128 µm, base, θ = 0, con el runner nuevo. Se compara fila a fila con `D3_out/V1_w6_d128_base.json`.

**Diagnósticos (no son el veredicto K1; sirven para decidir si el veredicto es fiable), solo para w0 = 12 µm, el candidato más favorable (M baja con w0 en D4):**
- G12a: w0 = 12, 256 µm, dx = 0,25 µm (N = 1024), dz = 2,5 µm, 800 pasos.
- G12b: w0 = 12, 256 µm, dx = 0,5 µm, dz = 1,25 µm, 1600 pasos (muestreo cada 80).

## Cola espectral (paso 3): definición fijada en este contrato
El encargo pide «la fracción de energía de Fourier fuera de la banda del absorbente», pero no fija la banda. La fijo aquí, antes de calcular:

- **Cinemática paraxial.** La ecuación es dA/dz = i/(2b0)∇²A − σA. Una componente de número de onda transversal (kx, ky) se desplaza con velocidad (kx, ky)/b0. Con θ = 0 el centro del haz está en x = 0.
- **Banda del absorbente en Fourier (primaria).** Una componente llega al borde absorbente, |x| o |y| = (1 − f)·L/2 = 102,4 µm, antes de z_max = 2,0 mm si max(|kx|, |ky|)·z_max/b0 ≥ (1 − f)·L/2. Así que la banda es el cuadrado max(|kx|, |ky|) ≤ k_c, con

  **k_c = b0·(1 − f)·(L/2)/z_max**, b0 = k0·n0 ≈ 5,853e6 m⁻¹, L = 256 µm, f = 0,2, z_max = 2,0 mm → k_c ≈ 2,997e5 m⁻¹.

- **Fracción fuera de la banda:** F_fuera(w0) = Σ_{max(|kx|,|ky|) > k_c} |Â0(k)|² / Σ |Â0(k)|², con Â0 la FFT de A(0) en la malla del solver (N = 512, dx = 0,5 µm).
- **Forma analítica (referencia).** Para una gaussiana, la energía espectral es ∝ exp(−k²w0²/2) por eje. Por tanto F_fuera = 1 − erf(k_c·w0/√2)².
- **Sensibilidad (descriptiva, sin pass):** banda radial |k| ≤ k_c.
- **Nota.** La banda es una definición cinemática del encargo, no una propiedad medida del absorbente.

## Definiciones
- P0 = Σ|A(0)|²·dx² (= 1). ΔP_u(z) = P_u,num(z) − P_u,an(z). Zona útil r < 40 µm.
- **M = máx_{z ∈ W} |ΔP_u(z)|/P0**, con W = {0,2 ≤ z ≤ 2,0 mm}, 19 muestras. Es la métrica de K1 de D4.
- q = M(dx 0,5)/M(dx 0,25) (G12a frente a la corrida principal de w0 = 12).

## Criterios numéricos (umbrales fijados AHORA)
- **K0 (herramienta). Pasa si se cumplen todos:**
  - K0a: el control de reproducción (w0 = 6, 128 µm, base) coincide con `V1_w6_d128_base.json`: max|ΔΔP_u|/P0 ≤ 1e-9 y max|ΔE| ≤ 1e-9 en todas las muestras.
  - K0b: σ del runner igual a `adi2d.sigma_map(N, dx, 4e4, 0,2)`, diferencia relativa ≤ 1e-12, en las corridas nuevas.
  - K0c: |A(0) − A_an(0)|/max|A(0)| ≤ 1e-9 en las 3 principales y en G12a y G12b.
  - K0d: P_total no aumenta entre muestras más de 1e-9·P0, en todas las corridas nuevas.
  - K0e: |P0 − 1| ≤ 1e-12, en todas las corridas nuevas.
  - K0f: 19 muestras en W en las 3 principales.
- **K1 (retorno, principal).** Pasa si **alguna** de las 3 corridas principales cumple M < 1e-4. G12a y G12b no cuentan para K1. Si pasa, se publica como **cambio de protocolo de haz**.
- **K2 (cola espectral, verificación).** Pasa si:
  - K2a: la forma analítica 1 − erf(k_c·w0/√2)² coincide con una integral 1D numérica fina de la energía espectral normalizada, con error relativo ≤ 1e-6, para w0 ∈ {2; 4; 6; 8; 12} µm.
  - K2b: |F_fuera(FFT) − F_fuera(analítico)| ≤ 0,02 (absoluto) para w0 ∈ {2; 4; 6; 8; 12} µm. La tolerancia cubre la cuantización del borde de la banda: k_c/Δk ≈ 12,2, con Δk = 2π/(N·dx).
- **K3 (malla, w0 = 12 µm).** q = M(corrida principal, dx 0,5)/M(G12a). Pasa si la clase de q no es «indeterminado» (bandas de 009c).
- **K4 (paso temporal, w0 = 12 µm).** Pasa si |M(dz 2,5) − M(dz 1,25)|/M(dz 1,25) < 0,10, con G12b frente a la corrida principal de w0 = 12.
- **K6 (descriptivo, sin pass).** Exponente log-log de M(w0) en 256 µm para w0 ∈ {2; 4; 6; 8; 12}. Tabla de F_fuera(w0) (primaria y radial). Descriptivo del efecto de dominio: M(w0 = 6, 128 µm) frente a M(w0 = 6, 256 µm).

## Reglas de decisión (paso 3 y 4)
- **Si K1 pasa** para alguna variante w0 ∈ {6; 8; 12}: se declara «CAMBIO DE PROTOCOLO DE HAZ, w0 = X µm». Se da F_fuera(X) con la banda primaria (y la radial como sensibilidad). Se declara que esto **no** valida el absorbente con el criterio original. Si G12a o G12b contradicen el resultado de la corrida principal, se dice.
- **Si ninguna cumple K1:** se publica «ningún haz de los probados (w0 = 2, 4, 6, 8, 12 µm) cumple K1 = 1e-4 con el absorbente base y dominio 256 µm». Así la validación de vacío con K1 no se cumple con ningún haz probado.

## Reglas de publicación
- Cada criterio se evalúa con código. `pass_` queda en `resultados009c_D5.json` calculado por el script.
- `status = "done"` solo si todos los criterios se evaluaron. `"partial"` si falta alguno. `"blocked"` si depende de algo externo.
- Cada criterio no cumplido se publica con sus cifras.
- Separación explícita: lo calculado (K0–K4, M, F_fuera) frente a lo supuesto (definición de banda, tolerancias K2b y K0a).

## Lo que NO afirmo
- Solo θ = 0. Paraxial, δn = 0. Nada se extiende a θ > 0, a guía ni a dispositivo.
- El muestreo cada 0,1 mm no ve los máximos entre muestras.
- La conclusión K1 vale para el absorbente base (f = 0,2, p = 4) y dominio 256 µm. No se ha probado otro absorbente a 256 µm en D5.
- La banda de Fourier es una definición cinemática fijada en este contrato. No es una medida del absorbente.
- No se consultó el enrutador JEV con provenance=jev para la definición de banda. Se usó `router.py plan` (ver JSON).
- Un criterio no cumplido se publica con sus cifras.

## Límites conocidos (antes de calcular)
- Con w0 = 12 µm, la aproximación paraxial es más sólida que con 2 µm, pero el dominio de 256 µm sigue siendo el de 009c.
- La malla dx = 0,5 µm tiene unos 24 puntos por radio a w0 = 12 µm. El diagnóstico G12a comprueba la convergencia de malla.
- **Corrección antes de calcular (sin cambio de umbrales).** El haz libre se ensancha según w(z) = w0·√(1 + (z/zR)²), con zR = b0·w0²/2. A z = 2 mm: w(2 mm) ≈ 114 µm para w0 = 6 µm, ≈ 86 µm para w0 = 8 µm y ≈ 59 µm para w0 = 12 µm. El borde absorbente está en |x| = 102,4 µm. Con w0 = 6 y 8 µm, el haz libre alcanza el absorbente dentro de la ventana. La referencia analítica no incluye absorción. Esto es un límite del diseño, no algo que D5 corrige. Se publica tal cual.
