# Resultado independiente K626: negativo

La ejecución terminó en 3371,950 s: 28 checkpoints (11 y 17 particiones),
48 celdas geométricas independientes, fuentes y entradas conservadas.
La auditoría independiente pasa. El resultado científico es FAIL y el
punto 3 permanece abierto. No se reajustaron las predicciones congeladas.

| Método | Predicción | Potencia observada R17 | Residuo | Límite |
|---|---:|---:|---:|---:|
| Campo bilineal | 0,3327881552636028 | 0,3328026610406906 | 1,45057771e-5 | 1,12503848e-5 |
| Intensidad bilineal | 0,3328526391824184 | 0,33286676949768584 | 1,41303153e-5 | 7,61571002e-6 |

La diferencia relativa de campo R11/R17 es 5,87269e-10, dentro de 1e-9.
Las diferencias de potencia son 3,90551e-10 y 3,90626e-10: ambas exceden
el límite independiente 1e-10. La cuadratura pasa. Conservar los dos
fallos de predicción y los dos de concordancia de potencia.

Un diagnóstico posterior, expresamente ajeno a la aceptación, reconstruye
el detector cúbico histórico: N626 R17 da 0,3329668172481241, superior a
N640 0,3329597828900894. La variación espacial no monótona existe también
en este detector. No demuestra su causa ni convierte la dispersión en
una cota de error. K640 favorable por sí solo no cierra la convergencia.

Evidencia: `resultados/codex/point03_linear_probe_20261007_K626/` contiene
assessment, execution, manifest, integrity_audit, cubic_diagnostic y
campos originales. No se repitió el ensayo E ni se inició el barrido modal.

Siguiente contraste dentro del punto 3: segundo integrador temporal del
mismo operador FD, con controles conocidos y contrato previo propio.
