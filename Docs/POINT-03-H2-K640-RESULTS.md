# Referencia H2 terminada y contraste K640

7 de octubre de 2026. H2 completo en4290,219s de recuperación; auditoría
independiente PASS de76checkpoints (48retenidos,28nuevos),14fuentes intactas,
entradas/cadenas/potencias brutas y disipatividad verificadas.

H2 **FAIL científico**. Campo reconstruidoN640=0,3329597828900894,
predicción previa0,3329580848002981. Residual1,698089791e-6 frente
límite1,274259159e-6 (factor1,33261). Intensidad reconstruida también
falla:1,708866664e-6 frente1,274777926e-6. Consistencia de referencias,
error temporal directoADI, Gaussianas, cuadratura y presupuesto local
pasan; no sustituir la predicción fallida con estos controles favorables.

J, diagnóstico registrado, aplicado a cinco referencias completas y
consistentes. Indicador seleccionado campoN640=2,48545546e-4;
envolvente distinta=7,86948476e-4. Son estimadores condicionales, sin
cobertura acreditada. No convierten H2 enPASS ni cierran punto3.

K640: detectores lineales registrados817d020, predicciones congeladas
e611a23 antes de medir estos observables; ambas primarias pasan.

| Funcional | Potencia N640 | Residual de predicción | Límite previo | Combinado local |
|---|---:|---:|---:|---:|
| Campo bilineal |0,33280274547140776|7,658786944e-6|1,125882788e-5|2,82041638e-4|
| Intensidad bilineal |0,3328642007882665|7,323667739e-6|7,358839074e-6|2,05679146e-4|

K640 **PASS de todos sus controles registrados**, pero no cierre propio:
reutiliza la trayectoria H2, no es simulación nueva independiente.
La intensidad pasa estrechamente, margen3,51713355e-8; se informa esa
proximidad sin cambiar el límite. Diferencia de detectores6,145531686e-5
incluida en presupuesto; errorADI directo1,3623e-7, referencia5,9629e-11,
cuadratura32/16cero al redondeo reportado. No reclamar precisión mayor
por usar una representación de menor orden ni cota rigurosa.

Se cumple la condición registrada para ejecutar la prueba NUEVA N626:
H2 no cerró, K640 sí pasó; fuentes K62646f3567 anteriores a los resultados
y ninguna entrada/propagaciónN626 hasta esta evaluación. Exigir ambas
predicciones congeladas,28checkpoints y48controles geométricos, sin refit
conN640. Punto3 sigueABIERTO hasta esa evidencia; no barrido modal.

Originales E/G/H1/H2 y errores previos se conservan. Mainpreservado;
JEVfallbacklocal identificado, sin avalremoto ni reintento bloqueado.
