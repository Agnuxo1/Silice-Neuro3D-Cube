# CONTRATO-curvas-r4: signo del desplazamiento de n_eff y radio critico por continuacion (Tarea I4)

Hora de escritura: 2026-10-10 10:02 UTC (antes de ejecutar ningun calculo de la ronda 4). Hora limite de entrega: 10:30 UTC (entrega parcial si no llega).
Repositorio: D:/PROJECTS/.cognition/audit/silice-origin-main (rama auditoria-20261009). Carpeta: experimentos/curvas_claude/.
Naturaleza: MODELO NUMERICO. No es un dispositivo ni una medida. Ninguna cifra es dato de laboratorio.
Umbrales de rondas anteriores que se mantienen y se citan: C0-C9 (CONTRATO-curvas.md), I2.0-I2.4 (CONTRATO-curvas-r2.md), I3.0-I3.3 (CONTRATO-curvas-r3.md). No se mueven.

## 0. Estado previo (verificado en ficheros)

- Ronda 3 (RESULTADOS-curvas-r3.md): cadena 50, 30, 20, 15, 10 mm con n_eff del nucleo; I3.0 PASS, I3.1 PASS (3/3), I3.2 observado "crece al bajar R" en L = 40, 60, 80, 100, I3.3 FALSE (sin cruce de P_out = 1 % en [10; 50] mm).
- Ronda 3, recto: n_eff = 1,442191871838; R = 50, 20, 10 mm a L = 80: 1,442194819527; 1,442210322528; 1,442266315212.
- Ronda 3 no guardo los campos psi: esta ronda recalcula la cadena desde el recto (no se reutilizan ficheros de r3 como entrada; solo se leen sus n_eff de L = 40 para el contraste I4.0a).

## 1. Hipotesis

- H-I4a (signo, analitica). Con n_eq = n_xy (1 + X/R) y el nucleo centrado (simetria X -> -X), el termino de primer orden en 1/R de n_eff es nulo; el primer termino no nulo es O(1/R^2) y tiene signo positivo: delta(n_eff^2) = lambda^2 [<D2> + S2] / k0^2 con <D2> > 0 y S2 >= 0 (suma sobre estados excitados con mu0 - mu_m > 0). Por tanto n_eff crece al bajar R, con pendiente logaritmica -2 en R.
- H-I4b (radio critico, sin prejuicio). El modo de nucleo se separa del recto al bajar R; el radio donde su solape con el recto cae por debajo de 0,9 se llama R_c(S). Se estima por log-log entre dos radios consecutivos de la cadena.
- Se contrasta la expectativa de la ronda 1 (C2: n_eff decreciente al bajar R) solo como registro; ya se sabe que no se cumple (I3.2).

## 2. Modelo y metodo (fijados ahora)

- Modelo identico a r3: lam = 1,55 um; k0 = 2 pi / lam; a = 6 um; n1 = 1,444; n2 = 1,439; s_sub = 8; h = 0,25 um; n_modes = 12; L en {40, 80, 100} um (L = 60 no se ejecuta en esta ronda).
- Indice curvado: n_eq(X,Y) = n_xy(X,Y)(1 + X/R), R en um (R = mm x 1000), X hacia el exterior. Paso 0 = recto.
- Cadena de radios (fijada): R = 50, 20, 10, 7, 5, 4, 3, 2,5, 2 mm (descendente). Se detiene en el primer paso con S_prev <= 0,9 (modo perdido por continuacion) o al llegar a 2 mm.
- Seguimiento: shift-invert con sigma = (k0 n_eff,prev)^2, which = LM, k = 12; se elige el modo con mayor solape S_prev = (sum psi psi_prev h^2)^2 con el modo del paso anterior. S_rec = solape con el recto de la misma caja. Mismas definiciones que r3.
- Verificacion de la perturbacion (I4.0b y I4.1): con el recto a L = 40, P0 = operador P = nabla^2 + k0^2 n^2 (misma convencion que r3). Desarrollo exacto del operador en lambda = 1/R: P(lambda) = P0 + lambda D1 + lambda^2 D2 con D1 = 2 k0^2 cavg(n^2 X), D2 = k0^2 cavg(n^2 X^2) (cavg = promedio subpixel de solver2d, misma convencion). Coeficiente de segundo orden: <D1> = u0.D1.u0; S2 = g^T chi con g = D1 u0 proyectado fuera de u0, chi = (mu0 I - P0)^{-1} g en el complemento, resuelto con sistema bordeado; c2 = (<D2> + S2)/(2 k0^2 n_eff0) en um^2; prediccion Delta n(R) = c2 / R_um^2.
- Se reproduce r3 a L = 40 (R = 50, 20, 10) para contrastar el metodo.
- h = 0,125 no se ejecuta (coste; ya se registro como pendiente).
- Restricciones: solo CPU, python -B, OMP_NUM_THREADS=1, sin instalar nada. curvas_r3.py no se importa (abre y sobrescribe log_curvas_r3.txt); sus funciones se copian aqui.

## 3. Criterios numericos (umbrales fijados AHORA)

- I4.0 (verificacion). Pass si se cumplen todos:
  (a) L = 40: |n_eff(R = 50, 20, 10) - n_eff(r3, ckpt_curvas_r3_L40.json)| <= 1e-10 y recto igual dentro de 1e-10.
  (b) Coeficiente de perturbacion a L = 40: |Delta n_num(R = 10 mm) / (c2 / R_um^2) - 1| <= 0,02 (2 %). Umbral fijado ahora; r3 ya mostro que Delta n R^2 varia 1 % entre R = 50 y R = 10 mm.
  (c) Eigenpares de todos los modos seleccionados (L = 40, 80, 100): residuo relativo <= 1e-8 y |sum psi^2 h^2 - 1| <= 1e-10.
- I4.1 (signo y pendiente de n_eff - n_recto con R). Pass si se cumplen todos:
  (i) Delta n_eff = n_eff(R) - n_eff(recto) > 0 en todos los puntos de la cadena evaluados, a L = 40, 80 y 100.
  (ii) <D1> (primer orden) con |<D1>| <= 1e-10 (simetria) y c2 > 0 (ambos terminos de segundo orden positivos).
  (iii) Pendiente logaritmica d ln(Delta n)/d ln(R) entre R = 50 y R = 10 mm a L = 100 en [-2,05; -1,95].
- I4.2 (radio critico por solape, L = 100 como criterio principal; L = 80 para la convergencia). Regla fijada:
  R_a = mayor R de la cadena con S_rec(L = 100) > 0,9; R_b = siguiente punto de la cadena con S_rec <= 0,9 o paso fallido (S_prev <= 0,9). R_c(S) = interpolacion log-log de S_rec = 0,9 entre R_a y R_b; si el paso fallido impide S_rec en R_b, R_c queda acotado en [R_b; R_a] y se publica como cota, sin interpolar.
  Pass = true solo si: (i) R_c existe en [2; 50] mm (cruce o cota) y (ii) todos los puntos de la cadena con R >= R_a cumplen |n(L = 100) - n(L = 80)| < 1e-6 y S_rec > 0,9 en ambos L. En otro caso pass = false (radio critico no establecido). Si la cadena no alcanza R_a en ambos L, pass = null.
- I4.3 (perdida por radiacion). No se calcula. pass = null. Se dice asi en el texto.
- Informativo (fuera de criterio): R_x = a / (n_eff / n2 - 1) (radio en que la posicion de retorno x_t iguala el radio del nucleo a = 6 um) y R_cA = A n2 / (n_eff - n2) (ronda 1), sin evaluar.

## 4. Estado final (regla fijada)

- estado = "done" solo si I4.0, I4.1 e I4.2 tienen pass true o false (no null). "partial" si alguno queda null o si la cadena no llega a R = 2 mm en L = 80 o 100 (entonces se publica el ultimo R evaluado).
- Cada pass sale del codigo en resultados_curvas_r4.json. Este texto no se edita tras ver resultados.

## 5. Lo que NO afirmo

- No calculo perdida por radiacion ni dB/cm. n_eff no es perdida. No comparo con Lee et al. (2021).
- La caja de Dirichlet no representa radiacion ni un limite L -> infinito. La convergencia se prueba solo en el par 80-100 y solo como en I3.1.
- R_c(S) es propiedad del modelo escalar de caja finita con esta regla. No es un radio de fabricacion ni de dispositivo.
- Nada vectorial (TE/TM), acoplo, fabricacion, dispositivo fs, ni red 3D.
- No copio ni consulto codigo de src/silice/, tests/, scripts/. No toco coordinacion/ ni Docs/. No hago git add, commit ni push.

## 6. Entregables

- CONTRATO-curvas-r4.md (este fichero); curvas_r4.py; resultados_curvas_r4.json (pass por codigo); log_curvas_r4.txt; ckpt_curvas_r4_L{40,80,100}.json; RESULTADOS-curvas-r4.md.
- Salidas solo en D: (esta carpeta). Tiempo de calculo estimado: L = 100 unos 10 min.
