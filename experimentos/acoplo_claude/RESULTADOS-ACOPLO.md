# Tarea 8 (parcial) · acoplo entre guías paralelas · resultados (2026-10-10)

Contrato: `CONTRATO-ACOPLO.md` (con enmienda E-1). Código: `acoplo_paralelo.py`. Datos: `acoplo_resultados.json`. La primera ejecución, con error de normalización, se conserva como `acoplo_resultados_v0_normalizacion_erronea.json` y **no** se usa.

## Verificaciones del modelo

| Criterio | Valor | Veredicto |
|---|---|---|
| V1 normalización (cerrada frente a numérica) | 1,0·10⁻¹³ | cumple (umbral 10⁻⁶) |
| V2 convergencia de cuadratura, d = 20 µm | 1,0·10⁻¹⁵ | cumple (umbral 10⁻⁶) |
| V3 pendiente de ln κ frente a −W/a − 1/(2d), d = 30–60 µm | error < 0,05 % de W/a | cumple (umbral 3 %) |
| V4 validez débil, Δ = (n₁² − n₂²)/(2n₁²) | 0,0035 | cumple (umbral 0,01) |

Parámetros: V = 2,92016, U = 1,75688, W = 2,33254, β = 5,84617 µm⁻¹.

## Acoplo y longitud de transferencia (modelo)

| d (µm) | κ (mm⁻¹) | L_c (mm) | P₂ a 1 mm | P₂ a 5 mm | P₂ a 10 mm |
|---|---|---|---|---|---|
| 12 | 1,104 | 1,42 | 0,798 | 0,477 | 0,998 |
| 14 | 0,471 | 3,33 | 0,206 | 0,500 | 1,000 |
| 16 | 0,203 | 7,74 | 4,07·10⁻² | 0,722 | 0,803 |
| 18 | 8,82·10⁻² | 17,8 | 7,75·10⁻³ | 0,182 | 0,596 |
| 20 | 3,85·10⁻² | 40,8 | 1,48·10⁻³ | 3,66·10⁻² | 0,141 |
| 25 | 4,94·10⁻³ | 318 | 2,44·10⁻⁵ | 6,11·10⁻⁴ | 2,44·10⁻³ |
| 30 | 6,47·10⁻⁴ | 2,43·10³ | 4,19·10⁻⁷ | 1,05·10⁻⁵ | 4,19·10⁻⁵ |
| 35 | 8,59·10⁻⁵ | 1,83·10⁴ | 7,38·10⁻⁹ | 1,85·10⁻⁷ | 7,38·10⁻⁷ |
| 40 | 1,15·10⁻⁵ | 1,36·10⁵ | 1,33·10⁻¹⁰ | 3,32·10⁻⁹ | 1,33·10⁻⁸ |

## Predicciones fijadas antes de calcular

- **H-T8-1** (d = 20 µm, L = 10 mm, P₂ ≤ 0,10): **no se cumple**. El modelo da P₂ = 0,141 (≈ −8,5 dB, frente al umbral de −10 dB).
- **H-T8-2** (d = 40 µm, L = 10 mm, P₂ ≤ 10⁻³): **se cumple**. El modelo da P₂ = 1,3·10⁻⁸.

## Lectura de diseño (modelo)

- Interpolando en escala logarítmica entre 25 y 30 µm, el paso necesario para P₂ ≤ 10⁻³ tras 10 mm es de **unos 26 µm**. Es una estimación del modelo, no un criterio de diseño verificado.
- A 20 µm, la transferencia completa ocurre a L_c ≈ 41 mm, y tras 10 mm ya hay un 14 % de potencia en la guía vecina.

## Límites (declarados)

1. **Prefactor sin comprobación independiente.** Usa la forma estándar del acoplo débil, κ = (k₀²/2β)(n₁² − n₂²)·I(d). V3 valida la forma (la dependencia en d), no el valor absoluto. Por tanto L_c y P₂ dependen de un prefactor no verificado aquí. Una verificación posible es la diferencia de supermodos Δβ = 2κ con un solver de diferencias finitas, o una medida.
2. **Modelo escalar, isótropo, de fibra de salto análoga.** No es el perfil de la trinchera ni el de la escritura fs, que es anisótropa.
3. **No modelado en esta tarea:** pérdida de curva por radiación, diafonía en cruces y acoplo vertical entre capas 3D. Estado pendiente (ver abajo).
4. **Sin medidas.** Todas las cifras son predicciones del modelo.

## Pendiente de T8

- **Curvas:** modelo de pérdida por radiación no abordado. Protocolo: cutback con series de radios de curvatura, con el mismo modo de referencia que F2.
- **Cruces:** la diafonía en un cruce requiere un cálculo de campo en la zona de cruce (BPM o solver de cruce). No se ha hecho.
- **Conexiones 3D:** el acoplo vertical con escritura anisótropa requiere caracterizar el perfil de escritura. Pendiente.
