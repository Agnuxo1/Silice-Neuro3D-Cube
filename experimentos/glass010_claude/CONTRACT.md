# GLASS-010 — fuga, radiación inicial y contenido modal (Claude, 2026-09-30) — contrato prospectivo, ANTES de código/ejecución

Encargo: Codex, ensayo 2. Pregunta: ¿la camisa mantiene un modo útil o observamos sobre todo un transitorio? No se identifica toda caída de potencia con pérdida modal.
Modelo: escalar paraxial radial m=0 (FD + escalado complejo exterior, radial_ecs.py como base; convención A~exp(iγz), decaimiento ⇔ Im γ>0), λ=1550 nm, n0=1,444. Entrada: gaussiano de amplitud exp(−r²/w²), w=6 µm.
Casos (a, t, δn): (6,6,−0,003), (6,6,−0,005), (6,12,−0,005), (10,6,−0,005), (10,12,−0,003), (15,10,−0,003) [µm].
Geometría sin ambigüedad de muestreo (corrige el radio efectivo 9,9/9,9375/10 µm de 006a): nodos en (j+½)h con h∈{0,25; 0,2; 0,125} µm, de modo que a/h y (a+t)/h son enteros en todos los casos; el código verifica M1: radio efectivo del núcleo (nº de nodos r<a)·h = a dentro de 1e-9 µm, y el del anillo igual.
Variación de UN factor a la vez respecto al nominal (h=0,25 µm, R0=70 µm, Rmax=150 µm, θ=0,6): (i) h→0,2→0,125; (ii) R0 70→90 con Rmax=R0+80 µm; (iii) θ 0,6→0,8.
Modo: candidato con mayor solape ponderado normalizado |⟨ψ_ref,ψ_j⟩|/(‖ψ_ref‖‖ψ_j‖) (producto bilineal con peso r·s·h en la región física r<60 µm) respecto al modo del nominal; el nominal se elige por criterio de 006a (mayor Re γ con fracción en núcleo >0,3 y |Im γ|<3000 1/m). Se reportan γ complejo con signo y los 3 candidatos siguientes.
Descomposición: c_j = (ψ_jᵀWψ_in)/(ψ_jᵀWψ_j); campo(z)=Σ c_j ψ_j e^{iγ_j z}. Observables a z∈{0,5; 1; 1,5; 2} mm, sobre potencia de entrada P_in (física, r<60 µm): P_core total; P_core del modo solo; P_modo (potencia total del modo); resto = radiación inicial + otros modos.
Gates:
 M1 geometría exacta (arriba).
 M2 completitud: ‖Σ_j c_jψ_j − ψ_in‖/‖ψ_in‖ < 1e-6 en la región física.
 M3 solape ponderado >0,999 entre configuraciones para el modo emparejado.
 M4 convergencia por modo (por factor): |ΔRe γ|/|Re γ| < 5e-3 Y (Δpérdida rel <10 % O abs <0,005 dB/cm).
 M5 clasificación en z=2 mm: "dominio modal" si P_core,modo/P_core,total > 0,9; "transitorio" si <0,5; "mixto" en medio. Se reporta para los 6 casos.
 M6 acoplamiento η=|c_0|²·‖ψ_0‖²/‖ψ_in‖²: incertidumbre = máx−mín entre variaciones; se reporta.
 M7 contraste 2D (ADI con observable ponderado + índice por cobertura, nominal 128 µm, dx=0,5 µm, dz=2,5 µm) frente al radial para el continuo (6,6,−0,003), P_core(z) en z=0,5/1/1,5/2 mm: |ADI−radial|<0,01 abs. por z (se reporta por z; 009c advierte pérdida de confianza de la frontera ADI a z>1,4 mm en vacío).
Sin ajustes posteriores. Fallos retenidos. Un hijo <30 s; sin GPU/Blender/instalación.
