# Punto 3, ensayo G: refinamiento con detector reconstruido

Registro previo: 7 de octubre de 2026. Congelar contrato, runner y evaluador
en Git antes de preparar y propagar. E y B permanecen FAIL; F es diagnóstico.
No relanzar E. Hipótesis: la reconstrucción del funcional y una reducción
adicional de dz permiten satisfacer los mismos criterios de consistencia
numérica, y predecir una malla nueva cuyo campo todavía no existe.

## Modelo y reutilización

Mantener íntegros los parámetros de E: ancho nominal 128 um, lambda1550 nm,
n0=1.444, z=2 mm, 96 trazos de radio1.25 um, anillo6/12 um, dn=-0.003,
amortiguador cuártico4e4 m^-1, gaussiana de cintura6 um y ceros fantasma.
Usar exactamente el Stepper ADI y el backend SuperLU ya auditados en C.
No modificar operadores, usar GPU, alinear fases ni normalizar salidas.

Entradas N256/320/400/500: reutilizar NPZ de E byte a byte. N640: nueva
cobertura analítica con el mismo spec serializado de D y la misma convención
de coordenadas, dx=128um/640. Construir A0/sigma/detector geométrico mediante
las mismas funciones originales; comprobar potencia inicial1±1e-12 y área
del detector pi*(6um)^2 con error relativo<=1e-12.

Verificar cobertura N640: fracciones crudas en [-1e-12,1+1e-12], cierre
geométrico local<=1e-11*dx, únicamente correcciones de extremos; área global
relativa<=1e-12. Contrastar 48 celdas preseleccionadas (16 bordes internos,
16 externos y16 celdas parciales distribuidas lexicográficamente) con la
referencia independiente de D. Exigir calidad de referencia y discrepancia
fraccional<=1e-12. No seleccionar celdas por su error ni omitir rechazos.

## Trayectorias nuevas y orden

| Caso | N | dz (um) | Pasos | Papel |
|---|---:|---:|---:|---|
| g_n256_mid |256|0.3125|6400|primaria nueva|
| g_n320_mid |320|0.3125|6400|primaria nueva|
| g_n400_fine |400|0.15625|12800|control longitudinal nuevo|
| g_n500_fine |500|0.15625|12800|control longitudinal nuevo|
| g_n640_holdout |640|0.3125|6400|predicción prospectiva espacial nueva|

Las otras dos primarias N400/500,dz0.3125 y los dos controles gruesos
N400/500,dz0.625 se reutilizan de E con hashes exactos. Son cuatro
trayectorias reutilizadas y cinco nuevas, todas llegan a2 mm. Conservar
las9, sin seleccionar las favorables. Las5 nuevas suman44800 pasos.

## Observable, criterios y predicción

Usar **ambas** reconstrucciones de F, sin cambiar grados, cuadraturas ni
tolerancias: spline cúbico del campo complejo y spline cúbico de intensidad;
Gauss–Legendre/trapezoidal (64,256),(128,512),(256,1024). Controles gaussianos
de F deben pasar también en N640; cambio de las dos cuadraturas finales
<=1e-8 en cada resultado; diferencia de los métodos en N500/640<=1e-7.

Las4 primarias, ahora todas con dz0.3125, forman r=1.25. Aplicar la función
`assess_values` del evaluador original de E sin modificar sus umbrales:
signos/órdenes positivos, estabilidad20%, residual predictivo10% del último
incremento, q de los controles en[1.8,2.2], radio longitudinal prefijado con
q_min1.8/Fs1.25, presupuesto10%, cuatro esquinas, indicador combinado<=1e-3
y<=1% de la potencia más fina. Aplicar por separado a ambos observables.
Reetiquetar únicamente IDs para pasar los datos a esa función; guardar IDs
reales, fuentes y pasos. No implica aceptar retrospectivamente E.

Antes de iniciar **cualquier** propagación N640, evaluar las4 primarias y
congelar la predicción N640 para cada método. Del último trío (320,400,500):
p=log((P400-P320)/(P500-P400))/log(1.25),
Pinf=P500+(P500-P400)/(1.25^p-1),
Ppred640=Pinf+(P500-Pinf)*(500/640)^p.
Si p no es positivo/finito, registrar predicción nula y conservar igualmente
el nuevo caso. Exigir |P640-Ppred640|<=0.10*|P640-P500|, con diferencia
resoluble>1e-12. No refit con N640. El orden de generación e identidades
deben verificarse en un evaluador que no importe la propagación.

Los cuatro casos de G conocidos antes de N640 no constituyen un holdout
independiente; N640 aporta la nueva comprobación prospectiva. El ajuste de
la predicción es solo extrapolación numérica; no ajuste de parámetros físicos.

## Integridad, recursos y aceptación

Fuentes, contrato, antecedentes E/D/F y entradas congelados por SHA antes de
propagar. Checkpoints enlazados cada200 pasos, campos complex128 finitos,
Pcore reconstruida finita en[0,Ptotal+1e-8], P_in1±1e-12 y potencia final
cruda<=1.001. No imponer monotonicidad L2 por paso. El evaluador recomputa
potencias y hashes; los fallos operativos/científicos se conservan.

CPU aislada de Point01, un hilo; presupuesto total7200s. Preparación
geométrica<=180s; propagación en hijos200 pasos<=35s y límite externo40s.
Reserva4s de retención, controles RAM>1.5GiB/disco>2GiB al empezar/terminar
y cada20 pasos. Registrar muestras y tiempos; no estimarlos como máximos
globales. Evaluación<=120s. Parar tras fallo operativo sin reanudación
automática. Guardar todos los arrays/logs anteriores al fallo.
Una pausa del usuario conserva el checkpoint y detiene hijos propios.

La copia principal permanece intacta. El checkpoint factual de coordinación
puede actualizarse durante el ensayo; los contratos, fuentes científicas y
arrays congelados no. No instalaciones, publicación ni modificaciones peer.

Aceptación local del punto3 solo si pasan ambos observables, todos los
controles, integridad y N640. Un FAIL mantiene el punto abierto. Una
aceptación restringe su alcance al funcional de potencia del núcleo y este
modelo/entrada/perfil/z; no certifica campo complejo/fase/frontera, validez
Maxwell, precisión experimental ni una guía fabricada.

Método contrastado con [NASA, convergencia espacial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html)
y [Hansen–Henningsson, análisis espacio–tiempo](https://arxiv.org/abs/1512.05931).
Sus hipótesis no acreditan automáticamente este perfil discontinuo. Los
umbrales son decisiones locales previas, no normas universales.
JEV: fallback local identificado; bloqueo remoto heredado preservado.
