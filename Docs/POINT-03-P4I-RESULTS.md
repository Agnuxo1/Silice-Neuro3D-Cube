# P4I: precisión temporal todavía insuficiente

El ensayo terminó en 13658,516 segundos. El auditor independiente
verificó sus 224 campos complejos guardados, las cadenas de cálculo,
los hashes, la potencia y los recursos: integridad aprobada.

Se compararon dos familias temporales sobre la misma malla conforme
T96 de 74785 grados de libertad. Padé con 16384 pasos se contrastó
con Radau con 32768 pasos, a una longitud de propagación de 2 mm.
La salida no se renormalizó ni se alineó su fase.

| Criterio registrado | Resultado | Límite | Dictamen |
|---|---:|---:|---|
| Diferencia relativa del campo, norma de masa | 3,14854e-5 | 1e-4 | Aprobado |
| Diferencia de potencia, campo cuadrático | 1,00595e-8 | 1e-6 | Aprobado |
| Diferencia de potencia, intensidad lineal | 6,26142e-8 | 1e-6 | Aprobado |
| Cota PSD del observable, campo cuadrático | 1,024906e-5 | 1e-5 | Fallido |
| Cota PSD del observable, intensidad lineal | 1,592164e-5 | 1e-5 | Fallido |

El dictamen global es **negativo**. La proximidad de las potencias por
sí sola no permite aprobar un ensayo que incumple sus cotas registradas.
Estos resultados y criterios se conservan sin modificación.

El nuevo ensayo P4I2, registrado en el commit b7f837c antes de calcular,
añade únicamente Padé con 32768 pasos. Reutiliza la referencia Radau
retenida y conserva los tres límites. Su dictamen depende de completar
los 128 tramos y auditarlos; mientras tanto está pendiente.

Incluso una aprobación temporal sólo comprobaría precisión práctica en
una malla. El cierre T96/Q4 exige además el nuevo contraste espacial
prospectivo, el muestreo y la sensibilidad de potencia al dominio.
No se ha pasado al barrido modal ni a las siguientes tareas.

Los campos intermedios completos permanecen en la copia aislada local.
La publicación en GitHub incorpora metadatos, informes y campos finales
seleccionados; no equivale a publicar todos los campos intermedios.
El entorno original y el checkout principal se preservan.
