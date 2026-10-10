# CONTRATO-bpm-r5 - convergencia en dz de la perdida del BPM (B5)

Fecha de escritura: 2026-10-10, antes de cualquier calculo de la ronda 5 (hora de escritura aproximada: ~10:21 UTC; la hora exacta no se registro).
Nota de orden: la referencia P_pert (seccion 1) y la verificacion V2 (seccion 2) se calcularon despues de escribir este contrato y antes de las corridas de dz. Ninguna cifra de dz existia al escribirlo.
Agente: Claude (subagente), carpeta experimentos/bpm_claude/.
Hora limite de entrega: 12:45 UTC.
Naturaleza: modelo numerico escalar paraxial. No es un dispositivo ni una medida. Sin datos de laboratorio.
Restricciones: solo CPU, OMP_NUM_THREADS=1, python -B, sin instalar nada, temporales y salidas en D:,
escritura solo en experimentos/bpm_claude/, sin git add/commit/push, sin informe .md (este contrato es el unico .md de la ronda).
Consulta JEV previa (router.py plan, fase verify): executor deterministic_tool, esfuerzo xhigh, sin paralelo, sin segunda opinion (remote_decision = true).

## 0. Contexto heredado (no cambia)

- B3 (ronda 1): perdida del modo guiado a 1 mm, umbral 1e-5. El umbral NO se cambia en r2, r3, r4 ni r5.
- r4 (CONTRATO-bpm-r4.md, resultados_bpm_r4.json):
  - dz = 1 um: P_perd(1 mm) = 2,4600e-4 (control).
  - dz = 0,5 um: 7,3692e-5. Cociente 3,34; orden aparente 1,74.
  - W60 y W80 (CAP proporcional): 2,4497e-4 y 2,4143e-4. La ventana W no influye (D-W pasa).
  - P-EIG (autovector del propio paso U, dz = 1): 2,4985e-4. El modo del esquema pierde la misma potencia.
- Propagador: split-step de Strang, bpm_r2.py (no se modifica). Unitario sin CAP (r2, V0: 1e-13).
- Configuracion fija de r5: n_ref = n1 = 1,444; n2 = 1,439; a = 6 um; lambda = 1,55 um; h = 0,2 um;
  W = 40 um (N = 401); CAP base s0 = 28, w = 12, R0 = 0,5; E0 = LP01 analitico muestreado; z = 1000 um.

## 1. Protocolo de la ronda 5

- Solo cambia dz en {1, 0,5, 0,25, 0,125} um. Los cuatro casos se ejecutan en serie (no en paralelo), para que los cronometros sean comparables.
- Cronometro: tiempo de pared de la llamada de propagacion (sin construir la malla). Se reporta por caso y el numero de pasos.
- Orden de convergencia: P(dz) = P0 + C dz^p. Orden observado p_last con la terna (dz = 0,5; 0,25; 0,125):
  p_last = log2[(P(0,5) - P(0,25)) / (P(0,25) - P(0,125))]. Se reporta tambien el orden de cada par (1 -> 0,5; 0,5 -> 0,25; 0,25 -> 0,125).
- Extrapolacion de Richardson:
  - con p observado: P_ext = P(0,125) + (P(0,125) - P(0,25)) / (2^p_last - 1).
  - con p = 2 (orden nominal de Strang), como referencia: P_ext2 = P(0,125) + (P(0,125) - P(0,25)) / 3.
- Referencia analitica de primer orden (comprobacion añadida, no cambia el protocolo):
  P_pert = 1 - exp(-2 R0 <t^2> L), con L = 1000 um, R0 = 0,5 um^-1 y
  <t^2> = sum(t^2 |E0|^2) / sum(|E0|^2) sobre la misma malla (E0 = LP01 muestreado, t = clip((s - 28)/12, 0, 1), s = max(|x|, |y|)).
  Es la perdida de primer orden del CAP sobre el modo guiado (la perdida fisica si el CAP solo actua sobre la cola del modo).

## 2. Verificaciones previas (condicion para creer las cifras)

- V0 (control dz = 1): |P(dz = 1) - 2,4600e-4| / 2,4600e-4 <= 1e-3.
- V1 (control dz = 0,5): |P(dz = 0,5) - 7,3692e-5| / 7,3692e-5 <= 1e-3.
- V2 (unitariedad sin CAP, dz = 0,125, z <= 100 um, cap = False): max_z |P(z)/P(0) - 1| <= 1e-9.

## 3. Criterio principal (umbral sin cambio)

- B3-r5: existe dz en {1, 0,5, 0,25, 0,125} um con P_perd(1 mm) <= 1e-5 (W = 40, h = 0,2, CAP base).
  pass = true si existe. dz* = la mayor dz que cumple B3 (la mas barata). Si no existe, dz* = no definida.

## 4. Diagnosticos (pass calculado por codigo; no deciden B3-r5)

- D-ORD: |p_last - 2| <= 0,25. pass = orden de Strang observado. Se espera fallo si el orden se mantiene cerca de 1,7.
- D-CONV: |P(0,125) - P(0,25)| / P(0,125) <= 0,10. pass = convergencia en dz al 10 % en dz = 0,125.
- D-EXT: P_ext (Richardson con p_last) <= 1e-5. pass = el limite dz -> 0 extrapolado cumple B3.
- D-PERT: |P_ext - P_pert| / P_pert <= 0,10. pass = el limite dz -> 0 coincide con la perdida de primer orden del CAP sobre el modo.

## 5. Contingencia de coste (declarada ahora)

- Si una corrida (de dz o de G3) supera 15 min de pared, se reduce la malla a h = 0,25 um (N = 321 con W = 40) y se declara en el JSON.
  El umbral y el criterio no cambian. Si con h = 0,25 sigue superando 15 min, la corrida se declara "no completada por plazo" y el estado sera "partial".
- No se reduce dz para ahorrar coste: la dz es la variable de la ronda.

## 6. G3 (condicional)

- G3 se ejecuta solo si B3-r5 pasa. Si no pasa: G3 = "no ejecutado: condicion no cumplida". No se calcula.
- Geometria: dos nucleos a x = -d/2 y x = +d/2, radio a = 6 um, n1 = 1,444 (nucleo), n2 = 1,439 (fondo), d = 14 y 16 um.
  W = 40, h = 0,2 (o 0,25 solo por la contingencia de la seccion 5), dz = dz*, CAP base.
- E0 (lanzamiento A0) = LP01 analitico de un nucleo centrado en -d/2.
- psi_R = LP01 analitico de un nucleo centrado en +d/2.
- Observable (definicion de CONTRATO-acoplador.md, seccion 2):
  P2m(z) = |<psi_R | A(z)>|^2 / (<psi_R | psi_R> <A0 | A0>), con inner products h^2.
- z_max = primer maximo local de P2m(z) (refinado por parabola sobre tres puntos). Debe ser interior (no en z_end).
- kappa_FD (um^-1), de experimentos/acoplador_claude/resultados_g1_g2.json (G1_main_h0125, kappa_FD_per_um):
  d = 14: 4,716394e-4 um^-1 (= 0,47164 mm^-1). d = 16: 2,0305398e-4 um^-1 (= 0,20305 mm^-1).
- L_c = pi / (2 kappa). z_end = 1,1 L_c (d = 14: ~3,66 mm; d = 16: ~8,51 mm).
- G3.d14: |z_max - L_c| / L_c <= 0,10.  G3.d16: |z_max - L_c| / L_c <= 0,10.
- G3: pass = G3.d14 y G3.d16. Si ambos pasan, G3 pasa.

## 7. Estado final

- "done": todos los criterios de las secciones 2, 3, 4 y 6 (o 6 declarado "no ejecutado") evaluados por codigo.
- "partial": falta alguno (por ejemplo, una corrida no completada por plazo).
- "blocked": no aplica (todo es local).
- Los fallos se publican como fallos. Nada se reescribe despues de ver las cifras.

## 8. Salidas

- experimentos/bpm_claude/CONTRATO-bpm-r5.md (este archivo).
- experimentos/bpm_claude/run_bpm_r5.py: corridas dz y V2; un JSON por caso en experimentos/bpm_claude/r5_runs/.
- experimentos/bpm_claude/run_g3_r5.py: G3 (solo si B3 pasa); JSON en r5_runs/.
- experimentos/bpm_claude/evaluar_bpm_r5.py: calcula todos los pass y escribe experimentos/bpm_claude/resultados_bpm_r5.json.
- Evidencia pesada (> 2 MB): ninguna prevista. Si la hubiera, a D:/PROJECTS/.cognition/archivo/ con manifiesto SHA-256.

## 9. Lo que NO afirmo

- Nada sobre la red 3D, escritura fs, fabricacion, dispositivo ni vectorial. Escalar paraxial, cifras de un modelo sin calibrar.
- Si B3-r5 no pasa, no se afirma causa: solo se publican las cifras medidas.
