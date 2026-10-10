# CONTRATO-V1 - verificacion independiente y adversarial de A (solver2d), B (BPM), C (radial2)

Escrito antes de ejecutar ningun calculo propio (UTC, ver `date -u` en la cabecera de V1). Plazo 06:20 UTC.
Naturaleza: modelos numericos. Solo CPU, `python -B`, OMP_NUM_THREADS=1, numpy/scipy. Escribo solo en experimentos/verificacion_claude/.
Mi codigo es independiente: no importo solver2d.py ni bpm.py ni copio src/silice. Para C solo importo radial2.py (necesario para re-ejecutar su salida), sin escribir en su carpeta.
Hecho ya observado antes de este contrato (no lo oculto): solo se leyeron contratos, codigo, logs y JSON de A, B y C; en A NO existe resultados.json (el run terminó tras A1_sub_L40_h0.125, ver log_run.txt).

## Hipotesis nulas a refutar (H0 = "la afirmacion falla")
- A1: orden observado en [1,8; 2,2] y error(sub, h=0,125) < error escalonado de referencia (4,2164e-6).
- A3: observable de potencia con cobertura reproduce Gamma analitica con error relativo <= 1e-3 a h = 0,125.
- B1: overlap^2 >= 0,999 y |n_eff_impl - n_eff analitico| <= 1e-5 a 1 mm.
- B2: convergencia en dz y en h.
- C1: error de n_eff del solver de disparo frente a la ecuacion cerrada <= 1e-8 (modelo E) y <= 0,01 Delta (modelo P).

## Criterios (umbrales fijados ahora)
Preregistro (P): mtime(CONTRATO) < mtime(JSON/RESULTADOS) en cada grupo; umbrales del codigo/JSON == umbrales del contrato. Un grupo sin JSON = "sin evidencia persistida" (fallo de entrega parcial), no se da por confirmada ninguna afirmacion que solo viva en un log truncado salvo que mi re-ejecucion la reproduzca.

A (mi solver FD propio, 5 puntos, Dirichlet, n^2 promediado por celda con s=8, L=40):
- VA1a reproducibilidad: |n_eff_mio - n_eff_log_de_A| <= 1e-9 para h=0,5; 0,25; 0,125 (sub). Tambien s=1 (escalonado) frente a su log, <= 1e-9.
- VA1b: e_sub(0,125) = |n_eff_mio - n_eff_analitica(mia, brentq propio)| <= 4,2164e-6 y <= 1e-6.
- VA1c robustez del orden: p_diff = log2[(n(0,5)-n(0,25)) / (n(0,25)-n(0,125))] en [1,8; 2,2] (a L=40, independiente del sesgo de dominio). Ademas triplete fino a L=24 (h=0,25; 0,125; 0,0625): p_diff en [1,8; 2,2]. Orden confirmado solo si ambos cumplen.
- VA1d: sesgo de dominio: |n(L=40,h=0,25) - n(L=60,h=0,25)|; si es mayor que e_sub(0,125), se declara que el error pequeno a h=0,125 incluye cancelacion de sesgos (informativo, sin umbral).
- VA3a: Gamma cerrada vs quad propias: |dif|/Gamma <= 1e-8.
- VA3b: con mi psi (h=0,125) y cobertura exacta por subpuntos s=32, |Gamma_FD - Gamma_exacta|/Gamma_exacta <= 1e-3. Reporto tambien con s=1 y s=8, y el orden entre h=0,25 y 0,125.
- VA3c: control: cobertura aplicada a psi analitica en nodos (aisla el observable); mismo umbral 1e-3.

B (mi BPM propio split-step Strang, numpy.fft; h=0,2 um, N=401, dz=1 um, CAP del contrato):
- VB1a: |n_eff_impl(1 mm) mio - el de B| <= 1e-8 y overlap^2 mio dentro de 1e-8 del de B (misma ecuacion, implementacion independiente).
- VB1b: overlap^2 >= 0,999 y |n_eff_impl - analitico| <= 1e-5.
- VB1c: n_eff por pendiente de fase entre z=500 y 1000 um (independiente del origen del desenrollado): |.-analitico| <= 1e-5.
- VB1d: perdida con CAP a 1 mm: reproduzco 2,46e-4 dentro de 1% (el criterio C5 de B falla; verifico que es perdida real y no error de conteo).
- VB2a: |n(dz=0,5) - n(dz=1)| <= 1e-6 (h=0,2).
- VB2b: secuencia en h = 0,4; 0,2; 0,1; 0,05 (dz=1): cambios sucesivos decrecientes con razon >= 2, y |n(h=0,05) - n_paraxial_pred| <= 3e-7, con n_paraxial_pred = n_ref + (n_eff^2 - n_ref^2)/(2 n_ref) (1,4421932971). Si no, "convergencia solo nominal".
- VB2c: |n(h=0,1,dz=1) - n(h=0,1,dz=0,5)| <= 1e-6.

C (re-ejecucion de radial2.py solo para C1 + calculo cerrado propio):
- VC1a: todas las raices de C1 re-ejecutadas coinciden con resultados_radial2.json a <= 1e-13 (E y P).
- VC1b: mis raices cerradas (brentq propio sobre la ecuacion de log-derivada) coinciden con sus 'closed_neff' a <= 1e-12 y con solver E a <= 1e-8 (C1.1).
- VC1c: modelo P: mis raices cerradas del problema paraxial (Bessel J0/K0 con kappa^2 = 2 b0 (k0 Delta - g)) coinciden con solver_P a <= 1e-9; y error P / Delta <= 0,01 recalculado.
- VC1d (adversarial, orden RK4): con h = 400, 200, 100 nm (E, Delta=0,010, LP01) el error frente a la cerrada decrece con orden observado en [3,5; 4,5] (si el error ya esta en el suelo, se declara saturado y el orden de C3.2 de C queda "no demostrado por orden observado").
- VC1e: conteos de raices: l=0: 1,1,2 ; l=1: 0,1,1 para Delta=0,003; 0,005; 0,010.

## Que NO afirmo
No afirmo nada fisico ni de dispositivo. No evaluo C2 (trinchera) mas alla de leer su resultado. No juzgo la relevancia de los umbrales de A, B, C salvo para marcar umbrales laxos o criterios reescritos.
