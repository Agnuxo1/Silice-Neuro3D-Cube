# GLASS-010 · base biortogonal para modos cuasi-ligados · CONTRATO-BIORT-r4 (2026-10-10)

Publicado antes de calcular. Los umbrales de esta ronda se fijan aquí y no cambian tras ver resultados. Los umbrales de rondas anteriores (C1 < 10⁻⁴, C2 < 10⁻⁴, C3 < 10⁻⁶ de CONTRATO-DESCOMPOSICION-V2) se mantienen tal como están registrados allí; no se aplican a esta prueba, que es algebraica y no usa cuadratura de malla.

## Objetivo

Una descomposición de campos sobre modos no ortogonales que cierre exactamente y no dé η > 1 por construcción. Motivo: en GLASS-010 (run010.py, línea 50) η_m = |c_m|² N_m / P_in se calcula modo a modo; con modos no ortogonales, las proyecciones por modo no suman la potencia guiada correcta (véase RESULTADOS-DESCOMPOSICION-V2.md).

## Alcance

- **Prueba sintética:** dos modos no ortogonales conocidos φ₁, φ₂ en una malla 1D, con matriz de Gram no diagonal y compleja. Los campos de prueba se construyen con coeficientes conocidos.
- **Producto:** hermítico, ⟨u, v⟩ = Σ conj(u_j) v_j Δx. Es el producto de potencia.
- **Fuera de alcance (pendiente):** la convención bilineal de un operador no hermítico con pares izquierda/derecha reales de GLASS-010. Se trata en un contrato posterior, porque necesita los modos del solver.
- **No se aplica a GLASS-010 original.** Ese caso (modos de trinchera con fuga) queda pendiente: requiere los modos del solver y el producto bilineal de run010.py, que esta prueba no contiene.

## Cambio de protocolo declarado

Ninguno respecto de las reglas del encargo. Se define η de forma explícita (sección Definiciones). El método A reproduce la definición modo a modo de run010.py. El método D (base dual) es la propuesta que se evalúa.

## Modos y malla

- Malla: N = 4001 puntos en x ∈ [−40, 40] µm (unidades abstractas, Δx = 0,02 µm).
- φ_m(x) = exp(−(x − x_m)² / (2 s²)) · exp(i k_m x), con s = 2 µm, x₁ = 0, k₁ = 0, x₂ = δ, k₂ = 0,7 µm⁻¹.
- Cada modo se normaliza a ⟨φ_m, φ_m⟩ = 1, así que G_mm = 1.
- δ ∈ {10; 4; 2; 1; 0,5; 0,1} µm. El solape |G₁₂| se mide y se publica para cada δ.

## Campos de prueba (coeficientes conocidos)

- **T1 (genérico, en el span):** a = (0,8 + 0,3i; −0,5 + 0,9i).
- **T2 (interferencia destructiva, en el span):** a = (1; −1).
- **T4 (interferencia constructiva, en el span):** a = (1; 1).
- **T3 (fuera del span):** ψ = Φa_T1 + 0,3·‖Φa_T1‖·r/‖r‖, con r complejo aleatorio, semilla 20261010 (numpy.random.default_rng).

## Definiciones

- Gram: G_mn = ⟨φ_m, φ_n⟩ (G_mm = 1). Matriz Φ = [φ₁ φ₂].
- Base dual (biortogonal): χ = Φ G⁻¹, de modo que ⟨χ_i, φ_j⟩ = δ_ij.
- **Método D (propuesta):** d_m = ⟨φ_m, ψ⟩, c = G⁻¹ d, η_D = ‖Φc‖² / ‖ψ‖².
- **Método A (GLASS-010, modo a modo):** c^A_m = d_m / G_mm, η_A,m = |c^A_m|² G_mm / ‖ψ‖², η_A = Σ_m η_A,m.
- η (criterio B2) = η_D. El método A se publica como contraste.

## Criterios (fijados ahora)

- **B1 (reconstrucción con base dual):** máx. sobre T1, T2, T4 y todos los δ de ‖ψ − Φc‖ / ‖ψ‖ < 10⁻¹². Método D.
- **B2 (η ≤ 1):** máx. sobre todos los casos (T1 a T4, todos los δ) de η_D ≤ 1 + 10⁻¹².
- **B3 (recuperación de coeficientes):** máx. sobre T1, T2, T4 y todos los δ de ‖c − a‖ / ‖a‖ < 10⁻¹⁰.

## Verificación previa (antes de creer las cifras)

- **V1 (biortogonalidad):** máx. |⟨χ_i, φ_j⟩ − δ_ij| < 10⁻¹² para todos los δ.
- **V2 (cruce con otro método):** error relativo entre c_D y numpy.linalg.lstsq < 10⁻¹⁰ en T1, T2, T3 y T4 para todos los δ.
- **V3 (caso analítico en R²):** φ₁ = (1, 0), φ₂ = (0,6; 0,8), ψ = φ₁ − φ₂. Debe recuperarse a = (1; −1) con error < 10⁻¹².
- **V4 (caso analítico en R²):** para ψ = φ₁ + φ₂, η_A = 1 + G₁₂ = 1,6 con error < 10⁻¹². El valor analítico se fija aquí.

## Diagnósticos y predicciones (publicados; no son criterios de aprobación)

- **D1 (cierre, T3):** |‖ψ‖² − ‖Φc‖² − ‖ψ − Φc‖²| / ‖ψ‖² < 10⁻¹².
- **P1 (η_A > 1):** para T4, η_A > 1 en todos los δ con |G₁₂| ≥ 0,6. Si no se cumple, se publica igual.
- **P2 (escala de B3):** el error de B3 se compara con cond(G) · ε_máquina. Se publica el cociente, sin umbral.

## Salidas

- experimentos/glass010_claude/biortogonal_sintetico.py
- experimentos/glass010_claude/resultados_biort.json (pass calculado por el código)
- experimentos/glass010_claude/RESULTADOS-BIORT.md

## Restricciones de ejecución

- Solo CPU, python -B, OMP_NUM_THREADS=1. Sin instalaciones; numpy solamente.
- Tiempo: la corrida es de milisegundos. No hay recortes de malla.
