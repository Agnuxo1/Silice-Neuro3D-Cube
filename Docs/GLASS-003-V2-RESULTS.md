# GLASS-003-v2 — resultado, 2026-09-30 08:42 UTC

Contrato congelado f7b1903 ANTES de ejecutar. Solver sin cambios desde V1.
15 casosCPU9.205s; maxbalance1.74416e-13. JSON íntegro
`resultados/codex/glass003_v2.json`; todos los fallos conservados.

Observable nuevo: potencia_final_en_nucleo / potencia_total_entrada.
Camisa continua6um/radio6um/lambda1550nm/cintura6um/z2mm, supuestos ideales.

| delta_n de camisa | Potencia en núcleo/entrada, dominio192um | Dominio144→192 | dz10→5um | dx0.75→0.5um |
|---|---|---|---|---|
| -0.001 | 1.0902% | PASS | PASS | PASS |
| -0.003 | 33.6642% | PASS | PASS | PASS |
| -0.005 | 65.8075% | FAIL | FAIL | PASS |

Gate general de V2 FAIL; no ocultar filas fallidas. La fila -0.003 satisface
los tres refinamientos separados, pero **no** certifica convergencia
combinada del campo en el dominio192um ni de todas las distancias.
El perfil es ideal/no medido, no se infiere loss_dB/cm ni modo propio.
No asumir -0.005 como mejor diseño fabricable porque confina más en un
ensayo todavía sin convergencia suficiente.

Interpretación local: en V1 el denominador de fracción núcleo/restante
cambiaba con el amortiguador; V2 mantiene referencia a entrada y no borra
ese fallo. Una camisa muy débil deja poca potencia dentro del núcleo;
ampliar contraste cambia mucho el resultado. Esto identifica la medición
necesaria de delta_n/perfil y grosor, no valida una receta láser concreta.

Próximo paso útil: crítica independiente GLASS005 y segundo solver,
comparación con trazos discretos/ranuras y acoplador de dos guías. Escribir
su contrato antes de medir, no trasladar cifras ideales a fabricación.
13testsCPU PASS0.343s. Sin GPU/Blender/instalación/publicación.
