# Fe de erratas al CONTRATO (Claude, detectada en la primera ejecución; CONTRACT.md sin tocar, SHA c948f8df…)

Convención A∝exp(iγz) ⇒ |A|²∝exp(−2 Im γ·z): **decaimiento ⇔ Im γ > 0**. El contrato escribió lo contrario (Im γ<0 decae; G1 "Im γ≤0").
La primera ejecución (resultados_v0_signo_contrato.json) evaluó G1 tal como estaba escrito y dio FALSE en todos los casos; se retiene como fallo del contrato, no del solver.
Corrección: G1' = Im γ ≥ 0 (decae o neutro); Im γ < −1e-6·|Re γ| ⇒ crecimiento ⇒ fallo. Pérdida (dB/cm) = +2·Im γ·4.343e-2.
Además: el docstring de radial_ecs.py dice "Perdida = −2 Im g" (mal). Las cifras de GLASS-005 modes.py usaron abs(), por lo que las magnitudes son correctas pero el signo nunca se comprobó: se comprueba ahora (G1').
El resto de gates no cambia. No se ajusta ningún umbral.
