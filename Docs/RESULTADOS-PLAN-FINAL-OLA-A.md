# Resultados del plan final, ola A (2026-10-11, 10:17 UTC)

Ejecución: `wf_0d24bcbf-05c`. Contratos nuevos (-r4). Umbrales de rondas anteriores sin cambio. Todo es modelo numérico, no medida.

| Tarea | Estado | Resultado | Lectura |
|---|---|---|---|
| B4: origen de la pérdida del modo guiado (BPM) | **no cumple B3-r4** (≤ 1e-5) | Control reproduce 2,4600e-4 (V0). El contorno no es la causa: con ventanas W = 40, 60, 80 µm, la pérdida cambia solo un 1,45 %. Depende del paso temporal: dz = 1 µm da 2,4600e-4 y dz = 0,5 µm da 7,369e-5 (cociente 3,34). El modo propio del propio esquema pierde 2,4985e-4. | Hipótesis: la pérdida viene de la partición temporal del propagador. **Mecanismo no demostrado.** G3 no ejecutado (condicionado a B3). Siguiente paso: dz = 0,25 y 0,125 µm, con contrato nuevo. |
| F4: convergencia de caja de la camisa continua | **parcial; criterio no evaluable** | Control analítico −6,4e-6 (cumple). Con caja Dirichlet, el modo de núcleo está ligado en L = 60, 80 y 120 µm, pero **no en L = 100** (P máx. 0,43). El criterio de convergencia en L no se puede aplicar. Trazos no ejecutados. | Limitación del método (modo casi ligado con caja de Dirichlet). Hace falta otro tratamiento de la fuga, por ejemplo escalado complejo. |
| I4: radio crítico y signo de I3.2 | **parcial** (I4.0 a I4.2 cumplen; I4.3 no) | Δn_eff(R) = c₂/R², con c₂ = 7367 µm². La predicción analítica coincide con la numérica a 0,03 %, 0,18 % y 0,96 % para R = 50, 20 y 10 mm. El signo es positivo: n_eff sube al bajar R. | Coherente con la perturbación de primer orden del índice equivalente, y **en contra** de lo que esperaba el contrato de la ronda 1. El radio crítico no se establece: el cruce del solape S = 0,9 cae entre 5 y 7 mm según L. |
| D4: 009c en ventana común y factor dominante | **no cumple K1** en ninguna variante | Con ventana común z ∈ [0,2; 2,0] mm, el factor dominante es el ancho del haz inicial w₀ (η² = 0,999996). El dominio aporta η² = 1,2e-6 y el absorbente 2,8e-7. M = 2,06e-2 con w₀ = 2 µm y 4,4e-3 con w₀ = 4 µm. | El retorno parece venir de la cola espectral del haz inicial, no del absorbente. **Sin verificación independiente.** Con K1 tal como está, ningún haz cumple. Redefinir el protocolo de haz es una decisión que hay que declarar. |
| T4: base biortogonal para modos cuasi-ligados | **cumple en el caso sintético** (B1, B2, B3) | Con la base biortogonal, el error es ~1e-15. Con el método A (suma por modo), η = 1,09 a 1,61 en los casos sintéticos: **reproduce la anomalía de GLASS-010**. | Aplicación a GLASS-010 original **pendiente**: hacen falta los modos de trinchera con fuga del solver y su producto. |

## Consecuencias para el plan

- **BPM:** G3 sigue bloqueado. La ronda r5 (dz = 0,25 y 0,125 µm) es el siguiente paso.
- **Tracks:** el método actual no sirve para la convergencia en L. Hay que cambiar el tratamiento de la fuga.
- **Curvas:** el radio crítico sigue sin establecerse. El signo contradice el contrato de la ronda 1, y la predicción analítica es consistente.
- **009c:** la validación de vacío, tal como está definida, depende del haz de entrada. Eso es un problema de protocolo, no del absorbente, y debe decidirse y declararse.
- **Biortogonal:** resuelto en el caso sintético. Falta el caso GLASS-010.
