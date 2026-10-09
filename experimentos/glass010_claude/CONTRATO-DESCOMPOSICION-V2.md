# GLASS-010 · descomposición modal corregida · contrato prospectivo (2026-10-10)

Publicado antes de calcular. Tarea 3 del encargo: corregir la descomposición modal incorporando interferencias y una separación justificada entre modos y radiación. Motivo: en GLASS-010, η > 1 para modos con fuga fuerte, y la potencia del "resto" se calculó por separado, sin el término de interferencia.

## Alcance de esta versión

- **Caso exacto:** guía de salto análoga (a = 6 µm, Δn = 0,005, λ = 1550 nm, V = 2,9202). Sus modos guiados escalares LP₀₁ y LP₁₁ (cos φ y sen φ) son **ortonormales**, así que la teoría es exacta y no requiere bases no hermíticas.
- **No cubre:** modos cuasi-ligados de trinchera (GLASS-010 original). Su descomposición correcta requiere bases biortogonales de un operador no hermítico, que se tratará en un contrato posterior.

## Método

Base ortonormal de modos guiados {φ₀₁, φ₁₁ᶜ, φ₁₁ˢ}, normalizada numéricamente en el plano (x, y). Para una entrada ψ:

- coeficientes c_m = ⟨φ_m, ψ⟩;
- potencia guiada P_g = Σ|c_m|²;
- resto no guiado ψ_r = ψ − Σ c_m φ_m, con potencia P_r = ∫|ψ_r|² dA;
- cierre: P_tot = P_g + P_r, sin término cruzado porque ψ_r es ortogonal a los modos guiados por construcción.

Interferencia: para ψ = ψ_A + ψ_B, P_g(ψ) − [P_g(ψ_A) + P_g(ψ_B)] = 2 Re Σ_m c_m^A* c_m^B. El término cruzado se calcula explícitamente y se compara con la diferencia medida.

## Entradas

- Gaussiana ψ_{x0} = exp(−((x − x0)² + y²)/w0²), w0 = 6 µm, x0 ∈ {0; 2; 4} µm.
- Superposición ψ_A + ψ_B, centros en ±3 µm (interferencia entre dos haces guiados).

Malla: 601 × 601 puntos en [−30; 30] µm.

## Criterios (fijados ahora)

- **C1 (cierre):** |P_tot − P_g − P_r| / P_tot < 10⁻⁴.
- **C2 (ortonormalidad):** |⟨φ_i, φ_j⟩ − δ_ij| < 10⁻⁴ para los tres modos.
- **C3 (interferencia):** |[P_g(ψ_A + ψ_B) − P_g(ψ_A) − P_g(ψ_B)] − 2 Re Σ c^A* c^B| < 10⁻⁶ (relativo a P_tot).

## Predicciones

- **P1 (simetría):** para x0 = 0, c₁₁ˢ = c₁₁ᶜ = 0, por la simetría de la gaussiana centrada en el eje.
- **P2 (dirección):** la potencia guiada de la gaussiana centrada, con w0 = 6 µm y un modo de radio comparable, es mayor que 0,5. Si no lo es, el modelo escalar de LP₀₁ no describe bien este haz.
- **P3 (interferencia):** el término cruzado de ψ_A + ψ_B es distinto de cero cuando los dos centros están dentro del núcleo. Si es cero, la separación del caso A y B no tiene interferencia y no se explica la diferencia de GLASS-010.

## Lo que no hace

- No corrige los η de GLASS-010 original (eso necesita modos biortogonales).
- No incluye birrefringencia vectorial. El error escalar-vectorial de los índices es de 10⁻⁶ (ver `VECTORIAL-RESULTADOS`).
