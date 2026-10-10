# Resultados del plan final, ola B (2026-10-11, 10:30 UTC)

Ejecución: `wf_8dcce990-818`. Los tres agentes devolvieron resultados parciales porque sus corridas en segundo plano no terminaron antes de cerrar. Después, el orquestador ejecutó los análisis que ya estaban escritos. Todo es modelo numérico, no medida.

| Tarea | Estado | Resultado | Lectura |
|---|---|---|---|
| B5: convergencia en dz de la pérdida del BPM | **en curso** (recálculo lanzado por el orquestador) | Control: dz = 1 µm da 2,4600e-4 (reproduce r4). Unitariedad sin CAP: 3,8e-13. La pérdida de primer orden del CAP es 3,2e-8 por mm, unas 8000 veces menor que la pérdida medida: el CAP no es la causa. | Pendiente: dz = 0,5, 0,25 y 0,125 µm, y su evaluación con `evaluar_bpm_r5.py`. G3 solo si B3 cumple. |
| D5: 009c con haces de cola controlada (cambio de protocolo declarado) | **no cumple K1** con ningún haz probado | Con dominio 256 µm y absorbente base: w₀ = 6 µm, M = 1,90e-3; w₀ = 8 µm, M = 1,03e-3; w₀ = 12 µm, M = 4,38e-4. La pendiente log-log de M frente a w₀ es −2,15. K2 (cola espectral) cumple: error relativo 4e-12 en la fórmula y Parseval 5e-16. | Extrapolación, no medida: con M ∝ w₀⁻², cumplir K1 exigiría w₀ ≈ 25 µm, que no cabe en un dominio de 256 µm con el absorbente actual. K3 y K4 (malla y paso para w₀ = 12 µm) **no evaluables**: esas corridas no terminaron. El agregado K0 figura como no cumplido aunque 5 de sus 6 subcriterios cumplen; no investigado. |
| T6: solver vectorial de orden 2 con promediado en la interfaz | **puerta no evaluada** (el controlador no terminó) | Escalar con interfaz promediada: n_eff = 1,4421921238 con h = 0,125 µm, frente a 1,4421921655 analítico (error 4,2e-8; con h = 0,25 µm, 1,2e-7). Semivectorial H_y con h = 0,125 µm: n_eff = 1,4421892848. | La diferencia semivectorial − escalar es −2,8e-6, del mismo orden que la separación TE/TM de la ronda 1 (~3e-6). **Es una pista, no una conclusión**: falta la referencia vectorial analítica de HE11 (`vector_step.py`) para decidir si la puerta pasa. |

## Consecuencias

- **BPM:** la pérdida no es absorción del CAP ni depende del dato inicial. Depende del paso temporal. Si al completar dz = 0,125 µm no se llega a 1e-5, el BPM queda como causa no encontrada.
- **009c:** la validación de vacío con K1 no se cumple con ningún haz probado. Para cerrarla hace falta una decisión de protocolo (cambiar el criterio, el dominio o el absorbente), que es tuya, no mía.
- **T6:** la puerta de factibilidad depende de la referencia vectorial analítica. Pendiente.
