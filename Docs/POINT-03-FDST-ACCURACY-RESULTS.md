# L2 completo: precisión práctica aprobada en dos mallas

Contrato9983936 anterior a la única trayectoria nueva N400. Ejecución
completa3225,980s,32tramos/12800pasos; N626 fino reutilizado por hash.
Auditor separadoa576436:32campos leídos,18fuentes intactas, criterios
recalculados. Máxima discrepancia de potencia cruda5,32907e-15.

| N | Campo relativo | Error potencia campo | Error potencia intensidad | Cota y controles respecto a referencia | Resultado |
|---:|---:|---:|---:|---:|---|
| 400 | 6.88801679e-07 | 6.35024986e-08 | 6.35218939e-08 | 1.057151e-06 | PASS |
| 626 | 5.14488636e-06 | 4.21172111e-07 | 4.2103251e-07 | 7.89385208e-06 | PASS |

Campo<=1e-4, ambas potencias<=1e-6, concordancia de campo de referencia
<=1e-9, cuadratura<=1e-10 y cota con controles<=1e-5: todos PASS.
La cota se refiere a referencias discretizadas calculadas, no al continuo.
La concordancia empírica no certifica exactitud ilimitada de la referencia.

L1 conserva su FAIL de orden. E/G/H/K conservan sus propios fallos.
L2 no demuestra orden cuatro ni convergencia espacial y no habilita el
barrido modal. Punto3 permanece abierto. La incidencia de versionado del
control auxiliar de cota se conserva separadamente y no afecta al registro
óptico previo de L1/L2. JEV: fallback local identificado.
