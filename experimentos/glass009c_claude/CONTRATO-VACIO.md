# GLASS-009c-VACIO · completar la validación en vacío de la frontera absorbente · contrato prospectivo

Redactado: 2026-10-10 03:33 UTC, ANTES de ejecutar ninguna corrida nueva. Hora límite de entrega: 04:50 UTC.
Estado de partida: 009c (CONTRACT.md) y 009c-2 (CONTRACT-2.md) están cerrados como fallos parciales. Validado: B4 (error de potencia en ventana) y C3 en θ=0; C1 con dx=0,5 para θ ≤ 0,02. No validado: B1 y B5 con dx=1,0; C1 para θ ≥ 0,05; la ventana de confianza a θ ≥ 0,05. Este contrato no reabre esos fallos; los amplía.

## Pregunta
¿Cuánta energía vuelve desde el absorbente hacia la zona útil r < 40 µm en vacío (δn = 0), y ese retorno es del absorbente o de la discretización?

## Modelo (no es un dispositivo)
- Solver `adi2d.py` (glass009_claude, ADI Peaceman-Rachford, paraxial, sin FFT). Ecuación dA/dz = i/(2 b0) ∇⊥²A + i k0 δn A − σ A, con δn = 0.
- Absorbente: σ(e) = σmax · max((e − (1 − f))/f, 0)^p, con e = max(|x|,|y|)/(N dx/2), σmax = 4·10⁴ m⁻¹ fijo.
- Línea de base 009c: f = 0,2, p = 4. Haz gaussiano w0 = 6 µm con inclinación θ, referencia analítica exacta de 009c (sin frontera).
- Predicción y medida, separadas: el analítico es la predicción sin frontera; el numérico es el modelo discreto. No hay medida de laboratorio.

## Definiciones (fijadas aquí)
- P0 = Σ|A(0)|² dx² (normalizada, ≈ 1). Todas las potencias se dan en unidades de P0.
- Zona útil r < 40 µm. Banda absorbente de la configuración: e > 1 − f.
- z_arr: primer z con P_banda,an > 1e-4·P0 (misma definición que 009c; con f = 0,2 coincide con 009c).
- ΔP_u(z) = P_u,num(z) − P_u,an(z). Retorno ρ(z) = max(0, ΔP_u); pérdida λ(z) = max(0, −ΔP_u).
- Ventana W = { z ≥ z_arr }. Muestreo cada 40 pasos (dz = 2,5 µm, 20 instantes), igual que 009c.
- Error de campo E(z) = ‖A_num − A_an‖/‖A_an‖ en r < 40 µm.
- Nota: al variar f o p cambia z_arr y por tanto la ventana. Las comparaciones entre configuraciones usan cada una su ventana.

## Hipótesis
- H0 (nula): en la malla 009c, max_W |ΔP_u|/P0 < 1e-4 para θ ∈ {0; 0,02; 0,05; 0,08}.
- H1: el error de potencia en W es de discretización (cae con dx², orden 2), no un retorno de la pared.
- Predicción provisional, previa a datos nuevos: con el 0,24 % de error de potencia de 009c a θ = 0 (dx = 0,5), H0 probablemente falla y el error se atribuye sobre todo a discretización. Se comprueba en D4, no se afirma antes.

## Métodos
- **D1 (retorno en vacío, malla 009c).** Dominio nominal 128 µm y ampliado 256 µm, dx = 0,5 µm (f = 0,2, p = 4). Se reutilizan las corridas existentes de 009c (out/, out2/) sin re-ejecutarlas, y se añaden las que faltan (256 µm con θ = 0,02 y 0,08). Dx = 1,0 µm se reporta como diagnóstico.
- **D2 (barrido del absorbente).** Configuraciones (f, p): (0,2; 4) de línea de base, (0,2; 2), (0,2; 6), (0,1; 4), (0,3; 4). Malla nominal 128 µm, dx = 0,5 µm, σmax fijo, θ ∈ {0; 0,02; 0,05; 0,08}. Se reporta la absorción integrada A_int = σmax·f·W/(p+1), con W = N dx/2.
- **D3 (fase frente al ángulo).** Con el campo final (z = 2 mm): ψ_ov(θ) = arg⟨A_an, A_num⟩ sobre r < 40 µm, y ψ_err(θ) = arg⟨A_an, A_num − A_an⟩. Se compara con arg(r) de `experimentos/frontera_claude/fase_resultados.json` en θ coincidentes (0,02 y 0,08).
- **D4 (malla fina).** dx = 0,25 µm (N = 512, 128 µm), mismo resto que la línea de base, θ ∈ {0; 0,02; 0,05; 0,08}. Se compara con dx = 0,5 µm.
- **Referencia 1D.** R(θ) = R0^(sin θ), R0 = 1e-4 (absorbente 1D de `RESULTADOS-ABSORBENTE.md`). Se compara sólo bajo el criterio K6.

## Criterios numéricos (umbrales fijados AHORA)
- **K0 (verificación de herramienta).** (a) Con f = 0,2, p = 4, el runner nuevo reproduce las filas de 009c: |ΔE| y |ΔP_u| < 1e-9 para los 4 θ. (b) σ del runner igual a `adi2d.sigma_map` (f = 0,2, p = 4): diferencia máxima < 1e-12·σmax. (c) |A(0) − A_an(0)| / max|A(0)| < 1e-9. (d) P_total,num no aumenta entre muestras (tolerancia relativa 1e-9).
- **K1 (retorno en vacío).** Pasa si max_W |ΔP_u|/P0 < 1e-4 (−40 dB de la potencia de entrada) para cada θ y cada malla de D1, dx = 0,5 µm. Dx = 1,0 µm se evalúa con el mismo criterio, como diagnóstico. El umbral 1e-4 se toma como referencia de diseño (mismo orden que R0 = 1e-4 del 1D). No se ajusta después.
- **K2 (dependencia del absorbente).** Para cada θ, s(θ) = max/min sobre las configuraciones de D2 de max_W |ΔP_u|/P0. "Depende" si s(θ) > 2 para algún θ; "no depende" si s(θ) ≤ 2 para todo θ. Además: pasa si existe una configuración con max_W |ΔP_u|/P0 < 1e-4 para todo θ ∈ {0,02; 0,05; 0,08}.
- **K3 (fase).** "Comparable" sólo si (i) ambas magnitudes son el mismo observable (fase del retorno del campo) y (ii) misma geometría (haz gaussiano 2D frente a onda plana 1D, mismo plano de referencia). Pre-declarado: (i) y (ii) no se cumplen, así que el veredicto es "no comparable". La diferencia numérica |ψ_ov − arg r_1D| se publica como diagnóstico.
- **K4 (malla).** Clasificación por q = max_W|ΔP_u|(dx = 0,5)/max_W|ΔP_u|(dx = 0,25): q ∈ [2,5; 6] → "discretización (orden 2)"; q ∈ [0,67; 1,5] → "retorno del absorbente, independiente de la malla"; otro valor → "indeterminado". Además, el veredicto de K1 para θ = 0 con dx = 0,25 debe cumplir B1 de 009c (E_suelo < 1e-3 antes de la llegada); si no, se publica el fallo.
- **K5 (energía).** La potencia total numérica P_total(z) decae de forma monótona. Pasa si ninguna muestra aumenta más de 1e-9·P0 respecto a la anterior.
- **K6 (aplicabilidad de la ley 1D).** Pre-declarado: la ley R0^(sin θ) describe la reflectancia (amplitud) de una PML de coordenada compleja en onda completa, no la energía que llega a r < 40 µm del absorbente paraxial. La comparación numérica no es de reflectancia. Veredicto "no aplicable"; se publican los números.

## Lo que NO afirmo
- No afirmo que el absorbente real de un dispositivo refleje o no. No hay medida; esto es un modelo numérico.
- No afirmo nada con guía (δn ≠ 0), ni sobre la esponja de `src/silice/bpm.py` (Codex, otro modelo).
- No cierro la anomalía de 009c a θ > 0,04 rad ni la P-T1 del 1D.
- No validé el solver contra un segundo esquema; el analítico es la única referencia independiente. El solver adi2d es compartido con 009c; no se copia código de `src/silice/`.
- Un criterio no cumplido se publica como fallo, con sus cifras.

## Enmienda 1 (2026-10-10, 03:40 UTC, tras ver D1 y antes de ejecutar el control)
Motivo: en D1, a θ = 0,08 los valores máximos de la ventana en z = 0,3 y 0,4 mm son idénticos para los tres absorbentes ensayados (1,06e-2 y 1,63e-2). En ese instante el absorbente aún no actúa sobre r < 40 µm, así que el error temprano no puede ser un retorno del absorbente. Para separar el error del núcleo (discretización) del efecto de frontera se añade un control, sin cambiar ningún criterio:
- C-ref: dominio 512 µm (N = 1024), dx = 0,5 µm, mismo absorbente de línea de base (f 0,2, p 4), θ ∈ {0,05; 0,08}, dz 2,5 µm, 800 pasos. Su error de potencia frente al analítico mide el error de discretización del núcleo sin frontera próxima.
- C-sin: dominio 128 µm, dx 0,5 µm, σmax = 0 (sin absorbente, pared de Dirichlet), θ ∈ {0; 0,02; 0,05; 0,08}. Es el control negativo: cuánto retorno produce la pared sin absorbente.
- Descomposición: ΔP_128 − ΔP_ref ≈ efecto de la frontera (absorbente más pared). Se reporta; no tiene umbral nuevo.
- K0–K6 no cambian. La enmienda no altera los resultados ya obtenidos.
