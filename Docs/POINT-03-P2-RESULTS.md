# P2 completo: precisión aprobada, prerrequisito de orden negativo

Terminado en5069,011s, sin error operativo ni relanzamiento. Auditor:
87campos revisados,75nuevos y12reutilizados deP1; integridad PASS.
Las cuatro mallas primarias pasan referencia/cotas/cuadratura. No se
generó ni propagó M800 por fallo del prerrequisito. Punto3 sigue abierto.

| Intervalos físicos M | Nodos interiores N | Potencia campo | Potencia intensidad |
|---:|---:|---:|---:|
| 320 | 319 | 0,332133234587353 | 0,332379458387767 |
| 400 | 399 | 0,332445023532911 | 0,332602421297077 |
| 500 | 499 | 0,332624448905541 | 0,332724893812649 |
| 640 | 639 | 0,332746734863589 | 0,332808184539600 |

Todos los fantasmas son±64µm;dx=128µm/M, mismo dato físico interior,
detector y trazos ideales. P1M400 se reutilizó por hashes. Las referencias
en cada malla concuerdan en campo relativo<=5,334e-10 y potencia
<=5,739e-11; cotas por normas<=8,180e-10. Máximo residuo entre potencia
total guardada y recalculada6,66134e-15.

Órdenes de320/400/500 y400/500/640:
- Campo:2,47628546 y2,06970869; discrepancia16,42%,PASS20%.
- Intensidad:2,68490300 y2,07894233; discrepancia22,57%,FAIL20%.

El fallo de intensidad impide aprobar P2. Una referencia temporal precisa
no sustituye la estabilidad espacial. No relajar20% ni ejecutar el punto
fino dentro de este ensayo. Se conservan todos los datos y evaluaciones.

La siguiente hipótesis P3 es distinta y posterior a estos resultados:
contrastar el intervalo fino400/500/640/800, cuyos primeros órdenes están
próximos a2. Su predicción se registra antes de nueva geometría; conserva
M320 como diagnóstico y LOS MISMOS límites finos de P2. Esa selección
posterior de ventana se declara, no se atribuye a la hipótesis P2 ni se
presenta como aprobación retrospectiva. P3 debe tener un dato fino nuevo
y auditoría antes de cualquier conclusión local.

Modelo escalar ideal/dominio fijo; no Maxwell/frontera general/fabricación.
JEVfallbacklocal por bloqueo heredado. Evidencias completas locales en
`resultados/codex/point03_fixed_domain_20261007_P2/`.
