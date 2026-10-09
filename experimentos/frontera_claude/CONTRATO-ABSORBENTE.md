# Tarea 3 · reflexión del absorbente (PML) frente al ángulo de incidencia · contrato (2026-10-10)

Publicado antes de calcular. Problema de onda completa en una dimensión (uniforme, n₀ = 1,444, λ = 1550 nm). Interpreta el límite θ > 0,04 rad de GLASS-009c: el absorbente lateral refleja más para incidencias rasantes.

## Modelo
- Ecuación u'' + κ²u = 0 con κ = k₀n₀ sin θ en el interior físico (x < L). Capa absorbente (PML) de espesor D con estiramiento complejo s(x) = 1 + iσ(x)/k₀n₀ y σ(x) = σ_max ((x−L)/D)², y pared perfecta en x = L + D (u = 0).
- Reflexión R(θ) = |u(L) − u′(L)/(iκ)| / |u(L) + u′(L)/(iκ)|, que mide la onda que vuelve desde la capa.

## Parámetros
- θ ∈ {0,005; 0,01; 0,02; 0,04; 0,08; 0,16} rad.
- D ∈ {5; 10; 20} µm. σ_max = (3/(2 n₀ D)) ln(1/R₀) con R₀ = 10⁻⁴ a incidencia normal (diseño fijo, no ajustado a θ).

## Validación previa
- **V0.** Sin absorbente (σ = 0), R = 1 con precisión 10⁻⁶ para todo θ (pared perfecta).
- **V1.** Para incidencia normal (θ ≈ 90°, κ = k₀n₀ en el límite) R tiende a R₀ con error menor que un orden de magnitud.

## Predicciones
- **P-T1.** R(0,04 rad) < 10⁻³ para D = 10 µm.
- **P-T2.** R(0,01 rad) > R(0,04 rad) (aumenta al ser más rasante).
- **P-T3.** Al aumentar D a 20 µm, R disminuye en todo el rango de θ.

## Qué no afirma
- Sin BPM. El haz paraxial real tiene componentes de θ pequeños; la conclusión es sobre el absorbente, no sobre el solver de propagación.
- Una dimensión, sin pérdida de material ni no linealidad.
