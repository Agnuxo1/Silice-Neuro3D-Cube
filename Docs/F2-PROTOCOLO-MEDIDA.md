# F2 · Protocolo de calibración y predicciones congeladas (2026-10-09)

**Estado: protocolo publicado antes de cualquier medida. Ninguna medida se ha realizado.** Requiere un laboratorio con láser de femtosegundo para escritura, fuente a 1550 nm, banco de corte y cámara de campo cercano. Ninguno de estos recursos está disponible en el repositorio ni en esta sesión.

Este documento congela qué se medirá, qué predicciones se someten a prueba y qué resultado las falsaría. Cualquier cambio posterior debe registrarse como enmienda con fecha, antes de medir.

## 1 · Dispositivos de calibración

| Dispositivo | a (µm) | t (µm) | δn | Predicción de fuga ideal (GLASS-006a) |
|---|---|---|---|---|
| A (primario) | 6 | 12 | −0,005 | **0,0443 dB/cm** |
| B (secundario) | 6 | 9 | −0,005 | 0,436 dB/cm (ver `RESULTADOS-G2-N.md`; incertidumbre ±0,01) |

La fuga ideal es el límite inferior de pérdida de una camisa continua de espesor t. Una camisa de trazos discretos tiene pérdidas adicionales por dispersión y defectos de escritura que el modelo no incluye.

## 2 · Predicciones fijadas

- **P-F2a (cota inferior de pérdida).** En el dispositivo A, la pérdida de propagación medida por corte debe cumplir **L_medida ≥ 0,044 dB/cm − 3σ**, con σ la incertidumbre de la pendiente. Si L_medida < 0,044 − 3σ, el modelo de fuga o la geometría asumida son incorrectos. Esa es la falsación.
- **P-F2b (campo modal, guía análoga).** Para la guía de salto ideal análoga (a = 6 µm, Δn = 0,005, λ = 1550 nm), el modo LP₀₁ escalar tiene **MFD (Petermann II) = 11,74 µm** y **diámetro 1/e² de intensidad = 11,97 µm**, con **89 % de la potencia en el núcleo**. Esto es una referencia, no una predicción del dispositivo real: el perfil de índice real debe medirse antes y dar la entrada del modelo. La comparación válida es con ese perfil medido, y el criterio es acuerdo dentro del 5 %.
- **P-F2c (acoplador).** Pendiente. Requiere calcular el coeficiente de acoplamiento κ(d) con un contrato de cálculo propio. No se incluye aquí.

## 3 · Procedimiento de medida

1. **Índice de refracción.** Medir el perfil de índice del trazo y de la camisa por microscopía de fase cuantitativa o campo cercano refractivo. Incertidumbre objetivo ≤ 5 × 10⁻⁵ en δn. Referencia del material: [SK1310-FUENTES](SK1310-FUENTES.md) (índice de SK-1310 a 1550 nm ≈ 1,44463 con un supuesto a verificar).
2. **Pérdida por corte.** Longitudes L = 1, 2, 3 y 4 cm en el mismo chip, tres chips por geometría. Transmisión con potencia de entrada fija y medida en salida. Pendiente de la regresión lineal de dB frente a L da α (dB/cm). Criterio de calidad: incertidumbre de la pendiente ≤ 0,01 dB/cm. Una pendiente con incertidumbre mayor se declara **no concluyente** y no se usa para falsar P-F2a.
3. **Polarización.** Medir TE y TM por separado. Las pérdidas de acoplamiento de entrada y salida (literatura: ≈ 0,2 dB por faceta en guías escritas por fs; [arXiv:2408.06688](https://arxiv.org/abs/2408.06688)) no se incluyen en la pendiente, porque se obtienen como ordenada en el origen.
4. **Campo cercano.** Imagen del modo LP₀₁ a 1550 nm con objetivo de apertura adecuada. El MFD se obtiene con la definición Petermann II y con el diámetro 1/e², y se compara con P-F2b tras calibrar el perfil de índice.

## 4 · Referencia de literatura (no es predicción)

Arnés de comparación: [arXiv:2408.06688](https://arxiv.org/abs/2408.06688) reporta **0,07 dB/cm** de pérdida de propagación en guías multiscan de sílice fundida, con un acoplamiento de 0,2 dB por faceta. El resumen no indica la longitud de onda. Una búsqueda secundaria sitúa la caracterización en 920 nm. No se usa para falsar nada: sirve para ubicar el orden de magnitud de las pérdidas reales.

## 5 · Criterios de resultado

- **Se confirma P-F2a** si L_medida ≥ 0,044 − 3σ en A. No prueba que el modelo sea completo.
- **Se falsa P-F2a** si L_medida < 0,044 − 3σ con σ ≤ 0,01 dB/cm. Se publica el fallo y se revisa la geometría o el modelo.
- **No concluyente** si σ > 0,01 dB/cm o si el perfil de índice no está medido.

## 6 · Lo que este protocolo no hace

- No mide nada. No afirma que exista un dispositivo fabricado.
- No demuestra la red óptica ni la función neuronal (F3 y puntos 12–18 del roadmap).
- No incluye birrefringencia de escritura, que no está caracterizada (ver [SK1310-FUENTES](SK1310-FUENTES.md)).
- No sustituye la revisión de un equipo experimental externo.

## Recursos necesarios

Láser fs con control de energía, banco de corte con fibra de entrada y salida, fuente sintonizable a 1550 nm, medidor de potencia calibrado, cámara InGaAs para campo cercano y microscopio de fase cuantitativa. Socio experimental: ver decisiones del titular en [ESTADO-ACTUAL](ESTADO-ACTUAL.md).
