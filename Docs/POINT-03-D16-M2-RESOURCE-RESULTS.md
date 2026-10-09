# M2: fallo operativo y campos conservados

M2 terminó el 9 de octubre a las 01:53:07,426068 UTC al alcanzar el
límite de 900 s acumulados de espera por memoria. Se calcularon 32/32
tramos Padé y 51/64 Radau: 83 de los 96 previstos. Tiempo total registrado
10654,7637205 s desde el inicio original. No hubo evaluación temporal
completa y no se atribuye un resultado científico negativo a los campos
que aún faltan. El fallo operativo se conserva sin sobrescribir.

La auditoría parcial independiente aprobó los 83 campos: hashes,
complex128, finitud, cadena de reportes, potencias iniciales y entre tramos,
pasos y recursos iniciales/finales de cada trabajador. Las 25 fuentes
congeladas coinciden con el manifiesto. Residuo máximo de potencia
recalculada: 0 con el cálculo numérico empleado. No se ha auditado aún
el resultado temporal final, que necesita los trece tramos restantes.

El controlador registra wait_s=285,8266042000214, correspondiente a las
esperas cerradas antes del último bloqueo. La condición que abortó suma
la última espera abierta y exige un total <=900. Por tanto esa cifra
parcial no representa espera disponible para una recuperación. M2-R1
no permite espera adicional ni reinicia el presupuesto global.

La reanudación preservó el checkout principal: 333 archivos versionados
y su estado Git sin cambios; 603 productos originales de E sin cambios.
La verificación no certifica todo contenido no versionado del principal.

## Recuperación preparada, todavía sin campos nuevos

[M2-R1](POINT-03-D16-M2-RECOVERY-CONTRACT.md) conserva el trabajador
bd47274d y el manifiesto original dc396b00, y sólo permite Radau 52–64.
Los ocho controles del nuevo controlador aprobaron, incluidos presupuesto,
recursos, dependencia no finalizada y rechazo de salida ya existente.
El auditor se generó como copia independiente revisada; no importa el
evaluador. Los controles de recursos ficticios pertenecen sólo al test
de software y no se usan para la propagación real.

Paquete verificado: 69 633 620 bytes, 202 archivos, SHA-256
146fecfa22ca7d8c0624461f9ffae59d47a049e057b3c86d6f1eb766fe6f05e6.
CRC y todos los hashes internos aprobados. Incluye las fuentes numéricas,
los 83 campos conservados, el fallo y auditoría originales, y el protocolo
de recuperación. Su verificación no significa que se haya ejecutado.

Se creó un cuaderno Colab separado y se midieron recursos genéricos a
las 01:55:46,094603 UTC: Linux/Python 3.13.16, 12 659 486 720 bytes
de RAM disponibles y 93 637 111 808 bytes de disco. No se propagó T96
en esa medición. Sus versiones iniciales (NumPy 2.1.3, SciPy 1.16.3,
psutil 5.9.5) no sirven para el protocolo: se prepara una ruta aislada
con las versiones científicas fijadas antes de cualquier nuevo campo.
La creación inicial de venv falló; se conserva ese fallo de preparación,
sin datos científicos generados por él.

Tarea 1/T96-Q4 abierta. Convergencia espacial, predicción y dominio
pendientes; tareas 2–22 sin iniciar. JEV: doctor local ready, bloqueo
remoto retenido y fallback local explícito.

Evidencia: carpeta original `point03_d16_mid_refined_time_20261008`,
`point03_d16_mid_recovery_controls_20261009.json`,
`point03_d16_mid_recovery_package_20261009/manifest.json` y
`point03_preservation_resume_20261009.json`.
