# VERIFICACION-V7: F2 (tracks), I2 (curvas), B2 (BPM con G3), ronda 2

Verificador independiente y adversarial. Modelos numericos escalares; ninguna cifra es medida ni dispositivo.
Hora de comprobacion: 2026-10-10 05:25 a 05:45 UTC (date -u). Limite: 06:20 UTC. Solo CPU, OMP_NUM_THREADS=1, python -B.
Todo lo que sigue sale de comandos ejecutados; los scripts y JSON propios estan en esta carpeta (`v7_*.py`, `v7_*.json`, `v7_*.log`).
No se ha modificado nada fuera de `experimentos/verificacion_claude/`.

## 0. Orden contrato / resultados (ls -l --time-style=full-iso, hora local +0200; restar 2 h para UTC)

| Tarea | contrato r2 | codigo | resultados | Veredicto del orden |
|---|---|---|---|---|
| F2 tracks | 06:57:12 | `run_tracks_r2.py` 06:56:37 | `resultados_tracks_r2.json` 06:58:59 | El codigo es 35 s ANTERIOR al contrato. Los umbrales del codigo (1e-6, 1e-5, 1e-4, 0,5, 1e-6, 0,5 %) coinciden con el contrato (`grep` de TOL_*), asi que no hay cambio de umbrales, pero el orden "contrato antes que codigo" no se cumple al segundo. |
| I2 curvas | 06:54:46 | `curvas_r2.py` 06:59:26 | `resultados_curvas_r2.json` 07:18:03 | PASA el orden. |
| B2 bpm | 06:54:16 | `bpm_r2.py` 06:55:14, `evaluar_bpm_r2.py` 06:57:32 | `resultados_bpm_r2.json` 06:57:33 | Contrato anterior. Pero el JSON es ANTERIOR a las corridas (ver B2). |

## 1. F2 (tracks)

### 1.1 Estado entregado: NO COMPLETO
- `resultados_tracks_r2.json`: `runs` tiene 1 clave (`i|L40|h0.25`), `criteria = []`, `status = null`, `summary = {}`.
- `log_run_r2.txt` termina a las 04:58:59 UTC con ese unico caso. No hay proceso python de tracks vivo (Get-CimInstance). Tienen que ejecutarse al menos ~15 casos del bloque B, 15 del C, A, D.
- Por tanto NINGUN criterio F21-C*, F22-C*, F23-* tiene un pass calculado por el codigo entregado. Cualquier afirmacion "F2 done/partial con criterios X" no tiene respaldo en el JSON.
- Lo unico entregado y comprobable: `analytic` (raices de i y iii_N), `fracs` y la corrida `i|L40|h0.25`.

### 1.2 Recalculo con otra caja y otra malla (solver FD propio `v7_fd.py`, no usa solver2d ni run_tracks)
Caso i (anillo 6<r<12, n = 1,439; resto 1,444), K = 30, shift en n_eff = 1,44219587, ventana 0,002, P(r<=12) >= 0,5.

| L (semilado, um) | h | n_core | P(r<=12) | ligado |
|---|---|---|---|---|
| 40 (entregado) | 0,25 | 1,4421952407054 | 0,8181 | si |
| 40 (propio, exacto) | 0,25 | 1,4421952407054077 | 0,8181459 | si (identico al digito) |
| 40 (propio) | 0,20 | 1,4421952698605 | 0,8180 | si (dif. en h = 2,9e-8; umbral F21-C4 1e-5: OK) |
| 50 | 0,25 | 1,4421934699 | 0,763 | si (ronda 1: 1,4421935, 0,76: coincide) |
| 60 | 0,25 | 1,4421891015 | 0,538 | si (ronda 1: 1,4421891, 0,54: coincide) |
| 65 | 0,25 | 1,4422113354 | 0,554 | si |
| 70 | 0,25 | 1,4422111860 | 0,696 | si |
| 75 | 0,25 | no ligado (mejor P = 0,491 en n = 1,4422124) | 0,491 | NO |
| 80 | 0,25 | 1,4421908377 | 0,590 | si |
| 90 | 0,25 | 1,4421944808 | 0,762 | si |
| 100 | 0,25 | no ligado (mejor P = 0,433 en n = 1,4422054) | 0,433 | NO |

Conclusiones adversariales:
- La cifra entregada (L = 40) se reproduce al digito con codigo independiente: la implementacion es correcta y la cifra es robusta en h.
- HF2.1 se confirma, y mas de lo que dice el contrato: n(L) NO es monotono (salta +2,2e-5 entre L = 60 y 65) y la bandera de ligado cambia (L = 75 y 100 no ligados). Una unica comparacion de pares es mala prueba de convergencia.
- F21-C1 (|n(80) - n(60)| < 1e-6): con mis cifras |1,4421908377 - 1,4421891015| = 1,736e-6 >= 1e-6. FALLARIA (coincide con la prediccion P1), por un margen pequeno. Ojo: sin los puntos 65 a 75, un par mas cercano (p. ej. 40 frente a 50: 1,8e-7) habria "pasado". Es un criterio fragil.
- F21-C2 (ligado en L = 40, 60, 80): pasaria (P = 0,818, 0,538, 0,590), pero 60 esta a 0,038 del umbral 0,5 y 75/100 ya no cumplen.

### 1.3 Pregunta principal (no calculada en la entrega; la calculo yo, informativo)
L = 40, h = 0,25, N = 48 (phase 0, discos r = 1,5 en radio 9):
- ii_48: n = 1,4427378532, P = 0,755, ligado.
- iii_48 (= caso i, reproduce 1,4421952407 exacto).
- Delta = n_ii - n_iii = +5,43e-4 >> 1e-5. F23-C1 (umbral 1e-5) FALLARIA en N = 48; la prediccion P3 (>= 1e-4) se cumple. No es una cifra "de la entrega": es mi calculo.
- N = 16, L = 40: ii = 1,4428192 (P 0,525) frente a iii = 1,4427662 (P 0,580): Delta = +5,3e-5.
- N = 8, L = 40: ni ii_8 (P max 0,19; con shift en 1,4430 tampoco, P 0,30) ni iii_8 (P max 0,19) ligados con el criterio P >= 0,5. P2 apoya que algunos casos no estan ligados.
- ii_48 a L = 60: no ligado (P max 0,05 con el shift del contrato; 0,305 con shift en 1,44274; L = 80 con shift 1,44274: 0,453). La ligadura de los trazos se pierde al crecer L, igual que en el caso continuo; no es solo un artefacto de la ventana de K = 30.

### 1.4 Geometria (F23-G1/G2) segun las cifras entregadas
- `f_union_grid` (dx = 0,01): N = 8 -> 0,16666362 frente a f = 0,16666667 (|dif| = 3,05e-6); N = 16 -> 0,33335141 frente a 0,33333333 (1,81e-5). Si F23-G1 se evalua con la estimacion de malla, falla (> 1e-6); si se evalua con el valor exacto disjunto (0,1666666666666667), pasa trivialmente. El contrato es ambiguo y el codigo (`run_tracks_r2.py`, lineas 305-310) usa el valor "exacto si disjuntos", que es N pi r^2 / area y por construccion es igual a f(N): F23-G1 pasaria de forma tautologica (no mide geometria). No se llego a ejecutar `evaluate()`.
- El error relativo de la malla en N = 16 es 5,4e-5 (< 0,5 %): F23-G2 pasaria.

## 2. I2 (curvas)

### 2.1 Lo que se confirma
- Contrato antes de resultados. Umbrales de ronda 1 citados.
- I2.0 (recto): mi solver propio da n_recto(L = 80, 100; h = 0,25) = 1,442191871838009, identico al entregado (1,442191871838); error frente a la analitica 1,442192165457: -2,94e-7 (<= 1e-6). PASA, verificado.
- Cifras a h = 0,2 (otro h) en L = 40, comparadas con las de h = 0,25 del JSON (D = n_curvo - n_recto en la misma caja):

| R (mm) | n_core h=0,2 (propio) | n_core h=0,25 (entregado) | D h=0,2 | D h=0,25 |
|---|---|---|---|---|
| 10 | 1,4422663293 | 1,4422662481 | 7,4373e-5 | 7,438e-5 |
| 20 | 1,4422104063 | 1,4422103225 | 1,8450e-5 | 1,845e-5 |
| 50 | 1,4421949039 | 1,4421948195 | 2,9476e-6 | 2,948e-6 |

  Diferencias n(h=0,2) - n(h=0,25) ~ 8e-8: las cifras de L = 40 se reproducen y son robustas en h. Los solapes S coinciden (0,9689, 0,9924, 0,99879).

### 2.2 Lo que se REFUTA: "I2.1 FAIL: no converge en L para R = 10 y 20 mm"
Los fallos de I2.1/I2.2 vienen del metodo de busqueda (shift en el maximo de n^2 con 40 modos: el modo nucleo queda fuera de los 40 modos cuando hay continuo exterior), no de la fisica del modelo. Con shift-invert cerca de n_eff (1,44227 para R = 10; 1,44221 para R = 20) y K = 12, h = 0,25:

| R | L | n_core (propio) | S | referencia entregada |
|---|---|---|---|---|
| 10 | 80 | 1,4422663152 | 0,968 | entregado: modo espurio 1,446321, S = 0 |
| 10 | 100 | 1,4422663028 | 0,961 | entregado: modo espurio 1,449205, S = 0 |
| 20 | 100 | 1,4422103225 | 0,9924 | entregado: modo espurio 1,443553, S = 0 |

- |n(100) - n(80)|: R = 10 -> 1,24e-8; R = 20 -> ~1e-12 (frente a 1,442210322528 de L = 80); R = 50 -> 0. Los tres < 1e-6 con S > 0,90. Es decir, I2.1 PASARIA con una busqueda que encuentre el nucleo. La conclusion publicada ("no converge", "FAIL") describe el procedimiento, no el modelo.
- Incoherencia interna: el contrato (Q5 opcion A) dice que si I2.2 falla, I2.1 se publica "no evaluable" para ese R; el codigo y el RESULTADOS tabulan FAIL con diferencias de 2,9e-3 y 1,3e-3 que son modos espurios.
- I2.2 FAIL: es cierto en la letra (con n_modes = 40 hay 4 casos sin S > 0,9 y 1 con corte espectral), se publica asi y es honesto. Pero no es un fallo del fisico.

### 2.3 Riesgo no cubierto: I2.3 (tendencia) probablemente FALLARIA con la direccion del contrato
- n_core(L = 40, h = 0,25): R = 50 -> 1,44219482; R = 20 -> 1,44221032; R = 10 -> 1,44226625. El n_eff del modelo n_eq = n (1 + X/R) CRECE al disminuir R. H-I2c e I2.3 piden n(50) > n(20) > n(10) con margen u. Esa direccion es la contraria a la del modelo. Si I2.1 pasara para R = 10 (como muestro arriba), I2.3 se evaluaria y daria FAIL. El estado "no evaluado" oculta un fallo previsible (es una prediccion mia; no la ha evaluado el codigo entregado).
- Interpretacion: n_eff aqui es el indice efectivo en el marco conforme, no la constante de propagacion fisica ni una perdida; la hipotesis H-I2c mezcla ambos.

### 2.4 Otros limites
- h = 0,125 no se ejecuto (declarado). No he ejecutado h = 0,125 tampoco (RAM libre ~4 GB, otros procesos GPU/CPU activos).
- I2.4 (radio critico) no evaluado por decision; la afirmacion de ronda 1 para R < 7,5 mm sigue invalida.

## 3. B2 (BPM con G3)

### 3.1 El JSON entregado esta OBSOLETO
`resultados_bpm_r2.json` (06:57:33 local = 04:57:33 UTC) se escribio ANTES de las corridas: `status = partial`, `sin_evaluar = [D6, D1, D2, D4, D5, G3.d14, G3.d16, G3]`, `regla_R_seleccion = "base"`, `perdida_1mm_por_corrida` con 6 nulos. Pero `r2_runs/*.json` (06:55 a 07:07 local) existen completos (G0, W60, W60c, W80, disc, dz05, g3_d14, g3_d16). No hay `RESULTADOS-bpm-r2.md`. El contrato exige que el pass lo calcule el codigo entregado: con el JSON vigente solo C0, V0, D3, B2.2 tienen pass; el resto esta sin evaluar. Los numeros siguientes los calculo yo a mano con los umbrales del contrato a partir de `r2_runs/` (no es una evaluacion del codigo entregado).

Perdida a 1 mm (h = 0,2): base 2,4600e-4; G0 2,2791e-4; s0 2,4293e-4; disc 2,4596e-4; dz05 7,3692e-5; W60 2,4497e-4; W80 2,4143e-4.

| Criterio | valor (mio, desde r2_runs) | umbral | resultado |
|---|---|---|---|
| D1 contorno | 1,47 % | <= 10 % | PASA |
| D2 amplitud CAP | 7,36 % | <= 10 % | PASA |
| D3 posicion CAP | 1,25 % | <= 10 % | PASA (ya en el JSON) |
| D4 dz | 70,0 % | <= 10 % | FALLA: el paso dz contribuye |
| D5 dato discreto | 2,4596e-4 | <= 1e-5 | FALLA |
| D6 autoestado | 4,02e-7 | <= 1e-5 | PASA |
| B2.2 | 2,46e-4 (base) / 2,41e-4 (W80) | <= 1e-5 | FALLA |

- La regla R, con D5 falso y D1 verdadero, selecciona R-W80, no R-base (el JSON dice base porque D1 estaba sin evaluar). El resultado B2.2 es el mismo (falla), pero la configuracion registrada es incorrecta.
- Hipotesis con evidencia: solo H-DZ (D4 falla). Bajar dz de 1 a 0,5 divide la perdida entre 3,3, pero aun queda 7,4e-5 > 1e-5. La perdida de 2,5e-4/mm es, por tanto, en buena parte error de separacion; no se ha probado dz mas pequeno.
- Dependencia fuerte con dz en G3: perdida al final (d = 14): dz = 2 -> 1,09e-2; dz = 1 -> 1,34e-3 (entregado); dz = 0,5 -> 5,8e-4.

### 3.2 Longitud de transferencia con otro dz (G3), criterio 10 % con kappa_FD de `resultados_g1_g2.json`
kappa_FD (campo `G1_main_h0125`.`kappa_FD_per_um`): d = 14 -> 4,716394e-4 /um; d = 16 -> 2,030540e-4 /um. L_c = pi/(2 kappa): 3330,50 um y 7735,86 um.

| d (um) | dz (um) | z_max (um) | L_c (um) | error relativo | pasa 10 % | P2 max |
|---|---|---|---|---|---|---|
| 14 | 1,0 (entregado) | 3361,80 | 3330,50 | +0,94 % | si | 0,9972 |
| 14 | 2,0 (mio) | 3358,48 | 3330,50 | +0,84 % | si | 0,9884 |
| 14 | 0,5 (mio) | 3362,08 | 3330,50 | +0,95 % | si | 0,9979 |
| 16 | 1,0 (entregado) | 7670,92 | 7735,86 | -0,84 % | si | 0,9970 |
| 16 | 2,0 (mio) | 7647,60 | 7735,86 | -1,14 % | si | 0,9771 |

G3 se CONFIRMA: la longitud de transferencia es insensible a dz (cambio < 0,2 %) y queda a ~1 % de L_c, muy dentro del 10 %.
- Comprobacion independiente de kappa_FD con mi solver FD (`v7_kappa.py`, dos nucleos, L = 40, h = 0,2): kappa = 4,71613e-4 /um (d = 14) y 2,03079e-4 /um (d = 16); L_c = 3330,69 um y 7734,89 um. Coinciden con el JSON a 5,7e-5 y 1,2e-4 relativo.
- Nota: el contrato escribe L_c(14) = 3,3323 mm y L_c(16) = 7,7451 mm; el valor correcto de pi/(2 kappa) es 3,3305 y 7,7359 mm. El codigo usa los correctos; el texto del contrato tiene una errata de ~0,05 a 0,12 %. No afecta al resultado.
- El 10 % es un umbral holgado (el acuerdo real es ~1 %). Es limpio pero poco exigente; ademas BPM y kappa_FD comparten el mismo modelo escalar, asi que G3 valida la numerica, no la fisica.

## 4. Riesgos no cubiertos por los criterios
1. F2: la entrega esta truncada (1 corrida). Sin criterios ni estado. El bloque ii/iii, la pregunta principal, no tiene ningun dato entregado.
2. F2: n depende de L de forma no monotona y la bandera de ligado cambia (L = 75, 100). El "modo de nucleo" de un solver de caja es un cuasi-ligado con fuga; F21-C1 compara solo dos puntos. Un L distinto del contrato cambiaria el veredicto.
3. F2: F23-G1 es ambiguo (exacta o malla) y la malla de dx = 0,01 da errores de 3e-6 a 2e-5.
4. I2: busqueda del nucleo por ventana espectral fija: da falsos "no converge". Falta una busqueda con shift guiado y control de S.
5. I2: la hipotesis de tendencia H-I2c tiene el signo contrario al del modelo.
6. B2: JSON obsoleto y regla R mal aplicada. La perdida numerica es en gran parte error en dz (D4), no probada hasta 1e-5.
7. Modelo: todo es escalar, sin perdidas por radiacion reales; "Dirichlet en caja" no representa radiacion. Ninguna cifra es dato de laboratorio.
8. Ninguna de las tres tareas ha usado h = 0,125 en L grande por RAM; la verificacion en h la hice a 0,2.

## 5. Archivos propios
`v7_fd.py` (solver FD propio: f2, f2t, f2e, i2), `v7_b2.py` (BPM con otro dz), `v7_kappa.py` (kappa de dos nucleos), `v7_f2*_*.json`, `v7_i2*_*.json`, `v7_b2_d*_dz*.json`, `v7_kappa_d*.log`.
