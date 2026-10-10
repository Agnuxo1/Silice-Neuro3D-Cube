# CONTRATO - BPM escalar paraxial independiente (TAREA B)

Fecha de escritura: 2026-10-10, 03:33 UTC (antes de cualquier calculo).
Agente: Claude (subagente), carpeta experimentos/bpm_claude/.
Naturaleza: modelo numerico. No es un dispositivo ni una medida.

## 1. Hipotesis

- H1. Un propagador escalar paraxial de split-step de Fourier (Strang) con potencial absorbente complejo (CAP) en el contorno propaga el LP01 de la fibra de salto (lambda = 1,55 um, a = 6 um, n1 = 1,444, n2 = 1,439) sin perdida apreciable del modo guiado, y su n_eff implicito por la fase coincide con el analitico dentro de 1e-5.
- H2. Los resultados convergen con dz y con h dentro de los umbrales de este contrato.
- H0 (nula, a refutar). Los errores de dz, h o del muestreo del indice superan los umbrales.

## 2. Modelo y convenciones

- Ecuacion del enunciado: 2 i k0 n_ref dA/dz = lap_perp A + k0^2 (n^2 - n_ref^2) A.
  Se integra como dA/dz = -i/(2 k0 n_ref) [lap_perp A + k0^2 (n^2 - n_ref^2) A - i Gamma A].
- Gamma(x,y) >= 0 es un CAP en contorno: Gamma = G0 t^2, t = clip((s - 28)/12, 0, 1), s = max(|x|,|y|), G0 = 2 k0 n_ref * 0.5 um^-1. Tasa de atenuacion en el borde: 0,5 um^-1.
- Convencion de fase: E = A exp(-i k0 n_ref z). Para un modo guiado A(z) ~ psi0 exp(-i k0 (n_eff - n_ref) z). Por tanto n_eff,impl(z) = n_ref - phi(z)/(k0 z), con phi = arg<psi0|A(z)> desenrollada. Es la misma convencion que deriva de la ecuacion del enunciado; no se cambia.
- n_ref = n1 = 1,444 (referencia en todas las corridas).
- Malla centrada, N impar, nodos x_i = (i - M) h, M = 200 (h = 0,2 um, N = 401) o M = 400 (h = 0,1 um, N = 801). Ventana cuadrada de semilado 40 um.
- Propagador: split-step de Fourier de Strang, periodico en la ventana, con CAP en el contorno. Paso: A <- P_half . IFFT[ D(dz) . FFT(P_half . A) ], con P_half = exp(-i dz V/(4 k0 n_ref)), V = k0^2 (n^2 - n_ref^2) - i Gamma, y D = exp(+i dz K^2/(2 k0 n_ref)). Sin CAP, el paso es unitario.

## 3. Criterios numericos (umbrales fijados ANTES de calcular)

- V0 (verificacion del codigo, unitariedad). Sin CAP, h = 0,2 um, dz = 1 um, 200 um: max |P(z)/P(0) - 1| <= 1e-9.
- C0 (referencia analitica). Mi solucion de la ecuacion caracteristica da n_eff = 1,4421922 con |diferencia| <= 1e-6.
- C1 (B1, solape). |<psi0|psi(1 mm)>|^2 normalizado >= 0,999 (h = 0,2 um, dz = 1 um, indice promediado por celda).
- C2 (B1, n_eff). |n_eff,impl(1 mm) - n_eff,analitico| <= 1e-5.
- C3 (B2, dz). |n_eff,impl(dz = 0,5 um) - n_eff,impl(dz = 1 um)| <= 1e-6 (h = 0,2 um).
- C4 (B2, h). |n_eff,impl(h = 0,1 um) - n_eff,impl(h = 0,2 um)| <= 1e-5 (dz = 1 um).
- C5 (B3, perdida del modo guiado). 1 - P(1 mm)/P(0) <= 1e-5, con CAP activo.
- C6 (B4, dos nucleos, solo informa). Primer maximo local de P2m(z) con 0 < z <= 10 mm, h = 0,2 um, dz = 1 um. Se reportan z_max y P2m,max. pass = maximo encontrado en la ventana. No hay umbral frente a L_c; eso lo contrasta otro agente.
- I1 (sensibilidad, informativo, sin umbral). n_eff,impl a 1 mm con muestreo nodal de n (sin promediar) frente a promedio de n^2 por celda.

## 4. Metodos

- Analitico: LP01 de fibra de salto. psi(r) = J0(u r/a)/J0(u) para r <= a, y K0(w r/a)/K0(w) para r > a. Ecuacion caracteristica u J1(u)/J0(u) = w K1(w)/K0(w), con u^2 + w^2 = V^2 y V = k0 a sqrt(n1^2 - n2^2). n_eff = sqrt(n1^2 - (u/(k0 a))^2).
- Indice: n^2 promediado por celda (subcuadricula 16 x 16 por nodo). Es el caso principal. El muestreo nodal es sensibilidad.
- Overlap: ip(z) = sum conj(psi0) A(z) h^2. P2m(z) = |<psi2|A(z)>|^2 / (<psi2|psi2> <A0|A0>), con psi2 el LP01 centrado en x = +8 um y A0 el LP01 centrado en x = -8 um.
- Prediccion (informativa, no criterio): el BPM paraxial da n_eff,par = n_ref + (n_eff^2 - n_ref^2)/(2 n_ref) = n_eff + ~1e-6.
- Convergencia: dz y dz/2; h y h/2. Comparaciones entre pasos consecutivos.

## 5. Lo que NO afirmo

- No afirmo nada sobre la red 3D, la escritura fs, la fabricacion ni los dispositivos. Es un modelo numerico.
- No afirmo nada vectorial (TE/TM, polarizacion). Es escalar paraxial.
- No afirmo nada sobre L_c ni el acoplador: solo entrego z del primer maximo y su valor.
- No afirmo reflectividad cero del CAP. Solo mido la perdida del modo guiado.
- No copio codigo de src/silice/. La implementacion es independiente y no importa ese modulo.
- No hay datos de laboratorio: las cifras son de un modelo sin calibrar.

## 5b. Enmienda de implementacion (03:50 UTC, antes de cualquier cifra de resultado)

- Motivo: la CPU esta al 87 % de carga por otros procesos y numpy.fft tarda ~170 ms por paso con N = 401. Se cambia el backend de FFT a scipy.fft con workers = 1. El metodo (SSF de Strang), la malla (N impar, h = 0,2 y 0,1 um), la ventana (+-40 um), el CAP y todos los umbrales de la seccion 3 no cambian.
- Verificaciones previas al calculo de resultados: solo se comprobo que el codigo corre y que el n_eff analitico propio da 1,4421921655 (diferencia 3e-8 respecto de 1,4421922, dentro de C0). No se ha mirado ninguna cifra de propagacion.

## 6. Salidas

- experimentos/bpm_claude/bpm.py (interfaz run(...) y propagate(...)).
- experimentos/bpm_claude/verificar_bpm.py (evalua los criterios V0, C0 a C6, I1).
- experimentos/bpm_claude/resultados_bpm.json (cifras y pass/fail evaluados por el codigo).
- experimentos/bpm_claude/log_bpm.txt.
