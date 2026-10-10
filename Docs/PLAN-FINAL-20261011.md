# Plan final del proyecto (2026-10-10 → 2026-10-11, 24 h)

Principio: sin cierres falsos. Cada tarea termina en uno de estos estados: **hecho** (criterio preregistrado cumplido), **fallido** (criterio no cumplido, publicado tal cual), **bloqueado** (con criterio de aceptación y dueño), o **fuera de alcance** (declarado).

## Olas (máximo 5 agentes por ola)

| Ola | Ventana UTC | Trabajo |
|---|---|---|
| A | 08:15 → 10:30 | B4 BPM (propagador y ventana), F4 tracks (convergencia de caja a L ≥ 80), I4 curvas (radio crítico y signo de I3.2), D4 009c (ventana común y factor dominante), T4 base biortogonal (prueba sintética) |
| B | 10:30 → 13:30 | T6 solver vectorial de orden 2 con promediado en la interfaz y contraste TE/TM con δn = −0,003; G3 si B4 cumple; pérdida de curva por modo casi ligado si el seguidor lo permite |
| C | 13:30 → 16:30 | Documentos: revisión de novedad (LITERATURA-NOVEDAD), T19 y T20 reescritas con el antecedente verificado, T5 con el presupuesto actualizado, T12 cerrada como resultado negativo, criterios de aceptación de los bloqueados |
| D | 16:30 → 19:30 | Verificación adversarial de todo lo nuevo, tabla final hecho/fallido/bloqueado, RESULTADOS-FINAL |
| Entrega | 20:00 | Informe a Fran, con margen hasta las 08:00 UTC del 11 |

## Bloqueados que dependen de Fran o de terceros

| Punto | Criterio de aceptación para cerrarlo |
|---|---|
| PDF del artículo SK1310 (*Optical Materials*, 2025) | Texto completo leído. Permite fijar la novedad de la trinchera a 1550 nm. |
| Medidas de cutback a 1550 nm (T9, T13, T14) | Al menos 3 muestras, con IC 95 % de la pérdida, dos polarizaciones, y registro entre caras < 1 µm (1σ). |
| Lazo de control de fase (T15) | Error de transferencia < 1e-2 durante 1 h, con deriva medida. |
| Rendimiento y consumo (T17) | Energía por operación del sistema completo con IC 95 %, frente a un baseline electrónico con los mismos datos. |
| Reproducción independiente (T21) | Un tercero reproduce T2 y T11 con las mismas cifras (tolerancia 1e-6 relativo en el modelo). |
| Seguimiento a 12 meses (T22) | Revisión con indicadores fijados hoy. |
| Acceso a F1 (Colab) y respuesta de Codex (T1, T7) | Recuperación de F1, o declaración formal de que no se recupera. |
| Licencia, visibilidad y Zenodo | Decisión de Fran. |

## Reglas de ejecución

- Cada ola escribe contrato antes de calcular. Los umbrales de rondas anteriores no cambian; si se propone un cambio de protocolo, se declara como tal.
- Cada resultado persiste en JSON con los pass calculados por el código.
- Ninguna evidencia pesada entra en el repositorio (límite de 10 MB; archivo con manifiesto SHA-256).
- Commits por tarea, sin tocar src/silice, tests ni scripts (Codex).
