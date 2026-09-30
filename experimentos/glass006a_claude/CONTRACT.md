# GLASS-006a — contrato prospectivo (Claude, 2026-09-30, ANTES de ejecutar)

Pregunta: ¿cómo escala la fuga del modo cuasi-ligado de una camisa **continua ideal** con grosor t, radio a y δn?
Es cota inferior de la fuga de una camisa real de trazos discretos (GLASS-007 lo pondrá a prueba). No es receta ni pérdida certificada.
Modelo: escalar paraxial radial m=0 (radial_ecs.py, SHA registrado en la salida), λ=1550 nm, n0=1,444. Solo CPU, un hilo.

Barrido: a∈{6,10} µm; t∈{3,6,9,12,18} µm; δn∈{−0,003,−0,005} (20 casos). Se reportan TODOS, incluidos los sin modo.
Modo: autovalor de mayor Re γ con fracción de potencia en r<a > 0,3 y |Im γ|<3000 1/m. Se reportan γ **complejo con signo** y los 3 candidatos siguientes. Convención A∝exp(iγz): decaimiento físico ⇒ Im γ<0; **Im γ>0 ⇒ crecimiento ⇒ fallo de ese caso** (no se toma valor absoluto).
Refinamientos (config): N=500,R0=70,Rmax=150,θ=0,6 (nominal) vs N=800,θ=0,8 vs N=700,R0=90,Rmax=200,θ=0,5.
Identificación de modo por solape del vector en región física, no por orden.

Gates (fijados antes de medir):
G1 signo: Im γ ≤ 0 para todo modo cuasi-ligado.
G2 convergencia por modo: pérdida (dB/cm) entre configs: cambio relativo <10 % O absoluto <0,005 dB/cm; Re γ cambia <1 %.
G3 predicción falsable de túnel (WKB): κ²=2β0(Re γ − k0δn) (β0=k0n0); para t creciente con a y δn fijos, loss(t1)/loss(t2) ≈ exp(2κ(t2−t1)) con desacuerdo <factor 2 en el rango donde ambas pérdidas >0,005 dB/cm y G2 pasa.
G4 consistencia con Codex: fracción de potencia en núcleo a z=2 mm para Gaussiano w=6 µm, a=6,t=6,δn=−0,003 vs BPM 007 continuo (0,3488, dominio 128 µm, dz 2,5 µm): |Δ|<0,03 abs. Diferencia se reporta sea cual sea.
No se reajustan umbrales tras ejecutar. Fallos retenidos en resultados.json.
