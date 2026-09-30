# Primer hito Codex — 2026-09-30 08:35 UTC

CPU solamente. 11 pruebas propias PASS0.368s, tres ensayos/control de fase,
gaussiano y pérdida; entradas inválidas/deadline/superposición incluidos.
Primer test gaussiano falló0.0015735 porque dominio96um no representaba
el espacio infinito. Se amplió SOLO el dominio del control analítico a192um,
sin relajar umbral1e-5. Falla y corrección retenidas aquí. Primer intento de
guardar report denegado por permisos; repetir ejecución aprobada produjo
archivo nuevo, no se atribuye evidencia al intento sin artefacto.

## GLASS-003-v1

13 casos/variantes en2.928s. BalancePASS, convergenciaFAIL. Nominal camisa
6um/-0.001 a2mm: potencia núcleo/entrada0.012773; potencia total
restante0.32343aprox. Ampliar dominio96→144um cambia la fracción núcleo/
potencia RESTANTE en0.0211478>0.02. No promover gatefallido. Otrosrefinamientos
dz ydx pasaron. Parámetros ideales supuestos, ningún guiado real certificado.
Report `resultados/codex/glass003_v1.json` preservado.

## GLASS-004-v1

Report `resultados/codex/glass004_v1.json`; 0.513s. Cinco hashes peer intactos.
Cos/sin independiente vs CMT maxcampo2.0015e-16. IntensidadDFT4 nominal
errorrelmedio2.82548e-5 conorden[0,2,1,3]. Controlesfasepi/acopladooff
detectados. El campo NO es DFT4 sin fases adicionales: errorcrudo0.6230,
tras diagnosticar fase por salida error1.9455e-5. Esto no invalida su tarea
de intensidad pero obliga a conservar fases al encadenar etapas coherentes.

400 muestras de ruido independiente hipotético porcaso (no piezas reales):

| Ruido sigma | Error medio | p95 | Fracción con error>10% |
|---|---|---|---|
| Fase0.05rad | 5.58% | 9.58% | 3.50% |
| Fase0.10rad | 11.10% | 18.97% | 56.25% |
| kL0.03rad | 5.49% | 9.27% | 3.25% |
| kL0.05rad | 9.13% | 15.35% | 36.75% |

Objetivos<=0.05 excluidos de métrica peer: errores absolutos de esos puertos
retenidos en JSON, no omitidos silenciosamente. No garantía de fabricación.

## Nueva pregunta

Normalizar por potencia superviviente de una frontera absorbente cambia
el denominador al variar el dominio. Preparar V2 con observables absolutos
respecto a entrada y gates propios antes de ejecutarlo. Mantener V1fallido.
CríticaClaude GLASS-005 solicitada. JEVblocked, fallbacklocal, no reintentos.
