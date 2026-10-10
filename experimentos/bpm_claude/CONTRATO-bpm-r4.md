# CONTRATO-bpm-r4 - origen de la perdida del modo guiado en el BPM (B4)

Fecha de escritura: 2026-10-10, antes de cualquier calculo de la ronda 4 (hora de escritura ~10:08 UTC).
Agente: Claude (subagente), carpeta experimentos/bpm_claude/.
Naturaleza: modelo numerico escalar paraxial. No es un dispositivo ni una medida. Sin datos de laboratorio.
Restricciones: solo CPU, OMP_NUM_THREADS=1, python -B, sin instalar nada, temporales y salidas en D:.
Escritura solo en experimentos/bpm_claude/. No se toca src/silice/, tests/, scripts/, coordinacion/ ni Docs/.
No se hace git add, commit ni push. Hora limite de entrega: 10:30 UTC.

## 0. Contexto heredado (no se cambia)

- Ronda 1, B3: perdida del modo guiado a 1 mm = 2,460e-4 (h = 0,2 um, dz = 1 um, CAP W = 40, s0 = 28, w = 12, R0 = 0,5). Umbral 1e-5. FALLO.
- Ronda 2 (datos en r2_runs/, se citan, no se rehacen en r4 salvo los indicados):
  - base (W40, dz1): 2,4600e-4. disc (dato Lanczos): 2,4596e-4. dz05 (W40, dz 0,5): 7,3692e-5.
  - G0 (R0 = 0,05): 2,2791e-4. s0 (s0 = 34, w = 6): 2,4293e-4.
  - W60 (s0 = 48, proporcional): 2,4497e-4. W60c (s0 = 28, absoluto): 2,4745e-4. W80 (s0 = 68, proporcional): 2,4143e-4.
  - Lectura de r2 que se cita: la perdida casi no depende de W ni de la posicion del CAP; si depende de dz.
- Ronda 3: r3_runs/ tiene solo logs vacios (0 bytes) y ningun JSON. No hay cifras de r3 que citar.
  Las corridas de r3 (fd_*) no se toman como evidencia.
- Descartadas en la ronda 3 (no se repiten): dato inicial discreto (E0 FD solver2d, 2,4601e-4 frente a 2,4600e-4 analitico)
  y absorcion de primer orden del CAP (3,2e-8 por mm).
- El umbral 1e-5 de B3 NO se cambia en esta ronda.

## 1. Hipotesis de la ronda 4 (fijadas ahora)

- H-PROP: la perdida viene del propagador (split-step de Strang): el esquema no tiene un modo guiado estacionario
  identico al del Hamiltoniano discreto, y emite potencia hacia el CAP.
- H-CONTORNO: la perdida viene del contorno periodico de la ventana (la radiacion que sale por un borde vuelve por el otro).

## 2. Esquema y protocolo (declaracion de cambio de protocolo)

- Esquema actual: split-step de Fourier de Strang (bpm_r2.py: A <- P IFFT[D FFT(P A)]). NO es Crank-Nicolson.
  Por tanto la prueba (a) del encargo (SSF con la misma malla si el esquema es CN) NO APLICA: el esquema ya es SSF.
- CAMBIO DE PROTOCOLO (declarado): la prueba (a) se sustituye por P-EIG. P-EIG usa el autovector guiado del propio
  operador de un paso U = P D P (con CAP), obtenido con eigs (ARPACK, mayor |lambda|). Es el "autovector del propio esquema"
  que la ronda 3 dejo pendiente. No es el autovector discreto del Hamiltoniano (ese control ya dio 2,4596e-4).
- Propagador: bpm_r2.py de esta carpeta (propio; no se modifica).
- Modelo: n_ref = n1 = 1,444; n2 = 1,439; nucleo radio 6 um; lambda = 1,55 um; N = 2M+1 con h = 0,2 um;
  CAP Gamma = 2 k0 n_ref R0 t^2, t = clip((s - s0)/w, 0, 1), s = max(|x|, |y|); E0 = LP01 analitico muestreado.

## 3. Corridas (todas hasta 1 mm, cap activo)

- r4_W40_dz1: W = 40, s0 = 28, w = 12, R0 = 0,5, dz = 1. CONTROL (debe reproducir la ronda 2).
- r4_W60_dz1: W = 60, s0 = 48, w = 12, R0 = 0,5, dz = 1. (b) ventana, CAP proporcional.
- r4_W80_dz1: W = 80, s0 = 68, w = 12, R0 = 0,5, dz = 1. (b) ventana, CAP proporcional. N = 801.
- r4_W40_dz05: W = 40, s0 = 28, w = 12, R0 = 0,5, dz = 0,5. (c) paso.
- r4_PEIG_W40_dz1: W = 40, dz = 1, E0 = autovector guiado de U (P-EIG). (a sustituida)
- No se ejecuta dz = 0,25 ni W x dz cruzados: plazo de 10:30 UTC. Queda declarado como no ejecutado.

## 4. Criterios numericos r4 (umbrales fijados AHORA)

Verificacion (condicion previa para creer las cifras):
- V0 (control): |P_perd(r4_W40_dz1) - 2,4600e-4| / 2,4600e-4 <= 1e-3.
- V1 (P-EIG convergido): residuo ||U E - lambda E|| / ||E|| <= 1e-6 y solape con LP01 analitico ov2 >= 0,999.
- V2 (consistencia P-EIG): |P_perd(r4_PEIG_W40_dz1) - (1 - |lambda|^(2 N_pasos))| <= 1e-6 (N_pasos = 1000).

Prueba principal (umbral de la ronda 1, sin cambio):
- B3-r4: existe alguna configuracion de C = {r4_W40_dz1, r4_W60_dz1, r4_W80_dz1, r4_W40_dz05, r4_PEIG_W40_dz1}
  con P_perd(1 mm) <= 1e-5. pass = true si existe. Solo CAP activo; no se usan corridas sin CAP como criterio.

Diagnosticos (pass calculado, no decide B3-r4):
- D-W (H-CONTORNO): max(|P60 - P40|/P40, |P80 - P60|/P60) <= 0,10. pass = la perdida no depende de W (contorno refutado).
- D-dz (dependencia de la particion): |P_dz05 - P_dz1|/P_dz1 <= 0,10. pass = la perdida no depende de dz.
  Se espera fallo (r2: 3,3 veces menos con dz 0,5).
- D-PROP (H-PROP): P_perd(r4_PEIG_W40_dz1) <= 1e-5. pass = el propio autovector del esquema no pierde potencia
  (la perdida es desajuste dato-esquema y se corrige con el modo del esquema). Si falla, la perdida con el modo del
  esquema sigue siendo > 1e-5: la fuente es intrinseca al propagador con el CAP, y no se corrige cambiando el dato.
- D-CONS (consistencia de la perdida por paso): |P_perd(r4_PEIG_W40_dz1) - (1 - |lambda|^2000)| / P_perd <= 0,10
  (la perdida es la de un autovector estacionario del esquema).

G3 (condicionado): solo si B3-r4 pasa. Si no pasa, G3 = "no ejecutado: condicion no cumplida" y no se calcula.
Si pasara, G3 quedaria "pendiente: no ejecutado por plazo" (dos nucleos, d = 14 y 16 um, necesitan propagar
hasta ~1,1 L_c con h = 0,2 um, mas de 10 min por corrida).

## 5. Clasificacion (no es un pass)

- Si B3-r4 pasa: la configuracion que pasa se declara y se dice cual. No se afirma que la causa sea universal.
- Si B3-r4 no pasa: "la causa no se encontro" con las cifras de las corridas. No se afirma causa.
- Si D-W pasa y D-dz falla: la perdida no viene del contorno y depende de la particion temporal (lectura descriptiva).

## 6. Estado final

- "done" solo si todos los criterios de las secciones 4 y 5 se evaluaron por codigo (pass en resultados_bpm_r4.json).
- "partial" si falta alguno (por ejemplo, si una corrida no termina a tiempo o P-EIG no converge).
- "blocked" si dependiera de algo externo (no aplica).
- Un criterio que falla se publica como fallo. Nada se reescribe despues de ver las cifras.

## 7. Salidas

- experimentos/bpm_claude/CONTRATO-bpm-r4.md (este archivo).
- experimentos/bpm_claude/run_bpm_r4.py (corridas; un JSON por corrida en experimentos/bpm_claude/r4_runs/).
- experimentos/bpm_claude/evaluar_bpm_r4.py (calcula todos los pass y escribe resultados_bpm_r4.json).
- experimentos/bpm_claude/resultados_bpm_r4.json (pass calculado por el codigo; incluye resumen en texto).

## 8. Lo que NO afirmo

- No afirmo nada sobre la red 3D, la escritura fs, la fabricacion ni el dispositivo.
- No afirmo nada vectorial. Es escalar paraxial. Sin datos de laboratorio. Cifras de un modelo sin calibrar.
- No se afirma causa si ningun criterio de causa se cumple. Solo se dice lo que se midio.
