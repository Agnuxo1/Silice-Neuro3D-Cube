# CONTRATO: camisa continua frente a camisa de trazos discretos (Tarea F, modelo ideal)

Hora de escritura: 2026-10-10 04:02 UTC, antes de ejecutar ningun calculo. Plazo de entrega: 05:50 UTC.
Repositorio: D:/PROJECTS/.cognition/audit/silice-origin-main (rama auditoria-20261009). Carpeta: experimentos/tracks_claude/.
Naturaleza: MODELO NUMERICO ESCALAR IDEAL. No es un dispositivo, no es una medida, no es fabricacion. Ninguna cifra de aqui es un dato de laboratorio.
Solver: experimentos/solver2d_claude/solver2d.py (Tarea A), cargado con sys.path. Comprobacion independiente: referencia analitica radial con condicion de radiacion (seccion 3) y convergencias propias.

## 1. Hipotesis

- H1. n_eff del modo de nucleo de la camisa de trazos discretos, n_ii(N), se separa de la continua equivalente por area n_iii(N) (formula de la tarea) por una cantidad no nula que no desaparece al crecer N.
- H2. La formula de area de la tarea, f = N/48, supone que los trazos no se solapan y que la fraccion de area del anillo que ocupan es f. Esto solo es fisicamente valido para f <= 1 y sin solapes. Predigo que f_union(N) < f(N) para N >= 24 (los trazos de radio 1,5 um con separacion 2 pi 9 / N < 3 um se solapan) y que f_union satura en 0,5 (area de la banda 7,5 < r < 10,5 frente al anillo 6 < r < 12).
- H3. Con N creciente, n_ii(N) converge a la banda continua equivalente (iv): anillo 7,5 < r < 10,5 con n = 1,439 y fondo 1,444, y no a la continua (i) de anillo 6 < r < 12.
- H4. El solver 2D (cuadrado de lado L) reproduce la referencia analitica radial del caso continuo (i) en el modo de nucleo con error <= 1e-4, y el error baja al crecer L.

## 2. Geometria y casos (fijados ahora)

- lam = 1,55 um; k0 = 2 pi / lam. Nucleo y fondo: n = 1,444 (el nucleo es el propio vidrio; no hay contraste de nucleo, solo la camisa). Camisa: n = 1,439 (delta n = -0,005).
- Anillo de camisa: a < r < a + t con a = 6, t = 6, es decir 6 < r < 12. Radio medio a + t/2 = 9, radio de trazo r_t = 1,5, de modo que cada trazo ocupa 7,5 < r < 10,5 (dentro del anillo).
- Casos:
  - (i) continua: anillo 6 < r < 12 con n = 1,439.
  - (ii) trazos: N cilindros de radio 1,5 centrados en (9 cos th_k, 9 sin th_k), th_k = 2 pi k / N, k = 0..N-1, n = 1,439; fuera, n = 1,444. N en {8, 16, 24, 32, 48, 64, 96}.
  - (iii) continua equivalente por area, segun la tarea: n_eq^2 = f 1,439^2 + (1 - f) 1,444^2 con f = N pi r_t^2 / (2 pi (a + t/2) t) = N/48. Se aplica el anillo 6 < r < 12 con n_eq. Para N = 64 y 96, f > 1 y la formula no es una fraccion de volumen; se calcula igual y se marca.
  - (iv) diagnostico, limite N -> infinito de (ii): banda continua 7,5 < r < 10,5 con n = 1,439.
  - Diagnosticos sin umbral: (iii') continua con fraccion de area realmente cubierta, f_union(N) = area(union de trazos dentro del anillo) / area(anillo), n_eq'^2 = f_union 1,439^2 + (1 - f_union) 1,444^2; y fase de trazos desplazada pi/N para N = 8 y 16.
- Dominio principal: cuadrado de lado L = 40 um, Dirichlet psi = 0 en el contorno (solver de la Tarea A). Malla principal h = 0,125 um, promediado subpixel s = 8. Verificaciones: h = 0,25 y 0,5; L = 50 y 60.
- Modelo escalar (no vectorial), sin perdidas de material, sin escritura, sin rugosidad ni tension.

## 3. Metodo

- Problema de autovalores: (d2/dx2 + d2/dy2 + k0^2 n^2) psi = beta^2 psi, n_eff = beta / k0.
- Naturaleza fisica del modo (decision fijada ahora): con n_fondo = n_nucleo = 1,444 > n_eff, el exterior del anillo es radiativo. El modo de nucleo esta cuasi-ligado por la barrera de camisa (altura k0^2 (1,444^2 - 1,439^2) = 0,237 um^-2) y su energia de confinamiento queda por debajo de la barrera. Por tanto el autovalor de la caja depende de L y no es un autovalor de vidrio infinito. Se mide esa dependencia (C2, C3).
- Los autovalores de la caja incluyen modos del exterior (fondo 1,444), que tienen n_eff mas alto que el modo de nucleo. Por eso NO se toma el modo superior. Se pide el solver para K modos (K = 30 con L = 40; K = 45 con L = 50; K = 60 con L = 60) y se elige el modo de nucleo como el de mayor n_eff con potencia dentro de r <= a + t = 12 mayor o igual que 0,5. Este criterio de seleccion se aplica igual a todos los casos.
- Referencia analitica (C3): modo radial m = 0, escalar, con condicion de radiacion en el exterior. Para region interna 0 < r < r1 (indice n1), anillo r1 < r < r2 (indice n2) y exterior r > r2 (indice n0), con q = k0 sqrt(n^2 - neff^2) y p = k0 sqrt(neff^2 - n2^2):
  - interior: psi = J0(q1 r);
  - anillo: psi = A I0(p r) + B K0(p r);
  - exterior: psi = C H0^(1)(q0 r), saliente.
  Raiz compleja de F(neff) = g' H0(q0 r2) + g q0 H1(q0 r2) = 0, con g, g' el valor y la derivada de la solucion del anillo en r2 (A, B fijados por continuidad en r1 con J0). Se toma la raiz cercana al valor de la caja. Se reporta Re(neff) y Im(neff), donde Im(neff) es perdida por radiacion del modelo (no absorcion del material).
  - (i): r1 = 6, r2 = 12, n1 = n0 = 1,444, n2 = 1,439. (iii): igual con n2 = n_eq(N). (iv): r1 = 7,5, r2 = 10,5, n2 = 1,439.
- Convergencia en h (C1) y en L (C2) con el mismo solver.
- Area de union de trazos: calculo independiente por malla fina (dx = 0,01 um), comprobado con la area exacta para N = 8 y 16, donde no hay solapes (distancia entre centros 18 sin(pi/N) >= 3 um).

## 4. Criterios numericos (umbrales fijados AHORA; no se cambian despues de ver resultados)

- C1 (convergencia en h, solver): para (i), (ii, N = 8) y (ii, N = 48), |n(h = 0,25) - n(h = 0,125)| <= 1e-5 en L = 40.
  - C1b: para (i), orden observado p = log2(|n(0,5) - n(0,25)| / |n(0,25) - n(0,125)|) >= 1,5 (si ambas diferencias son > 1e-9; si no, no evaluable).
- C2 (dominio en la caja): |n(L = 50, h = 0,25) - n(L = 40, h = 0,25)| <= 1e-5 para (i) y (ii, N = 48). Umbral de sensibilidad: si falla, el valor de la caja depende de L a ese nivel y las diferencias (ii) - (iii) deben leerse con esa incertidumbre.
- C3 (analitica, i): |Re n_caja(i; L = 40, h = 0,125) - Re n_analitica(i)| <= 1e-4.
  - C3b: el error respecto a la analitica baja al crecer L: |Re n(L = 60, h = 0,25) - Re n_analitica| < |Re n(L = 40, h = 0,25) - Re n_analitica|.
- C4 (seleccion del modo de nucleo): en cada caso reportado, el modo elegido tiene P(r <= 12) >= 0,5 y su indice en la lista descendente es <= K - 5.
- C5 (geometria de trazos): f_union(8) = f(8) y f_union(16) = f(16) con error <= 1e-6 (exacto por geometria); estimador de malla: error <= 0,5 % en N = 16.
- C6 (pregunta principal, umbral de la tarea): |n_ii(N) - n_iii(N)| < 1e-5 para N = 48, 64 y 96 (criterio con N >= 48 de la tarea). Para N = 64 y 96 el valor se calcula con f > 1, que no es una fraccion de volumen; el pass se marca, pero su interpretacion fisica no es valida.
- C7 (convergencia en N hacia la banda): |n_ii(N = 96) - n_iv| <= 1e-5 (L = 40, h = 0,125).
- Sin umbral (informativo): Delta(N) = n_ii(N) - n_iii(N) para todo N; n_ii(N) - n_iii'(N); n_ii(N) - n_analitica(iii); Im(neff) analitico; P(r <= 12) del modo; tendencia de n_ii(N) con N.

## 5. Estado y reglas de publicacion

- Se publican todos los casos, incluidos los que fallen, con sus cifras. Un criterio es pass = true solo si lo evalua el codigo entregado.
- "done" solo si todos los criterios se evaluaron; "partial" si faltan (por ejemplo, por tiempo); "blocked" si el solver no funciona.
- Si el solver de la Tarea A falla, se marca blocked. Si falta tiempo, se entrega partial con lo medido.

## 6. Lo que NO afirmo

- No afirmo nada vectorial: no hay TE/TM, ni birrefringencia, ni contraste delta n = -0,003 (eso es otra tarea).
- No afirmo que la camisa continua ideal sea equivalente a una camisa discreta. El contraste mide cuanto se separan, no que coincidan.
- No afirmo fabricacion, escritura fs, rugosidad, pérdidas por cm ni ninguna medida.
- No afirmo convergencia mas alla de N = 96 ni de L = 60. No afirmo valor infinito de la caja mas alla de C3.
- No afirmo que la banda (iv) sea lo que produce el laser. Es un limite matematico del modelo.
- No copio ni consulto codigo de src/silice/, tests/ ni scripts/. No toco coordinacion/ ni Docs/. No hago git add, commit ni push. Salidas solo en D:.

## 7. Entregables

- experimentos/tracks_claude/run_tracks.py (ejecuta casos, criterios y analitica; escribe resultados.json con pass calculado por el codigo).
- experimentos/tracks_claude/resultados.json y log_run.txt.
- Este contrato, sin modificar umbrales despues de ejecutar.

## 8. Enmienda 1 (2026-10-10 04:10 UTC, antes de ejecutar los casos discretos)

Motivo: durante la comprobacion previa al calculo principal aparecieron dos problemas de metodo. Los umbrales C1 a C3, C5 a C7 y las definiciones de casos no cambian.

1. Correccion del dominio. El solver define la malla con x_i = (i - (N-1)/2) h y N = 2 round(L/h) + 1, de modo que L es el SEMILADO: la caja es [-L, L]^2, de lado 2L. La seccion 2 decia "cuadrado de lado L = 40 um", y eso es incorrecto. Las comparaciones L = 40, 50 y 60 se leen como semilados 40, 50 y 60 um (lado 80, 100 y 120 um). Esto mismo afecta a la descripcion del dominio de la Tarea A y debe revisarse alli.
2. Seleccion del modo de nucleo. Con el solver por defecto (los K autovalores mas altos), los modos del exterior (fondo 1,444) ocupan el extremo superior del espectro. Con K = 30 no aparece ningun modo con P(r <= 12) >= 0,5 (ver el primer chequeo: P_in <= 0,1 en los 30 primeros modos, y el modo de nucleo esta mas abajo). Por eso se usa shift-invert con sigma = (k0 sigma_neff)^2, donde sigma_neff = 1,44219587 es la raiz analitica del caso (i) (modo radial m = 0 con radiacion, seccion 3). Se piden k = 12 autovalores mas cercanos. El resto de la discretizacion es la de solver2d.solve.
   - El criterio C4 original (indice <= K - 5) se sustituye por: P(r <= 12) >= 0,5 y |n_eff - sigma_neff| <= 0,002 en cada corrida. Es el mismo espiritu (el modo elegido es el de nucleo y no un modo del exterior), con una ventana fijada ahora.
3. Busqueda de raices analiticas. Una primera version fallo (secante con polos espurios y malla gruesa). Se corrigio a G = det * F (sin polos) con arranques multiples de Newton. Validacion: reproduce la raiz LP01 de una fibra de salto (n1 = 1,444, n2 = 1,439, a = 6 um) en 1,4421921654570125, frente a 1,4421921654570133 de la Tarea A (diferencia 8e-16). Esta validacion se hizo antes de ver cualquier caso discreto.

Hallazgo previo (solo de la camisa continua): la raiz analitica del caso (i) es n_eff = 1,44219587 + i 1,30e-5. Es un modo cuasi-ligado de nucleo con fuga muy debil. Su parte imaginaria es perdida por radiacion del modelo, no absorcion del material. El solver de caja (L = 40, h = 0,25, sigma en la raiz) da 1,44219524 con P(r <= 12) = 0,818.
