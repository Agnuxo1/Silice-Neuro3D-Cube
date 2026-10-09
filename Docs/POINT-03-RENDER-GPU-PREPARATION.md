# Preparación del banco gráfico R1 — 9 de octubre de 2026

La petición nueva del usuario fija la investigación de la red dentro del
motor 3D como dirección del proyecto. Los controles CPU/FEM conservan su
papel de referencias para comprobar el campo y la precisión. Los trabajos
de la lista siguen en orden: T96/Q4 permanece abierta.

Se preparó el contrato R1 y un worker Blender con rasterización de
triángulos 3D y fragment shader para campo P2 complejo. Su supervisor
requiere reserva FIFO, fuentes/executable fijados, RAM y VRAM suficientes,
deadline y corte independiente del hijo. El auditor reconstruye todos los
píxeles y todos los gates; un resultado parcial no se adopta como completo.
El banco no contiene una red funcional ni propaga T96.

## Evidencia realizada

- Doce grupos de controles CPU aprobados: propiedad nodal, partición de
  unidad, polinomio cuadrático complejo, tres interferencias, cinco grupos
  de entradas inválidas y rechazo de alteración de fase. No se importó GPU.
- Cinco fuentes Python compilan; eso no comprueba compilación GLSL.
- Ejecutable Blender 4.5.14 instalado fijado por SHA en los perfiles.
- Preflight local 07:05UTC: RAM libre 6,5153 GiB <8 GiB; VRAM usada
  0,7158 GiB; temperatura 27 C. Resultado resource_block_retained;
  ningún Blender/worker GPU iniciado por este ensayo.
- Perfil preparado v1 conservado. v2 añade un timer independiente de
  115 s, dentro del máximo declarado de 120 s; sin datos GPU entre versiones.
- F1 continúa sin editar: lectura fresca 07:06UTC Padé64/64 y Radau18/128,
  total82/192 reportados, elapsed13400,241755703 s. Sin dictamen final.

Los intentos de lectura web de API4.5 devolvieron403; los ejemplos
primarios indexados se conservaron como documentación, no como prueba de
compatibilidad del ejecutable. Un import auxiliar de requests falló porque
no está instalado; se usó urllib sin instalación, cuyo acceso también dio403.
El control Inf emitió una advertencia NumPy al construir una entrada
deliberadamente inválida; el rechazo pasó. No hubo campos T96 en estos pasos.

## Archivos y continuación

Perfil vigente: resultados/codex/point03_render_profile_v2_20261009.json,
SHA ad2475ff795a3cb540a226974c57c7ace9bbe340a9fae9c93bc46d8f24c42c54.
Controles: point03_render_reference_controls_20261009.json.
Preflight: point03_render_preflight_20261009/guard.json.

No repetir controles exclusivos. Tras publicar y verificar fuentes y perfil,
volver a comprobar recursos con una carpeta NUEVA para el preflight. Sólo
si cumple RAM>=8 GiB y la cola autoriza turno, ejecutar una única reserva:

```text
python D:/PROJECTS/.cognition/gpu_queue/gpuq.py run --name Silice:R1-raster --vram 2 --ram 8 --max-wait 1 --cwd D:/PROJECTS/Silice-Neuro3D-Cube-work-20261006 -- python scripts/guard_point03_render_gpu.py --profile resultados/codex/point03_render_profile_v2_20261009.json --out resultados/codex/point03_render_gpu_run01_20261009 --published-commit COMMIT_VERIFICADO
```

Ambos python deben ser el entorno científico Windows existente. Nunca
rebajar la reserva para aprovechar VRAM libre ni interferir con otro proyecto.
Al completar: audit_point03_render_gpu.py --out carpeta_del_ensayo. Publicar
también resultados negativos, filas crudas y costes con arranque/readback.
La tarea1 sólo se cierra con sus propias pruebas temporal/espacial/dominio.
JEV fallback local; no consulta remota ni atribución de resultados de otra red.
