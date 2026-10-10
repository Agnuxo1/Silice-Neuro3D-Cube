# VERIFICACION-V4 - F (tracks), H (observable), I (curvas), K (registro)

Verificador independiente y adversarial. Contrato propio: `CONTRATO-V4.md` (escrito antes de mis calculos de tabla; el unico calculo previo fue una integral angular de f_union, ver nota). Cabecera horaria: inicio 2026-10-10 04:11 UTC, cierre 04:38 UTC (plazo 06:20 UTC). Solo CPU, `python -B`, OMP_NUM_THREADS=1, numpy/scipy. Mi codigo es propio (`v4_*.py` en esta carpeta); no importe `solver2d.py` ni `src/silice`. De los grupos solo importe `kappa` de `acoplo_paralelo.py` (K lo hace igual) y lei `adi2d.py` solo para entender la convencion del observable. No modifique nada de los grupos.

Nota de honestidad: antes de escribir mi contrato lance una integral angular de f_union (`v4_f_union.py`) y la lei; su resultado no determino ningun umbral de este contrato. El run de F seguia ejecutandose cuando empece (terminó 04:29:15 UTC con `status=partial`); verifique sobre el JSON final.

## 1. Preregistro (mtime, UTC = hora de fichero - 2 h)

| Grupo | Contrato | Primer codigo/resultado | Veredicto |
|---|---|---|---|
| F | `CONTRATO-camisa-trazos.md` 04:09:44 | `run_tracks.py` 04:09:15 (anterior a la ultima edicion del contrato), run 04:09:45 | PASA con reservas: el contrato se edito despues del script y 1 s antes de la ejecucion; incluye la Enmienda 1 (cambio de dominio y sustitucion del criterio C4) escrita tras un primer chequeo que vio `P_in<=0,1` en 30 modos. Umbrales C1..C3, C5..C7 del codigo == contrato. El mtime solo prueba la ultima edicion. |
| H | `CONTRATO-OBSERVABLE-COBERTURA.md` 04:00:07 | `observable_cobertura.py` 04:00:46, `h2_guia_salto.py` 04:02:04 | PASA. Umbrales G0/G1/G3 del codigo == contrato. La robustez "no gate" de H2 se anadio tras la primera pasada (declarado en el script). |
| I | `CONTRATO-curvas.md` 04:02:25 | `curvas.py` 04:03:48, resultados 04:09:11 | PASA para C0..C9 (umbrales del codigo == contrato). `supp_r5.py` (04:04:26) y `check_variacional.py` (04:06:16) nacieron durante el run principal, tras ver R=5 mm con S=0; el contrato NO se enmendo (la "Enmienda A1" solo existe en el docstring de `supp_r5.py`). Marcados como informativos. |
| K | `CONTRATO-REGISTRO.md` 04:04:13 | `registro_k.py` 04:04:57, resultados 04:08:24 | PASA. Umbrales V-K*/K* del codigo == contrato (E-1, E-2 incluidas en el contrato). `verif_generador/verif_mc_convergencia` (04:09-04:10) son posteriores y con criterio propio. |

## 2. F (tracks): camisa continua frente a trazos

Estado de F verificado en `tracks_claude/resultados.json`: `status = partial`. Pasan C1_i (2,1e-7), C2_i (1,8e-6), C3 (4,2e-7), C5a, C5b (5,4e-5). Fallan C1b_i (p = -0,11), C3b (6,3e-7 -> 6,8e-6), C4. No evaluables (`evaluable=false`, `pass=false`): C1_ii_N8, C1_ii_N48, C2_ii_N48, C6_N48/64/96, C7. De las 40 corridas, solo (i), (iii, N=48) y (iii, N=64) encuentran modo de nucleo; los 16 casos (ii) y (iv) devuelven `n_core = None`.

Re-ejecuciones mias:

- VF1 geometria (integracion angular exacta, distinta de la malla fina de F): f_union(N) = 0,16667; 0,33334; 0,44141; 0,46871; 0,48651; 0,49249; 0,49670 para N = 8, 16, 24, 32, 48, 64, 96. Diferencia maxima con F: 3e-5 (<= 2e-4). PASA. Otros N: 12 -> 0,25000; 20 -> 0,40913; 40 -> 0,48038; 72 -> 0,49409; 128 -> 0,49816; 256 -> 0,49958 (monotona, tiende a 0,5). N = 1024 da 0,50017: FALLA mi criterio `<= 0,500`; es error de mi cuadratura (singularidad de raiz en el borde del anillo), no del limite, que es 0,5 exacto. Confirma H2 de F: f_union < f_formula para N >= 24 y saturacion en 0,5.
- Raices analiticas (disparo ODE complejo + condicion de Hankel saliente, metodo distinto de la forma cerrada de F): (i) 1,44219587036024 + i1,30414e-5; (iv) 1,44273267702966 + i6,85705e-5; (iii, N = 24/48/64) idem. Diferencia con F <= 2,2e-16 en Re y 5e-18 en Im. CONFIRMADO.
- Reproduccion de (i) con mi FD (L = 40, h = 0,25, s = 4): n = 1,4421958 frente a 1,4421952 de F: dif 5,9e-7 (<= 1e-6). PASA.
- Hallazgo central. El `n_core = None` de F es un artefacto de seleccion, no de la fisica: F fija el desplazamiento shift-invert en la raiz de (i) (1,442196) y pide k = 12 autovalores, que cubren solo 1,4421-1,4424; los modos de nucleo de (iv) y de los trazos estan en torno a 1,4427. Con shift 1,4425-1,4427 y k = 60 (L = 40) aparece un modo de nucleo claro (P(r<=12) = 0,70-0,77) en todos los casos:

| Caso | n (h = 0,25) | n (h = 0,125) | n - n_iv (h = 0,125) |
|---|---|---|---|
| (i) | 1,4421958 | 1,4421954 | |
| (iv) banda | 1,4427293 | 1,4427294 | 0 |
| (ii) N = 24 | 1,4427646 | 1,4427649 | +3,55e-5 |
| (ii) N = 48 | 1,4427379 | 1,4427380 | +8,6e-6 |
| (ii) N = 96 | 1,4427317 | 1,4427315 | +2,1e-6 |
| (ii) N = 192 | 1,4427297 | 1,4427299 | +5,5e-7 |

  Consecuencias que F no recoge porque no las evalua: H3 (convergencia a la banda (iv)) se cumple con diferencia que cae ~ 1/N^2 y C7 (|n_ii(96) - n_iv| <= 1e-5) habria PASADO con 2,1e-6 (L = 30: 2,5e-6; L = 50: 1,8e-6); C6 (|n_ii - n_iii| < 1e-5) habria FALLADO por tres ordenes de magnitud: n_ii(48) - n_iii(48) = 1,442738 - 1,442196 = 5,4e-4 (con N = 64, 96 las analiticas de (iii) 1,44204 y 1,44184 dan 7e-4 y 9e-4). Es decir, la hipotesis H1 de F (la continua por area NO es equivalente) esta respaldada, pero fuera de los criterios de F.
- Dependencia del dominio (riesgo): el pico de nucleo se mueve con L por hibridacion con estados de caja: (i) 1,4421943 (L = 30), 1,4421958 (40), 1,4421940 (50), 1,4421895 (60, reparte el peso en dos modos, W 0,53/0,37); (iv)/(ii) pasan de 1,44277 (L = 30) a 1,44271 (L = 50). El cierre de C3 (4e-7) es en parte casual; el error a L = 60 (6,8e-6) lo muestra. Las diferencias entre casos a igual L son robustas (picos paralelos); los valores absolutos de la caja no se pueden comparar con la raiz analitica por debajo de ~1e-5.
- VF2 con mi criterio de centroide (peso W >= 0,02) no discrimina (el centroide queda en ~1,4422-1,4425 por modos del continuo con peso pequeno); lo declaro: FALLA como metrica, y uso el pico (no preregistrado, post hoc). Con el centroide, la tendencia ii(N) -> iv tambien se cumple (|ii_96 - iv| = 2e-6 < |ii_24 - iv| = 1,2e-5 a h = 0,25).
- C5a de F es una identidad algebraica (N pi r_t^2 / area del anillo == N/48): pasa por construccion; la prueba informativa es la grilla (C5b) y mi integral angular.

Veredicto F: sus cifras publicadas son correctas y honestas (`partial`), pero 8 de los criterios quedaron sin evaluar por una eleccion de metodo evitable; evaluados bien, C6 FALLA y C7 PASA.

## 3. H (observable por cobertura)

- VH1: LP01 y Gamma con brentq y cuadratura propias: Gamma_mia == Gamma_H (diferencia 0,0). Cobertura propia por integral exacta en las celdas de frontera (400 lineas). Orden por minimos cuadrados de |O_w - Gamma|: 2,029 (h = 0,4..0,05); 2,010 (mallas no conmensurables 6/17,3..6/138,4); 2,069 (8 mallas no conmensurables). H da 2,033. PASA ([1,8; 2,3]). Errores: h = 0,05 -> -8,5e-6 (H: -8,3e-6).
- VH2: `H1_G3_PASS = false` (1,38e-4 > 1e-4), declarado en el JSON de H. CONFIRMADO que H no lo da por cumplido.
- VH3: el orden del indicador en el centro no es 1 de forma robusta: H da 0,97; yo obtengo 1,51; 1,71; 1,67 en tres series. Cambia de signo entre mallas. La hipotesis "H-A: O(h)" no queda establecida (H tampoco la usa como gate).
- Q2/Q3/Q4 desde los campos guardados (no repropague): con mi cobertura exacta, P(0,4; 0,5; 0,625) = 0,363178; 0,363082; 0,363428 (Cd) y 0,332671; 0,332230; 0,332640 (T96d). Dif con P64 de H <= 7,1e-6. Veredictos identicos: Q2 y Q3 cumplen, Q4 continuo cumple, Q4 de 96 trazos NO cumple (4,10e-4 < 4,41e-4) con cualquier observable de area. CONFIRMADO.
- Hallazgo: el observable original (indicador en el centro) a dx = 0,4 um depende del redondeo en los nodos que caen justo sobre r = a (a/dx = 15 exacto, 12 nodos con i^2 + j^2 = 225). En SI (como `adi2d.core_fraction`) cuenta 705 nodos; en um 697; el conteo exacto con `<` estricto es 697. Efecto en P: +1,58e-3 (Cd) y +1,48e-3 (T96d), del orden de la diferencia entre mallas (diff_04_05 de Pc: 4,37e-3 en SI frente a 2,79e-3 en um; umbral 5e-3). Los veredictos no cambian, pero las cifras Pc de 0,4 um no son reproducibles entre sistemas de unidades.
- No comprobable: R0 (reproduccion bit a bit de 009d, dif = 0,0) exige repropagar con ADI; no lo hice. La reserva 028 y la replica GLASS-007 V2 no se tocaron.

## 4. I (curvas)

Mis corridas (n_eq = n(1 + x/R) del contrato, mi FD, seleccion por solapamiento):

| Malla/dominio | D(50) | D(20) | D(10) | D(5) (modo de nucleo) |
|---|---|---|---|---|
| h 0,5 / L 40 | 2,946e-6 | 1,844e-5 | 7,433e-5 | 3,277e-4 (S = 0,757) |
| h 0,25 / L 40 | 2,949e-6 | 1,846e-5 | 7,441e-5 | 3,266e-4 (S = 0,766) |
| h 0,5 / L 30 | 2,946e-6 | 1,844e-5 | 7,434e-5 | 2,770e-4 (S = 0,746) |
| h 0,25 / L 30 | 2,949e-6 | 1,846e-5 | 7,442e-5 | 2,760e-4 (S = 0,741) |

- VI1: n(50) < n(20) < n(10) < n(5) en las cuatro combinaciones; C2 de I (n_eff decrece al bajar R) FALLA con independencia de malla y dominio. CONFIRMADO el fallo. Ademas el signo de la prediccion era erroneo de entrada: el desplazamiento de segundo orden del modo fundamental es positivo (perturbacion), no una anomalia numerica.
- VI2: D(10)/D(20) = 4,03 y D(20)/D(50) = 6,26 (teoria 1/R^2: 4 y 6,25); D > 0. PASA.
- C1 de I (2,95e-6 > 1e-6) es un fallo real y mesh-independiente; con D ~ R^-2 haria falta R >= 86 mm. El umbral era inalcanzable a 50 mm.
- VI3: a R = 5 mm el modo elegido por I (S = 1,4e-6, P_core = 0) es un estado de caja del borde exterior. Existe un modo de nucleo (P_core 0,70, S 0,77, n = 1,442519), que I solo halla en `supp_r5.py` con 40 modos. Por tanto C2 (n5), C4, C5, C9 a 5 mm se evaluaron sobre un modo equivocado. Con el modo correcto: D5/D10 = 4,39 (L = 40; dentro de [3,6; 4,4] por 0,2 %) y 3,71 (L = 30): depende del dominio en un 17 % (fuga a la region permitida exterior). <x>5/<x>10 = 4,19 (L = 40) o 4,68 (L = 30), fuera de [1,8; 2,2]: C4 fallaria tambien con el modo correcto. A 10 y 20 mm el cociente de centroides es 2,05 (en rango).
- C6 de I (|n(L=40) - n(L=80)| = 6,5e-3 a R = 10 mm) es un artefacto de seleccion: con mi seleccion (k = 60, shift) el modo fundamental da 1,44226415 (L 40), 1,44226410 (L 60), 1,44226423 (L 80): dif 8,0e-8 <= 1e-6. Con el modo correcto C6 habria PASADO. REFUTADO el fallo como propiedad fisica.
- C7 (R_c,num = 8,65 mm frente a R_c,A = 2,70 mm): el barrido de I usa la misma seleccion top-12; en R = 7,5 mm el modo elegido tiene S = 4e-4 (estado de caja, P_out = 0,945). La cifra de R_c,num no es fiable. NO COMPROBABLE por mi (no repeti el barrido completo).
- Dominio: el contrato dice "dominio de +-20 um" para L = 40 pero el solver usa [-L, L] (+-40 um); error de descripcion, sin efecto en las cifras.
- Resumen: I publico 3/10 pass=true. Con seleccion correcta: C6 pasaria, C5 pasaria por 0,2 %, C2/C4/C9/C1/C7 seguirian fallando o inciertos.

## 5. K (registro entre caras)

- VK1: `kappa` directo + brentq: d* = 20,434507 um, delta_max = 20 - d* = -0,434507 um, P2(20) = 0,141016. K1-C1 FALLA (confirmado). PASA.
- VK2: seed 11, R = 2000, 12 celdas a d = 20 um: |E_mio - E_K| max = 0,0055 (<= 0,02); |E_mio - E_analitico| <= 0,0035. PASA. sd(f_chip) crece con l en las tres sigmas (K2-H-b reproducido).
- VK3 (prefactor de kappa, el riesgo declarado por K): splitting de supermodos con mi FD escalar de dos nucleos: kappa_FD / kappa_acoplo = 1,0019 (d = 20, h = 0,25), 1,0056 (h = 0,5), 1,0009 (d = 16, h = 0,25). PASA (<= 5 %). El prefactor se confirma dentro del modelo escalar.
- K3-C5 (Y = 0,585) coincide con la binomial P(X >= 190 | n = 200, p = 0,95) = 0,583. K3-C2 es identidad de diseno: d* + 1,645 sigma da 0,95 por construccion (mi E_ana = 0,9499996, Phi = 0,95); pasa por la tolerancia 1e-4 de E-2, no es validacion independiente (VK4).
- Riesgos no cubiertos: sigma, l, N, sigma_res son supuestos; modelo escalar de fibra analoga; fase igualada y sin desajuste inducido por el desplazamiento; l en "celdas" sin escala fisica.

## 6. Riesgos transversales

1. Las cifras de caja (F, I) dependen de la hibridacion con el continuo de Dirichlet a nivel 1e-5; ningun criterio con umbral <= 1e-5 sobre valores absolutos de caja es robusto salvo comparaciones a igual L.
2. Seleccion de modo: F (shift fijo) e I (top-12) fallan por la misma causa. Un criterio `pass=false` con `n_core` equivocado es peor que `no evaluable`.
3. La maquina estuvo saturada por otros procesos; algunos tiempos se multiplicaron por 10; no cambia cifras.
4. No verifique propagacion ADI (H3), ni la reserva 028, ni GLASS-007 V2, ni `check_variacional`.

## 7. Archivos

`CONTRATO-V4.md`, `v4_fd2d.py`, `v4_f_union.py`, `v4_f_union.json` (renombrado de `v_f_union.json`: ver nota), `v4_f_spec.py` + `v4_f_spec_L40_h0.25.json` + `v4_f_spec_L40_h0.125.json`, `v4_f_L.py` + `v4_f_L_resultados.json`, `v4_f_analitica.py` + `.json`, `v4_h.py` + `v4_h_resultados.json`, `v4_h3_check.py`, `v4_h3_check2.py` + `.json`, `v4_i.py` + `v4_i_resultados.json`, `v4_i2.py` + `v4_i2_resultados.json`, `v4_k1.py` + `v4_k1_resultados.json`, `v4_k2.py` + `v4_k2_resultados.json`.
