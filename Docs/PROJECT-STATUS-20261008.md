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
cotas PSD del observable. P4I2 terminó y fue auditado: 128 campos nuevos
y 224 retenidos; la cota PSD de intensidad 1,169059e-5 supera 1e-5,
por lo que su dictamen sigue siendo negativo. P4I3 añade sólo Radau
con 65536 pasos y conserva Padé de P4I2; se interrumpió por recursos en
el tramo 75. La auditoría parcial aprobó los 74 anteriores. Se registró
una recuperación sólo de los tramos restantes, manteniendo el presupuesto
original. La primera continuación guardó 15 tramos nuevos y se detuvo
antes del 90 por dos lecturas fluctuantes de RAM. Se corrigió la reserva
para tomar una sola muestra y se auditaron los 89 tramos retenidos.
La continuación 90–256 se detuvo por agotar la espera de memoria:
hay 100 tramos válidos, sin dictamen a 2 mm. Una malla no
certifica convergencia espacial. Detalles en POINT-03-P4I3-RESOURCE-RESULTS.md.

PreparaciónP5A/B:mallas h0,546875/0,4375µm y todos sus controlesPASS;
h0,35 existente se reutilizará porhashes si precisión temporal aprueba.
h0,28 reservado y sin generar; protocolo espacial y predicción antes de
sus campos. P5C registra la propagación de las dos mallas gruesas, que
sólo podía empezar si P4I2 aprobaba: no se ha iniciado. Un eventual
aprobado P4I3 requerirá registrar la nueva dependencia antes de campos.
P5D fija los criterios espaciales antes de las potencias P5C. Su evaluador
superó 11 controles con leyes conocidas y rechazos, sin datos ópticos T96.

Nuevo control de rigidez: triangular8 no certifica las cotas en prototipo
ni malla intermedia. Gauss–Duffy por bloques12/16 frente a24 sí aprueba
en el prototipo; pendientes las otras mallas por recursos. Colab CPU
comprobado con11,65GiB libres mediante prueba genérica; paquete preparado
localmente y transferencia pendiente de autorización específica. No se
han ejecutado datos del proyecto en Colab. Detalles en
POINT-03-DUFFY-AND-RESOURCE-RESULTS.md.

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

## Plataformas propuestas por el usuario — 2026-10-08

BlenderPhotonics732799f y Optics Simulator2b488e2 fijados. Control auxiliar
de espectro angular homogéneo y exportación JMesh: PASS, contrato5f2d9c3.
No se propagó T96 ni se ejecutó Blender/Maxwell. Véase
BLENDER-PLATFORMS-ASSESSMENT-20261008.md. Tarea1 sigue abierta.

Controles Duffy coarse repetido y mid completados con PASS, sin cambiar
contrato97a33b9; intento coarse original preservado. Duffy16 se fija como
regla común antes de nuevas propagaciones. Cotas potencia16–24 <1e-6 en
las tres mallas. Nuevos controles longitudinales/espaciales/dominio pendientes.

D16-C1 nuevo: contrato e2f3cb9, adaptaciones portables3f6e5ad; coarseK16,
P6/R5 ambos32768pasos. Controles densos/evaluador/trabajador manufacturado
PASS, hashes20entradas reales y norma inicial PASS. Ensayo completo sin
iniciar por RAM local insuficiente (1,676GiB). ZIP6,082MB y cuaderno CPU
validados, transferencia/ejecución Colab pendiente de aprobación específica.
Colab reconectado y sólo prueba genérica11,593GiB libres. Véase
POINT-03-D16-PREPARATION-RESULTS.md. No se cierran T96/Q4 ni tareas posteriores.

D16-C1 completo7621,698s/64tramos; ZIP198archivos recuperadoSHA/CRCPASS;
auditoría local y remota integridadPASS, precisiónFAIL por PSDintensidad
1,3491078e-5>1e-5. OtroscuatrocriteriosPASS. X1reproducción primeros1024
pasos Linux/WindowsPASS conMrel≈1,8e-14; no es trayectoria2mm adicional.
M1preparado/noiniciado porque su requisito temporal C1PASS es falso.
D16-C2 prereg3de7556 añade sóloRadau65536 desde misma entrada, conserva
Padé32768 completo porhash y el negativo anterior. Fuente/control3DOFPASS;
CPUlocal iniciado, pendienteevaluación/auditoría. Tarea1sigueabierta.
Véase POINT-03-D16-C1-RESULTS.md para métricas y trazabilidad de transporte.
