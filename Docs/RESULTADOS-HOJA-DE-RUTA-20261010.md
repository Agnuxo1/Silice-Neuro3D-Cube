# Resultados de la hoja de ruta de Fran (2026-10-10)

Estado al cierre de la sesión (05:50 UTC). Dos rondas de workflow (`wf_25a8b230-999` y `wf_fef02470-1d2`) y dos verificaciones adversariales (V1 a V7). Todo es modelo numérico, no medida. Ningún punto se da por cerrado si no pasa su criterio preregistrado.

| # | Punto de la hoja | Estado | Resultado verificado | Pendiente |
|---|---|---|---|---|
| 1 | Solver 2D escalar independiente | **hecho** (19 de 20 criterios) | LP01 de la fibra de salto: error 7,4e-8 a h = 0,125 µm con sub-píxel, frente a 4,2e-6 del esquema escalonado. Orden 1,76 en el par grueso: **no cumple** el umbral de 1,8 en ese par; 1,99 en el fino. | Informe de A4 a h = 0,125 µm (RAM insuficiente en la ejecución). |
| 1 | BPM escalar paraxial | **parcial; no cumple B3** | Pérdida del modo guiado a 1 mm: 2,46e-4, frente al umbral de 1e-5, y no converge con h. No depende de la posición del CAP (2,43e-4 con CAP estrecho y exterior). Hipótesis, sin verificar: el dato inicial no coincide con el modo discreto y radia. | Corridas W60, W80, disc, dz05 y **G3** (longitud de transferencia del acoplador) sin completar. |
| 1 | Segundo solver radial | **parcial** (C1 y C2 cumplen) | C1: error en n_eff ≤ 1e-8 frente a las ecuaciones cerradas. C2: los cuatro casos primarios cumplen Re g (0,5 %) y pérdida frente a radial_ecs. C3: convergencia en paso con cambio relativo ~1e-12. El verificador no reproduce el orden RK4 declarado. | Orden RK4 y validación de la fracción de núcleo. |
| 2 | Camisa continua y de trazos discretos | **parcial; resultados de trazos no válidos** | Camisa continua: n_eff del modo casi ligado 1,44219587 + i 1,3e-5 (coincide con la ronda 1). Diseño corregido: la fracción de área real de la banda de trazos en 7,5–10,5 µm tiende a 0,5, no a f = N/48 (f > 1 para N ≥ 64 en el diseño original; ese diseño es erróneo). | Los casos de trazos no tienen modo de núcleo ligado en la caja: hay que rehacer el cálculo con el modo casi ligado. |
| 3 | Observable con área parcial y perfil por cobertura (009b/d) | **hecho en modelo** | Orden 2,03 frente a 0,97 del observable original. En 009d, la potencia en el núcleo cambia en ~4e-3 con el observable original y ~4e-6 con el de cobertura. | Réplica GLASS-007 V2: no completada en esta sesión (documentos en Docs/ según el agente; no revisados). |
| 4 | Frontera y fase en guías (009c) | **falla su criterio de vacío** | Retorno al núcleo en vacío: 6e-3 con dominio de 128 µm y 1,5e-3 con 256 µm, frente al umbral de 1e-4. | Diagnóstico de la fuente del retorno (ventana, absorbente o dato inicial). Fase: no concluida. |
| 5 | Perfiles y trazos medidos de SK1310 y modos reales | **bloqueado** | Ficha OHARA verificada. El artículo SK1310 (*Optical Materials*, 2025) existe: título verificado, texto completo no accesible (403). Índice de 1,44463 a 1550 nm: supuesto, no verificado. | PDF del artículo (lo debe subir el titular o un acceso institucional). |
| 6 | Cerrar el acoplador (GLASS-006b) | **parcial** | Base modal par/impar: κ_FD = 0,47164 mm⁻¹ a d = 14 µm (modelo T8: 0,471) y 0,20305 mm⁻¹ a d = 16 µm (modelo: 0,203). Confirmado por V2 (6 afirmaciones). | G3, contraste de longitud de transferencia con BPM (depende del punto 1). |
| 7 | Curvas | **parcial** | I2.0 cumple (recto con error 2,9e-7). I2.1 falla: a R = 10 mm el modo de núcleo se pierde en L = 80 µm con este método; el verificador lo recupera con otro método (convergencia a 1e-8). La tendencia n_eff(R) sube al bajar R, lo contrario de lo que esperaba el contrato; el modelo de índice equivalente lo predice. | Radio crítico no establecido. Pérdida por radiación no calculada. Seguimiento del modo en R ≤ 5 mm. |
| 7 | Registro entre caras y tolerancias correlacionadas | **modelo hecho** (medida bloqueada) | Para P₂ ≤ 0,10 a 10 mm, la separación de 20 µm no basta: hacen falta 20,4 µm. Tolerancias simétricas: 21 µm → 0,57 µm; 22 µm → 1,57 µm; 23 µm → 2,57 µm; 25 µm → 4,57 µm. Monte Carlo con correlación a d = 20 µm: fracción 0,19 (σ = 0,5 µm), 0,33 (1 µm) y 0,42 (2 µm). | Medida real del registro entre caras: laboratorio (T9). Los parámetros σ, ℓ y σ_res son supuestos. |
| 7 | Calibración | **modelo** (medida bloqueada) | Compilador de la tarea 11: C3 se cumple en 28 de 36 realizaciones (78 %). | Medida de δ: laboratorio (T14). |
| 8 | Red pequeña con tarea congelada, separando detección y no linealidad | **hecho** | Control E0: M_full reproduce la exactitud de prueba de F3-b (0,6425). H-A2 **cumple**: la detección intermedia aporta (0,862 frente a 0,5905). H-A1 **no cumple**: la activación MZI reduce la exactitud (0,6425 frente a 0,8620 sin activación). Es una red de dos capas, no tridimensional. | Lectura de la pérdida por periodicidad de T(I): no reproducida por V3. |
| 9 | Fabricación | **fuera de alcance actual** (según la hoja) | — | — |

## Verificación adversarial de las dos rondas

- V1 (ronda 1: solver, BPM, radial): 6 confirmadas, 3 refutadas, 1 no reproducida.
- V2 (ronda 1: acoplador y prefactor de T8): 6 confirmadas, 1 no reproducida, 1 sin verificar.
- V3 (ronda 1: 009c y ablación): 11 confirmadas, 1 refutada, 1 no reproducida.
- V4 (ronda 1: tracks, observable, curvas, registro): 16 confirmadas, 4 refutadas, 1 no reproducida, 2 sin verificar.
- V5 (bibliografía): 9 confirmadas, 3 sin verificar, 2 refutadas. Ver `Docs/LITERATURA-NOVEDAD.md`, sección 8.
- V6 (ronda 2: solver y radial): 14 confirmadas, 2 no reproducidas, 2 sin verificar. La igualdad exacta con la referencia escalonada es circular, y dos criterios de solver son tautológicos.
- V7 (ronda 2: tracks, curvas, BPM): 9 confirmadas, 4 refutadas, 1 sin verificar. Refutadas: tracks sin criterios evaluados, un criterio tautológico, I2.1 no reproducido por el verificador, y BPM sin criterios evaluados.

## Novedad (cambio de la sesión)

- HUST/SJTU (2026, DOI 10.1038/s41467-026-72316-9): red 3D de 8 capas escrita con láser fs en vidrio borosilicato. **Antecedente de la parte 3D.**
- SK1310 (2025, *Optical Materials*): guías de camisa deprimida en banda de telecomunicaciones. **Antecedente de la idea de trinchera a 1550 nm.** Leer el texto completo antes de cualquier afirmación de novedad.
- Lee et al. (2021, DOI 10.1038/s41598-021-03116-y): 1 dB/cm a 10 mm y 1550 nm. Verificado.

## Decisiones que necesita Fran

1. Leer el artículo de SK1310 (acceso institucional).
2. Si lanzamos una tercera ronda para BPM (hipótesis del dato inicial), tracks (rehacer con modo casi ligado) y curvas (seguimiento del modo). Estimado: 60 minutos de cálculo.
3. Licencia, visibilidad y Zenodo.
4. Socio o equipo para las medidas de laboratorio (puntos 5, 6 y 7).
