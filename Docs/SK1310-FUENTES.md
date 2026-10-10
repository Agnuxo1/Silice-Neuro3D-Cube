# SK1310: fuentes, comprobación del índice de refracción y estado del artículo (2026-10-09)

## Qué se buscó y qué se obtuvo

| Objetivo | Resultado |
|---|---|
| Artículo «Camisa deprimida SK1310» (Optical Materials, ScienceDirect `S0925346725000102`) | **No obtenido.** La página completa devuelve 403 a acceso automatizado, y la búsqueda no lo localiza por título ni por SK1310. Pendiente: que el titular suba el PDF desde su acceso institucional. |
| Ficha técnica del fabricante (OHARA, SK-1310 fused silica) | **Obtenida.** Índices a 25 °C en aire, dn/dT, densidad, birrefringencia de deformación ≤ 20 nm/cm, OH < 1 ppm. Fuente: [OHARA SK-1310](https://oharacorp.com/wp-content/uploads/2025/02/SK1310.pdf). |
| Índice de sílice de referencia a 1550 nm | **Obtenido.** Coeficientes de Sellmeier atribuidos a Malitson (1965); n(1550 nm) = 1,44402. Fuentes: [Wikipedia, ecuación de Sellmeier](https://en.wikipedia.org/wiki/Sellmeier_equation); [arXiv:2105.12408](https://arxiv.org/pdf/2105.12408); [RP Photonics](https://www.rp-photonics.com/sellmeier_formula.html). El artículo original de Malitson no se consultó directamente. |

## Comprobación cuantitativa del índice

Índices de la ficha (aire → vacío con factor 1,000277) frente a Malitson en los siete puntos:

| λ (µm) | SK-1310 (vacío) | Malitson | diferencia |
|---|---|---|---|
| 0,3650 | 1,47516 | 1,47454 | +0,00062 |
| 0,4047 | 1,47023 | 1,46962 | +0,00061 |
| 0,4358 | 1,46730 | 1,46669 | +0,00060 |
| 0,4861 | 1,46374 | 1,46313 | +0,00061 |
| 0,5461 | 1,46068 | 1,46008 | +0,00061 |
| 0,5876 | 1,45906 | 1,45846 | +0,00060 |
| 0,6563 | 1,45697 | 1,45637 | +0,00061 |

- **Diferencia media:** +0,000608, con desviación típica 0,000006 (1 %). La diferencia es casi constante en todo el rango medido.
- **Supuesto.** Si la diferencia es independiente de la longitud de onda también a 1550 nm, el índice de SK-1310 a 1550 nm es **1,44463**. Ese supuesto no está verificado: la ficha no da datos por encima de 656 nm.
- **Comparación con el proyecto.** El n₀ = 1,444 usado en el proyecto coincide con la sílice de referencia (1,44402) con 6·10⁻⁴ de diferencia. Respecto de SK-1310 (supuesto anterior) queda 6·10⁻⁴ por debajo.

## Qué significa para el proyecto

- **Contrastes de índice (Δn).** No cambian: el desplazamiento es común a núcleo y camisa. Los resultados de [VECTORIAL-RESULTADOS](VECTORIAL-RESULTADOS.md) son relativos y no se ven afectados.
- **Número V.** Cambia menos de 0,1 %, porque depende de n₁² − n₂² y el desplazamiento es común.
- **Constante de propagación absoluta.** Cambia en torno a 4·10⁻⁴ relativo. Afecta a fases absolutas, no a la validez de los contrastes.
- **Decisión sobre n₀.** No se cambia el código ni los contratos publicados. Si el material se confirma como SK-1310, la actualización de n₀ debe hacerse con un contrato nuevo.

## Birrefringencia de la sílice en bulto (dato del fabricante)

La ficha indica birrefringencia de deformación ≤ 20 nm/cm, es decir, Δn ≤ 2·10⁻⁶ en el bulto. Esto es del mismo orden que la dispersión vectorial calculada en H2 (≈ 3,8·10⁻⁶ en índice absoluto). **La birrefringencia inducida por escritura láser no está caracterizada** y puede ser mucho mayor. Esa cuestión sigue abierta.

## Límites

- Un solo fabricante, datos a 25 °C en aire, sin incertidumbres de temperatura.
- Malitson se obtiene a partir de la relación de Sellmeier citada en fuentes secundarias.
- La extrapolación de un ajuste de Cauchy de tres términos a 365–656 nm dio 1,4503 a 1550 nm. Eso está fuera de su validez y **no se usa**.

## Corrección (2026-10-10, verificación V5)

- La línea que decía que la búsqueda no localiza el artículo «ni por título ni por SK1310» es **incorrecta**: la búsqueda sí lo localiza. Título: «Femtosecond laser writing of telecom-band depressed-cladding waveguides and mode modulation in SK1310 glass» (ScienceDirect, PII S0925346725000102; Crossref).
- El PDF completo sigue sin obtenerse: ScienceDirect devuelve 403 y Crossref no indica licencia abierta. Pendiente: que el titular o un acceso institucional lo suba.
- La ficha OHARA está confirmada: https://oharacorp.com/wp-content/uploads/2025/02/SK1310.pdf. Las tablas son imágenes y se leyeron visualmente. El supuesto del proyecto de n(1550 nm) = 1,44463 **no está verificado** (V5, P3f).
