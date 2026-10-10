# CONTRATO r2: cierre del solver 2D escalar (Tarea A2, LP01 de la fibra de salto)

Hora de escritura: 2026-10-10 04:55 UTC. Plazo de entrega: 06:00 UTC.
Repositorio: D:/PROJECTS/.cognition/audit/silice-origin-main (rama auditoria-20261009). Carpeta: experimentos/solver2d_claude/.
Naturaleza: MODELO NUMERICO escalar. No es un dispositivo ni una medida. CPU solo (OMP_NUM_THREADS=1, python -B). Ninguna cifra es un dato de laboratorio.

## 0. Transparencia antes de fijar este contrato

- El log parcial de la ronda 1 (log_run.txt, hasta A1_sub_L40_h0.125) era visible antes de escribir r2. Solo contenia n_eff de subpixel a h = 0,5; 0,25; 0,125 con L = 40 y los valores analiticos. No se ha cambiado ningun umbral tras ver resultados. La ronda 1 no genero resultados.json.
- Conflicto de umbral detectado: el brief de la ronda 2 pide orden entre 1,8 y 2,2 en AMBOS pares, mientras que el CONTRATO-solver2d.md (r1) fija C1.3 solo como orden (0,25 -> 0,125) >= 1,8, sin cota superior ni criterio para (0,5 -> 0,25). Ambas versiones se evaluan (ver C1.3 y C1.3b).
- Consulta a JEV (provenance=jev, status=connected, modelo jev-1.13.0), agrupada en dos preguntas:
  - q_umbral_orden: respuesta A (confianza 0,95). Criterio vinculante = C1.3 de r1. La banda [1,8; 2,2] en ambos pares se publica como criterio adicional, etiquetado como procedente del brief.
  - q_alcance_A4: respuesta B (confianza 0,18, baja). Intentar A4 con h = 0,125 solo si la RAM libre es >= 4 GB al empezar y la hora UTC es anterior a 05:20. Si no se cumple, se declara limite. A4 con h = 0,125 no es criterio vinculante.

## 1. Hipotesis (heredadas de r1, sin cambio)

- H1. El solver FD escalar (Laplaciano de 5 puntos, Dirichlet, promediado subpixel de n^2) converge al n_eff analitico del LP01 con orden observado >= 1,8.
- H2. El promediado subpixel reduce el error a h = 0,125 um por debajo del error del escalonado de referencia (4,2164e-6 en experimentos/vectorial_claude/fd_escalar_convergencia.json).
- H3. El observable de potencia en el nucleo con cobertura subpixel reproduce la fraccion analitica (Gamma = 0,890419692) con error relativo <= 1e-3 a h = 0,125 um.
- H4 (informativa). Dos nucleos a +-8 um dan kappa_FD = k0 (n_par - n_impar)/2 positivo y con paridad correcta. Solo se informa.

## 2. Modelo y metodo (fijado; identico a r1)

- Unidades um. lam = 1,55; k0 = 2 pi / lam. Fibra de salto: a = 6, n1 = 1,444, n2 = 1,439. V = 2,9201606467.
- Ecuacion: (d2/dx2 + d2/dy2 + k0^2 n^2) psi = beta^2 psi; n_eff = beta/k0.
- Malla: N = 2 round(L/h) + 1 nodos por eje, incluidos los contornos; Dirichlet psi = 0 en el contorno. Incognitas (N-2)^2.
- Solver: solve(shapes, n_bg, lam_um, L_um, h_um, n_modes=1, s_sub=8, index_fn=None) de solver2d.py, sin cambios. eigsh shift-invert, sigma = k0^2 max(cell_n2), which = 'LM'.
- Subpixel: s = 8. Escalonado: s = 1.
- Analitica LP01 (escalar exacta para n por tramos): U J1(U) K0(W) = W K1(W) J0(U), U^2 + W^2 = V^2; n_eff = sqrt(k0^2 n1^2 - U^2/a^2)/k0; Gamma en forma cerrada y por quad.
- Observable: Gamma_h = sum cov_ij |psi_ij|^2 / sum |psi_ij|^2, con cov_ij la fraccion de celda dentro de r < a (s = 8). Control Gamma_obs(psi analitica en nodos) aisla el error del observable.
- Dominio: L = 40 para A1, A2 y A3. L = 30 para reproducir la referencia. L = 50 para el control de dominio. L = 80 para A4.

## 3. Criterios y umbrales (fijados AHORA)

Los umbrales marcados "(r1)" son los de CONTRATO-solver2d.md, sin cambio.

A1 (LP01 frente a analitica):
- C1.1 (r1): |n_eff_sub(0,125) - n_eff_ana| <= 4,2164103664e-6 (error escalonado de referencia).
- C1.2 (r1, estricto): |n_eff_sub(0,125) - n_eff_ana| <= 1,0e-6.
- C1.3 (r1, VINCULANTE): orden p_sub(0,25 -> 0,125) >= 1,8.
- C1.3b (brief de la ronda 2, ADICIONAL): orden p_sub en [1,8; 2,2] para AMBOS pares (0,5 -> 0,25) y (0,25 -> 0,125). Se publica, no sustituye a C1.3.
- C1.4 (r1): orden escalonado L = 40 (0,25 -> 0,125) en [1,2; 1,6].
- C1.5 (r1, validacion del codigo): max_h |n_eff_stair(L = 30, h) - n_eff_ref(h)| <= 1e-9, h en {0,5; 0,25; 0,125}.
- C1.6 (r1, dominio): |n_eff(L = 40, h = 0,25) - n_eff(L = 50, h = 0,25)| <= 1e-7.
- C1.7 (r1, analitica): |n_eff_ana - 1,4421921654570133| <= 1e-12.

A2 (normalizacion, simetria, forma del modo; L = 40, h = 0,125, subpixel):
- C2.1 (r1): |sum |psi|^2 h^2 - 1| <= 1e-10.
- C2.2 (r1): max|psi(x,y) - psi(-x,y)| / max|psi| <= 1e-6.
- C2.3 (r1): max|psi(x,y) - psi(x,-y)| / max|psi| <= 1e-6.
- C2.4 (r1): max|psi| en el contorno = 0.
- C2.5 (nuevo en r2, diagnostico de LP01): min(psi) / max(psi) >= -1e-9. El modo fundamental no tiene cambios de signo.

A3 (observable de potencia en el nucleo; L = 40):
- C3.1 (r1): |Gamma_cerrada - Gamma_quad| / Gamma_quad <= 1e-8.
- C3.2 (r1, criterio principal, h = 0,125): |Gamma_FD - Gamma_exacta| / Gamma_exacta <= 1e-3.
- C3.3 (r1): orden del error relativo (0,25 -> 0,125) >= 1,5. Evaluable solo si ambos errores > 1e-9. Si no, no evaluable.

A4 (dos nucleos a +-8 um, d = 16 um, L = 80; h = 0,5 y 0,25 vinculantes):
- C4.1 (r1), por h: n_par - n_impar > 0.
- C4.2 (r1), por h: asimetria del modo par bajo x -> -x <= 1e-5 y del impar (psi(x,y) + psi(-x,y)) <= 1e-5, relativas a max|psi|.
- Informativos sin umbral: kappa_FD(h) = k0 (n_par - n_impar)/2 para h = 0,5 y 0,25; kappa(0,25) - kappa(0,5).
- Opcional (no vinculante): A4 con h = 0,125 solo si RAM libre >= 4 GB al empezar y hora UTC < 05:20. Si no se ejecuta, se declara limite. No cambia el estado "done".

## 4. Verificacion previa

- Analitica: C1.7 y C3.1 (forma cerrada frente a quad).
- Convergencia: ordenes de C1.3 y C1.4.
- Reproduccion de la referencia escalonada: C1.5.
- Control de dominio: C1.6.

## 5. Estado y pass

- pass = true/false lo calcula run_tareas_r2.py con los umbrales de la seccion 3. No se editan a mano.
- Estado "done" solo si todos los criterios vinculantes y adicionales se evaluaron. "partial" si falta alguno. "blocked" si depende de algo externo. Un criterio que no se cumple no baja el estado a "partial".
- Lo calculado se separa de lo supuesto en resultados_solver2d.json (seccion "supuestos").

## 6. Lo que NO afirmo

- No afirmo nada vectorial: no hay TE/TM, birrefringencia ni contraste con delta n = -0,003 (eso es T6).
- No afirmo que kappa_FD coincida con ningun modelo de acoplo ni con ninguna medida.
- No afirmo convergencia para L -> infinito mas alla de C1.6.
- No afirmo que el promediado subpixel sea optimo.
- No afirmo kappa a h = 0,125 si la ejecucion opcional no se hace.
- No afirmo nada sobre fabricacion, el dispositivo fs ni la red 3D.
- No copio ni consulto codigo de src/silice/, tests/ ni scripts/.

## 7. Entregables

- CONTRATO-solver2d-r2.md (este archivo).
- run_tareas_r2.py (ejecuta A1 a A4, evalua los criterios y escribe resultados_solver2d.json con pass calculado por el codigo).
- resultados_solver2d.json y log_run_r2.txt.
- solver2d.py y analitico_lp01.py sin cambios.
- Salidas solo en D: (esta carpeta). Sin git add, commit ni push.
- RESULTADOS-solver2d.md no se escribe: la regla de la sesion prohibe informes .md, asi que el resumen va en la respuesta estructurada final.
