# CONTRATO: solver 2D escalar independiente y observable de potencia en el nucleo (Tarea A)

Escrito antes de ejecutar ningun calculo. Hora de escritura: 2026-10-10 03:31 UTC. Plazo de entrega: 04:50 UTC.
Repositorio: D:/PROJECTS/.cognition/audit/silice-origin-main (rama auditoria-20261009). Carpeta: experimentos/solver2d_claude/.
Naturaleza: MODELO NUMERICO. No es un dispositivo ni una medida. Ninguna cifra de aqui es un dato de laboratorio.

## 1. Hipotesis

- H1. El solver FD escalar (Laplaciano de 5 puntos, Dirichlet, promediado subpixel de n^2) converge al n_eff analitico del LP01 de la fibra de salto con orden observado >= 1,8.
- H2. El promediado subpixel reduce el error a h = 0,125 um por debajo del error del escalonado publicado en experimentos/vectorial_claude/fd_escalar_convergencia.json (4,2164e-6).
- H3. El observable de potencia en el nucleo con cobertura subpixel reproduce la fraccion de potencia analitica con error relativo <= 1e-3 a h = 0,125 um.
- H4 (informativa). Dos nucleos a +-8 um dan un acoplo kappa_FD = k0 (n_par - n_impar)/2 con signo positivo y paridad correcta. Solo se informa.

## 2. Modelo y metodo (fijado ahora)

- Unidades: um. lam = 1,55; k0 = 2 pi/lam. Fibra de salto: a = 6, n1 = 1,444 (nucleo), n2 = 1,439 (fondo). V = k0 a sqrt(n1^2 - n2^2) = 2,92016.
- Ecuacion: (d2/dx2 + d2/dy2 + k0^2 n^2(x,y)) psi = beta^2 psi. Autovalor beta^2, n_eff = beta/k0.
- Malla: N = 2 round(L/h) + 1 nodos por eje, x_i = (i - (N-1)/2) h, incluidos los contornos. Psi = 0 en el contorno (Dirichlet). Incognitas: interiores, (N-2)^2.
- Discretizacion: P = (T (x) I + I (x) T)/h^2 + diag(k0^2 cellN2), con T = tridiagonal(1, -2, 1). Autovalores de P con eigsh en shift-invert, sigma = k0^2 max(cellN2), which = 'LM'.
- Promediado subpixel: cellN2 es la media de n^2 sobre una malla s x s de subpuntos de cada celda h x h centrada en el nodo. s = 8 es el caso subpixel. s = 1 (muestreo en el nodo) es el escalonado.
- Convencion de matrices: psi[iy, ix] (fila = y, columna = x). Normalizacion: sum |psi|^2 h^2 = 1. Signo: el maximo de |psi| es positivo.
- Solucion analitica LP01: U J1(U) K0(W) = W K1(W) J0(U), con W = sqrt(V^2 - U^2) (brentq). n_eff = sqrt(k0^2 n1^2 - U^2/a^2)/k0.
- Fraccion de potencia en el nucleo, forma cerrada: Gamma = (J0(U)^2 + J1(U)^2)/(J1(U)^2 + J0(U)^2 K1(W)^2/K0(W)^2). Se contrasta con integracion numerica (quad) de la forma analitica de psi.
- Observable FD: Gamma_h = sum_ij cov_ij |psi_ij|^2 / sum_ij |psi_ij|^2, con cov_ij la fraccion de celda dentro del nucleo r < a (muestreo subpixel s = 8). Como control de separacion: Gamma_obs(psi_analitica muestreada en nodos) aisla el error del observable del error del solver.

## 3. Dominio y casos (decisiones propias, fijadas ahora)

- Dominio principal de A1 y A3: L = 40 um. Motivo: con L = 30 el valor de psi en el contorno es ~0,7 % del maximo, y con L = 40 es ~0,09 %. Se usa la comparacion de dominio C1.6 para verificarlo.
- Reproduccion de la referencia: escalonado con L = 30 y h = 0,5; 0,25; 0,125 (mismo grid que el JSON de referencia). Criterio C1.5.
- Dominio de A4: L = 80 um (los nucleos llegan a |x| = 14 um). Se ejecutan h = 0,5 y h = 0,25. h = 0,125 (~1,6 M incognitas) no se ejecuta si la RAM libre (2,1 GB medidos a las 03:30 UTC) no alcanza. Se declara como limite.

## 4. Criterios numericos (umbrales fijados AHORA, no se cambian despues de ver resultados)

A1 (LP01 frente a analitica, L = 40, h = 0,5; 0,25; 0,125):
- C1.1: |n_eff_sub(h = 0,125) - n_eff_analitica| <= 4,2164e-6 (no peor que el escalonado de referencia).
- C1.2 (estricto): |n_eff_sub(h = 0,125) - n_eff_analitica| <= 1,0e-6.
- C1.3: orden observado p_sub = log2(e(0,25)/e(0,125)) >= 1,8.
- C1.4: orden observado p_stair = log2(e(0,25)/e(0,125)) en [1,2; 1,6] (la referencia da 1,36 con L = 30).
- C1.5 (validacion del codigo): max_h |n_eff_stair(L = 30, h) - n_eff_ref(h)| <= 1e-9 para h en {0,5; 0,25; 0,125}, con n_eff_ref del JSON de referencia.
- C1.6 (dominio): |n_eff(L = 40, h = 0,25) - n_eff(L = 50, h = 0,25)| <= 1e-7.
- C1.7 (analitica): |n_eff_analitica - 1,4421921654570133| <= 1e-12 (coherencia con la referencia del JSON).

A2 (normalizacion y simetria, L = 40, h = 0,125, subpixel):
- C2.1: |sum |psi|^2 h^2 - 1| <= 1e-10.
- C2.2: max|psi(x,y) - psi(-x,y)| / max|psi| <= 1e-6.
- C2.3: max|psi(x,y) - psi(x,-y)| / max|psi| <= 1e-6.
- C2.4: max|psi| en el contorno = 0 (exacto por construccion).

A3 (observable de potencia en el nucleo, L = 40, h = 0,125):
- C3.1: |Gamma_forma_cerrada - Gamma_quad| / Gamma_quad <= 1e-8 (coherencia analitica).
- C3.2 (criterio principal): |Gamma_h - Gamma_exacta| / Gamma_exacta <= 1e-3 a h = 0,125.
- C3.3: orden del error relativo del observable entre h = 0,25 y h = 0,125 >= 1,5. Solo se evalua si ambos errores superan 1e-9. Si no, se declara no evaluable.

A4 (dos nucleos a +-8 um, d = 16 um, L = 80, h = 0,5 y 0,25):
- C4.1: n_par - n_impar > 0 en cada h (criterio de signo).
- C4.2: paridad de los dos modos: el par cumple max|psi(x,y) - psi(-x,y)|/max|psi| <= 1e-5 y el impar cumple max|psi(x,y) + psi(-x,y)|/max|psi| <= 1e-5.
- Se informan kappa_FD(h), la diferencia kappa(0,25) - kappa(0,5) y los valores de A4 sin umbral adicional.

## 5. Lo que NO afirmo

- No afirmo nada vectorial: no hay TE/TM, ni birrefringencia, ni contraste con delta n = -0,003 (eso es T6).
- No afirmo que kappa_FD coincida con el modelo de acoplo ni con ninguna medida. Esa comparacion la hace otro agente.
- No afirmo convergencia para L -> infinito mas alla de la comparacion C1.6 (L = 40 frente a L = 50).
- No afirmo que el promediado subpixel sea optimo. Solo que se compara con el escalonado en el mismo grid.
- No afirmo kappa a h = 0,125 si no se ejecuta.
- No afirmo nada sobre fabricacion, el dispositivo fs ni la red 3D.
- No copio ni consulto codigo de src/silice/, tests/ ni scripts/. La comprobacion es independiente.

## 6. Entregables

- solver2d.py (interfaz fija: solve(shapes, n_bg, lam_um, L_um, h_um, n_modes=1, s_sub=8, index_fn=None)).
- analitico_lp01.py (U, W, n_eff, Gamma en forma cerrada y por quad).
- run_tareas.py (ejecuta A1 a A4, evalua los criterios y escribe resultados.json con pass = true/false calculado por el codigo).
- resultados.json y log_run.txt.
- Las salidas van solo a D: (esta carpeta). Sin git add, commit ni push.
