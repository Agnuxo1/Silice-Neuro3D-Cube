# CONTRATO-curvas-r2: convergencia de dominio de la guia curvada (Tarea I2)

Escrito antes de ejecutar ningun calculo de la ronda 2. Hora de escritura: 2026-10-10 04:55 UTC. Hora limite de entrega: 06:00 UTC (entrega parcial si no llega).
Repositorio: D:/PROJECTS/.cognition/audit/silice-origin-main (rama auditoria-20261009). Carpeta: experimentos/curvas_claude/.
Naturaleza: MODELO NUMERICO. No es un dispositivo, no es una medida. Ninguna cifra de aqui es dato de laboratorio.
Los umbrales de la ronda 1 (CONTRATO-curvas.md, seccion 3, C0-C9) se mantienen y se citan como tales; no se mueven.

## 0. Correcciones y hallazgos previos (verificados en el codigo, no cambian umbrales)

- Dominio de solver2d: N = 2 round(L/h) + 1 y x_i = (i - (N-1)/2) h. Por tanto el dominio es [-L, +L], es decir, L es la semidimension. CONTRATO-curvas.md (seccion 2) decia "dominio Dirichlet de +-20 um" para L = 40; el codigo usa +-40 um. Se corrige aqui; las cifras de la ronda 1 no cambian (eran calculadas con el codigo).
- Ronda 1, n_modes = 12 con sigma = k0^2 max(n^2_celda) (eigsh, 'LM'): el modo nucleo no aparece entre los 12 valores mas altos para R = 5 mm (S = 0; supp_r5.py con n_modes = 40 da S = 0,758, sin resolver). El barrido de radio critico de la ronda 1 para R < 7,5 mm no es valido. Esto motiva la ronda 2.
- Ronda 1, R = 10 mm: n_eff pasa de 1,442267 (L = 40) a 1,448733 (L = 80) con h = 0,5. El valor de L = 80 es un modo espurio de caja en la region exterior clasicamente permitida (x > x_t, x_t = 22,7 um para R = 10 mm). Por eso la convergencia en L hay que comprobarla explicitamente.

## 1. Hipotesis

- H-I2a. Para R en {10, 20, 50} mm, el n_eff del modo nucleo converge en L: |n_eff(L = 100) - n_eff(L = 80)| < 1e-6 a h = 0,25.
- H-I2b. Con n_modes = 40, el modo nucleo se identifica con S > 0,90 en todos los casos (R, L) de h = 0,25.
- H-I2c. Si R = 10 mm converge, n_eff(50) > n_eff(20) > n_eff(10) a L = 100 um con diferencias mayores que la incertidumbre de dominio.

## 2. Modelo y metodo (fijados ahora)

- Unidades: um. lam = 1,55; k0 = 2 pi / lam. a = 6 um, n1 = 1,444, n2 = 1,439, s_sub = 8.
- Indice curvado: n_eq(X,Y) = n_xy(X,Y) (1 + X/R), X hacia el exterior. Recto: n_xy. Mismo codigo que la ronda 1 (funcion n_eq, n_bg = n2).
- solver2d se importa desde experimentos/solver2d_claude/solver2d.py. No se copia codigo ni se modifica solver2d.
- Radios: R en {10, 20, 50} mm. R = 5 mm queda fuera de la I2.1 (no resuelto en la ronda 1).
- Semidimension L en {40, 60, 80, 100} um, malla h = 0,25 (criterio principal, todos los L).
- h = 0,125 NO es factible a L = 80 y 100 con ~4 GB de RAM libres (N = 1281 y 1601; 1,6 M y 2,6 M incognitas). Solo se ejecuta como comprobacion informativa de malla a L = 40 y 60 (fuera de criterios).
- n_modes = 40 en todos los casos (la ronda 1 usaba 12). Decision JEV Q1 (opcion A, provenance = jev, confianza 0,58).
- Modo nucleo: entre los 40 modos calculados, el de mayor solapamiento S = (sum psi psi_rec h^2)^2 con el LP01 recto de la MISMA caja, malla y n_modes. psi normalizada con sum psi^2 h^2 = 1.
- Marca de corte espectral: si el indice del modo nucleo es >= 37 (ultimos 3 de 40), el caso se marca "no fiable".
- Medidas por caso: n_eff del modo nucleo; <x> = sum x psi^2 h^2; x_t = R (n_eff/n2 - 1); P_out = sum_{x > x_t} psi^2 h^2; P_core = sum_{r<a} psi^2 h^2; S; error de normalizacion; simetria y.
- Verificacion del recto: LP01 analitico de Snyder-Love (V = 2,920161, brentq, misma formula que curvas.py). Se compara el recto a cada L y h = 0,25.
- Radio critico (I2.4): NO se evalua en esta ronda. Decision JEV Q4 (opcion C, provenance = jev, confianza 0,89): no ejecutar el barrido de radio critico en esta ronda. Queda sin establecer.

## 3. Criterios numericos (umbrales fijados AHORA)

- I2.0 (verificacion del metodo): |n_eff,recto(L, h = 0,25) - n_eff,analitica| <= 1e-6 para cada L; y |sum psi^2 h^2 - 1| <= 1e-10 para el modo nucleo de cada caso. Pass si se cumplen todos.
- I2.1 (convergencia de dominio, criterio principal, decision JEV Q3 opcion A): para cada R en {10, 20, 50} mm, |n_eff(L = 100) - n_eff(L = 80)| < 1e-6 a h = 0,25, con modo nucleo S > 0,90. Pass = los tres R cumplen. Los pares 40-60, 60-80 se publican como informacion, sin criterio. Si no converge, se dice.
- I2.2 (identificacion del modo nucleo): S > 0,90 y sin marca de corte espectral para los 12 pares (R, L) de h = 0,25. Pass = los 12 cumplen. Si alguno falla, I2.1 se publica como no evaluable para ese R (decision JEV Q5 opcion A, confianza 0,70), y no se fuerza convergencia.
- I2.3 (tendencia con incertidumbre de dominio): solo se evalua si I2.1 pasa para R = 10 mm. Incertidumbre de dominio u = max_R |n_eff(L = 100) - n_eff(L = 80)| a h = 0,25. Pass = [n_eff(50, L = 100) - n_eff(20, L = 100) > u] y [n_eff(20, L = 100) - n_eff(10, L = 100) > u]. Si no se evalua, pass = null.
- I2.4 (radio critico): NO evaluado en esta ronda (decision JEV Q4). pass = null. Los umbrales de la ronda 1 (C7: cruce de P_out = 1 %, cociente con R_c,A en [0,67; 1,5] y ambos en [2; 5] mm) quedan citados, no evaluados.
- Informativo (fuera de criterios): diferencia h = 0,25 frente a h = 0,125 a L = 40 y 60 (R = 10, 20, 50); n_eff de la ronda 1 con n_modes = 12 frente a ronda 2 con n_modes = 40 a L = 40 (consistencia).

## 4. Lo que NO afirmo

- No calculo perdida por radiacion ni dB/cm. n_eff no es perdida; no se compara con Lee et al. (2021).
- El modelo de caja Dirichlet no representa radiacion. Los estados espurios en la region exterior permitida se identifican y se publican, no se eliminan.
- No afirmo convergencia para L -> infinito; solo el par 80-100 (I2.1).
- No afirmo radio critico (I2.4 no evaluado).
- No afirmo nada vectorial (TE/TM), acoplo, fabricacion, dispositivo fs, ni red 3D.
- No copio ni consulto codigo de src/silice/, tests/, scripts/. No toco coordinacion/ ni Docs/.

## 5. Entregables

- CONTRATO-curvas-r2.md (este fichero).
- curvas_r2.py (ejecucion, criterios, analitica), resultados_curvas_r2.json (pass calculado por el codigo), log_curvas_r2.txt.
- RESULTADOS-curvas-r2.md (cifras, criterios, fallos publicados).
- Salidas solo en D: (esta carpeta y D:/tmp). Sin git add, commit ni push. python -B, OMP_NUM_THREADS=1.
