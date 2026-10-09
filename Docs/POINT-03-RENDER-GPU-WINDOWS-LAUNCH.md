# R1: identidad del supervisor en Windows

Prerregistro del segundo intento, posterior al bloqueo auditado del primero.
Ningún Blender, shader ni fotograma se ejecutó en run01. No se modifican
el contrato gráfico, seis fuentes congeladas, gates, resoluciones,
repeticiones, costes ni límites. F1 y S16 permanecen intactos.

## Fallo conservado y diagnóstico

run01 obtuvo reserva FIFO y RAM libre10,3341GiB, pero el supervisor bloqueó
antes de lanzar Blender: own live FIFO reservation required. Su guard.json
se conserva. El auditor completo devolvió exit1 porque no existe
render_result.json; stdout/stderr y blocked_integrity_audit.json conservan
el fallo y verifican cero archivos de fotogramas, sin aprobación completa.

Un diagnóstico CPU bajo reserva, sin GPU, observó que el lanzador del venv
Windows tenía PID4228, registrado como child_pid de la cola, y añadió el
runtime PID28008 cuyo padre era4228. La comprobación estricta exigía
child_pid=PID del supervisor y parent_pid=PID de la cola. No se cambia esa
comprobación ni se edita gpuq compartido.

Se registra ejecutar el supervisor directamente con el intérprete base
instalado C:/Python313/python.exe: Python3.13.7 y psutil6.1.1 verificados.
El hash de psutil/__init__.py coincide con el del entorno científico.
El perfilv3 fija el ejecutable por SHA. No se exporta PYTHONPATH hacia
Blender: el motor conserva su Python y NumPy propios. El supervisor sólo
usa psutil; la referencia CPU del ensayo sigue dentro del Blender fijado.
Las seis fuentes y el ejecutable Blender coinciden con perfilv2 publicado.

El primer diagnóstico con intérprete directo agotó un minuto de espera
porque otro proyecto tomó la cola. direct_base_output.txt conserva el
resultado negativo; su AssertionError significa gate no satisfecho,
no validación de identidad. No se amplía esa espera ni se interfiere.

## Gate antes del segundo intento

Cuando haya recursos, ejecutar un NUEVO diagnóstico CPU con salida nueva:
la cola conserva su invocación habitual y el comando hijo utiliza
C:/Python313/python.exe para probe.py ya guardado. Exigir a la vez
holder.child_pid=self_pid, holder.pid=parent_pid y horas de creación
consistentes (<2s), con GPUQ_HOLDER=1 y ninguna ejecución GPU.
Verificar de nuevo los hashes del runtime, perfil y fuentes. Un timeout,
fallo o identidad distinta mantiene bloqueado run02.

Después de publicar/verificar esta preparación y satisfacer el gate:

```text
D:/PROJECTS/.cognition/silice_fem_env_20261008/Scripts/python.exe D:/PROJECTS/.cognition/gpu_queue/gpuq.py run --name Silice:R1-raster-run02 --vram 2 --ram 8 --max-wait 1 --cwd D:/PROJECTS/Silice-Neuro3D-Cube-work-20261006 -- C:/Python313/python.exe scripts/guard_point03_render_gpu.py --profile resultados/codex/point03_render_profile_v3_20261009.json --out resultados/codex/point03_render_gpu_run02_20261009 --published-commit COMMIT_VERIFICADO
```

La carpeta run01 nunca se reutiliza. Reserva8GiB, floor6, VRAMtotal4,
80C, RSS1,5GiB, hijo120s/timer115s, espera1min y deadline13:45UTC siguen
vigentes. No existen campos calculados que repetir. El auditor completo
se ejecutará sólo sobre run02 y conservará cualquier negativo. No se
atribuye propagación guiada, red funcional, RT, ventaja general/energética
ni validación física a este banco.

## F1 y conexión

Última lectura fresca confirmada07:45UTC: Padé64/64, Radau32/128,
96/192 campos reportados; no auditoría completa ni dictamen final.
Chrome dejó de estar disponible en computer-use a08:00; el inventario
mostró sólo navegadores internos. No se puede certificar desde aquí el
estado actual de Colab ni renovar handoff; no se relanzó ninguna celda.
Se solicitó restablecer la conexión al cuaderno existente.

JEV: fallback local explícito por el bloqueo remoto heredado.
