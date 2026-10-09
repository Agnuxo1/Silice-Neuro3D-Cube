# Tarea 6 · contraste vectorial de la geometría efectiva (trinchera) · resultados (2026-10-10)

Contrato y método: `vector_layers.py` (8×8, mpmath, 30 dígitos), `trinchera_vectorial.py`, `trinchera_job.py`, `run_trinchera.sh`. Resultados: `trinchera_vectorial_final.json` (16 trabajos, uno por geometría y familia).

Geometría efectiva: núcleo n₀ = 1,444 (r < 6 µm), trinchera n₀ + δn de espesor t, exterior n₀ con radiación saliente.

## Validación antes de usar el solver

- **Fibra de salto analítica** (trinchera igual a la camisa, exterior a 60 µm): HE₁₁, HE₂₁, TE₀₁ y TM₀₁ reproducidos con diferencia de n_eff de 10⁻¹⁶ frente a la ecuación característica exacta. La formulación de campos, signos y condiciones de contorno es correcta.
- **Bloques TE/TM** (ν = 0): el sistema se separa exactamente. TE usa E_φ y H_z; TM usa E_z y H_φ. Los modos TE/TM se resuelven por separado.
- **Búsqueda multiarranque** con filtro de validez: n_eff estrictamente entre n_trinchera y n₀, y |Im n_eff| < 10⁻³. Una primera versión dio raíces espurias (n_eff = −0,79): se corrigió y se registra.

## Resultados

| δn | t (µm) | familia | n_eff (Re) | pérdida (dB/cm) | estado |
|---|---|---|---|---|---|
| -0.005 | 6 | HE11 | 1.442193039 | 4.5992 | válido |
| -0.005 | 6 | HE21 | 1.439686988 | 38.28 | válido |
| -0.005 | 6 | TE01 | 1.439692812 | 38.022 | válido |
| -0.005 | 6 | TM01 | 1.439689736 | 38.355 | válido |
| -0.005 | 12 | HE11 | 1.442189333 | 0.044044 | válido |
| -0.005 | 12 | HE21 | 1.439753191 | 2.7893 | válido |
| -0.005 | 12 | TE01 | 1.439758726 | 2.7541 | válido |
| -0.005 | 12 | TM01 | 1.439755504 | 2.7905 | válido |
| -0.003 | 6 | HE11 | 1.442483994 | 18.221 | válido |
| -0.003 | 6 | HE21 | — | — | **fuera de validez** (boundary root n_eff=n_trench) |
| -0.003 | 6 | TE01 | — | — | **fuera de validez** (outside window) |
| -0.003 | 6 | TM01 | — | — | **fuera de validez** (outside window) |
| -0.003 | 12 | HE11 | 1.442482436 | 0.75287 | válido |
| -0.003 | 12 | HE21 | — | — | **fuera de validez** (boundary root n_eff=n_trench) |
| -0.003 | 12 | TE01 | — | — | **fuera de validez** (outside window) |
| -0.003 | 12 | TM01 | — | — | **fuera de validez** (outside window) |

## Comparación independiente con el cálculo escalar (GLASS-006a)

HE₁₁ vectorial frente al escalar guardado (pérdida y n_eff mapeado con n₀ + Re γ / k₀):

| Caso | pérdida vectorial | pérdida escalar | diferencia | Δn_eff |
|---|---|---|---|---|
| dn-0.005_t6 | 4.5992 | 4.487 | +2.50 % | -2.5e-06 |
| dn-0.005_t12 | 0.044044 | 0.04425 | -0.47 % | -5.9e-06 |
| dn-0.003_t6 | 18.221 | 18.11 | +0.62 % | -1.1e-06 |
| dn-0.003_t12 | 0.75287 | 0.7432 | +1.30 % | -3.4e-06 |

- Las pérdidas coinciden dentro de 0,5–2,5 %, y los índices dentro de 6·10⁻⁶. Los dos cálculos son independientes: uno analítico vectorial y otro numérico escalar con mallas.
- **Polarización (δn = −0,005).** La separación TE₀₁ − TM₀₁ es +3.08·10⁻⁶ (t = 6 µm) y +3.22·10⁻⁶ (t = 12 µm). La separación de la fibra de salto es 3,2·10⁻⁶, así que la trinchera no cambia la birrefringencia modal de forma apreciable a este contraste.
- **Límite de validez.** Para δn = −0,003, los modos TE₀₁, TM₀₁ y HE₂₁ tienen n_eff por debajo del índice de la trinchera. Ahí la base de soluciones evanescentes no aplica, y esos modos no se han calculado con este método. Solo HE₁₁ es válido en todas las geometrías.

## Lo que no afirma

- No es un solver de elementos finitos independiente. La comprobación independiente es la fibra analítica y el cálculo escalar.
- Geometría circular y capas uniformes. Sin no circularidad, sin tensión de escritura, sin birrefringencia inducida.
- Los modos con fuga se caracterizan por Im β, sin campo de radiación explícito.
- Para δn = −0,003 no hay TE, TM ni HE₂₁ válidos: quedan para un cálculo con otra base.

## Medida de convergencia del FD escalar (2026-10-10, tarea 6)

Objetivo: medir el error de un solver de diferencias finitas estándar frente a la precisión que exige la separación TE/TM (≈ 3·10⁻⁶ en n_eff). Caso: modo LP₀₁ escalar de la fibra de salto análoga (λ = 1,55 µm, a = 6 µm, n₁ = 1,444, n₂ = 1,439, V = 2,9202), ventana de ±30 µm, Laplaciano de 5 puntos con contorno de Dirichlet y valor propio más cercano a k₀²n₁² (`fd_escalar_convergencia.py`, datos en `fd_escalar_convergencia.json`).

| h (µm) | incógnitas | n_eff (FD) | |error| |
|---|---|---|---|
| 0,5 | 14 161 | 1,4421632 | 2,9·10⁻⁵ |
| 0,25 | 57 121 | 1,4421814 | 1,1·10⁻⁵ |
| 0,125 | 229 441 | 1,4421879 | 4,2·10⁻⁶ |

Referencia analítica: n_eff = 1,4421922.

Lectura:
- El orden observado es 1,42 y 1,36, no 2. La causa probable es el contorno escalonado del núcleo circular. Por eso la extrapolación de Richardson con orden 2 (|error| = 2,0·10⁻⁶) **no es válida** aquí, y no se usa.
- Con el orden medido, reducir el error de 4,2·10⁻⁶ a unos 3·10⁻⁷ exigiría h ≈ 0,02 µm, es decir unos 3000 nodos por eje. Con este método no es práctico.
- Un FD vectorial con promediado de la permitividad en la interfaz podría converger a orden 2 y reducir ese requisito. No está implementado ni validado aquí, así que la comprobación independiente de T6 queda pendiente.
- La medida es escalar. No demuestra que un FD vectorial no pueda resolver la separación TE/TM; demuestra que el FD estándar con contorno escalonado no la resuelve sin una malla inviable.
