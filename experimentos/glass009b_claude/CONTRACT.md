# GLASS-009b — observable con área parcial de píxel (Claude, 2026-09-30) — contrato prospectivo, congelado ANTES de escribir/ejecutar

Hipótesis (formulada en 009, post-hoc): buena parte del fallo de K1 y de K4-dx se debe a que el observable "potencia en r<a" cuenta píxeles enteros con r²<a² (a=6 µm: área 0,9660 del círculo exacto a dx=0,5 µm; 0,9974 a dx=0,4 µm). 009b la pone a prueba con datos NUEVOS, sin reutilizar los gates fallidos de 009 (que permanecen FAIL).
Cambio único: peso de área del núcleo w(i,j)=fracción del píxel con r<a (supersampling 16×16), observable Σ w|A|² dx²/P0. El solver (adi2d.py, SHA en salida), λ, geometría de perfiles (discos 1,25 µm, 3 coronas), σmax=4e4 m⁻¹, dz=2,5 µm, 800 pasos (z=2 mm) y dominio 128 µm NO cambian. El perfil de índice se sigue pixelando con la máscara escalonada (no se pondera); su efecto se mide, no se corrige.
Casos (un hijo <30 s cada uno, dx=0,5 µm: N=256; dx=0,4 µm: N=320; el caso dx=0,4 de 800 pasos se parte en 2 trozos como en 009): 
 K1w: vacío δn=0, z=0,5 mm (200 pasos), dx∈{0,5; 0,4}. 
 Cw: perfil continuo, z=2 mm, dx∈{0,5; 0,4}. 
 T96w: 96 trazos (32/corona), z=2 mm, dx∈{0,5; 0,4}.
Gates:
 P4 área: |Σ w dx² − πa²|/πa² < 1e-4 para ambos dx.
 P1 K1w: |numérico ponderado − analítico 1−exp(−2a²/w(z)²)| < 1e-3, en ambos dx.
 P2 Cw: |P(dx=0,4) − P(dx=0,5)| < 0,005 absoluto y <10 % relativo.
 P3 T96w: mismos umbrales que P2.
Se reportan también los valores SIN ponderar de los mismos campos (comparación), y todos los fallos. Si P2/P3 fallan tras corregir el observable, la causa restante es el escalonado del perfil u otra fuente de dx, y no se declara resuelto.
No se relajan umbrales. No se toca src/, tests/ ni resultados de Codex. Sin GPU/Blender/instalación.
