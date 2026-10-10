# CONTRATO-bpm-r2 - diagnostico de la perdida del modo guiado (B2) y G3

Fecha de escritura: 2026-10-10, 04:54 UTC (antes de cualquier calculo de la ronda 2).
Agente: Claude (subagente), carpeta experimentos/bpm_claude/.
Naturaleza: modelo numerico escalar paraxial. No es un dispositivo ni una medida.
Restricciones: solo CPU, OMP_NUM_THREADS=1, python -B, sin instalar nada, salidas en D:.

## 0. Contexto de la ronda 1 (no se cambia)

- B3 de la ronda 1: perdida del modo guiado a 1 mm, h = 0,2 um, dz = 1 um, CAP activo = 2,460e-4.
  Umbral de la ronda 1: 1e-5. FALLO. Se publica asi.
- Diagnostico de la ronda 1 (diagnostico_perdida_bpm.json): sin CAP ya hay 1,30e-4 de potencia en s > 28 um a 1 mm.
  La perdida con CAP crece de forma aproximadamente lineal en z (8,6e-6 a 50 um; 2,46e-4 a 1 mm).
- El umbral 1e-5 de B3 NO se cambia en esta ronda.

## 1. Hipotesis (a contrastar)

- Referencia fisica: el LP01 de la fibra de salto (V = 2,92 > 0) es un estado ligado de la ecuacion paraxial
  continua; su perdida por radiacion es cero. Por tanto, cualquier perdida distinta de cero es numerica.
- H-CAP: la perdida la genera el CAP (su amplitud G0, su posicion s0 o su ancho). Predice dependencia fuerte con G0 o con s0.
- H-CONTORNO: la perdida la genera la ventana periodica (la radiacion que sale por un borde vuelve por el otro y se absorbe).
  Predice dependencia con el semiancho W de la ventana (la perdida baja al alejar el CAP).
- H-DATO: la perdida la genera el dato inicial. El LP01 muestreado no es autoestado del operador discreto
  y excita radiacion. Predice que el dato autoestado discreto reduce la perdida hasta <= 1e-5.
- H-DZ: la perdida la genera el error de separacion (dz). Predice dependencia con dz.
- H-h: la perdida depende de h (ya observada: 4,92e-4 con h = 0,1 um; no es convergente en h en la ronda 1).

## 2. Modelo y metodo (ronda 2)

- Mismo modelo que la ronda 1: ecuacion 2 i k0 n_ref dA/dz = lap A + k0^2 (n^2 - n_ref^2) A, n_ref = n1 = 1,444,
  split-step de Strang, CAP en la forma Gamma = G0 t^2, t = clip((s - s0)/w, 0, 1), s = max(|x|, |y|).
  Ventana cuadrada de semilado W, N = 2 M + 1 nodos con h = W/M (h = 0,2 um), indice por celda (16 x 16 subceldas).
- Implementacion propia nueva para esta ronda (bpm_r2.py): los parametros W, s0, w, G0, dz y el dato inicial son argumentos.
  No se modifica bpm.py. No se copia codigo de src/silice/.
- Dato inicial "analitico" (LP01 muestreado, como en la ronda 1).
- Dato inicial "discreto": autoestado del operador -(lap_spectral + V_real) con V_real = k0^2 (n^2 - n_ref^2) de malla
  W = 40 um, h = 0,2 um, obtenido con Lanczos (scipy.sparse.linalg.eigsh) sobre el operador FFT. Se toma el autovector
  de menor autovalor (es el modo guiado). Se reporta su n_eff discreto y su diferencia con el analitico.
- Diagnosticos a 1 mm. Perdida = 1 - P(1 mm)/P(0), P = sum |A|^2 h^2.

## 3. Barrido (B2.1) y configuraciones

Corridas (todas a 1 mm):
- R-base: W = 40, s0 = 28, w = 12, G0 = 0,5 um^-1, dato analitico, dz = 1, h = 0,2 (ya conocida: 2,460e-4).
- R-G0: W = 40, s0 = 28, w = 12, G0 = 0,05 um^-1. (amplitud del CAP)
- R-s0: W = 40, s0 = 34, w = 6, G0 = 0,5 um^-1. (inicio y ancho del CAP)
- R-W60: W = 60, s0 = 48, w = 12, G0 = 0,5 um^-1. (contorno, CAP en la misma posicion relativa al borde)
- R-W60c: W = 60, s0 = 28, w = 12, G0 = 0,5 um^-1. (contorno, CAP en la misma posicion absoluta)
- R-W80: W = 80, s0 = 68, w = 12, G0 = 0,5 um^-1. (contorno; N = 801)
- R-disc: W = 40, s0 = 28, w = 12, G0 = 0,5 um^-1, dato discreto. (H-DATO)
- R-dz05: W = 40, s0 = 28, w = 12, G0 = 0,5 um^-1, dz = 0,5 um, dato analitico. (H-DZ)

## 4. Criterios numericos r2 (umbrales fijados AHORA)

- D1 (H-CONTORNO): |P_perd(W = 80) - P_perd(W = 60)| / P_perd(W = 80) <= 0,10 con CAP en la misma posicion relativa (R-W60, R-W80).
  pass = la perdida es estable al crecer la ventana (no depende del contorno). Si D1 falla, el contorno contribuye.
- D2 (H-CAP amplitud): |P_perd(R-G0) - P_perd(R-base)| / P_perd(R-base) <= 0,10.
  pass = la perdida no depende de G0 (no es absorcion del CAP). Si D2 falla, el CAP contribuye.
- D3 (H-CAP posicion): |P_perd(R-s0) - P_perd(R-base)| / P_perd(R-base) <= 0,10.
- D4 (H-DZ): |P_perd(R-dz05) - P_perd(R-base)| / P_perd(R-base) <= 0,10.
- D5 (H-DATO): P_perd(R-disc) <= 1e-5.
- D6 (verificacion del autoestado discreto): |n_eff,disc - n_eff,analitico| <= 1e-5 (n_eff,disc = n_ref + lambda/(2 k0^2 n_ref), con lambda el autovalor
  mas alto de (lap + V_real) en la malla de W = 40 um; la referencia analitica es 1,4421922).
- B2.2 (B3 repetido con el umbral de la ronda 1): se toma la configuracion seleccionada por la regla R y se evalua
  P_perd(1 mm) <= 1e-5. pass o no pass, tal cual.
- Regla R (fijada ahora, provisional, solo para elegir la configuracion de B2.2 y de G3; no cambia el umbral 1e-5):
  (i) si D5 pasa, la configuracion seleccionada es R-disc (dato discreto, W = 40);
  (ii) si no, y D1 pasa, es R-W80 (W = 80, CAP con la misma posicion relativa);
  (iii) si no, es R-base. B2.2 se evalua en la configuracion seleccionada. Si ninguna pasa 1e-5, B2.2 = no pass.
- Clasificacion de la hipotesis: H-CAP si D2 o D3 fallan; H-CONTORNO si D1 falla; H-DATO si D5 pasa; H-DZ si D4 falla.

## 5. G3 (longitud de transferencia) - dos nucleos

- Nucleos (disco de radio a = 6 um, n1 = 1,444, fondo n2 = 1,439) en x = -d/2 y x = +d/2, d en {14, 16} um.
- E0 = modo de un nucleo en x = -d/2 con solver2d (experimentos/solver2d_claude/solver2d.py, n_bg = n2),
  muestreado en la malla BPM de la configuracion validada (h = 0,2 um).
- psi_R = modo de un nucleo en x = +d/2 (solver2d). P2(z) = |<psi_R|A(z)>|^2 / (<psi_R|psi_R> <A0|A0>), A0 = E0.
- L_c = pi/(2 kappa_FD) con kappa_FD = 0,47164 mm^-1 (d = 14) y 0,20305 mm^-1 (d = 16), de
  experimentos/acoplador_claude/resultados_g1_g2.json (campo kappa_FD_per_um, 4,716394e-4 y 2,030540e-4 um^-1).
  L_c(14) = 3,3323 mm; L_c(16) = 7,7451 mm.
- Primer maximo local de P2(z) para z > 0 (interpolado parabolicamente).
- G3 criterio: |z_max - L_c| / L_c <= 0,10 para cada d. pass por d; pass global = ambos.
- Si la configuracion validada no alcanza el tiempo para propagar hasta 1,1 L_c, se reporta como pendiente, no se inventa.

## 6. Salidas

- experimentos/bpm_claude/bpm_r2.py (propagador parametrico propio).
- experimentos/bpm_claude/run_b2_r2.py (barrido B2.1 y B2.2; un JSON por corrida en experimentos/bpm_claude/r2_runs/).
- experimentos/bpm_claude/run_g3_r2.py (G3; un JSON por d).
- experimentos/bpm_claude/evaluar_bpm_r2.py (calcula todos los pass y escribe resultados_bpm_r2.json).
- experimentos/bpm_claude/resultados_bpm_r2.json (pass calculado por el codigo).
- experimentos/bpm_claude/RESULTADOS-bpm-r2.md (texto a partir de los JSON).

## 7. Lo que NO afirmo

- No afirmo nada sobre la red 3D, la escritura fs, la fabricacion ni el dispositivo.
- No afirmo nada vectorial. Es escalar paraxial.
- No hay datos de laboratorio. Las cifras son de un modelo sin calibrar.
- Si el criterio de la regla R no se cumple, no se afirma que la perdida sea cero.
- No se consulta a JEV (router.py) en esta subtarea: las decisiones de barrido siguen el contrato del orquestador.
