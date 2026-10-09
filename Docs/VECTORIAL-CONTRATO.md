# Contraste vectorial de modos guiados: contrato prospectivo (2026-10-09)

Este contrato se publica **antes** de calcular nada. Los umbrales y los parámetros no se modifican después de ver resultados. Si una hipótesis falla, el fallo se publica.

## Pregunta

Cuánto se separa la constante de propagación vectorial de la escalar en una guía de sílice parecida a la camisa deprimida del proyecto, y con qué precisión es válido el modelo escalar que usan el BPM y los ensayos GLASS-003 a GLASS-010.

## Alcance

- **Incluido:** guía de salto circular ideal, núcleo de índice n1 y camisa de índice n2 de extensión infinita. Es el límite de espesor infinito de la camisa deprimida, donde no hay fuga.
- **Excluido:** la trinchera de espesor finito con fuga. Sus modos son cuasi-ligados y su tratamiento vectorial necesita condiciones absorbentes, fuera de esta entrega. Excluidos también la birrefringencia por tensión, la escritura láser, las medidas y el BPM.

## Parámetros fijos

- λ = 1550 nm; n1 = 1,444 (índice de referencia de GLASS-003); a = 6 µm (radio del núcleo).
- Contraste Δn = n1 − n2 ∈ {0,001; 0,003; 0,005}. El caso del proyecto es Δn = 0,005.
- V = k0 · a · √(n1² − n2²). Con Δn = 0,005 resulta V ≈ 2,92.

## Referencia analítica

Ecuación característica exacta de la fibra de salto, con U = a√(k0²n1² − β²) y W = a√(β² − k0²n2²). Forma verificada en arXiv:2005.01363 y arXiv:1706.04291:

- **ν = 0:**
  - TE₀ₘ: J₁(U)/(U·J₀(U)) + K₁(W)/(W·K₀(W)) = 0
  - TM₀ₘ: J₁(U)/(U·J₀(U)) + (n2²/n1²)·K₁(W)/(W·K₀(W)) = 0
- **ν ≥ 1 (híbridos HE y EH):** [A + B]·[A + (n2²/n1²)·B] = (ν·β/(k0·n1))²·(1/U² + 1/W²)², con A = J′ν(U)/(U·Jν(U)) y B = K′ν(W)/(W·Kν(W)).
- **Escalar (guiado débil), para comparar:** LP₀ₘ: U·J₁(U)/J₀(U) = W·K₁(W)/K₀(W); LP₁ₘ: U·J₀(U)/J₁(U) = −W·K₀(W)/K₁(W).

Modos: HE₁₁ (ν = 1) ↔ LP₀₁. El conjunto LP₁₁ se corresponde con TE₀₁, TM₀₁ y HE₂₁ (ν = 2).

## Hipótesis

- **H1 (validez escalar del modo fundamental):** |n_HE11 − n_LP01| / n1 ≤ 10⁻⁵ para Δn = 0,005.
- **H2 (polarización en LP11):** (máx − mín)/media de {n_TE01, n_TM01, n_HE21} / n1 ≥ 10⁻⁴ para Δn = 0,005. Es decir, el modelo escalar no basta a esa precisión en LP11.
- **H3 (escalado con el contraste):** la dispersión de H2 crece al aumentar Δn entre 0,001, 0,003 y 0,005.

Los umbrales 10⁻⁵ y 10⁻⁴ quedan fijados aquí.

## Validación del solver antes de usarlo

- **V1:** en el límite Δn → 0, TE01, TM01, HE21 y LP11 coinciden, con error relativo ≤ 10⁻⁶.
- **V2:** el corte de TE01 aparece en V = 2,4048 (primer cero de J₀), con error ≤ 10⁻⁴ en V.
- **V3:** cada raíz cumple |F(β)| ≤ 10⁻⁹ relativo al máximo de |F| en su entorno.
- **V4:** HE11 existe para cualquier V ≥ 0,5 (presencia del modo fundamental sin corte).
- **V5:** cada n_eff está estrictamente entre n2 y n1.

Si V1 a V5 fallan, no se publican resultados de H1 a H3. Se documenta el fallo y se corrige el solver con un nuevo contrato.

## Criterio de parada

Tres iteraciones de diagnóstico sin superar V1 a V5 detienen el trabajo, y el informe lo registra.

## Lo que este contrato no afirma

Nada sobre la trinchera con fuga, sobre el BPM, sobre el proyecto en su conjunto ni sobre fabricación. Los resultados solo informan sobre la validez del modelo escalar en la guía de salto ideal, que es la analogía del límite de espesor infinito.
