# TAREA C, ronda 2: campaña completa del segundo solver radial (contrato r2)

Fecha de registro: 2026-10-10, UTC 04:59, ANTES de la campaña r2 (run_radial2_r2.py). Hora limite: 06:00 UTC.
Autor: subagente Claude (Haiku 5.5), carpeta experimentos/radial2_claude/. Todo es modelo numerico; no hay medida.
Referencia de umbrales: CONTRATO-RADIAL2.md (ronda 1, SHA registrado en la salida).

## 0. Estado previo (transparencia)

- La ronda 1 se ejecuto como smoke test (run_log.txt, resultados_radial2.json, 05:51 UTC). Sus cifras eran visibles
  antes de redactar este contrato. Resultado de ronda 1 en los 4 casos primarios: t=6 (dn=-0,003 y -0,005) con raiz
  encontrada; t=12 (dn=-0,003 y -0,005) con 0 raices, por lo que C2.1, C2.2 y C2.3 no son evaluables.
  Se conserva sin cambios como resultados_radial2_ronda1_smoke.json.
- Diagnostico (diag_t12_r2.py, sin usar ECS): la malla gruesa de ronda 1 tiene paso 81,6 1/m en Re g. La anchura
  de la resonancia es del orden de Im g (8,6 1/m para dn=-0,003, t=12; 0,5 1/m para dn=-0,005, t=12). La malla no
  resuelve el modo; el minimo grueso de |F| queda lejos de la raiz (|F| ~ 2,6e5 en el minimo grueso).
- Este cambio de metodo de busqueda es POSTERIOR a ver los resultados de ronda 1. Se declara aqui, no se oculta.

## 1. Umbrales: sin cambios respecto a ronda 1

Se mantienen sin modificar: C1.1 (<= 1e-8), C1.2 (<= 0,01 Delta), C1.3, C1.4; C2.1 (Re g dentro del 0,5 %),
C2.2 (perdida dentro de max(10 %, 0,005 dB/cm)), C2.3 (a: residuo rF < 1e-7; b: Im g >= 0; c: k0 dn < Re g < 0;
d: fraccion de potencia en el nucleo >= 0,3); C3.1 (paso: rel. Re entre h/2 y h/4 <= 1e-6 y Im dentro de 1e-3 max(|Im|,1)
o |Im(h/4)| < 1), C3.2 (orden >= 3,5 o diferencias en suelo numerico, rel < 1e-9), C3.3 (r0 = 0,02 frente a 0,01 um:
rel. Re <= 1e-9), C3.4 (rF < 1e-7).

## 2. Cambio de metodo de busqueda (no cambia F, condiciones de contorno, perfil ni criterios)

M-a. t = 6 um: raiz por el mismo escaneo grueso de ronda 1 (150 x 141) y secante compleja, eligiendo la raiz valida
     de mayor Re g. Sin cambio.
M-b. t = 7, 8, ..., 12 um (paso 1 um): CONTINUACION en t. Semilla = raiz del paso anterior (predictor lineal con
     los dos ultimos pasos); la secante parte de semilla y semilla + 0,3 (y + 0,3 i). Se acepta la raiz con rF < 1e-7
     y dentro de la ventana de C2.3. Las semillas proceden UNICAMENTE de resultados del propio solver (nunca de
     glass006a/ECS). Cada paso registra tambien el resultado del escaneo grueso de ronda 1 como comprobacion
     (dice si la busqueda por malla lo encontraria).
M-c. Limite declarado: la continuacion no garantiza que sea la unica raiz de t dado. Para t = 12 no hay exhaustividad
     de malla. El criterio "mayor Re g" se aplica dentro de la rama seguida. Se declara en la salida.

## 3. Campaña (primaria)

Casos: a = 6 um, t in {6, 12} um, dn in {-0,003; -0,005} (4 casos). Los casos secundarios de ronda 1 no se repiten
en r2; quedan con sus cifras de ronda 1 y sin criterio de aprobacion en r2.
Traza de continuacion t = 6..12 um para cada dn: se publica (es la evidencia de la rama).

Comprobaciones:
- C1 completo (LP01, LP11; Delta 0,003, 0,005, 0,010) como en ronda 1 (mismo codigo, mismos criterios).
- C3 en el caso a = 6, t = 12, dn = -0,003 (rama de continuacion a h0, h0/2, h0/4) y C3 de la ronda 1 para C1 Delta = 0,010.
- C3.1-C3.4 se evaluan con el codigo.

## 4. Criterios: evaluados por el codigo

pass_C2_1, pass_C2_2, pass_C2_3 por caso; agregados C2_all_primary. C1 y C3 como en ronda 1.
"done" solo si todos los criterios se evaluaron; "partial" si faltan; "blocked" si depende de algo externo.
Si un caso no es valido, se declara con la causa (no se sustituye por ECS).

## 5. Lo que NO afirmo

- No afirmo que la camisa de 6 um con trinchera sea fabricable ni que su perdida sea de una fibra real.
- No afirmo validez vectorial, birrefringencia ni curvatura. Modelo escalar paraxial radial de un perfil ideal.
- radial_ecs no es verdad de referencia: la comparacion mide acuerdo entre dos metodos del mismo modelo.
- Convencion de signo: el solver usa perdida = 2 Im g * 4,343e-2 con decaimiento <=> Im g >= 0, igual que la salida
  de glass006a (loss_dB_per_cm > 0 con gamma_im > 0). El texto de CONTRACT.md de glass006a dice "Im gamma < 0 es
  decaimiento" con A ∝ exp(i gamma z), lo cual es inconsistente con su propia convencion; no se corrige aqui.
- Cualquier cifra de perdida es prediccion del modelo, no medida.
