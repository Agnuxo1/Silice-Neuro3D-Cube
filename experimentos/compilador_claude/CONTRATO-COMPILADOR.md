# Tarea 11 · compilador de red a malla realizable con componentes calibrados · contrato (2026-10-10)

Publicado antes de ejecutar. Prototipo de compilación: de una matriz unitaria objetivo a ajustes de fase de una malla rectangular 4×4 (6 MZI, 16 fases), con restricciones de fabricación y de control.

## Pipeline
1. **Ajuste continuo.** Fases p₀ que realizan el objetivo U_T (DFT₄ y dos unitarias aleatorias de semillas 1 y 2) con los acopladores ideales 50/50.
2. **Restricción de control.** Cuantización de cada fase a un DAC de **8 bits** (paso 2π/256). Es una restricción real del control térmico.
3. **Componentes no ideales.** Cada uno de los 12 acopladores tiene razón de división 50 % + δ, con δ ~ N(0; σ_δ), σ_δ = 0,02 (supuesto, a medir en la tarea 14).
4. **Compilación sin calibrar.** Se aplican las fases del paso 2 a la malla no ideal. Error ε₁.
5. **Compilación con calibración.** Se reajustan las 16 fases con los δ conocidos (medidos) y el DAC de 8 bits. Error ε₂.

Métrica: error de transferencia ε = ‖U − U_T‖_F / ‖U_T‖_F.

## Criterios (fijados ahora)
- **C1 (ajuste ideal).** ε del paso 1 < 10⁻⁹.
- **C2 (control).** Con DAC de 8 bits y malla ideal, ε < 5·10⁻³.
- **C3 (calibración).** Con δ conocidos y DAC de 8 bits, ε₂ < 10⁻²; y ε₂ < ε₁ / 3 para cada objetivo.
- **C4 (honestidad).** Si C3 no se cumple, se publica la cifra. No se relajan umbrales.

## Entrega
- Netlist en JSON: lista de MZI (columna, par de guías, θ, φ), fases de salida, δ asumidos y resultados. Sin layout de fabricación: no se comprueban radios de curvatura ni separaciones (se declara como límite).

## No afirma
- Sin medidas de δ ni de fases. Sin layout 3D. Sin restricciones de fabricación reales más allá del DAC.

## Enmienda E-1 (2026-10-10, registrada antes de la segunda ejecución)

- **Defecto de implementación de la primera ejecución.** El paso 5 llamaba al ajuste con cuantización dentro del residuo (`fit(..., bits=8)`). Un residuo escalonado tiene gradiente nulo, y la optimización no se movió: ε₂ = ε₁ en los tres objetivos. Es un error del código, no un resultado físico. La salida de esa ejecución se conserva en `compilador_resultados_v1_defecto.json`.
- **Corrección.** El paso 5 se resuelve como búsqueda discreta sobre la rejilla de 8 bits. Punto de partida: redondeo de la solución continua calibrada, con dos arranques más (solución ideal y códigos del paso 2). Movimientos de ±1 LSB en una fase y después en pares de fases, hasta que ninguno mejora. Así las fases finales son códigos de 8 bits, como exige el paso 5.
- **Sin cambios.** C1–C4, umbrales, objetivos (DFT₄, haar1, haar2), δ ~ N(0; 0,02) con la misma semilla (20261040) y la definición de C2 (cuantización directa de la solución ideal, paso 2).
- **Diagnósticos, no criterios.** (a) ajuste continuo calibrado sin cuantizar; (b) su redondeo a 8, 10 y 12 bits; (c) búsqueda discreta en malla ideal, para separar cuánto de C2 es cuantización directa y cuánto es la elección de códigos.
- **Límite declarado.** C2 mide la cuantización directa tal como se preregistró. Un compilador puede elegir códigos mejor que el redondeo; ese caso se reporta aparte y no cambia el veredicto de C2.
