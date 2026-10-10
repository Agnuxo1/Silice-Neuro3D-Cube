# VERIFICACION V6: A2 (solver2d, ronda 2) y C2 (radial2, ronda 2)

Verificador independiente y adversarial. Fecha 2026-10-10, 05:45 UTC. Todo es modelo numerico escalar/paraxial: no hay medida ni dispositivo.
Solo CPU, OMP_NUM_THREADS=1, python -B, numpy/scipy. No se ha modificado nada de solver2d_claude/ ni radial2_claude/ (comprobado: sin archivos nuevos ni pycache; SHA de los JSON intactos).
Scripts propios (todos en esta carpeta): v6_fd_propio.py, v6_cmt_a4.py, v6_radial_analitico.py, v6_radial_c1_trace.py, v6_radial_orden.py, v6_radial_balance.py, v6_cmp_radial_rep.py. Reejecuciones en v6_rep/.

## 1. Orden temporal contrato frente a resultados (ls -l --time-style=full-iso, hora local +0200)

| Tarea | Contrato r2 | Script | Resultados | Veredicto |
|---|---|---|---|---|
| A2 solver2d | 06:55:32 (04:55:32 UTC) | run_tareas_r2.py 06:56:27 | resultados_solver2d.json 07:00:08 (log: inicio 04:56:47 UTC) | PASA: contrato anterior |
| C2 radial2 | 06:57:28 (04:57:28 UTC) | run_radial2_r2.py 06:58:40 | resultados_radial2.json 07:11:37 | PASA: contrato anterior |

- Los SHA-256 de ambos contratos grabados en resultados_radial2.json coinciden con los ficheros actuales: el contrato no se tocó tras los resultados.
- Observaciones de transparencia: (a) el contrato C2-r2 declara hora 04:59 UTC pero el fichero tiene mtime 04:57:28 UTC (declaracion de hora inexacta, sin efecto). (b) diag_t12_r2.py y diag_t12_r2b.py (mtime 06:53) son anteriores al contrato r2: el diagnostico y el cambio de metodo de busqueda (continuacion en t) se hicieron viendo los resultados de ronda 1; el contrato lo declara. (c) Los umbrales r2 coinciden uno a uno con r1 en ambos contratos (revisado a mano y en el codigo).

## 2. Reejecucion del script principal

- A2: copia de run_tareas_r2.py + solver2d.py + analitico_lp01.py en v6_rep/solver2d_claude/. Resultado: todas las cifras numericas identicas bit a bit al JSON original (diferencia maxima 0, salvo el campo RAM libre/hora del A4 opcional). 19/20 criterios pass, 1 fail (C1.3b), estado done. PASA.
- C2: copia de radial2.py + run_radial2.py + run_radial2_r2.py en v6_rep/radial2_claude/. Diferencia relativa maxima 0 en todo el JSON, criterios_r2 identicos, status done (436 s). PASA.
- Una reejecucion bit a bit confirma determinismo, no correccion; la correccion se comprueba en las secciones 3 y 4 con codigo propio.

## 3. A2 (solver2d): criterios y evidencia propia

Codigo propio (v6_fd_propio.py): FD 5 puntos con promediado subpixel s x s, dominio completo y tambien cuadrante par-par con Neumann en los ejes; analitica con brentq sobre n_eff y Gamma por trapecio fino. No importa nada de solver2d_claude.

Analitica: n_eff = 1.4421921654570122 (propio) frente a ...0125 (entregado) y ...0133 (referencia C1.7): diferencias 3e-16 y 1.1e-15. U = 1.7568771017101, W = 2.3325353270696, una sola raiz. Gamma propio (trapecio) 0.8904196921597 frente a cerrada 0.890419692206 (diferencia 5e-11, error del trapecio).

n_eff subpixel s = 8, L = 40 (propio, dominio completo): 1.442191174270039 (h = 0,5), 1.4421918718380073 (0,25), 1.4421922393959987 (0,125). Coinciden con lo entregado a 1e-15. Error con signo: -9.9119e-7, -2.9362e-7, +7.3939e-8.

| Criterio | Estado | Evidencia |
|---|---|---|
| C1.1 error h=0,125 <= 4,2164e-6 | PASA | 7.3939e-8 (propio y reejecucion) |
| C1.2 <= 1e-6 | PASA | 7.3939e-8 |
| C1.3 orden (0,25 -> 0,125) >= 1,8 (vinculante r1) | PASA formal, con salvedad grave | Propio: log2(2.9362e-7/7.3939e-8) = 1.9895. Ver 3.1 |
| C1.3b orden en [1,8; 2,2] en ambos pares (brief, adicional) | FALLA | Par (0,5 -> 0,25): log2(9.9119e-7/2.9362e-7) = 1.7552 < 1,8. Confirmado |
| C1.4 orden escalonado L=40 en [1,2; 1,6] | PASA | 1.3575 (reproducido con `<=` en el borde, ver 3.2) |
| C1.5 reproduccion escalonado L=30 vs JSON | PASA, pero circular | Diferencia 0,0 exacta: el mismo algoritmo reproduce su propia referencia. Mi codigo con `<=` reproduce 1.442163197970607 / ...178063 / ...466474 (las referencias) al digito |
| C1.6 dominio L=40 vs L=50 | PASA | 1.3e-15 (reejecucion). Propio: L=30 frente a L=40 a h=0,125: 3.9e-12 |
| C1.7 analitica vs 1.4421921654570133 | PASA | 8.9e-16 entregado; 1.1e-15 propio |
| C2.1 normalizacion | PASA, tautologico | 2.2e-16; el solver normaliza por construccion |
| C2.2 / C2.3 simetria x / y | PASA | 9.5e-15 / 1.5e-14 (informativo de verdad: no son por construccion) |
| C2.4 contorno = 0 | PASA, tautologico | Dirichlet por construccion |
| C2.5 min/max >= -1e-9 | PASA, casi tautologico | -0,0; el modo se normaliza con maximo positivo y el contorno es 0 |
| C3.1 Gamma cerrada vs quad | PASA | 1.2e-16 entregado; mi trapecio concuerda a 5e-11 |
| C3.2 error rel. Gamma <= 1e-3 | PASA | 7.2748e-6 entregado; 7.2747e-6 propio (mismo Gamma_FD 0.8904132146064) |
| C3.3 orden Gamma (0,25 -> 0,125) >= 1,5 | PASA formal, con salvedad | 3.76. Ver 3.1 |
| C4.1 n_par - n_impar > 0 (h = 0,5 y 0,25) | PASA | 1.0049e-4 y 1.0022e-4 (reejecucion identica). No reimplementado A4 con FD propio |
| C4.2 paridad <= 1e-5 | PASA | 2e-14 y 9e-14 (reejecucion) |
| A4 opcional h=0,125 | NO COMPROBABLE (no ejecutado) | RAM libre 2,4 GB < 4 GB y hora > 05:20 UTC al lanzar. Limite declarado, no vinculante. En mi reejecucion (05:27 UTC, RAM 4,2 GB) tampoco se ejecuta por la hora |

Chequeo cruzado de kappa (informativo, v6_cmt_a4.py): modos acoplados con el campo LP01 analitico da kappa = 2.0295e-4 1/um frente a kappa_FD = 2.0314e-4 (h = 0,25) y 2.0368e-4 (h = 0,5): acuerdo 0,09 % y 0,36 %. No hay error de unidades ni de normalizacion en A4. (CMT es de primer orden; esto no valida el nucleo de acoplo del dispositivo.)

### 3.1 Hallazgo principal: el orden 1,99 de C1.3 no es un orden asintotico

- El error con signo de s = 8 cambia de signo entre h = 0,25 y 0,125: -9.91e-7, -2.94e-7, +7.39e-8. El contrato calcula el orden con |error|; con signo la razon no existe. La razon de diferencias sucesivas de n_eff (6.98e-7 / 3.68e-7) da orden 0,92, no 2.
- Al refinar con mi codigo (s = 8, L = 30): h = 0,0625 da error +8.54e-9. Orden (0,125 -> 0,0625) = 3,11, fuera de la banda [1,8; 2,2].
- Con cobertura casi exacta (s = 32) el error es monotono, del mismo signo y de orden 2: -1.397e-6, -3.370e-7, -6.518e-8, -1.781e-8, ordenes 2,05; 2,37; 1,87. Es decir, el solver FD converge a orden ~2, pero el 1,99 entregado con s = 8 sale de un cruce por cero (el sesgo del muestreo s = 8 compensa el error de truncado), no de una convergencia limpia.
- Mismo problema en Gamma: error relativo 4.0e-4, 9.9e-5, 7.3e-6, 2.9e-6 (L = 30 para el ultimo): ordenes 2,02; 3,76; 1,35. El 3,76 de C3.3 es transitorio; el siguiente paso da 1,35 < 1,5. Ademas el error de Gamma_FD (7.3e-6) es menor que el del observable solo (2.5e-5): hay cancelacion de errores de signo opuesto.
- Consecuencia: C1.3 y C3.3 son pass=true segun la formula del contrato (y la formula esta bien evaluada), pero H1 (orden >= 1,8) y la convergencia del observable no estan demostradas con s = 8 y tres mallas. La cifra de error absoluto a h = 0,125 (7.4e-8) si es correcta.

### 3.2 Otros riesgos de A2 no cubiertos por los criterios

- El escalonado de referencia (4.2164e-6) depende de la convencion en el borde: con r <= a (entregado) 4.2164e-6; con r < a (mi primera version) 4.9060e-6 (cuatro nodos exactamente sobre r = 6). El umbral C1.1 no se ve afectado (7.4e-8 << ambos), pero la cifra "H2: subpixel mejora al escalonado" mezcla una convencion arbitraria. C1.4 sigue dentro de [1,2; 1,6] con ambas (1.36 y 1.46).
- El texto de la seccion 3 del contrato r1 justifica L = 30 y 40 con amplitud en el contorno de 0,7 % y 0,09 %. Con el dominio [-L, L] real del solver, psi(borde)/psi(0) = 1.5e-5 (L = 30) y 2.7e-7 (L = 40); los valores citados corresponden a L = 15 y 20. Error de documentacion; no afecta a criterios (C1.6 mide el efecto real: 1e-15).
- L es semianchura (dominio [-L, L]^2), no anchura total: aclararlo al citar "L = 40".
- Un solo valor de s (8). No se ha demostrado que s = 8 sea suficiente para el orden (ver 3.1).

## 4. C2 (radial2): criterios y evidencia propia

Codigo propio (v6_radial_analitico.py): dispersion analitica por Bessel del mismo modelo paraxial (nucleo J0(kc r), trinchera A I0 + B K0, exterior H1_0 saliente), raiz por Newton, y conteo de raices por principio del argumento. No usa RK4, ni disparo, ni ECS.

| Caso (a = 6 um) | g radial2 (1/m) | g analitico propio (1/m) | dif. rel. Re / Im | perdida analitica (dB/cm) | ECS nominal (Re, Im, perdida) |
|---|---|---|---|---|---|
| t=6, dn=-0,003 | -6138.63596 + 208.69821j | -6138.63596 + 208.69821j | 5e-15 / 5e-13 | 18.1275 | -6140.99, 208.48, 18.1087 |
| t=12, dn=-0,003 | -6144.77048 + 8.58701j | -6144.77048 + 8.58701j | 7e-15 / 1e-12 | 0.74587 | -6138.10, 8.557, 0.7432 |
| t=6, dn=-0,005 | -7312.65022 + 52.50619j | -7312.65022 + 52.50619j | 9e-15 / 1e-12 | 4.5607 | -7299.70, 51.662, 4.4873 |
| t=12, dn=-0,005 | -7327.47444 + 0.49900j | -7327.47444 + 0.49900j | 4e-15 / 3e-12 | 0.043343 | -7315.74, 0.5095, 0.04425 |

- La rama de continuacion t = 7..11 tambien coincide con la analitica (Re 4e-15 a 8e-15, Im 5e-13 a 2.6e-12).
- Unicidad: el principio del argumento (400000 puntos, fase resuelta) da exactamente 1 raiz en la ventana Re g en [k0 dn, -1], Im g en [-100, 600] para los cuatro casos. Esto cubre el limite "la continuacion no garantiza unicidad" declarado en el contrato (M-c) para l = 0 en esa ventana.
- Balance de energia independiente: 2 Im g * Int|psi|^2 r dr = (b/b0) Im(psi* psi')(b) se cumple a 1e-13 con flujo saliente positivo. Convencion de signo (decaimiento <=> Im g > 0) y conversion 2 Im g * 4,343e-2 dB/cm correctas. No hay error de unidades (g en 1/m, K0 = 4,054e6 1/m).
- Fraccion de potencia en el nucleo (hasta b) 0.8027, 0.8025, 0.8884, 0.8906: concuerda con la de radial2. La ECS la define distinto (0.52 a 0.89); no son comparables.

| Criterio | Estado | Evidencia |
|---|---|---|
| C1.1 error modelo E <= 1e-8 | PASA | Raices cerradas propias (V = 2.2651; 2.9252; 4.1405) coinciden con las del JSON a 1e-15; error E <= 1e-11 |
| C1.2 error P <= 0,01 Delta | PASA | 0,058 %, 0,083 % / 0,104 %, 0,117 % / 0,223 % de Delta (LP01 / LP11) |
| C1.3 sin LP11 bajo corte | PASA | Delta = 0,003: V = 2.265 < 2.405, ninguna raiz LP11 (propio) |
| C1.4 numero de raices | PASA | Mis conteos: (1,0), (1,1), (2,1) = JSON |
| C2.1 Re g dentro de 0,5 % | PASA | 0,038 %; 0,109 %; 0,177 %; 0,160 % frente a ECS |
| C2.2 perdida dentro de max(10 %, 0,005 dB/cm) | PASA | Desv. frente a ECS 0,10 %; 0,35 %; 1,6 %; 2,1 % de la perdida exacta |
| C2.3 validez (residuo, Im g >= 0, ventana, nucleo >= 0,3) | PASA | rF <= 4e-13; Im g > 0; Re g dentro de (k0 dn, 0); nucleo 0.80 a 0.89 |
| C3.1 paso (h/2 vs h/4) | PASA | 4e-14 relativo (saturado) |
| C3.2 orden >= 3,5 o saturado | PASA solo por saturacion | El orden medido en h0 es 0,51; la pasa la rama "saturado". Prueba propia a pasos gruesos (trinchera t = 12, dn = -0,003): orden 3,93 (0,2 -> 0,1 um) y 5,13 (0,1 -> 0,05 um), consistente con RK4. Nota: radial2 limita el paso a r/40 (h_eff = min(h, r/40)), asi que h >= 0,2 um no cambia nada |
| C3.3 radio de arranque 0,02 vs 0,01 um | PASA | 1.5e-16; propio: variacion de g con r0 de 0,005 a 0,04 um < 1e-12 relativo |
| C3.4 residuo | PASA | rF <= 4e-13 |
| C3 en C1 Delta=0,010 (E y P) | PASA por saturacion | Orden -inf / None; las 3 cifras iguales a 1e-15. No demuestra orden, solo ausencia de dependencia en h |

### 4.1 Riesgos de C2 no cubiertos por los criterios

- radial2 es la solucion exacta del modelo (dispersion de Bessel, 1e-14), asi que lo que C2 mide en realidad es el error de ECS: 0,04 a 0,18 % en Re g (hasta 12 1/m) y 0,1 a 2,1 % en Im g. Pasa los umbrales porque son holgados, no porque ECS sea de referencia. Otras configuraciones de ECS en glass006a (p. ej. t=6, dn=-0,003, config A: Re g = -6143.26) se separan de la exacta mas que la nominal.
- La tolerancia de perdida en el caso t=12, dn=-0,005 la fija el suelo absoluto 0,005 dB/cm (11 % del valor), no el 10 %.
- Casos secundarios (a = 6 con t = 3, 9, 18; a = 10 um) no se repiten en r2: sin verificacion. El caso t = 3 no tiene modo cuasi-ligado en ECS.
- Todo el modelo es paraxial escalar con perfil ideal: la perdida es prediccion del modelo, no medida. La rama de salida H1 con Re k >= 0 se verifica por balance de energia, pero es una hipotesis comun a los dos metodos (no independiente) desde el punto de vista de la fisica del modelo.
- Los pasos t = 7..11 de la traza no entran en criterios (t = 12 si) y la malla gruesa de ronda 1 solo los reencuentra en 5 de 12 pasos (t = 7..10 para dn = -0,003 y t = 7 para dn = -0,005): el metodo de escaneo de ronda 1 sigue sin resolver las resonancias estrechas; la continuacion lo sustituye con exito (verificado en 4.).
- No verificado: coincidencia de C1 para l = 1 con modos LP12 y superiores, ni el modelo vectorial.

## 5. Resumen

- Todas las cifras entregadas se reproducen (bit a bit en la reejecucion; independientemente con codigo propio a 1e-15 para n_eff FD y a 1e-14 para g radial).
- Conteo: A2 19 de 20 criterios pass (1 fallo real y publicado, C1.3b); ningun pass calculado es erroneo segun la formula del contrato.
- Los puntos debiles no son de calculo sino de interpretacion: orden C1.3 y C3.3 transitorios (3.1), C3.2 por saturacion, C1.5 circular, C2 mide el error de ECS.
