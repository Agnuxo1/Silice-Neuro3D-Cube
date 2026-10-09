# M1 completo y auditado: resultado negativo — 7 de octubre de 2026

El ensayo original terminó en 12064,711 s, sin error operativo ni
relanzamiento. Se conservaron sus 90 tramos: referencias exponenciales
19/31 y 40 tramos FDST. El auditor separado recalculó los criterios y
confirmó el resultado negativo. **El punto 3 permanece abierto.**

## Resultado frente a los criterios registrados

Fracciones de potencia del núcleo respecto a la potencia de entrada;
valores del auditor independiente del evaluador original.

| Magnitud | Reconstrucción de campo | Reconstrucción de intensidad |
|---|---:|---:|
| Potencia N767 de referencia | 0,332843620175329 | 0,332886411053931 |
| Predicción congelada | 0,332853320535686 | 0,332896475240848 |
| Residuo absoluto | 9,70036e-6 | 1,00642e-5 |
| Límite registrado | 4,08747e-6 | 2,22103e-6 |
| Predicción | **FAIL** | **FAIL** |
| Nuevo orden observado | 3,22924 | 4,06006 |
| Discrepancia de orden | 29,93 % | 41,58 % |
| Límite de discrepancia | 20 % | 20 % |
| Estabilidad del orden | **FAIL** | **FAIL** |
| Diferencia FDST/referencia en potencia | 1,76645e-7 | 1,76592e-7 |
| Precisión longitudinal práctica | PASS | PASS |
| Indicador total condicional | 1,60087e-4 | 1,06607e-4 |

Un indicador pequeño no revoca los fallos de predicción y orden. El
indicador depende de hipótesis asintóticas que este ensayo no confirmó;
no constituye una cota rigurosa ni un intervalo de confianza.

La diferencia relativa de campo entre referencias es 3,41195e-10;
FDST frente a la referencia fina, 1,98989e-6. La cota por normas del
observable entre referencias es 5,23353e-10 y para FDST, 3,05226e-6.
Los controles globales de referencia, integración longitudinal y
cuadratura pasan. La variación medida entre las cuadraturas 16/32 es
cero a la precisión de cálculo; no es una prueba de integración exacta.

## Integridad y conservación

Auditoría PASS:90campos,4campos primarios anteriores vueltos a medir,
20fuentes y cadenas/hashes. Máximo residuo entre potencia total guardada
y recalculada:2,12053e-14. La geometría pasó48contrastes y área global.
Se conservan ejecución, evaluación y auditoría como archivos distintos.

Contratos prospectivos: controlador/contrato `bbc891d`, predicciones
`60684a5`, auditor `4fbde6e`. La diferencia CRLF/LF de la publicación
inicial está documentada en POINT-03-M1-SOURCE-BYTES.md. Los bytes
efectivamente ejecutados no cambiaron durante M1; ahora las20fuentes
coinciden con Git. No se reescribe el registro anterior.

E/G2/H2/K626/L1 conservan sus fallos originales. L2 sigue aprobado para
precisión longitudinal práctica. No se ajusta ningún umbral M1 después
de conocer este resultado, ni se inicia el barrido modal.

## Interpretación y alcance

Queda refutada la hipótesis operativa M1 de estabilidad/predicción bajo
sus criterios. Los datos no identifican por sí solos una causa única.
La discretización espacial de la geometría, reconstrucción del detector,
cancelación de términos de error y posición discreta de frontera siguen
siendo posibles contribuciones. No atribuir el fallo exclusivamente a
una de ellas sin un contraste que la separe de las demás.

Caso ideal escalar T96, entrada fijada,1550nm,2mm y dominio nominal128µm.
No se valida aquí frontera/fase general, Maxwell vectorial, material
medido ni fabricación. JEV: evaluación local identificada por el bloqueo
remoto heredado, sin recomendación externa nueva.

Evidencia original: `resultados/codex/point03_finer_20261007_M1/`
(`execution.json`, `assessment.json`, `integrity_audit.json`, manifiesto,
entradas y campos). No repetir estas trayectorias para buscar un PASS.

El siguiente trabajo dentro del punto3 será un diagnóstico distinto y
prospectivo con solución conocida; cualquier resultado favorable suyo
no cerrará T96/Q4 ni convertirá este FAIL en PASS.
