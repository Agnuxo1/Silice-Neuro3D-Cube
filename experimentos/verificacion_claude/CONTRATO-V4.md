# CONTRATO-V4 - verificacion independiente y adversarial de F (tracks), H (observable), I (curvas), K (registro)

Escrito antes de ejecutar ningun calculo propio de V4 (hora en la cabecera de VERIFICACION-V4.md). Plazo 06:20 UTC. Solo CPU, `python -B`, OMP_NUM_THREADS=1, numpy/scipy. Escribo solo en experimentos/verificacion_claude/ con prefijo `v4_`. No importo solver2d.py ni src/silice; mi solver FD es propio (`v4_fd2d.py`).
Hechos ya observados antes de este contrato (no los oculto): lei los cuatro contratos, `log_run.txt` parcial de F (el run de F seguia ejecutandose cuando empece; ver "estado de F" en el informe), `curvas_claude/log_run.txt` y `resultados.json`, `observable_claude/out/h2_stdout.txt`, `registro_claude/*.json`. Mis calculos propios aun no existen.

## Hipotesis nulas (H0 = la afirmacion del grupo es falsa)

### Preregistro (P)
- P1: para cada grupo, mtime(CONTRATO) < mtime(primer resultado). Excepcion declarada si el contrato se edito despues de la primera ejecucion. Limite: un mtime solo prueba la ultima edicion, no el contenido original.
- P2: los umbrales del codigo == umbrales del contrato (comparacion textual de C1..C9, G0..G3, K*).

### F (tracks)
- VF1 (geometria, N distinto): f_union(N) por integracion angular exacta (mi metodo, distinto de la malla fina de F) reproduce f_union_grid de F con error absoluto <= 2e-4 para N en {8,16,24,32,48,64,96}; y para N en {12,20,40,72,128,256,1024} f_union(N) crece monotonamente y f_union(1024) en [0,495; 0,500]. Prediccion de H2 de F: f_union < f_formula para N >= 24 y f_union -> 0,5.
- VF2 (valor espectral, otro N): con mi FD (L=40, h=0,25, s=4) calculo para (i), (iv), (ii, N=24,48,96,192) el peso espectral de nucleo W_m = P(r<=12) de los 40 autovalores mas cercanos a la raiz analitica de cada caso y el centroide n_res = sum(W n)/sum(W) sobre los modos con W >= 0,02. Criterio de tendencia: n_res(ii,N) crece con N y |n_res(ii,192) - n_res(iv)| < |n_res(ii,24) - n_res(iv)|. Criterio de reproduccion: n_core de (i) con mi solver frente al de F en h=0,25: |dif| <= 1e-6.
- VF3 (honestidad de F): cuantos casos (ii) tienen n_core=None en el JSON final de F, y si C6/C7 estan marcados evaluable=false (no pass=true). Un criterio con evaluable=false no puede contarse como "cumple".

### H (observable)
- VH1: con mi cobertura (submuestreo 128x128 en las celdas de frontera, LP01 recalculado con brentq propio, h en {0,4; 0,2; 0,1; 0,05} y TAMBIEN h no conmensurables {6/17,3; 6/34,6; 6/69,2; 6/138,4}) el orden por minimos cuadrados de |O_w - Gamma| esta en [1,8; 2,3] en ambas series, y |Gamma_mia - Gamma_H| <= 1e-12.
- VH2: H1-G3 de H: se reporta el valor y el pass que figura en el JSON de H (el JSON declara H1_G3_PASS=false); compruebo que el resumen de H no lo cuente como cumplido.
- VH3: el orden de H2 (indicador en centro) NO es 1 de forma robusta: reporto el orden en ambas series; criterio informativo.

### I (curvas)
- VI1 (monotonia, C2): D(R) = n_eff(R) - n_eff(recto) con mi FD y selecciones por solapamiento, para R en {10; 20; 50} mm, h en {0,5; 0,25; 0,125}(solo 0,5 y 0,25 si el tiempo apremia) y L en {30; 40}. Criterio: el orden n(50) < n(20) < n(10) se cumple en todas las mallas y dominios, es decir C2 de I falla (n_eff NO decrece al bajar R) de forma independiente de la malla.
- VI2: D(10)/D(20) en [3,6; 4,4] y D(20)/D(50) en [5,5; 7,0] (teoria 1/R^2: 4 y 6,25), y D>0.
- VI3: R = 5 mm: el modo elegido por I tiene P_core = 0 y S ~ 0: un estado de caja. Criterio de refutacion de la validez de C4, C5, C2(n5), C9 a 5 mm: con mi solver (k=20 modos, shift-invert en n_eff recto + 2e-4) existe un modo con P_core >= 0,5 y S >= 0,5, o no existe; informo cual.

### K (registro)
- VK1: d* con kappa de acoplo_paralelo.py llamado directo + brentq propio: |d* - 20,4345| <= 1e-3 um; delta_max = 20 - d* ~ -0,4345 um (K1-C1 falla).
- VK2: fraccion media a d=20 um con semilla distinta (11) y R=2000, 12 celdas: |E_mio - E_K| <= 0,02 en todas las celdas, y |E_mio - E_analitico_K| <= 0,02.
- VK3 (adversarial, kappa): comprobar el prefactor de kappa con un calculo independiente: Delta beta de supermodos de dos nucleos en FD escalar (d = 20 um): kappa_FD = Delta beta / 2; criterio: |kappa_FD/kappa_acoplo - 1| <= 0,05. Si falla, d* y delta_max de K heredan ese error y se dice.
- VK4: K3-C2 es una identidad de diseno (d_min = d* + 1,645 sigma da 0,95 por construccion) y pasa solo por la tolerancia 1e-4 (E_ana = 0,9499996): se anota como no informativo, no como validacion independiente.

## Reglas
- Un criterio mio es PASA/FALLA/NO COMPROBABLE solo si lo evaluo con codigo ejecutado. Umbrales fijados aqui no se cambian. Si el tiempo de CPU (la maquina esta saturada por otros procesos) impide una malla, el criterio queda NO COMPROBABLE o se reduce a la malla ejecutada, y se dice.
- No corrijo nada de los grupos. Solo informo.
