# F1: preparación aprobada y condición M2 pendiente

Se generaron cinco fuentes diferenciadas con sintaxis y hashes comprobados,
a partir de M2 intacta. Todavía no hay campos ópticos T96 de F1. La
propagación exige el aprobado local de M2-R1, que sigue en ejecución.

| Control previo | Resultado |
|---|---|
| Siete archivos numéricos | Hashes aprobados; 74049 grados de libertad libres |
| Potencia inicial en norma de masa | 1,0000000000000004, dentro de1e-12 respecto a uno |
| Evaluador frente a exponencial densa | Padé1,214e-14 y Radau2,610e-15, límite1e-10 |
| Error sólo de fase | Rechazado aunque las potencias coincidan |
| Error de amplitud | Rechazado |
| Dos tramos por familia,3DOF | Máximo error1,376e-13, límite1e-10 |
| Hash de campo anterior corrupto | Rechazado en ambas familias |
| Prerrequisito M2 temporal falso | Bloquea antes del manifiesto y del primer trabajador; cero campos |

Los recursos ficticios y el prerrequisito simulado pertenecen sólo a los
controles de software. El fallo provocado de la puerta queda conservado
y etiquetado en `point03_d16_fine_false_gate_controls_20261009`.
No representa un fallo óptico ni una propagación parcial de T96.

El control de entradas registra prerequisite_present=False y
prerequisite_pass=False porque el informe local final M2 no existe todavía.
Es una lectura histórica de preparación. El controlador lo comprobará
dinámicamente antes de permitir campos y no convierte ese falso en aprobado.

Trabajador probado SHA-256:
39b1024a2237edb1938873defd22aaac76e995fdb93adad2e5c7eb3339081456.
K16 existente: f251ae68…, sin regeneración de geometría ni matrices.
Se conservan todos los campos K8 históricos, que no se adoptan como K16.

Partición registrada antes de resultados: tramos512,64Padé y128Radau;
pasos totales32768/65536. Presupuesto nuevo32000s y límite absoluto de la
ventana13:45UTC, sin extender M2. El corte de hijos usa el menor tiempo
restante. Véase [contrato F1](POINT-03-D16-FINE-TIME-CONTRACT.md).

La auditoría local de M2-R1 tendrá salida separada
`local_integrity_audit.json`, mediante
`scripts/audit_point03_d16_mid_recovery_local.py`.
Preserva `integrity_audit.json` remoto y recalcula los96 campos y criterios,
comparando ambas auditorías dentro de1e-12. No ejecutar la CLI original
contra su salida existente, ni editar su fuente congelada para cambiarla.

Controles: `point03_d16_fine_generation_20261009.json`,
`point03_d16_fine_input_integrity_20261009.json`,
`point03_d16_fine_evaluator_controls_20261009.json`,
`point03_d16_fine_worker_controls_20261009/report.json` y
`point03_d16_fine_gate_controls_20261009.json`.
Tarea1 abierta; JEV fallback local por bloqueo remoto retenido.
