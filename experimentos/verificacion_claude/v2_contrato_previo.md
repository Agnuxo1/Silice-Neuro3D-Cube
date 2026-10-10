# Plan de verificacion V2 (escrito antes de calcular, 04:15 UTC aprox.)
Umbrales de refutacion fijados ahora:
- R1 (kappa_FD independiente, FD propio): |kappa_FD_propio(h->fino)/kappa_modelo_propio - 1| < 0.01 para d=14,16,20.
- R2 (independencia de malla): el cociente kappa_FD/kappa_modelo varia < 0.005 (absoluto) entre h in {0.2,0.15,0.1} con s_sub=16 y entre las mallas con centros fuera de nodo (h=0.15).
- R3 (kappa_modelo propio): integral propia (rejilla cartesiana + dblquad) coincide con acoplo_paralelo.kappa a <1e-4 relativo.
- R4 (BPM): kappa extraido del ajuste sin^2 de P2(z) con BPM propio, d=14, dz en {0.5,2,5}, coincide con kappa_FD (G1) a <2 % y z_max a <5 % de L_c; dependencia en dz < 1 %.
- R5 (H-T8-1): P2(20 um,10 mm)=sin^2(kappa*L) con kappa_FD propio > 0.10 (refuta) ; y P2_BPM(10 mm) > 0.10.
