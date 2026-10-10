# TAREA C — segundo solver radial (disparo + biseccion), contrato prospectivo

Fecha de registro: 2026-10-10, antes de ejecutar ningun calculo (UTC 03:33). Hora limite de entrega: 04:50 UTC.
Autor: subagente Claude (Haiku 5.5), carpeta experimentos/radial2_claude/. Todo es modelo numerico; no hay medida de laboratorio.

## 1. Hipotesis

H1. Un solver de disparo (integracion RK4 desde r=0 con serie de Frobenius, emparejamiento en la frontera con funciones de Bessel exactas: K_l en el revestimiento si el modo es ligado, H^(1)_l si es cuasi-ligado con salida radiante) reproduce las ecuaciones cerradas de LP (escalar exacto) con error <= 1e-8 en n_eff, y es convergente de orden RK4 en el paso h.

H2. El modelo paraxial radial de GLASS-006a (1/(2b0)(psi''+psi'/r) + k0 dn psi = g psi) reproduce los n_eff de LP01 y LP11 de la fibra de salto de 2 capas con error < 1 % de |delta n| frente a las ecuaciones cerradas escalares.

H3. Con el mismo modelo paraxial y la misma geometria de camisa con trinchera (a=6 um; t=6 y 12 um; dn=-0,003 y -0,005), mi solver da el mismo g (n_eff) y la misma perdida que radial_ecs (ECS, nominal N=500, R0=70 um, Rmax=150 um, theta=0,6) del JSON de GLASS-006a, dentro de los umbrales de C2.

## 2. Modelo y convenciones

- lambda = 1550 nm; n0 = 1,444; k0 = 2 pi / lambda; b0 = k0 n0 (mismas constantes que el contrato de GLASS-006a).
- Modelo paraxial (P): psi'' + psi'/r - l^2 psi / r^2 + Phi(r) psi = 0, con Phi(r) = 2 b0 (k0 dn(r) - g), g = k0 (n_eff - n0). A = psi exp(i g z).
- Modelo escalar exacto (E), SOLO para verificar el codigo contra las ecuaciones cerradas: Phi(r) = k0^2 (n(r)^2 - n_eff^2).
- Convencion de perdida: decaimiento <=> Im g >= 0; perdida (dB/cm) = 2 Im g * 4,343e-2. Im g < 0 es crecimiento: se reporta como fallo, no se toma valor absoluto.
- Revestimiento (r > frontera exterior): Phi_out = -2 b0 g (modelo P) o k0^2 (n0^2 - n_eff^2) (modelo E).
  - Modo ligado (Phi_out < 0 real): solucion K_l(q r), q = sqrt(-Phi_out).
  - Modo cuasi-ligado (Phi_out complejo): solucion saliente H^(1)_l(k r), k = sqrt(Phi_out) con Re k >= 0 (rama elegida antes de ejecutar; ver limites).
- Perfil C1: fibra de salto de 2 capas: n(r) = n0 + Delta para r < a, n0 para r > a; a = 6 um; Delta in {0,003; 0,005; 0,010}; n2 = n0.
- Ecuaciones cerradas (escalares exactas, tomadas del enunciado): LP0m: U J1(U) K0(W) - W K1(W) J0(U) = 0; LP1m: U J0(U) K1(W) + W K0(W) J1(U) = 0; U = a k0 sqrt(n1^2 - n_eff^2), W = a k0 sqrt(n_eff^2 - n2^2). Las verifico tambien por derivacion (emparejamiento de la log-derivada en r=a): coinciden.
- Perfil C2: a=6 um (y, secundariamente, a=10 um), t en {3, 6, 9, 12, 18} um, dn en {-0,003, -0,005}; capa 0 <= r < a con n0; capa a <= r < a+t con n0+dn; n0 fuera.

## 3. Metodo (no es el de radial_ecs.py)

- Disparo: integracion RK4 de (psi, psi') desde r0 = 0,02 um (serie de Frobenius hasta el termino r^4) hasta R = a (C1) o R = a+t (C2), con paso h fijo dentro de cada capa (la frontera cae exactamente en un nodo). No hay diferencias finitas ni escalado complejo.
- Emparejamiento con la funcion exterior en R: M(g) = psi'(R) f(R) - psi(R) f'(R), o de forma equivalente F(g) = psi'/psi - f'/f.
- C1 (ligado, real): biseccion en n_eff real sobre M (sin derivadas). Escaneo previo de n_eff para localizar todas las raices.
- C2 (cuasi-ligado, complejo): escaneo en el plano complejo de g (Re g en [k0 dn, -1], Im g en [-100, 600] 1/m), minimos locales de |F|, refinamiento por secante compleja. Se acepta una raiz si |F| residual cumple el criterio de convergencia de abajo.
- Seleccion del modo LP01 en C2: la raiz valida con mayor Re g (igual que en GLASS-006a).
- Verificacion analitica previa: la version escalar (E) del mismo codigo debe reproducir las ecuaciones cerradas de C1 (criterio C1.1). Si no lo hace, el codigo no se usa.

## 4. Criterios numericos (umbrales FIJADOS AHORA)

C1 (fibra de salto de 2 capas, a=6 um, Delta in {0,003; 0,005; 0,010}):
- C1.1 Verificacion del codigo: |n_eff(E, solver) - n_eff(cerrada)| <= 1e-8, para LP01 y LP11 en cada caso guiado.
- C1.2 Error del modelo paraxial: |n_eff(P, solver) - n_eff(cerrada)| <= 0,01 * Delta, para LP01 y LP11 en cada caso guiado. Se reporta el error con cifras aunque falle.
- C1.3 Corte: para Delta = 0,003 (V aproximadamente 2,26 < 2,405) no hay raiz LP11 en (n2, n1), ni en E ni en P. Para Delta = 0,005 y 0,010 existe raiz LP11 en ambos.
- C1.4 Numero de raices LP01: exactamente una raiz guiada en (n2, n1) para cada Delta.

C2 (camisa con trinchera, comparacion con radial_ecs nominal del JSON de GLASS-006a):
- Casos primarios (criterios de aprobacion): a=6 um, t in {6, 12} um, dn in {-0,003; -0,005} (4 casos).
- C2.1 Re g: |Re g(solver) - Re g(ECS)| / |Re g(ECS)| <= 0,5 %.
- C2.2 Perdida: |loss(solver) - loss(ECS)| <= max(0,10 * loss(ECS), 0,005 dB/cm).
- C2.3 Validez del modo: se declara VALIDO si (a) raiz residual |F| convergida (criterio C3.2); (b) Im g >= 0; (c) k0 dn < Re g < 0 (la trinchera es barrera evanescente y el nucleo es oscilatorio); (d) fraccion de potencia en nucleo ∫_0^a |psi|^2 r dr / ∫_0^{a+t} |psi|^2 r dr >= 0,3. Los casos que no cumplen (a)-(d) se declaran NO VALIDOS, con la causa.
- C2 secundario: los 16 casos restantes del barrido (a=6 y 10 um; t=3,9,18 y las otras combinaciones) se reportan con los mismos criterios. No cuentan para la aprobacion primaria, pero se publican con cifras aunque fallen.

C3 (convergencia del metodo):
- C3.1 Paso: con h0 = 0,005 um (nominal) y h0/2, h0/4 para el caso C2 (a=6, t=6, dn=-0,003) y para el caso C1 Delta=0,010 (LP01): |Re g(h0/2) - Re g(h0/4)| / |Re g(h0/4)| <= 1e-6 y |Im g(h0/2) - Im g(h0/4)| <= 1e-3 * max(|Im g|, 1 1/m), o bien |Im g(h0/4)| < 1 1/m.
- C3.2 Orden observado: p = log2(|g(h0)-g(h0/2)| / |g(h0/2)-g(h0/4)|) >= 3,5 (RK4 es de orden 4), salvo que las diferencias ya esten en el suelo numerico (< 1e-9 relativo), en cuyo caso se declara "saturado".
- C3.3 Radio de arranque: r0 = 0,02 um frente a 0,01 um: diferencia relativa en Re g <= 1e-9.
- C3.4 Tolerancia de busqueda: el residual |F| al final de la secante cumple |F| * max(|psi'|/|psi|,1) < 1e-7 (1/m) relativo al modulo de la escala de la log-derivada.

## 5. Lo que NO afirmo

- No afirmo que la camisa de 6 um con trinchera de dn=-0,003 sea una guia fabricable ni que su perdida se corresponda con una fibra real. Es un modelo escalar paraxial radial de un perfil ideal.
- No afirmo validez vectorial, birrefringencia, curvatura, ni efectos de trazos discretos.
- No afirmo que radial_ecs sea la verdad de referencia: la comparacion mide acuerdo entre dos metodos numericos del mismo modelo.
- Los modos cuasi-ligados (C2) se definen por la condicion de salida radiante (H^(1)); no se usa un valor absoluto de la perdida.
- No hago predicciones de laboratorio ni de fabricacion. El resultado es de modelo; cualquier cifra de perdida es prediccion del modelo, no medida.

## 6. Entregables

- experimentos/radial2_claude/radial2.py (solver), run_radial2.py (ejecucion y criterios), resultados_radial2.json (todas las cifras, incluidos fallos).
- Registro de SHA-256 de resultados de glass006a (JSON) y de radial_ecs.py en la salida (solo se leen, no se copia codigo).

## 7. Aclaraciones escritas antes de ejecutar (03:4x UTC; no cambian ningun umbral)

A1. Serie de Frobenius: psi = r^l sum_k a_k r^(2k), con a_0 = 1 y a_k = -Phi a_(k-1) / (4 k (k+l)), hasta k = 3 (termino r^6). En la seccion 3 "hasta el termino r^4" queda sustituido por esta version.
A2. Paso adaptativo cerca del origen: h_eff = min(h, r/40, distancia al siguiente borde de capa), para que el RK4 no tenga pasos grandes frente a 1/r. La convergencia de C3 se mide con h, el paso maximo.
A3. C1.4 (conteo de raices): el criterio correcto es que el numero de raices del solver coincida con el de las ecuaciones cerradas para cada l (LP0m y LP1m). Para Delta = 0,010 (V aproximadamente 4,13) hay LP01 y LP02 en l=0 y LP11 y LP12 en l=1 (LP12 no: su corte es V=5,52, luego no). Los errores de C1.1 y C1.2 se aplican a LP01 y LP11; las demas raices se reportan sin criterio de aprobacion.
A4. C3.4 operacional: residual relativo rF = |F| / (|psi'/psi| + |f'/f|) <= 1e-7, con F = psi'/psi - f'/f en R.
A5. Escaneo complejo de C2: Re g en [k0 dn, -1] y Im g en [-100, 600] 1/m, malla 150 x 141; minimos locales de |F| y secante compleja vectorizada.
