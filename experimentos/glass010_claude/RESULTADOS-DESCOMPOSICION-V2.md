# GLASS-010 · descomposición modal corregida · resultados (2026-10-10)

Contrato: [`CONTRATO-DESCOMPOSICION-V2.md`](CONTRATO-DESCOMPOSICION-V2.md), publicado antes de calcular. Código: `descomposicion_v2.py`. Datos: `descomposicion_v2.json`.

## Qué se corrige

En GLASS-010, los coeficientes η superaban 1 para modos con fuga fuerte. Eso ocurre al proyectar con un producto bilineal sobre modos no ortogonales (cuasi-ligados), y la potencia del resto se calculó por separado, sin el término de interferencia. Aquí se establece el procedimiento correcto en el caso donde la teoría es exacta: base ortonormal, cierre explícito y término cruzado calculado.

## Resultados (guía análoga, a = 6 µm, Δn = 0,005, V = 2,9202)

Base: LP₀₁, LP₁₁ᶜ y LP₁₁ˢ, con b(LP₀₁) = 0,638033 y b(LP₁₁) = 0,152892, normalizados numéricamente en una malla de 601 × 601 puntos en [−30, 30] µm.

| Entrada (gaussiana w₀ = 6 µm) | P_guiada / P_total | c₀₁ | c₁₁ᶜ | Cierre (C1) |
|---|---|---|---|---|
| x₀ = 0 µm | 0,997346 | 7,5099 | 0 | 2,8·10⁻¹³ |
| x₀ = 2 µm | 0,986686 | 7,0943 | 2,3381 | 2,3·10⁻¹³ |
| x₀ = 4 µm | 0,911579 | 5,9812 | 3,9717 | 1,6·10⁻¹³ |

**Interferencia (C3).** Para ψ_A + ψ_B con centros en ±3 µm: el término cruzado numérico 65,851307 coincide con la fórmula 2 Re Σ c^A* c^B = 65,851307, con diferencia de 5,6·10⁻¹². La potencia total del haz combinado es 181,6943 y coincide con P_A + P_B + 2⟨ψ_A, ψ_B⟩ = 181,6943.

**Ortonormalidad (C2).** Error máximo del Gram 3,8·10⁻¹⁵.

## Criterios y predicciones

| Criterio / predicción | Umbral | Valor | Veredicto |
|---|---|---|---|
| C1 cierre | < 10⁻⁴ | < 3·10⁻¹³ | Cumple |
| C2 ortonormalidad | < 10⁻⁴ | 3,8·10⁻¹⁵ | Cumple |
| C3 interferencia | < 10⁻⁶ relativo | 5,6·10⁻¹² | Cumple |
| P1 simetría (x₀ = 0) | c₁₁ = 0 | 0 | Cumple |
| P2 fracción guiada centrada | > 0,5 | 0,997 | Cumple |
| P3 término cruzado no nulo | ≠ 0 | 65,9 | Cumple |

## Interpretación

- **Separación justificada.** Con base ortonormal, la potencia de la componente no guiada se obtiene por diferencia (P_tot − P_g) y coincide con la potencia directa del resto ψ − Σcφ. Ese resto contiene la radiación y cualquier contenido no modal. No hay término cruzado entre modos guiados y resto, así que la separación es exacta en el caso ortonormal.
- **Interferencias.** Las potencias de componentes no se suman cuando los haces se solapan. El término 2 Re Σ c^A* c^B tiene el tamaño de la potencia en este caso (65,9 frente a P_total = 181,7). Ignorarlo, como en la versión anterior, sesga la contabilidad.
- **Lo que explica el η > 1 de GLASS-010.** No se puede explicar con la base ortonormal: en este caso no aparece. Aparece con modos cuasi-ligados no ortogonales. Para esos modos hace falta una base biortogonal, con vectores propios por la izquierda del operador. Eso es el contrato siguiente.

## Lo que no se afirma

- No corrige los η de GLASS-010 original (modos de trinchera con fuga). Ver el contrato siguiente, pendiente.
- Modelo escalar. La birrefringencia vectorial está fuera del alcance (error de índices de 10⁻⁶ según `VECTORIAL-RESULTADOS`).
- Entrada gaussiana sin fase. Un haz con fase no uniforme cambia los coeficientes, pero no la estructura de la descomposición.
