# P3: contraste prospectivo del intervalo fino con dominio fijo

Nueva hipótesis motivada por P2, no corrección retrospectiva de su FAIL.
P2 auditó87campos con precisión aprobada; su terna gruesa320/400/500
produjo orden de intensidad2,68490 frente a2,07894 en400/500/640,
discrepancia22,57%>20%. Se conservan todos esos resultados y el gate P2.

El intervalo fino400/500/640, antes de datos M800, da órdenes campo
2,06971/intensidad2,07894 próximos al orden esperado2. Pregunta nueva:
¿mantiene el siguiente refinamiento M800 esa ley en el intervalo fijo
400/500/640/800, con predicción congelada y dos detectores? Esta selección
del intervalo nace después de P2 y se declara; no se presenta como la
hipótesis original. Sólo el M800 nuevo proporcionará contraste prospectivo.
M320 queda informado como diagnóstico preasintótico, no desaparece.

Registrar fuente/auditor/contrato y predicción en Git ANTES de generar
geometría M800. No repetir propagaciones P1/P2. Reutilizar sus entradas,
refs y auditorías por hashes, revisándolas de nuevo. Dominio±64µm fijo,
N=M-1; misma geometría ideal T96, muestreo, entrada,1550nm y2mm.
Prerrequisito nuevo:último orden de ambos detectores en[1,8;2,2], referencias
y geometría íntegros/precisos. No exigir que la terna gruesa ya fallida
apruebe; su FAIL P2 permanece. No se conocen campos T96 M800.

Se prolonga el factor de refinamiento800/640=1,25 elegido antes en P2.
Predecir M800 con400/500/640 usando sus espaciados físicos; guardar
potencias,órdenes,fuentes/hashes y commit antes de geometría/cálculo.
No escoger otro M después de conocer su potencia.

Reutilizar sin editar funciones de P2 para geometría analítica, acción
exponencial y FDST. M800:48contrastes geométricos/globales, refs29/41,
FDST25600pasos/64tramos400pasos. Control analíticoN799 ya aprobado por
hash; gaussianas500/640/800 y fases0/2e5/4e5m^-1 antes de óptica fina,
orden[1,8;2,2] e indicador que cubra su error conocido.

Se conservan LOS MISMOS límites finos numéricos de P2:
- Ref campo<=1e-9,potencias<=1e-8,cota observable<=1e-6;quad<=1e-10.
- FDST campo<=1e-4,potencias<=1e-6,cota+consistencia+quad<=1e-5.
- Residuo de predicción<=10%de|P800-P640| para ambos detectores.
- Orden500/640/800 positivo y estable20% respecto400/500/640.
- Indicador espacial1,25*|incremento|/(1,25^min(p,2)-1),sumar temporal,
  ref,quad y diferencia de reconstrucción;total<=1e-3 y<=1%deP800.
- Integridad/finitos/recursos/entradas/cadenas/Gaussianas PASS y auditor
  independiente del evaluador antes de adoptar cierre LOCAL condicionado.

Unhilo,hijos360s/corte370s,RAM>1,5GiB/disco>2GiB,GLOBAL36000s sin
ampliación/recuperación automática. Coste esperado varias horas a partir
de N767 y del controlN799; no garantía. Todos los campos/reportes retenidos.
Si falla cualquier criterio, FAIL científico y punto3 abierto; no relajar
límites ni seleccionar otra terna después de datos. No alinear fase ni
renormalizar salidas.

Alcance de eventual cierre:potencia escalar T96 para el intervalo fino y
dominio fijo. No cota rigurosa/cobertura estadística, no Maxwell/frontera
general/campo/fase/fabricación. E/G/H/K/L1/M1/P2 mantienen todos sus FAIL.
Sólo entonces avanzar al barrido modal. JEVfallbacklocal/bloqueoheredado.
NASA https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html
