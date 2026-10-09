# Tarea 5 · índices y geometrías: incertidumbres y verificación del material (2026-10-10)

**Estado: parcial.** Las incertidumbres de material están verificadas en lo que permiten las fuentes. Las geometrías y el contraste δn **no están medidos**: las tolerancias de esta página son supuestos explícitos para propagar, y deben sustituirse por medidas (tarea 14).

## 1 · Índice del material

| Fuente | n a 1550 nm | Estado |
|---|---|---|
| Sílice de referencia (Malitson, 1965, según fuentes secundarias) | 1,44402 | Verificada en fuentes secundarias |
| SK-1310 (OHARA), supuesto de desplazamiento constante | 1,44463 | Desplazamiento +6,08·10⁻⁴ ± 0,06·10⁻⁴ en 365–656 nm; a 1550 nm es un supuesto |
| Valor usado en el proyecto (n₀) | 1,444 | Dentro de 6·10⁻⁴ de ambas referencias |

**Consecuencia.** El desplazamiento de índice es común al núcleo y a la trinchera, así que **no cambia el contraste δn**, pero sí la constante de propagación absoluta (β, fase). La validez de los resultados de contraste no depende de n₀ a este nivel.

## 2 · Sensibilidad de la pérdida de fuga (a = 6 µm, λ = 1550 nm)

Pendientes obtenidas de los resultados ya guardados de GLASS-006a (sin cálculo nuevo):

| Magnitud | Sensibilidad |
|---|---|
| d ln(pérdida) / dt, δn = −0,005, t 12–18 µm | −0,785 por µm |
| d ln(pérdida) / dt, δn = −0,003, t 12–18 µm | −0,529 por µm |
| d ln(pérdida) / dδn, t = 12 µm | +1410 por unidad de δn (≈ 4,1× por cada 10⁻³) |

La fuga depende exponencialmente del espesor y del contraste. Un error de 10⁻³ en δn cambia la pérdida prevista en un factor 4.

## 3 · Propagación con tolerancias supuestas

Supuestos (**no son medidas**): σ(t) = 0,5 µm, σ(δn) = 5·10⁻⁴.

| Término | u(ln pérdida) |
|---|---|
| Espesor | 0,392 |
| Contraste δn | 0,705 |
| Total | 0,807 |

Pérdida de referencia 0,0443 dB/cm; rango 1σ **[0,020; 0,099] dB/cm**. Con estas tolerancias la predicción de fuga no es útil para comparar con una medida de pérdida de 0,07 dB/cm. Para que la predicción sea útil (±10 %), hacen falta **σ(δn) ≲ 10⁻⁴ y σ(t) ≲ 0,1 µm**, o medirlas en cada muestra.

## 4 · Fuentes documentales pendientes

- Artículo «Camisa deprimida SK1310» (Optical Materials, `S0925346725000102`): no obtenido (403). Pendiente de acceso institucional del titular.
- Malitson (1965) original: no consultado directamente; coeficientes de fuentes secundarias.
- Medidas de δn y geometría de muestras reales: pendientes de laboratorio.

## Archivos

- `Docs/PRESUPUESTO-INCERTIDUMBRE-GEOMETRIA.json`: sensibilidades, supuestos y propagación.
