# Contraste vectorial de modos guiados: resultados (2026-10-09)

Ejecución del [contrato](VECTORIAL-CONTRATO.md), con su enmienda E1 registrada antes de calcular. Código y datos en [`experimentos/vectorial_claude/`](../experimentos/vectorial_claude/). Los hashes de los ficheros usados están en `resultados_contraste.json`.

## Resumen

| Hipótesis | Criterio (fijado antes) | Valor medido | Veredicto |
|---|---|---|---|
| **H1** validez escalar del modo fundamental | \|n_HE11 − n_LP01\|/n1 ≤ 10⁻⁵ | 1,99·10⁻⁶ | **Cumple** |
| **H2** polarización en LP11 relevante a 10⁻⁴ | dispersión(TE01, TM01, HE21)/n1 ≥ 10⁻⁴ | 2,62·10⁻⁶ | **No se cumple** |
| **H3** la dispersión crece con el contraste | creciente en Δn = 0,001 → 0,003 → 0,005 (V constante) | 1,04·10⁻⁷ → 9,40·10⁻⁷ → 2,62·10⁻⁶ | **Cumple** |

Las puertas de validación V1 a V5 pasan (8 pruebas unitarias, ejecutadas también en CI).

**Conclusión acotada.** En una guía de salto circular ideal con el contraste del proyecto (Δn = 0,005, a = 6 µm, λ = 1550 nm), el modelo escalar describe el índice modal del modo fundamental y de LP11 con errores relativos de 2–3·10⁻⁶. Los efectos vectoriales son de segundo orden en Δn: escalan como Δn² (cocientes 9,02 y 2,79 frente a 9,00 y 2,78 esperados). Esto **no** cubre la trinchera con fuga, la birrefringencia de la escritura, la no circularidad ni el acoplamiento. Esas cuestiones siguen abiertas.

## Índices modales (V* = 2,920161; Δn = 0,005; a = 6 µm)

| Modo | b = W²/V² | n_eff |
|---|---|---|
| HE₁₁ | 0,637458857758 | 1,442189297365 |
| LP₀₁ (escalar) | 0,638032750995 | 1,442192165457 |
| TE₀₁ | 0,152892341004 | 1,439765586162 |
| TM₀₁ | 0,152256523709 | 1,439762403242 |
| HE₂₁ | 0,151804646267 | 1,439760141126 |
| LP₁₁ (escalar) | 0,152892341004 | 1,439765586162 |

LP₁₁ escalar y TE₀₁ coinciden exactamente. Es una identidad algebraica: la ecuación de TE₀₁ no depende de Δn, solo de U y W. Por eso la dispersión de H2 es la de TM₀₁ y HE₂₁ respecto de TE₀₁.

## H3 a V constante (enmienda E1)

| Δn | a (µm) | dispersión/n1 | HE₁₁ − LP₀₁ (rel.) |
|---|---|---|---|
| 0,001 | 13,407 | 1,042·10⁻⁷ | −7,93·10⁻⁸ |
| 0,003 | 7,743 | 9,404·10⁻⁷ | −7,15·10⁻⁷ |
| 0,005 | 6,000 | 2,619·10⁻⁶ | −1,99·10⁻⁶ |

Cocientes entre contrastes consecutivos: dispersión 9,02 y 2,79; HE₁₁ − LP₀₁ 9,01 y 2,78. Para Δn² se esperan 9,00 y 2,78.

## Controles adicionales (no son hipótesis)

1. **Residuo en alta precisión.** Con mpmath a 60 cifras, la ecuación evaluada en la raíz de V* da ~2·10⁻¹⁸ para HE₁₁ y ~7·10⁻¹⁶ para HE₂₁. Las raíces de doble precisión son fiables en el caso del proyecto.
2. **Corte de HE₂₁.** La fórmula exacta (n1²/n2² + 1)·J₁(V) = V·J₂(V) da V_c = 2,40771508. Con mpmath, el signo de la ecuación híbrida con ν = 2 cambia en V_c (entre −10⁻⁵ y +10⁻⁵), así que la ecuación es correcta. El solver de doble precisión da 2,407572, es decir, un error de −1,4·10⁻⁴ en V. Es cancelación numérica cerca de b → 0, donde los términos crecen como W⁻⁶. No afecta a V* = 2,92, pero sí limita la precisión del solver cerca de cortes. Este resultado se publica como limitación.
3. **Identidad interna.** Para ν = 0, la ecuación híbrida es el producto de las ecuaciones de TE y TM (prueba unitaria).

## Historial del proceso (transparencia)

- **Enmienda E1**, publicada antes de programar el solver: H3 se evalúa a V constante, porque con a = 6 µm los contrastes 0,001 y 0,003 quedan por debajo del corte de LP₁₁.
- **Corrección numérica durante las puertas**: la primera ejecución de V4 falló porque `brentq` usaba una tolerancia absoluta de 10⁻¹⁶ en b, insuficiente a b ≈ 10⁻⁶ (error relativo en la raíz de 10⁻¹⁰). Se cambió a una tolerancia absoluta mínima para que la convergencia sea relativa. El criterio V3 y sus umbrales no cambiaron.
- Los umbrales 10⁻⁵ y 10⁻⁴ y los criterios V1 a V5 no se modificaron después de ver resultados.

## Limitaciones explícitas

- **Guía de salto ideal**, con camisa infinita. La trinchera con fuga del proyecto no está calculada: sus modos son cuasi-ligados y necesitan un solver con condiciones absorbentes.
- **No es un solver vectorial numérico independiente** (diferencias finitas o elementos finitos). La validación se apoya en la ecuación exacta, en el límite escalar, en el corte de TE₀₁ y en el corte de HE₂₁ con alta precisión. Un solver FD vectorial independiente es el siguiente paso.
- **Sin birrefringencia de escritura, tensión ni no circularidad.** Los efectos de polarización que puedan importar en fs-escrito no están modelados ni medidos. Su tamaño puede superar al de este cálculo.
- **Sin BPM.** Lo que se afirma es sobre índices modales, no sobre propagación, acoplamiento ni pérdidas.

## Consecuencia para el proyecto

- El modelo escalar puede seguir usándose para los índices modales de la guía ideal a la precisión de 10⁻⁵.
- La afirmación «el modelo escalar ignora polarización» es cierta, pero su efecto en el índice modal de esta guía ideal es de ~3·10⁻⁶. Cualquier otra afirmación sobre polarización necesita un contrato propio.
- Para la trinchera con fuga y la birrefringencia de escritura, la pregunta sigue abierta.

## Reproducir

```bash
cd experimentos/vectorial_claude
python -B -m unittest discover -s . -p "test_*.py"
python -B run_contrast.py
```

El segundo comando ejecuta primero las puertas V1 a V5 y solo después escribe `resultados_contraste.json`.
