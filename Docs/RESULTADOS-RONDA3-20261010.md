# Ronda 3 de la hoja de ruta (2026-10-10, 07:12–08:05 UTC)

Ejecución: `wf_6f986e80-41b` (relanzada con plazos de 08:20 y 08:40 UTC). La primera ejecución (`wf_6370a942-a67`) se detuvo sin resultados porque sus plazos ya habían vencido. Verificaciones V8 y V9. Todo es modelo numérico, no medida.

| Tarea | Estado | Resultado | Verificación |
|---|---|---|---|
| B3-r3: BPM con dato inicial discreto y G3 | **no evaluado** | No existe `resultados_bpm_r3.json`. Los seis logs de corrida son de 0 bytes: las corridas no llegaron a ejecutarse. G3 no se ejecutó. | V8 confirma la ausencia de resultados. Descarta la hipótesis del dato inicial: con E0 discreto (FD) la pérdida es 2,4601e-4, frente a 2,4600e-4 con E0 analítico (diferencia relativa 4e-5). Descarta la absorción del CAP como causa: tasa perturbativa de primer orden de 3,2e-8 por mm. **La causa de la pérdida de 2,46e-4 queda sin explicar.** |
| F3-r3: tracks con fracción de área real y caja convergida | **bloqueado** (0 corridas) | Contrato escrito a 07:15 UTC. Ninguna corrida produjo resultados; el estado es «blocked». | V8 calcula por su cuenta n(L = 60) = 1,4421891 y n(L = 80) = 1,4421908, con diferencia de 1,7e-6, que no cumple el umbral de 1e-6. Es un cálculo del verificador, no un resultado persistido del agente. |
| I3: curvas con seguimiento del modo de núcleo | **parcial**: I3.0 e I3.1 cumplen; I3.2 e I3.3 no | Recto: n_eff = 1,4421919 (error −2,9e-7 frente a la analítica). R = 50 mm: sin variación con L = 40–100. R = 20 mm: diferencia L = 80–100 de 8e-13. R = 10 mm: diferencia L = 80–100 de 1,24e-8, pero entre L = 60 y 80 hay 1,26e-7 y la sucesión oscila en torno a 1e-7. **I3.2 falla:** n_eff crece al bajar R; el contrato de la ronda 1 esperaba lo contrario, y el modelo de índice equivalente lo predice. **I3.3 no establecido.** | V9 confirma I3.1, pero señala la oscilación. Con σ en el recto a L = 120 el núcleo no aparece (S = 0,002), así que la robustez del seguimiento para cajas grandes no está demostrada. |
| D3: diagnóstico del retorno en vacío de 009c | **no cumple K1** | Ninguna de las 8 celdas cumple K1 (≤ 1e-4): M va de 3,6e-3 a 2,1e-2. Cumplen 7 de 19 criterios (K0a–K0e, K2 y K4_w2_d256). El agente atribuye el factor dominante al ancho del haz (w0 de 2 a 4 µm reduce M 4,6 veces). Él mismo señala un artefacto de ventana en la comparación (ventana común desde z = 0,2 mm). | V9 sostiene que, con la cola tardía (z ≥ 1 mm), el factor dominante es el dominio, no el haz. **Diagnóstico contestado.** |

## Lectura

- **BPM:** la pérdida de 2,46e-4 sigue sin explicación. Quedan descartadas dos hipótesis (dato inicial y absorción del CAP). Lo que queda por probar es la discretización del propagador o el contorno periódico, con un test nuevo.
- **Tracks:** ni los números de la ronda 3 ni los de la ronda 2 son utilizables. Con el cálculo del verificador, la caja L = 60–80 no converge al umbral de 1e-6.
- **Curvas:** la convergencia en L está demostrada hasta ~1e-7 para R ≥ 10 mm en este método, con oscilación. El radio crítico no se establece. La tendencia de n_eff(R) va en sentido contrario al que esperaba el contrato de la ronda 1.
- **009c:** ningún diseño de la matriz cumple el criterio de vacío (1e-4). La causa dominante no está resuelta. El propio agente propone una comparación en ventana común, que es el siguiente paso.

## Procesos

- Las corridas en segundo plano de BPM (`r3_runs/`) no llegaron a ejecutarse, pero el agente las dio por «en curso». Lo corrige V8.
- El plazo de la primera ejecución ya había vencido cuando se lanzó. Se relanzó con plazos nuevos.
- La consulta a JEV falló en la etapa local (`local_schema`): las decisiones de método tienen fallback local declarado en los contratos.
