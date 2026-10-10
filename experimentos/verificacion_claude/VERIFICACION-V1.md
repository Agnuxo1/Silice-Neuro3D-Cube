# VERIFICACION-V1: verificacion independiente y adversarial de A (solver2d), B (BPM) y C (radial2)

Verificador: Claude (V1). Fecha: 2026-10-10, ejecutado entre 04:16 y 04:46 UTC (plazo 06:20 UTC).
Contrato propio: `CONTRATO-V1.md` (mtime 06:16:11 CEST = 04:16:11 UTC, anterior a todos mis calculos: v1_a.py 04:16:33 UTC, v1_b.py 04:17:06 UTC, v1_c.py 04:18:51 UTC).
Todo es modelo numerico. Ninguna cifra es medida de laboratorio. Solo CPU, `python -B`, OMP_NUM_THREADS=1, numpy/scipy.
Divulgacion: antes de escribir mi contrato ya habia leido los contratos, el codigo, los logs y los JSON de A, B y C (para saber que verificar). Mis codigos v1_a.py (FD 2D) y v1_b.py (BPM) son independientes (escritos desde la especificacion del contrato, sin importar solver2d.py ni bpm.py). v1_c.py importa radial2.py en solo lectura (necesario para re-ejecutar su salida) y calcula las raices cerradas con codigo propio. No se escribio nada fuera de esta carpeta ni se hizo git.

## 0. Resumen ejecutivo

| Afirmacion | Veredicto | Motivo corto |
|---|---|---|
| A1 error menor que el escalonado a h = 0,125 | PASA | e_sub = 7,39e-8 frente a 4,2164e-6 escalonado (57 veces menor). Reproducido con codigo propio a 4e-14. |
| A1 orden 1,8 a 2,2 | PASA el valor puntual (1,99); FALLA como orden asintotico robusto | El error cambia de signo entre h = 0,25 y 0,125; el siguiente par da orden 3,18; el cociente de diferencias sucesivas da 0,92. Es coincidencia de un par. |
| A (entrega) | FALLA la persistencia | No existe resultados.json de A; el log se corta tras el 7.o de 10 calculos de A1. Al ejecutar una copia del mismo codigo en mi carpeta, 18 de 18 criterios dan pass. |
| A3 observable con cobertura | PASA (C3.2); FRAGIL (C3.3) | Error relativo 7,3e-6 (s = 8), 3,9e-5 (s = 32), 1,13e-3 sin cobertura (s = 1). El orden del error depende de s: 3,76 (s = 8) frente a 1,49 (s = 32). |
| B1 solape y n_eff implicito | PASA | Mi BPM propio da n_eff_impl = 1,4421924195095 (identico al de B) y overlap^2 = 0,9999926. Matiz: el acuerdo de 2,5e-7 con el analitico exacto surge de la cancelacion de dos sesgos de signo contrario. |
| B2 convergencia (n_eff) | PASA | dz: 8,0e-8; h: 5,7e-7; secuencia h = 0,4; 0,2; 0,1; 0,05 con razon de cambios 3,6 y 4,5. |
| B (perdida C5, publicada como FALLA) | El fallo es real pero es un artefacto numerico de dz, no del CAP ni fisica | Con h = 0,2 y dz = 1; 0,5; 0,25; 0,125 la perdida es 2,46e-4; 7,37e-5; 3,72e-5; 2,76e-8. Con dz = 0,125 C5 pasaria. |
| C1 error de n_eff con ecuacion cerrada | PASA | Re-ejecucion identica al JSON (dif. maxima 0,0). Error del modelo E <= 1,8e-15; del modelo P frente a su cerrada propia <= 1,8e-15; error P/Delta <= 2,2e-3. |
| C3.2 (orden RK4 con h) | NO DEMOSTRADO | Con h = 400 y 200 nm el error es identico (2,82e-12) por el tope h_eff = min(h, r/40). El orden solo aparece por debajo de 100 nm (2,98; 3,76; 3,94). |

Ninguna de las cinco afirmaciones pedidas queda refutada en su cifra principal. Las cifras de A, B y C se reproducen. Lo que si se refuta o se matiza: el orden asintotico de A1, la persistencia de los resultados de A, la lectura del fallo C5 de B, y la lectura de C3.2 de C.

## 1. Preregistro (paso 2 y 4 de la tarea)

Comando: `ls -l --time-style=full-iso` y `sha256sum`. Las horas son CEST (UTC + 2).

- A: CONTRATO-solver2d.md 05:32:03 < analitico_lp01.py 05:32:53 (solver2d.py 05:32:46) < run_tareas.py 05:33:52 < log_run.txt 05:34:17. PASA el orden. Los umbrales de run_tareas.py (C1.1 a C4.2) coinciden uno a uno con el contrato. FALLA la entrega: no hay resultados.json ni RESULTADOS en la carpeta; el log termina en `[A1_sub_L40_h0.125] ... t=11.8s` y no hay ningun proceso vivo. Ninguna pass=true de A fue escrita por el codigo en un JSON.
- B: CONTRATO-bpm.md 05:37:55 < resultados_bpm.json 05:52:54. PASA el orden. Los umbrales THR_* de verificar_bpm.py (1e-9, 1e-6, 0,999, 1e-5, 1e-6, 1e-5, 1e-5) coinciden con la seccion 3 del contrato. Reservas: (i) verificar_bpm.py (05:34:34) es anterior a la ultima version del contrato (05:37:55) y bpm.py se modifico 1,3 s antes que el contrato; (ii) la enmienda 5b dice "03:50 UTC" pero el contrato no se guardo despues de 03:37:55 UTC y la corrida empezo hacia las 03:38 UTC (894 s antes de las 03:52:54 UTC), asi que la hora declarada es inexacta. No he podido comprobar la afirmacion "no se ha mirado ninguna cifra". No hay violacion cronologica demostrable.
- C: CONTRATO-RADIAL2.md 05:35:24 < radial2.py 05:39:08 < run_radial2.py 05:39:36 < resultados_radial2.json 05:51:33. PASA. El sha256 del contrato guardado en el JSON (244f52bb...) es igual al del fichero actual: el contrato no se toco despues de ejecutar. Los umbrales del codigo coinciden con el contrato. Reservas: la seccion 7 se titula "03:4x UTC" pero el fichero tiene mtime 03:35:24 UTC; la aclaracion A3 reescribe C1.4 (el texto original "exactamente una raiz guiada" fallaria para Delta = 0,010, que tiene LP01 y LP02) y lo sustituye por "coincide el conteo con las ecuaciones cerradas". La reescritura esta dentro del contrato anterior a la ejecucion, pero es un cambio de criterio.
- Error documental en el contrato de A (no cambia ningun resultado): afirma que psi en el contorno es 0,7 % del maximo con L = 30 y 0,09 % con L = 40. Calculo propio con J0(U)/K0(W) K0(W L/a): 1,5e-5 (L = 30), 2,7e-7 (L = 40), 4,9e-9 (L = 50). Los valores del contrato estan equivocados en dos a tres ordenes de magnitud; la eleccion de L = 40 queda mas que justificada.

## 2. Grupo A (solver2d): A1 y A3

Referencia analitica propia (brentq sobre u J1/J0 = w K1/K0): V = 2,9201606467, U = 1,756877101709979, W = 2,332535327069695, n_eff = 1,4421921654570122 (el de A: ...0125, el JSON de referencia: ...0133; dif. <= 1e-15). Gamma cerrada = 0,8904196922063362, Gamma por quad = 0,8904196922063359.

### 2.1 Reproduccion con codigo propio (VA1a)
| h (um) | n_eff mio s = 8 | dif. con log de A | n_eff mio s = 1 | dif. con log de A |
|---|---|---|---|---|
| 0,5 | 1,4421911742700 | 3,9e-14 | 1,4421631979748 | 4,1e-14 |
| 0,25 | 1,4421918718380 | 7,3e-15 | 1,4421813615218 | 1,6e-14 |
| 0,125 | 1,4421922393960 | 1,8e-15 | 1,4421879490506 | 1,0e-14 |

VA1a: PASA (umbral 1e-9).

### 2.2 Error y orden (VA1b, VA1c, VA1d)
- Errores firmados frente al analitico (L = 40, s = 8): -9,912e-7 (h = 0,5), -2,936e-7 (0,25), +7,394e-8 (0,125). VA1b: PASA (7,39e-8 <= 4,2164e-6 y <= 1e-6).
- Ordenes por error absoluto: 1,755 (0,5 a 0,25), 1,990 (0,25 a 0,125). El de A (1,9895) se reproduce.
- Sesgo de dominio (VA1d): |n(L = 40) - n(L = 60)| a h = 0,25 = 1,3e-15; |n(L = 24) - n(L = 40)| = 4,7e-10. El dominio no es la causa de nada.
- Triplete fino a L = 24 (h = 0,25; 0,125; 0,0625): n_eff = 1,4421918713719; 1,4421922389322; 1,4421921735369. Errores: -2,941e-7; +7,348e-8; +8,080e-9. Ordenes por error absoluto: 2,00 y 3,18.
- Cociente de diferencias sucesivas (criterio preregistrado VA1c, independiente del valor exacto): L = 40: p_diff = log2(6,976e-7 / 3,676e-7) = 0,92. L = 24: diferencias +3,676e-7 y -6,540e-8, de signo contrario, p_diff no definido.
- VA1c: FALLA (se exigia p_diff en [1,8; 2,2] en ambos tripletes). Interpretacion: el error no es C h^2 puro; cruza cero hacia h = 0,15 (el promediado subpixel con borde curvo no da error monotono). El valor 1,99 es real pero un par aislado; el siguiente par da 3,18. No se puede extrapolar por Richardson ni citar "orden 2" como propiedad del metodo.

### 2.3 Escalonado (control)
Errores escalonados L = 40: -2,8967e-5; -1,0804e-5; -4,2164e-6. Orden (0,25 a 0,125) = 1,3575, dentro del rango preregistrado por A [1,2; 1,6]. Reproduce el JSON de referencia a 3,9e-12 (L = 40) y a 0,0 (L = 30, copia de su codigo).

### 2.4 Copia de su run_tareas.py (para suplir la ausencia de JSON)
Copie solver2d.py, analitico_lp01.py y run_tareas.py a `v1_copia_solver2d/` (solo cambia la ruta de REF_JSON a absoluta) y lo ejecute completo (04:24:55 a 04:27:06 UTC): 18 criterios, 18 pass. Cifras: C1.1 7,39e-8; C1.2 7,39e-8; C1.3 1,9895; C1.4 1,3575; C1.5 0,0; C1.6 1,3e-15; C1.7 8,9e-16; C2.1 2,2e-16; C2.2 9,5e-15; C2.3 1,5e-14; C2.4 0; C3.1 1,2e-16; C3.2 7,27e-6; C3.3 3,76; C4.1 y C4.2 pass en h = 0,5 y 0,25. Es una ejecucion mia de su codigo; no sustituye a un resultados.json suyo, pero demuestra que el codigo, tal como esta, da esas cifras.

### 2.5 A3 observable (VA3a, VA3b, VA3c)
VA3a: |Gamma_cerrada - Gamma_quad| / Gamma = 1,2e-16, PASA.
Error relativo de Gamma_FD frente a Gamma exacta (mi psi, mi cobertura):

| h (um) | s = 1 (sin cobertura) | s = 8 | s = 32 | psi analitica en nodos, s = 32 |
|---|---|---|---|---|
| 0,25 | 3,11e-3 | 9,87e-5 | 1,08e-4 | 2,42e-4 |
| 0,125 | 1,13e-3 | 7,27e-6 | 3,85e-5 | 5,63e-5 |

- VA3b: PASA (3,85e-5 con la cobertura mas fina y 7,27e-6 con la de A, ambos <= 1e-3). VA3c: PASA (5,6e-5).
- Sin cobertura subpixel (s = 1) el criterio 1e-3 FALLA a h = 0,125 (1,13e-3): la cobertura es lo que hace pasar el observable, como afirma A3.
- Fragilidad: el orden del error entre h = 0,25 y 0,125 vale 3,76 con s = 8 pero 1,49 con s = 32 (C3.3 exige >= 1,5). El 3,76 de A procede de una cancelacion; con cobertura mas fina C3.3 no pasaria. No es un fallo de A3 principal (C3.2), pero C3.3 no es un resultado robusto.

## 3. Grupo B (BPM escalar paraxial)

Implementacion propia (v1_b.py): split-step de Strang con numpy.fft, n^2 promediado por celda 16 x 16, CAP del contrato (28 a 40 um, tasa 0,5 um^-1), LP01 analitico con E(0) = 1, ventana +-40 um, n_ref = n1.
n_eff analitico propio = 1,4421921654570; prediccion paraxial n_ref + (n_eff^2 - n_ref^2)/(2 n_ref) = 1,4421932971.

### 3.1 Reproduccion (VB1a)
- Mi BPM, h = 0,2, dz = 1, 1 mm: n_eff_impl = 1,4421924195095, overlap^2 = 0,9999926128, perdida = 2,46000e-4. Igual que resultados_bpm.json.
- Re-ejecucion de su propio bpm.py (v1_b_theirs.py, solo B1): dif. con el JSON = 0,0 en n_eff, solape y perdida.
- VB1a: PASA (dif. < 1e-12; umbral 1e-8).

### 3.2 Tabla h, dz (todas mias, 1 mm, CAP activo)
| h (um) | dz (um) | n_eff_impl | n_eff - analitico | overlap^2 | perdida 1 mm |
|---|---|---|---|---|---|
| 0,4 | 1 | 1,4421903560 | -1,81e-6 | 0,99999558 | 1,149e-4 |
| 0,2 | 1 | 1,4421924195 | +2,54e-7 | 0,99999261 | 2,460e-4 |
| 0,2 | 0,5 | 1,4421924997 | +3,34e-7 | 0,99999834 | 7,369e-5 |
| 0,2 | 0,25 | 1,4421925491 | +3,84e-7 | 0,99999938 | 3,719e-5 |
| 0,2 | 0,125 | 1,4421925637 | +3,98e-7 | 0,999999998 | 2,758e-8 |
| 0,1 | 1 | 1,4421929880 | +8,23e-7 | 0,99998850 | 4,917e-4 |
| 0,1 | 0,5 | 1,4421930561 | +8,91e-7 | 0,99999648 | 2,066e-4 |
| 0,05 | 1 | 1,4421931146 | +9,49e-7 | 0,99998609 | 6,815e-4 |

La pendiente de fase entre 500 y 1000 um da n_eff dentro de 3e-10 de la de fase total en todos los casos.

### 3.3 Criterios
- VB1b: overlap^2 = 0,9999926 >= 0,999 y |n_eff - analitico| = 2,54e-7 <= 1e-5. PASA.
- VB1c (pendiente de fase): 1,4421924198; dif. 2,5e-7 <= 1e-5. PASA.
- VB2a: |n(dz = 0,5) - n(dz = 1)| = 8,02e-8 <= 1e-6. PASA. VB2c (h = 0,1): 6,81e-8 <= 1e-6. PASA.
- VB2b: cambios sucesivos en h con dz = 1: 2,064e-6; 5,685e-7; 1,266e-7 (razones 3,63 y 4,49, ordenes 1,86 y 2,17). |n(h = 0,05) - n_paraxial| = 1,83e-7 <= 3e-7. PASA. Extrapolando, el limite ronda 1,442193 (compatible con la prediccion paraxial de 1,4421933).
- VB1d (la perdida de 2,46e-4 es reproducible): PASA, pero ver 3.4.
- Cancelacion de sesgos (aviso): el acuerdo de 2,5e-7 con el n_eff exacto a h = 0,2 no es "precision": la prediccion paraxial difiere del exacto en +1,13e-6 y la discretizacion h = 0,2 desplaza -8,8e-7. Al refinar h, n_eff_impl se aleja del analitico exacto (+8,2e-7 a h = 0,1; +9,5e-7 a h = 0,05) y converge a la prediccion paraxial. La comparacion de B1 con el exacto sirve porque el umbral (1e-5) es holgado (40 veces mayor que la diferencia medida).
- Normalizacion (aviso): overlap^2 se normaliza con la potencia en z (no la inicial). Respecto de la potencia inicial vale 0,9999926 x (1 - 2,46e-4) = 0,99974, tambien >= 0,999.

### 3.4 La perdida C5 (B3): el fallo es real pero lo causa dz
B declara C5 = FALLA (2,46e-4 > 1e-5) y lo publica, correcto. Pero la tabla muestra:
- A h fijo (0,2), la perdida cae con dz: 2,46e-4; 7,37e-5; 3,72e-5; 2,76e-8. Con dz = 0,125 el criterio C5 (<= 1e-5) pasaria (overlap^2 = 0,99999998).
- A dz fijo (1), la perdida crece al refinar h: 1,15e-4; 2,46e-4; 4,92e-4; 6,81e-4. Con dz = 0,5 y h = 0,1: 2,07e-4.
- Por tanto no es una perdida fisica del modo guiado ni una reflexion del CAP: es un artefacto del paso dz del split-step combinado con los armonicos altos de la malla (dz K_max^2 / (2 k0 n_ref) = 42 rad por paso con dz = 1 y h = 0,2). El diagnostico de B ("perdida lineal en z y 1,3e-4 fuera de s > 28 sin CAP") no identifica esta causa.
- Alcance: en B las conclusiones de convergencia del n_eff (B2) no cubren la potencia. La perdida no esta convergida con (h, dz) = (0,2; 1). Esto afecta a B4 (primer maximo de acoplo en 7,67 mm, perdida final 2,7e-3 con dz = 1), que no re-ejecute (NO COMPROBABLE en esta pasada).

## 4. Grupo C (radial2, disparo + biseccion): C1

### 4.1 Re-ejecucion (VC1a, VC1e)
Rehice C1 con sus funciones (`closed_roots`, `real_roots`, h = 5 nm, modelos E y P) para Delta = 0,003; 0,005; 0,010 y l = 0, 1. Diferencia maxima con resultados_radial2.json = 0,0 en cerradas, E y P. Conteos de raices: l = 0: 1, 1, 2; l = 1: 0, 1, 1 (iguales a los de la ecuacion cerrada). VC1a y VC1e: PASAN.

### 4.2 Raices cerradas propias (VC1b, VC1c)
Codigo propio: forma generica LP_lm, `u J_{l-1}(u) K_l(w) + w K_{l-1}(w) J_l(u) = 0` (distinta de la que usa C), brentq con xtol 1e-16, escaneo de 20001 puntos.
- Mi cerrada frente a la "closed_neff" de C: dif. maxima 6,7e-16.
- Solver E frente a mi cerrada: dif. maxima 1,8e-15 (umbral C1.1: 1e-8). PASA.
- Modelo P: cerrada paraxial propia con V_P = a k0 sqrt(2 n0 Delta) y n_eff = n0 + W^2 / (2 k0^2 n0 a^2). Solver P frente a ella: dif. maxima 1,8e-15 (umbral 1e-9). PASA.
- Error del modelo paraxial frente a la ecuacion cerrada escalar exacta dividido por Delta: 5,8e-4 (LP01, Delta = 0,003); 8,3e-4 y 1,04e-3 (LP01 y LP11, 0,005); 1,17e-3, 1,33e-3 (LP01, LP02) y 2,23e-3 (LP11) para 0,010. Todos <= 0,01 (C1.2). PASA. Margen minimo 4,5 veces.
- "Demasiado bueno": los 1e-15 de C1.1 no son un artefacto del comparador. El perfil de salto tiene solucion exacta de Bessel; el RK4 con h = 5 nm alcanza el suelo de redondeo. La comprobacion es valida pero poco exigente.

### 4.3 Orden RK4 (VC1d, adversarial)
Modelo E, Delta = 0,010, LP01, error frente a mi cerrada:
- Preregistrado (h = 400, 200, 100 nm): 2,819e-12; 2,819e-12; 2,176e-12. Ordenes 0,0 y 0,37. FALLA (criterio [3,5; 4,5]). Causa: el codigo usa h_eff = min(h, r/40, ...), y r/40 vale 150 nm en r = a; con h >= 150 nm el paso efectivo es el mismo en todo el nucleo.
- Desviacion declarada del preregistro: rehice con h = 100, 50, 25, 12,5 nm: errores 2,18e-12; 2,76e-13; 2,04e-14; 1,33e-15 (ordenes 2,98; 3,76; 3,94). El RK4 es de orden 4 cuando h < r/40 y antes de tocar el suelo de redondeo.
- Consecuencia: el h nominal de 5 nm esta en el suelo de redondeo, de modo que C3.2 de C se cierra por "saturado" (p = -0,27 en el JSON). Es legitimo segun el contrato, pero el orden 4 no esta demostrado con los datos de C; solo lo demuestra mi barrido. Ademas, el tope r/40 nunca se refina, de modo que "convergencia en h" no es convergencia del paso completo.
- C2 (trinchera) no fue objeto de esta verificacion; C publica C2 = FALLA en los 4 casos primarios, y no es un resultado que yo haya revisado.

## 5. Riesgos no cubiertos por los criterios

1. A no deja JSON ni RESULTADOS. Cualquier lectura posterior depende de que alguien repita el run. A4 (kappa_FD) no esta en ningun fichero de A; mi copia da kappa(0,5) = 2,0368e-4 y kappa(0,25) = 2,0314e-4 um^-1 (cambio de -5,4e-7, -0,26 %); h = 0,125 no se ejecuta, y el kappa no esta convergido mejor que ~0,3 %.
2. El error de A1 no es monotono en h (cruza cero). Un orden estimado con tres puntos, sea 1,99 o cualquier otro, no es predictivo; cualquier uso de una barra de error "h^2" para n_eff o kappa es injustificado.
3. La cobertura subpixel de A3 usa s = 8, la misma que el solver; el error del observable cambia de 7,3e-6 a 3,9e-5 con cobertura mas fina. El criterio 1e-3 se cumple con margen de 25 veces, pero la cifra 7e-6 no debe citarse como precision del observable.
4. B: la perdida (C5) y quiza el acoplo B4 dependen de dz. Los umbrales de B son 12 a 40 veces mas holgados que los resultados (C2, C3, C4), y la comparacion de n_eff con el analitico exacto (no paraxial) esconde que el limite del propio BPM es 1,4421933. B4 (7,67 mm) no esta verificado frente a h ni dz.
5. B: las horas declaradas en la enmienda 5b y las de C seccion 7 no coinciden con los mtime; no demuestra mala fe, pero un preregistro en el que la hora escrita no es fiable pierde fuerza.
6. C: el criterio C1.4 fue reescrito dentro del contrato (conteo por l), C3.2 se cierra por saturacion, el tope r/40 es una dependencia no refinada, y los criterios C1.1/C1.2 son faciles de cumplir para un perfil con solucion de Bessel exacta. C1 valida el codigo; la parte que puede fallar (C2, cuasi-ligados) es la que C declara FALLA.
7. Todos los resultados son de modelo escalar sin calibrar; no hay datos de laboratorio. Nada de esto valida un dispositivo.

## 6. Ficheros (todos en D:\PROJECTS\.cognition\audit\silice-origin-main\experimentos\verificacion_claude\)
CONTRATO-V1.md; v1_a.py, v1_a_log.txt, v1_a_resultados.json; v1_b.py, v1_b_h*_dz*.json/.log, v1_b_theirs.py, v1_b_theirs.json; v1_c.py, v1_c_log.txt, v1_c_resultados.json, v1_c_h400.json; v1_copia_solver2d/ (copia del codigo de A ejecutada, con resultados.json y log_run_copia.txt). Otros ficheros de la carpeta (v_*, v2_*, v4_*, verif_*, VERIFICACION-V5) pertenecen a otros verificadores y no se tocaron.
