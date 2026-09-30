# GLASS-009 — contrato prospectivo: solver 2D Crank–Nicolson/ADI independiente (Claude, 2026-09-30)

Se congela ANTES de escribir o ejecutar el solver. Sin GPU/Blender/instalaciones. Un hilo, límite duro 30 s por proceso hijo, un caso por hijo; no se repite un caso ni se amplía el límite tras fallo (se retiene el fallo).
Modelo (idéntico signo/unidades a Codex): dA/dz = i/(2β0)(∂xx+∂yy)A + i k0 δn A, λ=1550 nm, n0=1,444, β0=k0 n0, escalar paraxial. SIN renormalizar por paso.
Método (distinto de SSFM): Peaceman–Rachford ADI con Crank–Nicolson (Cayley), diferencias finitas de 2º orden, Thomas vectorizado. El potencial i·k0·δn se reparte mitad en cada semipaso. Frontera abierta APROXIMADA y explícita: absorbente numérico σ(x,y) (perfil cuártico, ancho 20 % del semidominio, σmax fijado abajo) — potencia retirada = pérdida NUMÉRICA de frontera, no material.
Perfiles: reconstruidos desde la documentación del contrato 007 (3 coronas, centros radiales 7,25/9/10,75 µm, discos de 1,25 µm, offset π/N en corona impar, unión, máscara r∈[a,a+t), cuña por omisión de centros con |ángulo|<cuña/2), y VERIFICADOS contra `silice.tracks` solo como contraste (no oráculo único): igualdad de máscara píxel a píxel en la MISMA retícula (x=(arange−N//2)·dx).
Malla piloto: 256 puntos, ancho 128 µm, dx 0,5 µm, dz 2,5 µm, 800 pasos (z=2 mm), σmax=4·10⁵ m⁻¹ (amplitud). Resuelve discos de 1,25 µm con 5 px de radio (limitación declarada: contorno en escalera, error de máscara del orden de un píxel).

Controles del método (antes de comparar camisas):
 K1 vacío/difracción: Gaussiano (amplitud exp(−r²/w²), w=6 µm) a z=0,5 mm, δn=0: fracción en r<6 µm vs analítico 1−exp(−2a²/w(z)²), w(z)=w√(1+(z/zR)²), zR=β0w²/2. Gate |Δ|<1e-3.
 K2 fase uniforme: δn=−1e-3 en todo el dominio, mismo z: fracción idéntica a K1 (|Δ|<1e-6) y fase del pico frente a K1 igual a k0·δn·z módulo 2π con |Δ|<1e-3 rad.
 K3 unitariedad: σ=0, dominio sin pérdida a z=0,25 mm: |P/P0−1|<1e-10.
 K4 convergencia propia (perfil continuo): dz 2,5→1,25 µm y dx 0,5→0,4 µm (dominio 128 µm fijo): cada cambio en potencia núcleo/entrada abs<0,005 y rel<10 %.

Comparación (misma geometría y observable potencia_núcleo/entrada a z=2 mm; se reportan todos los casos):
 continuo, 48 trazos (16/corona), 96 (32), 192 (64), 88 (32 con cuña 30°).
 Gate C1: |mío − BPM007| < 0,03 absoluto en cada caso (dominios distintos: FFT periódico+esponja vs ADI+absorbente; la tolerancia refleja eso, fijada aquí).
 Gate C2: orden cualitativo: P(48) < P(88) < P(96) ≲ P(192) ≈ P(continuo) (con "≲/≈" = diferencia <0,03). Si el orden falla se reporta.
 Se compara además el BPM007 con δn refinado solo para informar; no cuenta como gate.
Gate G0 de perfil: máscara idéntica a `silice.tracks` (0 píxeles distintos) en los 5 perfiles; si no, se reporta el nº de píxeles y NO se declara PASS.
Gate operacional: cada hijo <30 s. Si algún hijo lo supera se retiene el fallo, se documenta y se reduce (malla/pasos) solo en un contrato nuevo.
Prohibido: ajustar σmax, umbrales o malla tras ver resultados. Alcance: piloto escalar 2D; no red, no cubo, no fabricación, no Maxwell.
