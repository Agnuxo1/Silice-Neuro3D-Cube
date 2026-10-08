# Estado factual — 8 de octubre de 2026

Complementa el inventario y la actualización del7deoctubre, sin modificar
sus resultados históricos. Trabajos sólo en la copia aislada.

Punto3 T96/Q4 **abierto**. El usuario pidió ejecutar secuencialmente las
22tareas y no pasar a la siguiente sin evidencia suficiente.

Correspondencia de numeración: este «punto 3» de los archivos históricos
es la tarea 1 de la lista actual de 22 tareas. La tarea 3 actual, sobre
frontera, dominio, campo complejo y fase conjuntamente, es posterior.

P1 terminó con auditoría PASS12campos/6fuentes y precisión PASS. La
hipótesis de dominio numérico despreciable FAIL: fijar los fantasmas
Dirichlet±64µm, manteniendo dx/interiores, cambia ambas potencias
~7,234e-5 frente al límite1e-6. Hay una contribución de borde discreto
identificada en N400, sin atribuirle toda la causa del FAIL M1.

P2 terminó5069,011s:auditorPASS87campos,75nuevos/12P1. Referencias y
cuadratura pasan en todas las primarias. Estabilidad de orden de intensidad
FAIL22,57%>20%; no se generó/calcultóM800 en ese ensayo. P2 queda negativo.

P3 terminó14051,339s,221campos auditados. Geometría/referencia/temporal
pasan, pero predicción/orden FAILambos:22,27%/31,46%>20%. El punto3
sigue abierto y todos los registros originales se mantienen.

Nueva investigaciónP4:FEM débil con interfaces conformes. Jerarquía1D
alineada con verdad analítica PASS, mallaT96curva/matrices y detector/
inicialización/amortiguador controlados. Dosfamilias temporalesPadé6/Radau5
contrastadas con referencias densas pequeñas. P4I terminó con 224 campos
auditados: integridad aprobada, precisión temporal fallida por sus dos
cotas PSD del observable. P4I2 añade sólo Padé con 32768 pasos y reutiliza
Radau retenido; está en curso con los mismos límites. Una malla no
certifica convergencia espacial. Detalles en POINT-03-P4I-RESULTS.md.

PreparaciónP5A/B:mallas h0,546875/0,4375µm y todos sus controlesPASS;
h0,35 existente se reutilizará porhashes si precisión temporal aprueba.
h0,28 reservado y sin generar; protocolo espacial y predicción antes de
sus campos. P5C registra la propagación de las dos mallas gruesas, que
sólo empezará si P4I2 aprueba con auditoría independiente.
P5D fija los criterios espaciales antes de las potencias P5C. Su evaluador
superó 11 controles con leyes conocidas y rechazos, sin datos ópticos T96.

Control previo de seno N799 PASS(error2,1477e-13); previsión FDST6958s,
estimación sin garantía. Presupuesto P2 global36000s; sin ampliarlo durante
el ensayo. No confundir ejecución parcial con aprobación científica.

E/G/H/K/L1/M1 conservan sus FAIL. L2 precisión práctica PASS y N1
diagnóstico1D se mantienen con sus alcances. El barrido modal y siguientes
no se han iniciado en este ciclo. Sin muestras físicas, Maxwell completo
ni ventaja funcional demostrados.

JEVfallbacklocal por bloqueo remoto heredado. Laboratorio P2PCLAW
consultado; no se obtuvo un ejecutor óptico verificado ni se realizaron
simulaciones externas. Fuentes/limitaciones en POINT-03-P2-LITERATURE.md.

Informes y contratos:
[P1](POINT-03-P1-RESULTS.md), [P2](POINT-03-P2-RESULTS.md),
[P3](POINT-03-P3-CONTRACT.md),
[P3 resultados](POINT-03-P3-RESULTS.md), [P4 controles](POINT-03-P4-CONTROL-RESULTS.md),
[M1](POINT-03-M1-RESULTS.md), [N1](POINT-03-N1-RESULTS.md).
