# Tarea 11 · compilador de red a malla realizable · resultados (2026-10-10)

Contrato: `CONTRATO-COMPILADOR.md`, con enmienda **E-1** (registrada antes de la segunda ejecución). Código: `compilar.py`. Resultados: `compilador_resultados.json`. Diagnósticos de robustez: `robustez_compilador.py` → `robustez_compilador.json`. La primera ejecución se conserva en `compilador_resultados_v1_defecto.json`.

**Modelo, no dispositivo.** Malla rectangular 4×4 (6 MZI, 16 fases), DAC de 8 bits (paso 2π/256), acopladores 50 % + δ con δ ~ N(0; 0,02) (**supuesto**, a medir en T14). Sin layout de fabricación: no se comprueban radios ni separaciones.

## Criterios preregistrados

| Criterio | DFT₄ | haar1 | haar2 | Veredicto |
|---|---|---|---|---|
| C1 ajuste ideal continuo, ε < 10⁻⁹ | 6,9·10⁻¹⁶ | 6,5·10⁻¹⁶ | 6,7·10⁻¹⁶ | **cumple** |
| C2 cuantización directa a 8 bits, malla ideal, ε < 5·10⁻³ | 1,30·10⁻² | 1,29·10⁻² | 1,70·10⁻² | **no cumple** |
| ε₁ sin calibrar (fases del paso 2 en malla no ideal) | 7,67·10⁻² | 3,60·10⁻² | 4,52·10⁻² | referencia |
| C3 reajuste con δ conocidos y DAC de 8 bits: ε₂ < 10⁻² y ε₂ < ε₁/3 | 8,55·10⁻³ | 9,25·10⁻³ | 8,87·10⁻³ | **cumple** (margen estrecho) |

C4 (publicar sin relajar umbrales): se publica la cifra de C2, que no cumple.

## Enmienda E-1 y defecto de la primera ejecución

En la primera ejecución el reajuste cuantizaba dentro del residuo de `least_squares`. El residuo escalonado tiene gradiente nulo, así que ε₂ = ε₁ en los tres objetivos. Era un error del código. La corrección es una búsqueda discreta sobre la rejilla de 8 bits (±1 LSB en una fase y en pares, con multiarranque). La definición de C2, los umbrales, los objetivos y la semilla de δ no cambian. Las cifras de C1, C2 y ε₁ de ambas ejecuciones coinciden con las mismas entradas, lo que sirve de comprobación de reproducibilidad.

## Diagnósticos (no son criterios)

1. **La calibración funciona en fases continuas.** Con δ conocidos, el ajuste continuo reproduce el objetivo a 3·10⁻¹⁶ (DFT₄). Los acopladores no ideales se compensan por completo con fases libres.
2. **Cuello de botella: resolución del DAC.** El redondeo de la solución calibrada da 1,07·10⁻² a 8 bits, 3,19·10⁻³ a 10 bits y 9,65·10⁻⁴ a 12 bits (DFT₄).
3. **La búsqueda discreta sola no basta.** Códigos optimizados sin calibrar dan un error prácticamente igual a ε₁ (5,2·10⁻² frente a 5,2·10⁻², mediana de 12 realizaciones). La ganancia viene de la calibración, no de elegir códigos.
4. **Sensibilidad de C2.** Con malla ideal y códigos optimizados, el error a 8 bits es 6,9·10⁻³–1,1·10⁻² (ni siquiera la búsqueda local cumple 5·10⁻³ con 8 bits). A 9 bits, 5,0·10⁻³–6,4·10⁻³ (marginal). A 10 bits, 2,0·10⁻³–2,1·10⁻³ (cumple). **Para cumplir C2 con esta malla hacen falta unos 10 bits.** Con 8 bits, C2 no se cumple aunque se optimicen los códigos.

## Robustez de C3 (diagnóstico, 12 realizaciones de δ por objetivo, semilla 20261100)

| Objetivo | C3 cumple | ε₂ mediana | ε₂ rango |
|---|---|---|---|
| DFT₄ | 8/12 (67 %) | 9,4·10⁻³ | 8,6·10⁻³ – 1,05·10⁻² |
| haar1 | 11/12 (92 %) | 9,0·10⁻³ | 6,3·10⁻³ – 9,9·10⁻³ |
| haar2 | 9/12 (75 %) | 9,5·10⁻³ | 6,7·10⁻³ – 1,10·10⁻² |
| **Total** | **28/36 (78 %; IC 95 % de Wilson ≈ 62–88 %)** | | |

El cumplimiento de C3 en la realización preregistrada es real, pero el margen es estrecho: el umbral de 10⁻² está en medio de la distribución de ε₂. **C3 no es robusto por sí solo; depende de la realización de δ y de la resolución del DAC.**

## Netlist de DFT₄ (códigos de 8 bits)

Está en `compilador_resultados.json` (`netlist_DFT4`): seis columnas con par de guías, código θ (interior) y φ (entrada), razones de acoplo 0,5 + δ asumidas y códigos de salida. Verificación independiente: se reconstruye la malla solo desde la netlist y se obtiene ε₂ = 8,547·10⁻³ (igual que el valor almacenado). Los códigos son enteros en [0, 255] y la unitariedad es de 9,4·10⁻¹⁶.

## Límites declarados

- Modelo escalar de la estructura: no hay comprobación de radios de curvatura, separaciones ni pérdidas (sin layout).
- δ es un supuesto (σ = 0,02). Las conclusiones dependen de ese valor hasta medirlo (T14).
- La búsqueda discreta es local. No demuestra el óptimo global de los códigos, así que el error de 8 bits podría ser algo menor con otra búsqueda.
- Tres objetivos (DFT₄ y dos unitarias aleatorias). Es una prueba de concepto, no un conjunto de referencia.
- C2 se mide con cuantización directa, tal como se preregistró. El diagnóstico 4 muestra que el límite no depende solo de la búsqueda.
