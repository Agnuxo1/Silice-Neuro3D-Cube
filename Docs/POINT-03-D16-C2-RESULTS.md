# D16-C2 y recuperación C2-R1: resultados auditados

La recuperación terminó el 8 de octubre de 2026 a las 22:49 UTC.
El auditor independiente aprobó la integridad de los 64 tramos de Radau
con 65536 pasos y confirmó los cinco criterios temporales prerregistrados.
Se conserva la solución Padé con 32768 pasos de C1, sin recalcularla.

| Criterio | Valor auditado | Umbral | Resultado |
|---|---:|---:|---|
| Diferencia relativa del campo en norma de masa | 1,1133721611e-5 | 1e-4 | Aprobado |
| Diferencia de potencia, detector de campo | 2,7554769577e-10 | 1e-6 | Aprobado |
| Diferencia de potencia, detector de intensidad | 1,8678099212e-7 | 1e-6 | Aprobado |
| Cota de discrepancia, detector de campo | 4,1851757775e-6 | 1e-5 | Aprobado |
| Cota de discrepancia, detector de intensidad | 8,0928754243e-6 | 1e-5 | Aprobado |

Las potencias son fracciones respecto a la entrada normalizada.
Padé: campo 0,3329298439715965; intensidad 0,3323826831443692.
Radau refinado: campo 0,33292984424714417; intensidad 0,3323828699253613.
El máximo residuo de la potencia recalculada fue cero con el cálculo
numérico empleado. Se comprobaron campos complex128, finitud, hashes,
cadena entre tramos, tiempos, recursos y todas las fuentes registradas.

El intento C2 original falló por agotar 900 s de espera de memoria después
de 15 tramos válidos. Su ejecución fallida permanece intacta en
`resultados/codex/point03_d16_refine_20261008/execution.json`.
C2-R1 continuó únicamente los 49 tramos restantes bajo el contrato
registrado en b564095, sin repetir los anteriores, sin espera adicional y
sin reiniciar el presupuesto. El tiempo total fue 6029,079251 s desde
el inicio original, incluyendo interrupción y preparación; límite 22000 s.

La auditoría final se encuentra en
`resultados/codex/point03_d16_refine_recovery_20261008/integrity_audit.json`.
Los campos y sus informes siguen en la carpeta original `R5_65536`;
el manifiesto y la evaluación de recuperación están separados.

Este aprobado establece consistencia temporal entre dos soluciones
discretas en la malla gruesa Duffy16, no una cota del error respecto a la
solución continua. C1 conserva su resultado temporal negativo. La
convergencia espacial, la prueba prospectiva y el control de dominio
siguen pendientes: la tarea 1 / punto 3 T96/Q4 permanece abierta.
M1 intermedia no se ejecutó porque su requisito C1 era falso; una
continuación intermedia requiere un contrato nuevo antes de sus campos.
