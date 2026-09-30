# GLASS-009c — validación de la frontera absorbente (Claude, 2026-09-30) — contrato prospectivo, ANTES de código/ejecución

Encargo: Codex (programa de 8 ensayos, punto 1). Pregunta: ¿cuánto del resultado procede de la guía y cuánto de la frontera artificial? Se prueba con VACÍO (δn=0), donde existe solución analítica exacta, para aislar la frontera de toda física de guiado. Sustituye al K5 original (mal planteado, retenido FAIL).
Modelo/solver: adi2d.py (SHA en salida), λ=1550 nm, n0=1,444, dz=2,5 µm, 800 pasos (z=2 mm), σmax=4e4 m⁻¹, absorbente cuártico en el 20 % exterior del semidominio. Gaussiano de entrada w0=6 µm (amplitud exp(−r²/w0²)), inclinación transversal k_t = β0·θ con θ ∈ {0; 0,02; 0,05; 0,08} rad (dirigida a +x).
Referencia analítica (sin frontera): A(x,y,z)=N0/(1+iζ)·exp(−((x−xs)²+y²)/(w0²(1+iζ)))·exp(i k_t x)·exp(−i k_t² z/(2β0)), ζ=z/zR, zR=β0 w0²/2, xs=k_t z/β0 (normalización N0 idéntica a la discreta del paso 0).
Configuraciones: dominio nominal (128 µm) y ampliado (256 µm), ambos con dx=1,0 µm (vacío, Gaussiano de 6 µm bien resuelto: N=128 y 256). Control de discretización B5: dominio nominal con dx=0,5 µm (N=256), θ=0. Región útil: r<40 µm (entera por debajo del inicio del absorbente nominal, 51,2 µm). Muestreo cada 40 pasos (20 instantes).
Separación de fenómenos, por instante z:
 · tránsito/cola: z_arr = primer z en que la potencia de la solución ANALÍTICA dentro de la banda absorbente (borde>80 % del semidominio) supera 1e-4 de la entrada; antes de z_arr la frontera no puede influir.
 · error de campo E(z)=‖A_num−A_an‖/‖A_an‖ en la región útil.
 · potencia útil P_u(z) numérica y analítica; potencia total numérica; "retorno artificial" R(z)=max(0, P_u,num−P_u,an) en z≥z_arr.
Gates prefijados:
 B1 (discretización pura) E(z)<1e-3 para todo z<z_arr en todas las configuraciones.
 B2 (confianza tras llegada a la frontera) ventana de confianza = z máximo tal que E<0,02 en todos los instantes hasta él; se reporta por (θ, dominio). Un caso es "confiable a 2 mm" si E<0,02 en todos los instantes.
 B4 en la ventana B2, |P_u,num−P_u,an|/P_u,an<0,01.
 B5 E(z) de dx=0,5 vs dx=1,0 (nominal, θ=0): diferencia máxima <1e-3.
 B6 el dominio ampliado reduce el error máximo respecto al nominal o ambos <1e-3; si no, se reporta la anomalía.
Entrega: tabla de condiciones de confianza y rechazo. Sin ajustar σmax, umbrales ni región tras ver datos. Fallos retenidos. Sin GPU/Blender/instalación; un hijo <30 s.
