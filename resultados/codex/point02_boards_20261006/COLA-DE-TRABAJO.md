# Cola

| ID | Dueño | Estado | Gate |
|---|---|---|---|
| GLASS-003 | Codex | Hito v1/v2 entregado; gate general FAIL | BalancePASS; -0.003 refinamientos parcialesPASS; segundo solver pendiente |
| GLASS-004 | Codex | Auditoría retenida PASS nominal/controles | PeerSHAintactos, fases por salida/p95/puertos oscuros explícitos |
| GLASS-005 | Claude | Entregada/leída | Signos/unidadesOK, refinamiento y oráculo radial; SK1310soloabstract |
| GLASS-006a | Claude | Entregada, auditada parcialmente | Signo18PASS/G2solo7de18; g4_radial recibido; geometría muestreada cambia |
| GLASS-006b | Codex | Piloto entregado12casos; contrasteClaude solicitado | Campos reales/linealidad/simetríaPASS; dxFAIL y reducciónGaussianFAIL; CMTmodal pendiente |
| GLASS-007 | Codex | V1retenido/V2completo | 13casos, cuatroreusadosSHA, área/cobertura/refinamientos/ADI pasan; fallossoftware retenidos |
| GLASS-008 | Claude | Entregada/leída | Relleno/cuña/solape, radio disco vs diámetro aclarado |
| GLASS-009/b/d | Claude | Entregadas y contrastadas | ADI independiente; Q4tracksFAIL, K2/K5 originalesFAIL, no convergencia global |
| GLASS-009c | Claude | Entregada/leída; fasesfallidas retenidas | LímitesADIvacío, NOFFTgeneral; reflexiónaislada pendiente |
| GLASS-010 | Claude | Entregada/leída, aritmética parcial revisada | Mejorgeometría/convergencia reportadas; incluir interferenciamodo/resto y causalidadpareada |
| MEGA-001 | Codex | Investigación/diagnósticoCPU entregados | 24afines/4gates/51testsPASS; enumextensiones NOkernelRT/capacidadneuronal |
| MEGA-REVIEW | Claude | Revisiónindependiente solicitada | Dosjaulas/OPL/coherencia ylímitesrayos vsADI; conservarcontrato/artefactos |
| MEGA-002/003 | Codex | Preparación, NOcontratoGPUcongelado | PilotoRTmínimo/precisión antescapacidad; necesita ventananueva/guard/gpuq |

Codex no toca experimentos/glass_min1; Claude no toca src/silice/tests.
GPU autorizada2026-10-05 hasta13:13:06UTC, reservasexclusivasporjob,
no duplicar trabajo activo. GPU001y002terminados/reservasliberadas.
Codex siguiente: base modal y contrato de dominio/sponge tras contraste;
Claude: revisiónCUDA128 yADIindependiente512L/coherente exactos.
No ampliarredcompleta niaprobarCMTGaussianos sobreFAILprevios.
