# R2: nuevo ensayo P2 después de P0 auditada

Prerregistro posterior a P0 publicada2edbba5. R1run01/run02 y sus fallos
se conservan; no se adoptan ni transforman sus84crudos. Este nuevo ensayo
calcula salidas nuevas con un instrumento calibrado, en carpeta nueva.
F1/S16, sus datos, fuentes y límites no cambian. Banco auxiliar de tarea1;
no inicia tareas2–22, propagaciónT96 ni fabricación.

## Método y criterios que permanecen

Se conserva porSHA la referencia point03_render_reference.py y sus12controles
CPU ya aprobados; no se reejecutan. Misma geometría3D/nodosP2, NODAL,
perturbaciones k0..6, casos single/constructive/destructive/quarter,
resoluciones64/128/256, centros de píxel/origen inferior izquierdo,
blendADDITIVE/profundidadNONE, shader P2/rotación de fase original y
framebufferRGBA32F. Ninguna selección nueva de píxeles o alineación de fase.

Mismos gates científicos R1: máximo complejo<=5e-6, L2relativo<=5e-6 salvo
oscuro, diferencia absoluta de potencia<=5e-6, exterior<=1e-7,
potenciaoscura/potenciasimple<=1e-10, margen de borde2e-6 registrado.
La precisión GPU se comprueba con la referenciaCPUfloat64; no se presenta
como igualdad de aritmética de máquina ni ventaja general de hardware.

## Cambios de instrumento registrados antes de campos

Sólo se incorporan la lecturaBuffer1D antes de copia/reshapeC comprobada
por P0, tiempos perf_counter_ns y cierre del proceso propio tras guardar/
sincronizar el informe y liberar offscreens. El worker y supervisor exigen
P0local_integrity_audit.json fijado porhash con sus seis marcas aprobadas.
Un fallo/alteración del prerrequisito bloquea antes de campos. Perfil/fuentes
nuevos y publicación verificada antes de GPU; históricos intactos enGit.

Doce controlesCPU originales se reutilizan porhash; controles nuevos sólo
prueban rechazo de P0fallida/incompleta/fuera de alcance y tiempos0/inválidos.
No leen T96 ni crudosR1/P0. La auditoría completa local recalcula84campos
desde sus bytes, sin cambiar el umbral original de acuerdo de métricas
1e-14*max(1,valor). Guardar versiones del motor Python3.11.15/NumPy1.26.4
y auditorWindows NumPy2.2.6. Si difieren las métricas más que esa tolerancia,
se conserva el negativo y no se adopta, aunque los gates ópticos aprobaran.

## Costes y ejecución

84pares, siete por caso/resolución; ordenCPU/GPU alternado conservado.
GPU incluye clear, uniforms, dibujo, readback/copia; CPUevalúa misma malla/
suma con geometría preparada una vez. Guardar ns enteros y segundos
derivados, todos los pares, compilación/batch, preparaciónCPU y coste del
hijo/supervisor con arranque. No seleccionar mejor muestra ni excluir costes.
No hayGEMM/TensorCores/FFT/RT ni red entrenada; rasterización y shaders3D.

FIFO/RAM>=8GiB antes/floor6/VRAMtotal<=4GiB/80C/RSSpropio<=1,5GiB/unhilo;
espera<=1min/hijo<=120s(timer115)/worker110/deadline13:45UTC9oct.
Runtime directoC:/Python313/python.exe para guard; cola desde entorno
científico; no PYTHONPATH alBlender. Ninguna compra/instalación o cierre
ajeno. No editar fuentes durante ensayo activo; salidas exclusivas nuevas.
Auditar y publicar también resultados negativos antes de cualquier versión.

P0 no validó P2 retroactivamente. R2, aun si aprueba, sólo comprobaría
representación/interpolación/superposición del campo manufacturado y su
coste de lectura; no propagación guiada, red funcional, energía, ventaja
general o validación física. T96/Q4 abierta. JEVfallbacklocal.
