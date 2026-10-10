# CONTRATO T6 r5 · solver semivectorial de orden 2 con promediado en la interfaz

Fecha de fijación: 2026-10-10, antes de cualquier cálculo de T6 r5.
Carpeta: `experimentos/vectorial_claude/` (archivos nuevos: `fd_vectorial_*.py`, `CONTRATO-T6-r5.md`, `resultados_t6_r5.json`).
Restricciones: solo CPU, `python -B`, `OMP_NUM_THREADS=1`, numpy, scipy y biblioteca estándar. Sin instalaciones. Sin GPU. Temporales en D:. Memoria por proceso <= 2 GB.

## 0. Consulta a JEV y umbrales heredados

- Plan de paso (`router.py plan`): `remote_decision=true` (provenance=jev, conectado). Ejecutor: principal, esfuerzo alto, sin segunda opinión.
- Consulta agrupada (`router.py jev`, `t6_jev_estado.json` / `t6_jev_preguntas.json`): provenance=jev, conectado. Formulación elegida: semivectorial H_y promediado (confianza 0,98). Referencia de la puerta: HE11 vectorial exacto (confianza 0,5, se trata como orientación). Contraste con modos con fuga: no comparable (valor 0,22 sobre 1).
- Umbrales de rondas anteriores que se mantienen y se citan:
  - `test_vector_step.py` V1: límite escalar relativo 1e-6 (se usa como verificación de código, sección 5, V-a).
  - `test_vector_step.py` V3 y `vector_step.py`: residuo de raíz 1e-9 relativo (V-b).
  - `run_contrast.py`: H1 = 1e-5 y H2 = 1e-4 (no se reevalúan aquí).
  - Ronda 1 (`RESULTADOS-VECTORIAL-GEOMETRIA.md`): separación TE01 − TM01 en la trinchera dn = −0,005, t = 6 µm, +3,08·10⁻⁶ en Re n_eff. Se recalcula con `vector_layers.py` en esta ronda (sección 6).
  - `fd_escalar_convergencia.json` (escalar, escalonado): orden observado 1,42 y 1,36; error 4,2·10⁻⁶ a h = 0,125 µm.

## 1. Geometría y referencias (fijadas)

- Fibra de salto: λ = 1,55 µm, a = 6 µm, n1 = 1,444 (núcleo), n2 = 1,439 (revestimiento). V = 2,9201606 (idéntico a `fd_escalar_convergencia.json`).
- Referencia primaria de la puerta: HE11 vectorial exacto. Se obtiene con `vector_step.Guide.hybrid(b, nu=1)` y `top_root`, igual que `test_vector_step.modes`. Valor de la ronda previa: n_eff = 1,4421892973651511. Se recalcula y se compara.
- Referencia secundaria (diagnóstico, no puerta): LP01 escalar exacto, n_eff = 1,4421921654570133 (la de `fd_escalar_convergencia.json`). Sirve para comparar con la medida escalar previa.
- Diferencia física HE11 − LP01 = 2,87·10⁻⁶ en n_eff. Es mayor que el umbral de la puerta, así que la elección de referencia decide el veredicto y se declara aquí.

## 2. Formulación (declarada: semivectorial H_y)

- Ecuación para H_y (dominante x), derivada de las ecuaciones vectoriales para H_t con el término de acoplamiento ∂_y H_x despreciado:

  β² H = ε ∂_x( (1/ε) ∂_x H ) + ∂_y² H + k0² ε H

  con k0 = 2π/λ, β = k0 n_eff, ε = n² en la celda.
- Malla: celdas centradas de tamaño h en el cuadrante [0, L]², L = 30 µm (mismo L que la medida escalar previa). Simetría en x = 0 e y = 0 (Neumann, modo par en ambos ejes). Contorno en x = L e y = L: Dirichlet (H = 0 en la cara). La celda rota por la interfaz recibe ε promediado en el área exacta: ε_celda = n2² + (n1² − n2²) f, con f la fracción de área del disco de radio a dentro de la celda (fórmula analítica, sección 4).
- Coeficiente en caras (flujo de 1/ε): u_cara = 2/(ε_L + ε_R), media armónica de u = 1/ε entre celdas vecinas (flujo continuo en interfaz normal). En la cara de contorno, u = 1/ε de la celda interior.
- Discretización de orden 2 con paso h, 5 puntos en la dirección y. Autovalor en β² con `scipy.sparse.linalg.eigs` (shift-invert, σ = k0² n1²), que da el mayor autovalor (modo fundamental).
- Declaración de protocolo: el r5 cambia el solver escalar escalonado de `fd_escalar_convergencia.py` por este semivectorial promediado, y cambia la referencia de la puerta de LP01 a HE11. Se declara como cambio de protocolo.

## 3. Puerta de factibilidad (paso 1)

- Mallas: h ∈ {0,25; 0,125; 0,0625} µm. Para cada h se registran n_eff, error absoluto respecto a HE11, número de incógnitas y pico de memoria del proceso.
- Criterio G1 (puerta, evaluado por el código): |n_eff(h = 0,0625) − n_HE11| <= 1·10⁻⁶ y pico de memoria de la corrida de h = 0,0625 <= 2 GB. Pasa solo si se cumplen los dos.
- Si G1 no pasa: se detiene. Se declara factibilidad negativa. Se estima el h necesario con el orden observado (h_req = h · (umbral/error)^(1/p)).
- Diagnóstico (no es puerta): error respecto a LP01 para comparar con la medida escalar; orden observado p; extrapolación de Richardson del valor continuo; error de modelo = valor continuo − n_HE11. Si el error de modelo supera 1·10⁻⁶, la reducción de h no alcanza el umbral y se dice así.

## 4. Verificación del código (previa a la puerta; si falla, no se publica la puerta)

- V-a (ENMENDADO antes de calcular, ver sección 8, E1): medio uniforme n1 = n2 = 1,444 en la caja, h = 0,0625. Solución exacta del operador de 5 puntos con Neumann en x = 0 e y = 0 y Dirichlet en L: β²_exacto = k0² n² − (2/h²)(1 − cos(π/(2M))), M = L/h. Criterio: error relativo de β² <= 1·10⁻¹⁰ para semivectorial y escalar.
- V-b (residuo): ||A H − β² H|| / ||H|| <= 1·10⁻⁸ para el modo fundamental en cada h de la puerta.
- V-c (áreas): suma de f·h² sobre el cuadrante = π a²/4 con error <= 1·10⁻¹² (fórmula analítica de la celda de disco).
- V-d (simetría): en h = 0,25, el cuadrante con Neumann coincide con la malla completa [−L, L]² (mismo operador) con diferencia de n_eff <= 1·10⁻¹⁰.
- V-e (referencia): HE11 recalculado y residuo de la raíz <= 1·10⁻⁹ relativo (V3), y coincidencia con 1,4421892973651511 a 1·10⁻¹².
- V-f (caja): L = 30 frente a L = 36 en h = 0,125 con la semivectorial; diferencia <= 1·10⁻⁷. Si no se cumple, se reporta como límite de caja.

## 5. Contraste TE/TM (paso 2, solo si G1 pasa)

- Geometría: trinchera dn = −0,005, t = 6 µm (núcleo n0 = 1,444 con r < 6 µm; trinchera n0 + dn con 6 < r < 12 µm; exterior n0). La referencia es `vector_layers.py` (`trinchera_vectorial.solve`), en Re n_eff.
- Procedimiento: se resuelven dos modos H_y en el mismo cuadrante con las simetrías del lóbulo ν = 1: (a) TM-like, par en y, impar en x (Dirichlet en x = 0, Neumann en y = 0); (b) TE-like, par en x, impar en y (Neumann en x = 0, Dirichlet en y = 0). Δ_FD = n_TE-like − n_TM-like.
- Referencia: Δ_ref = Re(TE01) − Re(TM01) recalculada con `vector_layers.py` (sección 6).
- Criterio C-T: |Δ_FD − Δ_ref| < 0,10 · |Δ_ref|. Se evalúa con el código.
- Advertencia fijada de antemano: los modos de `vector_layers.py` en esta trinchera tienen Im n_eff del orden de 10⁻⁴ (fuga hacia el exterior de índice 1,444), por encima de la separación de 3·10⁻⁶. Una caja cerrada no reproduce esa fuga. El criterio se evalúa tal como está fijado, y se declara que la comparación no es como-con-como si la fuga domina.

## 6. Referencia vectorial (sin cambios)

- Se recalcula `vector_layers.py` (multiarranque de `trinchera_vectorial.solve`) para dn = −0,005, t = 6 µm, en TE01, TM01 y HE11. Se compara con los valores de `trinchera_vectorial_final.json` (1,439692812; 1,439689736; 1,442193039).

## 8. Enmiendas (declaradas, fijadas antes de cualquier cálculo de puerta)

- E1 (V-a): la versión original (límite escalar con V fijo y n2 = n1 − 10⁻⁷) exige un radio a = V/(k0 sqrt(n1² − n2²)) de unos 1340 µm. No cabe en la caja de L = 30 µm, así que no es implementable. Se sustituye por la comprobación exacta en medio uniforme (V-a de la sección 4). Es un cambio de protocolo de verificación, no de criterio de puerta. G1 y umbrales no cambian.
- E2: la referencia LP01 se mantiene solo como diagnóstico, no como puerta.
- E3 (procedimiento del paso 2, fijado antes de calcular el paso 2; no cambia G1):
  - Malla del paso 2: h = 0,0625 µm, L = 30 µm, cuadrante con los sectores de la sección 5.
  - Autovalor: σ = k0² (1,43969)². De los 8 autovalores más cercanos a σ, se toma el de mayor fracción de |H|² en r < a (núcleo). Se declara como selección física posterior a la solución, no como elección de resultado.
  - Δ_FD = n_TE-like − n_TM-like, con H_y en ambos sectores.
  - Δ_ref = Re(TE01) − Re(TM01) de `vector_layers.py` en dn = −0,005, t = 6 µm (recalculada, sección 6).
  - Criterio C-T sin cambios: |Δ_FD − Δ_ref| < 0,10 · |Δ_ref|.
  - Transparencia: antes de fijar E3 se hicieron comprobaciones rápidas de código con la fibra de salto en h = 0,25 y 0,125 (solo para verificar el solver, no para la puerta). Su resultado no cambia G1 ni ninguna otra regla.

## 7. Salidas y estado

- `resultados_t6_r5.json`: cada criterio con su id, descripción, valor, umbral y `pass` calculado por el script (no escrito a mano). Campos de memoria, tiempos, órdenes observados, error de modelo y estado `done` (todos los criterios evaluados), `partial` (faltan) o `blocked` (depende de algo externo).
- Ningún archivo de informe `.md` aparte de este contrato. El orquestador escribe los informes.
- Si una corrida supera 15 min, se reduce la malla y se dice. Hora límite: 13:30 UTC. Si no se llega, se entrega parcial y se dice qué falta.
