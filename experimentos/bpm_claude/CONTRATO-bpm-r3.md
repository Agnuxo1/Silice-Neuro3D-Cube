# CONTRATO-bpm-r3 - prueba de la hipotesis del dato inicial (B3) y, condicionado, G3

Fecha de escritura: 2026-10-10, 07:20 UTC (antes de cualquier calculo de la ronda 3).
Agente: Claude (subagente), carpeta experimentos/bpm_claude/.
Naturaleza: modelo numerico escalar paraxial. No es un dispositivo ni una medida. Sin datos de laboratorio.
Restricciones: solo CPU, OMP_NUM_THREADS=1, python -B, sin instalar nada, salidas y temporales en D:.
Escritura solo en experimentos/bpm_claude/. No se toca src/silice/, tests/, scripts/, coordinacion/ ni Docs/.
No se hace git add, commit ni push.

## 0. Contexto heredado (no se cambia)

- Ronda 1, B3: perdida del modo guiado a 1 mm = 2,460e-4 con h = 0,2 um, dz = 1 um, CAP activo (W = 40, s0 = 28, w = 12, G0 = 0,5 um^-1).
  Umbral de B3: 1e-5. FALLO. Se publica asi.
- Ronda 2 (datos ya existentes en r2_runs/ antes de este contrato, se citan y NO se rehacen):
  - r2_runs/disc.json: dato discreto = autovector Lanczos de -(lap espectral + V_real) en la misma malla
    (W = 40, h = 0,2). Perdida a 1 mm = 2,4596e-4. Es decir, el dato discreto espectral ya no cambio la perdida.
  - r2_runs/base.json: 2,4600e-4 (control de la ronda 2).
  - r2_runs/dz05.json: dz = 0,5 con dato analitico, perdida 7,369e-5 (la perdida depende de dz).
  - resultados_bpm_r2.json quedo en estado parcial (escrito a las 06:57, antes de que terminaran las corridas).
    Sus campos nulos NO se usan aqui. Las cifras de r2 se toman de r2_runs/*.json.
- El umbral 1e-5 de B3 NO se cambia en esta ronda.

## 1. Hipotesis de esta ronda (fijada ahora)

- H-DATO (ronda 3): la perdida viene de que el dato inicial LP01 muestreado no es el modo discreto del esquema.
  Prueba de esta ronda: E0 = modo guiado discreto obtenido con OTRO discretizado, solver2d (diferencias finitas de
  5 puntos, Dirichlet, misma malla h = 0,2 um, ventana L = 40 um, indice promediado 16 x 16 subceldas, n_ref = n1).
  Esta construccion es distinta del Lanczos espectral de la ronda 2, asi que es una segunda prueba independiente
  del dato discreto.
  - Si H-DATO es cierta: P_perd(1 mm) con E0 discreto <= 1e-5.
  - Si no: se dice que no es cierta, con la cifra.
- Diseno elegido por JEV (router.py jev, provenance=jev, opcion A, confianza 0,97): E0 discreto por solver2d + control
  analitico + diagnostico dz = 0,5, sin repetir Lanczos. Segunda opinion: no justificada (valor 0,54, no concluyente).
  Complejidad 3,05 (Complex). Consulta registrada en D:/tmp/jev_bpm_r3/.
- Hipotesis secundaria (diagnostica, no decide B3): la perdida depende de dz (ronda 2: 2,46e-4 con dz = 1 y 7,37e-5 con dz = 0,5)
  y es un error de particion (split-step) y no del dato. Se mide con la prueba D1-dz y R1 de abajo.

## 2. Modelo y metodo

- Mismo modelo que la ronda 2: 2 i k0 n_ref dA/dz = lap A + k0^2 (n^2 - n_ref^2) A - i Gamma A, n_ref = n1 = 1,444,
  split-step de Strang, CAP Gamma = 2 k0 n_ref R0 t^2, t = clip((s - s0)/w, 0, 1), s = max(|x|, |y|).
  lambda = 1,55 um, nucleo radio a = 6 um, n1 = 1,444, n2 = 1,439. Malla N = 401, h = 0,2 um.
- Propagador: bpm_r2.py de esta carpeta (propio; no se modifica). bpm.py de la ronda 1 no se toca.
- E0 analitico: LP01 muestreado (bpm_r2.lp01_analytic), como en la ronda 1.
- E0 discreto (esta ronda): solver2d.solve(shapes = [disco r = 6, n = n1], n_bg = n2, lam = 1,55, L = 40, h = 0,2, s_sub = 16).
  El mismo solver2d es el de experimentos/solver2d_claude/solver2d.py (solo lectura; su sha256 se registra en el JSON).
  Convencion: solver2d psi[iy, ix] -> BPM psi[ix, iy] (transposicion, como en la ronda 2).
- Verificacion del dato discreto: se compara con el autovector Lanczos espectral de la ronda 2 (bpm_r2.discrete_ground_state)
  solo como control de solape; no se usa como E0 de B3.
- Propagacion: dz = 1 um (B3) y dz = 0,5 um (diagnostico), hasta z = 1000 um.
- Diagnosticos a 1 mm. Perdida P_perd = 1 - P(1 mm)/P(0), P = sum |A|^2 h^2.
  Para el sin-CAP (R0 = 0): unitariedad max_z |P(z)/P(0) - 1|.
  Radiacion: fraccion de potencia en s > 28 um en 1 mm sin CAP, P(s > 28)/P(0).

## 3. Corridas (todas hasta 1 mm)

- an_cap_dz1: E0 analitico, CAP base, dz = 1. CONTROL de B3 (reproduce ronda 2).
- fd_cap_dz1: E0 discreto solver2d, CAP base, dz = 1. PRUEBA DE B3 (criterio de pass).
- an_cap_dz05: E0 analitico, CAP base, dz = 0,5. Control del diagnostico dz.
- fd_cap_dz05: E0 discreto solver2d, CAP base, dz = 0,5. Diagnostico dz.
- an_sin_dz1: E0 analitico, R0 = 0 (sin CAP), dz = 1. Unitariedad y radiacion.
- fd_sin_dz1: E0 discreto solver2d, R0 = 0 (sin CAP), dz = 1. Unitariedad y radiacion.

## 4. Criterios numericos r3 (umbrales fijados AHORA)

Verificacion (sin umbral de ciencia; condicion previa para creer las cifras):

- N1 (modo discreto es un modo guiado): |n_eff,solver2d - 1,4421922| <= 1e-5.
  (n_eff,solver2d = la salida neff de solver2d; referencia analitica 1,4421921655.)
- O1 (solape con el LP01 analitico): |<psi_FD | LP01>|^2 / (<psi_FD|psi_FD> <LP01|LP01>) >= 0,999.
- V1 (unitariedad sin CAP, dato discreto, 1 mm): max_z |P(z)/P(0) - 1| <= 1e-9 en fd_sin_dz1.
- V2 (reproduce el control): |P_perd(an_cap_dz1) - 2,4600e-4| / 2,4600e-4 <= 1e-3.

Prueba principal (criterio de pass, umbral de la ronda 1 sin cambio):

- B3-r3: P_perd(fd_cap_dz1, 1 mm) <= 1e-5. pass = la hipotesis H-DATO se sostiene para esta construccion del dato.

Clasificacion (no es pass, se reporta):

- H1 (el dato no cambia la perdida): |P_perd(fd_cap_dz1) - P_perd(an_cap_dz1)| / P_perd(an_cap_dz1) <= 0,10.
  Si H1 se cumple y B3-r3 no, la perdida no viene del dato (H-DATO refutada en esta construccion).
  Si H1 no se cumple y B3-r3 no, el dato influye pero no basta.

Diagnosticos (pass calculado, no decide B3-r3):

- D1-dz (dependencia en dz con dato discreto): |P_perd(fd_cap_dz05) - P_perd(fd_cap_dz1)| / P_perd(fd_cap_dz1) <= 0,10.
  pass = la perdida no depende de dz (si falla, la perdida depende de la particion temporal).
- R1 (radiacion sin CAP): |P(s>28)/P0 (fd_sin_dz1) - P(s>28)/P0 (an_sin_dz1)| / P(s>28)/P0 (an_sin_dz1) <= 0,10.
  pass = la radiacion sin CAP no depende del dato inicial.

## 5. G3 (condicionado)

- G3 solo se ejecuta si B3-r3 pasa (P_perd <= 1e-5 con E0 discreto). Si B3-r3 no pasa, G3 queda como
  "no ejecutado: condicion no cumplida" y no se calcula.
- Si se ejecutara, seguira el contrato G3 de la ronda 2 (dos nucleos a +-d/2, d = 14 y 16 um, L_c = pi/(2 kappa_FD),
  criterio 10 %).

## 6. Estado final

- "done" solo si todos los criterios de las secciones 4 y 5 se evaluaron por codigo.
- "partial" si falta alguno (por ejemplo, si una corrida no termina a tiempo).
- Un criterio que falla se publica como fallo. Nada se reescribe despues de ver las cifras.

## 7. Salidas

- experimentos/bpm_claude/CONTRATO-bpm-r3.md (este archivo).
- experimentos/bpm_claude/run_b3_r3.py (corridas; un JSON por corrida en experimentos/bpm_claude/r3_runs/).
- experimentos/bpm_claude/evaluar_bpm_r3.py (calcula todos los pass y escribe resultados_bpm_r3.json y RESULTADOS-bpm-r3.md).
- experimentos/bpm_claude/resultados_bpm_r3.json (pass calculado por el codigo).
- experimentos/bpm_claude/RESULTADOS-bpm-r3.md (texto generado a partir de los JSON).

## 8. Lo que NO afirmo

- No afirmo nada sobre la red 3D, la escritura fs, la fabricacion ni el dispositivo.
- No afirmo nada vectorial. Es escalar paraxial.
- No hay datos de laboratorio. Las cifras son de un modelo sin calibrar.
- No se afirma la causa de la perdida si ningun criterio de causa se cumple. Solo se dice lo que se midio.
- No se usa el autovector Lanczos de la ronda 2 como E0 del criterio B3-r3. Es solo control de solape.
- El autovector "del propio esquema" (Strang de un paso) no se calcula en esta ronda, por el plazo de las 08:20 UTC.
  Queda pendiente.
