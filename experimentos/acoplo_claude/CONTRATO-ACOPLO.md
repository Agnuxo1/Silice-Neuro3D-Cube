# Tarea 8 · pérdidas y diafonía: acoplamiento entre guías paralelas (modelo escalar) · contrato prospectivo (2026-10-10)

Publicado antes de calcular. Alcance **parcial**: solo diafonía entre guías paralelas idénticas en el modelo escalar de acoplamiento débil. **No se modelan** curvas (pérdida por radiación), cruces ni conexiones 3D. Esas partes quedan como protocolo y estado pendiente.

## Modelo
- Guía de referencia: fibra de salto análoga de `experimentos/vectorial_claude/` (enmienda E1): λ = 1,55 µm, radio de núcleo a = 6 µm, n₁ = 1,444 (núcleo), n₂ = 1,439 (revestimiento), V = k₀a·√(n₁² − n₂²) = 2,9202.
- Modo LP₀₁ exacto de salto: ψ(r) = J₀(Ur/a)/J₀(U) para r ≤ a; K₀(Wr/a)/K₀(W) para r ≥ a, con U² + W² = V² y U J₁(U)/J₀(U) = W K₁(W)/K₀(W). β = √(k₀²n₁² − U²/a²).
- Acoplo para dos guías idénticas separadas d (acoplo débil, Marcuse / Snyder–Love): κ(d) = (k₀²/2β)(n₁² − n₂²)·I(d), con I(d) = ∫_núcleo 2 ψ₁ψ₂ dA y ψ normalizado (∫|ψ|² dA = 1).
- Potencia transferida a la guía 2 tras L (fase igualada): P₂(L) = sin²(κL). Longitud de transferencia completa L_c = π/(2κ).
- Diafonía (dB) = 10·log₁₀ P₂(L).

## Verificaciones (criterios fijados ahora)
- **V1 (normalización).** La norma cerrada N² = πa²[J₁²(U)/J₀²(U) + K₁²(W)/K₀²(W)] coincide con la integral numérica a 10⁻⁶ relativo.

**Enmienda E-1 (2026-10-10, antes de la segunda ejecución).** La primera versión de V1 usaba N² = πa²[(J₀²+J₁²)/J₀² + 1 − K₁²/K₀²]. Tenía un error de signo: ∫ₓ^∞ t K₀²(t) dt = (x²/2)(K₁²(x) − K₀²(x)), no (x²/2)(K₀² − K₁²). La prueba V1 falló (error relativo 0,28) y detectó el error. La primera tabla queda descartada y se conserva en `acoplo_resultados_v0_normalizacion_erronea.json`. El umbral de V1, las predicciones H-T8-1 y H-T8-2 y el resto de criterios no cambian.
- **V2 (cuadratura).** I(20 µm) con 160×256 nodos y con 320×512 nodos difiere menos de 10⁻⁶ relativo.
- **V3 (forma asintótica).** Para d ∈ {30, 40, 50, 60} µm, la pendiente de ln κ cumple d(ln κ)/dd ≈ −W/a − 1/(2d) con error menor del 3 % de W/a.
- **V4 (validez débil).** Δ = (n₁² − n₂²)/(2n₁²) < 0,01.
- V3 valida la integración y la forma del acoplo, **no** el prefactor (k₀²/2β)(n₁² − n₂²): ese prefactor es la forma estándar sin comprobación independiente, y se declara como límite.

## Predicciones (fijadas antes de calcular; falsables con medida)
- **H-T8-1.** Para d = 20 µm y L = 10 mm, P₂ ≤ 0,10 (≤ −10 dB).
- **H-T8-2.** Para d = 40 µm y L = 10 mm, P₂ ≤ 10⁻³ (≤ −30 dB).

## Qué no afirma
- No es una simulación vectorial de las guías de trinchera ni del acoplo fs (la escritura es anisótropa; el modelo es isótropo).
- No hay pérdida de curva, ni diafonía en cruces, ni acoplo vertical entre capas: quedan pendientes (ver el resumen de estado en `RESULTADOS-ACOPLO.md`).
- Sin medidas. Los valores son predicciones del modelo.
