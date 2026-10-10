# VERIFICACION-V8 - verificacion adversarial de B3-r3 (BPM, dato discreto, G3) y F3-r3 (tracks)

Verificador independiente (Claude). Modelo numerico escalar. Solo CPU, python -B, OMP_NUM_THREADS=1. No se ha tocado nada fuera de
`experimentos/verificacion_claude/` (scripts y salidas propios en `experimentos/verificacion_claude/v8/`). Sin git. Hora de trabajo 07:34-07:57 UTC.
Todo el codigo de calculo es propio (BPM Strang, FD de 5 puntos, shift-invert); no se ha importado `bpm_r2.py`, `solver2d.py` ni `run_tracks.py`.

## 1. Estado de lo entregado (paso 1 y 2)

Marcas de tiempo (`ls -l --time-style=full-iso`, convertidas a UTC; el disco esta en +02:00):

| archivo | UTC |
|---|---|
| bpm_claude/CONTRATO-bpm-r3.md | 07:15:16 |
| bpm_claude/run_b3_r3.py | 07:15:47 |
| bpm_claude/r3_runs/log_*.txt (6, tamano 0) | 07:16:32 |
| bpm_claude/evaluar_bpm_r3.py | 07:17:05 |
| tracks_claude/CONTRATO-tracks-r3.md | 07:15:39 |
| tracks_claude/run_tracks_r3.py | 07:16:45 |
| tracks_claude/resultados_tracks_r3.json y RESULTADOS-tracks-r3.md | 07:16:54 |
| tracks_claude/log_run_r3.txt (ultima linea "inicio bloque F31") | 07:17:02 |

- Orden contrato -> resultados: correcto en los dos casos (el contrato es anterior a cualquier cifra).
- Detalle menor B3: el contrato dice "Fecha de escritura 07:20 UTC", pero el archivo se guardo por ultima vez a las 07:15:16 UTC. La hora escrita es 5 min posterior al mtime. No cambia ninguna cifra, pero la hora declarada no es fiable.
- Detalle menor B3: `evaluar_bpm_r3.py` se guardo (07:17:05) despues de lanzar las corridas (07:16:32). Sus umbrales coinciden con el contrato (1e-5, 1e-3, 0,999, 1e-9, 0,10): sin deriva.
- **B3: no hay resultados.** No existe `resultados_bpm_r3.json`, `RESULTADOS-bpm-r3.md` ni ningun JSON en `r3_runs/` (solo 6 logs vacios). A las 07:35 UTC no habia ningun proceso python de B3 vivo.
- **F3: no hay resultados.** `resultados_tracks_r3.json` tiene 0 corridas. Su estado "blocked" se escribio 8 s antes de empezar el bloque F31 y se quedo asi (placeholder). "blocked" en el contrato significa "el solver falla en todas las corridas"; aqui 0 corridas ok y 0 con error, asi que el rotulo es enganoso: lo correcto es "no ejecutado / partial". No hay proceso vivo de `run_tracks_r3`, y no se guardo ningun checkpoint (el bloque F31 a L = 80 tarda 15 s en esta maquina, asi que no fue un limite de memoria o de tiempo de la corrida: el proceso desaparecio).
- G3 en r3: segun el contrato (seccion 5) solo se ejecuta si B3-r3 pasa; como B3-r3 falla (ver 2), "no ejecutado: condicion no cumplida" es coherente.

Consecuencia: no hay cifras de B3-r3/F3-r3 que confirmar. Lo que sigue es la recalculacion independiente de lo que pedia la tarea.

## 2. B3: perdida a 1 mm con dato discreto (paso 3)

Configuracion fijada por el contrato: W = 40, h = 0,2 (N = 401), sub 16, CAP s0 = 28, w = 12, R0 = 0,5 um^-1, lambda = 1,55, a = 6, n1 = 1,444, n2 = 1,439, Strang, 1000 um.
E0 discreto = modo FD de 5 puntos (Dirichlet, misma malla; mi propia implementacion, equivalente a solver2d). Script: `v8/v8_bpm.py`, salida `v8/v8_bpm_base.json`.

Verificacion previa (condiciones N1, O1, V1, V2 del contrato, calculadas por mi):

| criterio | mi valor | umbral | resultado |
|---|---|---|---|
| N1 \|n_eff,FD - 1,4421922\| | 2,6e-7 (n_FD = 1,4421919059; analitico 1,4421921655) | 1e-5 | PASA |
| O1 solape FD-LP01 | 0,9999999678 | 0,999 | PASA |
| V1 unitariedad sin CAP (dato FD, dz=1) | 4,85e-13 | 1e-9 | PASA |
| V2 control (dato analitico, dz=1, CAP) | 2,4600e-4 | 2,4600e-4 +-1e-3 rel. | PASA |

Perdida a 1 mm (CAP base):

| dz (um) | E0 analitico | E0 discreto FD | \|fd-an\|/an |
|---|---|---|---|
| 1 | 2,4600e-4 | 2,4601e-4 | 4e-5 |
| 0,5 | 7,369e-5 | 7,370e-5 | 1e-4 |
| 0,25 | 3,719e-5 | 3,719e-5 | 2e-4 |

Lectura (adversarial):
- **H-DATO se refuta, y se podia prever sin propagar**: el modo discreto y el analitico se solapan en 1 - 3,2e-8. Cualquier construccion razonable del dato discreto da lo mismo. El resultado B3-r3 seria 2,46e-4 > 1e-5: FALLA. H1 (el dato no cambia la perdida) se cumple con 4e-5 de diferencia relativa (umbral 0,10).
- **La perdida no es el CAP comiendo la cola del modo.** Estimacion de primer orden de la tasa intrinseca del modo (integral de Gamma/(k0 n) |psi|^2 / integral |psi|^2): 3,2e-8 por mm con W = 40 (fraccion de potencia del modo en s > 28 = 1,3e-9). La perdida medida es 4 ordenes mayor. Con la ventana ampliada (W = 60, CAP en s0 = 48, misma anchura y R0) la perdida es 2,4497e-4 (an) y 2,4498e-4 (fd), practicamente igual (-0,4 %), mientras la estimacion intrinseca baja a 4e-15. Es decir, la potencia que absorbe el CAP no viene de la cola estacionaria del modo, y no depende de donde este el CAP.
- **Depende de dz**: 2,46e-4 -> 7,37e-5 -> 3,72e-5 (factores 3,34 y 1,98). D1-dz (umbral 0,10) daria |7,37e-5-2,46e-4|/2,46e-4 = 0,70: FALLA, como adelantaba el contrato. Es un efecto del esquema de particion, no del dato.
- Sin CAP la potencia total se conserva (4,9e-13 a dz=1) pero 1,2993e-4 (an) y 1,2994e-4 (fd) de la potencia pasan a s > 28 en 1 mm (6,59e-5 con dz=0,5; 3,53e-5 con dz=0,25). R1 (misma radiacion con ambos datos, umbral 0,10) PASA con 8e-5. Esas cifras coinciden con el diagnostico de la ronda 1 (1,30e-4).
- La perdida con CAP crece linealmente en z desde el origen (8,6e-6 a 50 um, 5,9e-5 a 250 um, 2,09e-4 a 850 um; ordenada en el origen ~0): es una tasa continua del esquema (~2,5e-7 por um a dz = 1), no un transitorio de arranque. Eso tambien contradice que el problema sea el "dato inicial".
- Mecanismo: **no determinado**. Probe exploratorio de resonancia en K alto (filtro pasa-bajos en K con corte 7, 10, 12 um^-1, dz = 1): la perdida sube (6,6e-4, 4,1e-4, 2,9e-4), asi que no apoya esa hipotesis y el filtro confunde el resultado. No se afirma causa. Lo medido es: dz-dependiente, independiente del dato, independiente de la ventana.
- El contrato (seccion 8) deja sin calcular "el autovector del propio esquema" (Strang de un paso). Es justo la prueba que podria distinguir "dato" de "esquema" y queda pendiente. Yo no la he hecho tampoco.

## 3. G3: longitud de transferencia con otro dz (paso 4)

Ronda 2 (dz = 1, W = 40, h = 0,2, CAP base), de `bpm_claude/r2_runs/g3_d*.json`: z_max = 3,3618 mm (d = 14) y 7,6709 mm (d = 16); L_c(kappa_FD) = 3,3305 y 7,7359 mm; errores +0,94 % y -0,84 %.
Mi recalculo (BPM propio, modos de un nucleo FD, supermodos FD de dos nucleos), `v8/v8_g3.py`:

| d (um) | dz (um) | z_max (mm) | error vs L_c supermodos | P2_max | perdida al final |
|---|---|---|---|---|---|
| 14 | 2 | 3,3585 | +0,83 % | 0,9884 | 1,09 % |
| 14 | 1 (r2) | 3,3618 | +0,94 % | 0,9972 | 0,134 % |
| 14 | 0,5 | 3,3621 | +0,94 % | 0,9979 | 0,058 % |
| 16 | 2 | 7,6476 | -1,13 % | 0,9771 | 2,43 % |
| 16 | 1 (r2) | 7,6709 | -0,84 % | 0,9970 | 0,227 % |

- L_c de mis supermodos FD (h = 0,2): 3,3308 mm (d = 14) y 7,7351 mm (d = 16), frente a 3,3305 y 7,7359 mm del contrato (kappa_FD, h = 0,125). Coinciden a 0,01 %.
- La longitud de transferencia es robusta frente a dz (variacion <= 0,25 % entre dz = 0,5 y 2 para d = 14; 0,3 % entre dz = 1 y 2 para d = 16). El criterio de G3 (10 %) se cumple con holgura en todos los dz probados. **Pero** P2_max y la perdida si dependen de dz (la perdida al final crece ~ dz^2: 0,058 %, 0,134 %, 1,09 %), consistente con el artefacto de B3. El desfase de ~1 % respecto a L_c tiene signo distinto para d = 14 (+) y d = 16 (-): no es un sesgo comun; no se ha explicado y es 10 veces menor que el umbral.
- Corridas no hechas: d = 16 con dz = 0,5 (tarda ~15 min). Si se necesita, queda pendiente.

## 4. F3.1: n_eff del caso i en L = 60 y 80 (paso 5)

Caso i: nucleo n = 1,444 (r <= 6), camisa n = 1,439 (6 < r <= 12), fondo 1,444; h = 0,25, s_sub = 8, Dirichlet, shift-invert en sigma = n_eff = 1,44219587036 (K = 10-12 modos en vez de 30; no cambia el LU). Seleccion: modo de mayor n_eff con P(r <= 12) >= 0,5 y \|n - sigma\| <= 0,002. Script `v8/v8_f31.py`, salidas `v8/v8_f31_L*.json`.

| L (um) | incognitas | indice del modo | n_eff | P(r<=12) |
|---|---|---|---|---|
| 50 | 159 201 | 8 | 1,4421934699 | 0,763 |
| 60 | 229 441 | 4 | 1,4421891015 | 0,538 |
| 70 | 312 481 | 4 | 1,4422111860 | 0,696 |
| 80 | 408 321 | 7 | 1,4421908377 | 0,590 |
| 90 | 516 961 | 8 | 1,4421944808 | 0,762 |

- L = 60 reproduce el valor de la ronda 1 (1,4421891, P = 0,54). Confirmado.
- F31-C1 (\|n(80)-n(60)\| < 1e-6): mi diferencia es 1,736e-6 -> FALLA (acuerda con la prediccion P1 del contrato). F31-C2 (ligado en ambas): PASA (P 0,538 y 0,590; \|n-sigma\| < 6e-6), pero 0,538 esta cerca del umbral 0,5. F31-C3 (\|n(80)-n_an\| = 5,0e-6 <= 1e-4): PASA.
- **No hay convergencia en L**: n_eff(L) = 1,4421952 (40, ronda 1), ...935 (50), ...891 (60), ...2112 (70), ...908 (80), ...945 (90). Salta 2,2e-5 entre 60 y 70. El modo de la camisa continua es un modo con fugas (camisa 1,439 < fondo 1,444) hibridado con modos de caja; su autovalor en una caja con Dirichlet oscila con L. Que \|n(80)-n(60)\| sea de 1,7e-6 es casualidad, no convergencia: si alguna pareja de L pasara 1e-6, no significaria que la caja esta convergida. El criterio F31-C1 con solo dos cajas (60, 80) no mide convergencia.
- No he recalculado F3.2/F3.3 (el paso 5 solo pedia F3.1). Su inferencia sobre "modos de nucleo contados" depende de la misma seleccion fragil (P cerca de 0,5, indice del modo cambiante), asi que cualquier \|Delta(N)\| < 1e-5 hay que leerlo con esa cautela: la incertidumbre de caja (>= 1,7e-6, hasta 2e-5) es comparable al umbral 1e-5.

## 5. Riesgos no cubiertos por los criterios

1. Entregables ausentes: B3-r3 y F3-r3 no tienen resultados; el RESULTADOS-tracks-r3.md existente dice "blocked" sin que el solver haya fallado. Hay que relanzar o declarar "partial/no ejecutado".
2. Procesos que mueren sin dejar rastro: ningun checkpoint ni mensaje de error en F3 ni B3; el contrato de F3 promete "se guarda al terminar cada resultado" y no hay ni uno.
3. El criterio B3 (1e-5) mide una propiedad del esquema BPM (dz), no del dispositivo; el umbral no se puede cumplir cambiando el dato (ya medido). Con dz = 0,25 la perdida sigue en 3,7e-5; no se sabe si dz -> 0 llega a 1e-5 (no calculado).
4. Un "pass" de B3 por reducir dz alteraria el esquema, no el dispositivo; el contrato debe decir que dz es parte del criterio.
5. Reloj: la hora escrita en el contrato B3 (07:20) no coincide con el mtime (07:15).
6. Todas las cifras son de un modelo escalar paraxial, sin datos de laboratorio.

## 6. Archivos

- `D:/PROJECTS/.cognition/audit/silice-origin-main/experimentos/verificacion_claude/VERIFICACION-V8.md` (este)
- Scripts y salidas: `.../experimentos/verificacion_claude/v8/` (v8_bpm.py, v8_pert.py, v8_g3.py, v8_f31.py, v8_res.py, y sus JSON y logs).
