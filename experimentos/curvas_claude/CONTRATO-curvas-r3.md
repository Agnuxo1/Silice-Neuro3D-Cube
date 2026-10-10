# CONTRATO-curvas-r3: seguimiento del modo de nucleo por continuacion en R (Tarea I3)

Hora de escritura: 2026-10-10 07:17 UTC (antes de ejecutar ningun calculo de la ronda 3). Hora limite de entrega: 08:20 UTC (entrega parcial si no llega).
Repositorio: D:/PROJECTS/.cognition/audit/silice-origin-main (rama auditoria-20261009). Carpeta: experimentos/curvas_claude/.
Naturaleza: MODELO NUMERICO. No es un dispositivo, no es una medida. Ninguna cifra de aqui es dato de laboratorio.
Los umbrales de la ronda 1 (CONTRATO-curvas.md, C0-C9) y de la ronda 2 (CONTRATO-curvas-r2.md, I2.0-I2.4) se mantienen y se citan como tales; no se mueven.

## 0. Estado previo (verificado en ficheros, no cambia umbrales)

- Ronda 2 (RESULTADOS-curvas-r2.md): I2.0 PASS; I2.1 FAIL; I2.2 FAIL; I2.3 y I2.4 no evaluados.
- Ronda 2, R = 50 mm: n_eff = 1,442194819527 en L = 40, 60, 80, 100 (S = 0,9988). Converge.
- Ronda 2, R = 20 mm: converge entre L = 40, 60 y 80 (diferencias < 1e-11, S = 0,9924). A L = 100 el nucleo no aparece entre los 40 modos (S = 0). El valor 1,443552 de L = 100 es espurio. La ronda 2 no puede usarlo.
- Ronda 2, R = 10 mm: nucleo en L = 40 (n_eff = 1,442266248, S = 0,969) y L = 60 (diferencia 6e-8 frente a L = 40). A L = 80 y 100 el nucleo no aparece entre los 40 modos.
- Causa identificada en la ronda 2: eigsh con sigma fijo en el maximo de n^2 devuelve los modos mas altos de la caja, que a L grande son estados exteriores espurios. La ronda 3 sigue el modo por solape con el paso anterior, no por cercania a un sigma fijo.

## 1. Hipotesis

- H-I3a. Para R en {10, 20, 50} mm, el modo de nucleo seguido por continuacion converge en L: |n_eff(L = 100) - n_eff(L = 80)| < 1e-6 a h = 0,25, con solape con el modo recto > 0,9 en ambos L.
- H-I3b (informativa). Al bajar R, n_eff crece en el modelo de indice equivalente. El contrato de la ronda 1 (C2) esperaba lo contrario: n_eff decreciente al bajar R (n(50) > n(20) > n(10) > n(5)). Se contrasta tal cual.
- H-I3c. Existe un radio critico R_c en [10; 50] mm definido por P_out = 1 % a L = 100, y queda establecido segun la regla de I3.3.

## 2. Modelo y metodo (fijados ahora)

- Modelo identico a la ronda 2: lam = 1,55 um; k0 = 2 pi / lam; a = 6 um; n1 = 1,444; n2 = 1,439; s_sub = 8.
- Indice curvado: n_eq(X, Y) = n_xy(X, Y) (1 + X/R), X hacia el exterior. Paso 0 = recto (n_xy).
- Cadena de radios en el orden de continuacion: R = 50, 30, 20, 15, 10 mm. Los radios 30 y 15 mm se anaden para cubrir la regla de I3.3 (R >= R_c); no tienen criterio propio en I3.1.
- Semidimension L en {40, 60, 80, 100} um. Malla h = 0,25 um para todos los L. N = 2 round(L/h) + 1; Dirichlet en el contorno (convencion de solver2d).
- h = 0,125 NO se ejecuta en esta ronda (coste y RAM libre de ~4,8 GB). Pendiente, no es criterio.
- solver2d no se modifica. Se importa solver2d.cell_average (promedio subpixel de n^2, misma convencion) y se construye el mismo operador P = Laplaciano de 5 puntos + k0^2 n^2 que solver2d.solve. solver2d.solve no admite sigma; por eso el seguimiento usa una funcion propia que llama a eigsh con sigma explicito. Esa funcion se verifica en I3.0.
- Continuacion (fijada): paso 0 = recto. Su modo es el autovalor mas cercano a la analitica de Snyder-Love (|n - n_an| <= 1e-5). Cada paso R_k usa shift-invert con sigma = (k0 n_eff,prev)^2, n_eff,prev del paso anterior, which = 'LM', n_modes = 12. Entre los 12 autovalores devueltos se elige el de mayor solape con el modo del paso anterior.
- Solape (fijado, JEV provenance=jev, confianza 0,72, respuesta S_potencia): S = (sum psi psi_ref h^2)^2. Es la definicion de la ronda 2 (potencia, equivale a |c| > 0,949 en amplitud). Se usa el mismo S en el paso de la cadena (psi_ref = modo del paso anterior) y en el solape con el recto de la misma caja (S_rec).
- Aceptacion de un paso: S_prev > 0,9. Si un paso no supera 0,9, la cadena se detiene en ese L y los R siguientes quedan sin evaluar. No se fuerza convergencia ni se reinicia con busqueda global (JEV provenance=jev, respuesta parar_cadena, confianza 0,40; decision de baja confianza, se publica asi).
- Medidas por paso: n_eff; x_t = R (n_eff/n2 - 1) en um; P_out = sum_{x > x_t} psi^2 h^2; P_core = sum_{r < a} psi^2 h^2; <x> = sum x psi^2 h^2; S_prev; S_rec; error de normalizacion |sum psi^2 h^2 - 1|; residuo relativo ||P psi - beta^2 psi|| / (|beta^2| ||psi||); simetria y; posicion del modo elegido en los 12 devueltos ordenados por cercania a sigma.

## 3. Criterios numericos (umbrales fijados AHORA)

- I3.0 (verificacion del metodo). Pass si se cumplen todos:
  (a) Operador: con sigma por defecto de solver2d (k0^2 max n^2_celda, n_modes = 12), L = 40, h = 0,5, recto: max |n_wrapper - n_solver2d| <= 1e-10 sobre los 12 autovalores.
  (b) Seleccion por sigma: L = 40, h = 0,5, recto: |n_eff(paso 0, sigma en analitica) - n_eff(solver2d, mas alto)| <= 1e-10.
  (c) Contraste independiente con la ronda 2 a L = 40, h = 0,25 (r2 usaba n_modes = 40 y sigma por defecto): |n_eff(R = 50, 20, 10) - n_eff,r2| <= 1e-9 con los valores de RESULTADOS-curvas-r2.md (1,442194819527; 1,442210322525; 1,442266248115).
  (d) Recto a h = 0,25: |n_eff,recto(L) - n_an| <= 1e-6 para L = 40, 60, 80, 100 (n_an = 1,442192165457).
  (e) Eigenpares: residuo relativo <= 1e-8 y |sum psi^2 h^2 - 1| <= 1e-10 para todos los modos seleccionados.
- I3.1 (convergencia en L, criterio principal). Para R en {10, 20, 50} mm: |n_eff(L = 100) - n_eff(L = 80)| < 1e-6 a h = 0,25, con S_rec(L = 80) > 0,9 y S_rec(L = 100) > 0,9, y cadena completa hasta ese R en ambos L. Pass por R = todas las condiciones. Pass global = los tres R cumplen. Si la cadena se detiene antes de R, ese R queda sin evaluar (pass = null); si un R evaluado falla, pass = false.
- I3.2 (informativo, pass = null). Se registra el signo de las diferencias n_eff(R_{k+1}) - n_eff(R_k) a lo largo de la cadena 50 -> 30 -> 20 -> 15 -> 10 mm, a L = 80 y L = 100. Valor observado: "crece al bajar R" si todas las diferencias son > 0; "decrece" si todas son < 0; "mixto" en otro caso; "no evaluado" si la cadena se detiene. Se compara con la expectativa de la ronda 1 (C2: decrece) sin cambiar el texto de la expectativa.
- I3.3 (radio critico). Regla fijada: R_c = cruce de P_out = 1 % a L = 100, buscando desde R = 50 hacia abajo en la cadena, primer tramo (R_{k-1}, R_k) con P_out(R_{k-1}) < 0,01 <= P_out(R_k), interpolacion log-log en R (criterio C7 de la ronda 1, umbral 1 %, citado). Pass = true solo si (i) R_c existe en [10; 50] mm y (ii) todos los puntos de la cadena con R >= R_c cumplen la prueba de convergencia de I3.1 (|Delta n| < 1e-6 y S_rec > 0,9 en L = 80 y 100, cadena completa). En cualquier otro caso, pass = false y se publica como radio critico no establecido (JEV provenance=jev, respuesta pass_false, confianza 0,38; decision de baja confianza, se publica asi).
- Informativo (fuera de criterios): valor de R_cA = A n2 / (n_eff - n2) de la ronda 1 (citado, no evaluado); n_eff en L = 40 y 60 para ver la dependencia en L de todos los radios.

## 4. Estado final (regla fijada)

- estado = "done" solo si I3.0, I3.1, I3.2 (observado) e I3.3 se han evaluado todos. "partial" si alguno queda sin evaluar (cadena detenida) o si un paso no se ejecuto.
- Cada pass sale del codigo en resultados_curvas_r3.json. El texto de este contrato no se edita tras ver resultados.

## 5. Lo que NO afirmo

- No calculo perdida por radiacion ni dB/cm. n_eff no es perdida; no comparo con Lee et al. (2021).
- El modelo de caja Dirichlet no representa radiacion. La dependencia en L mide la interaccion del nucleo con estados exteriores de la caja; no es un limite L -> infinito.
- No afirmo convergencia para L -> infinito; solo el par 80-100 de I3.1.
- Radio critico R_c: es una propiedad del modelo escalar de caja finita con la regla de I3.3, no un radio de fabricacion ni de dispositivo.
- No afirmo nada vectorial (TE/TM), acoplo, fabricacion, dispositivo fs, ni red 3D.
- No copio ni consulto codigo de src/silice/, tests/, scripts/. No toco coordinacion/ ni Docs/. No importo curvas.py para no sobrescribir su log_run.txt; sus formulas (analitica, indice, metricas) se reproducen aqui por lectura directa.

## 6. Entregables

- CONTRATO-curvas-r3.md (este fichero).
- curvas_r3.py (ejecucion, verificacion, criterios); resultados_curvas_r3.json (pass calculado por el codigo); log_curvas_r3.txt.
- RESULTADOS-curvas-r3.md (cifras, criterios, fallos publicados).
- Salidas solo en D: (esta carpeta y D:/tmp/curvas_r3). Sin git add, commit ni push. python -B, OMP_NUM_THREADS=1. Solo CPU; no se usa la GPU.
