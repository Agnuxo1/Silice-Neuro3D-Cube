# P1: OpenGL y Vulkan ejecutados, ruta smooth negativa

Los dos ensayos nuevos ejecutaron 30 marcas en Blender 4.5.14 LTS / RTX 3090 bajo reserva FIFO. El protocolo 4ef9c1d precede a los 60 crudos. Ambos auditores locales aprueban integridad, fuentes, recursos, métricas a 1e-14, duraciones positivas y cierre normal. Cada backend tiene 21 marcas aprobadas y nueve negativas con umbral 1e-6; la calibración completa no se etiqueta PASS.

| Marca | Máximo OpenGL | Máximo Vulkan | Aprobadas por backend |
|---|---:|---:|---:|
| attribute_none | 5.4836273300e-09 | 5.4836273300e-09 | 3/3 |
| bary_analytic_add1 | 7.1525573797e-08 | 7.1028868343e-08 | 3/3 |
| bary_analytic_none | 7.1525573797e-08 | 7.1028868343e-08 | 3/3 |
| bary_smooth_add1 | 4.5483248929e-05 | 4.5483248929e-05 | 0/3 |
| bary_smooth_none | 4.5483248929e-05 | 4.5483248929e-05 | 0/3 |
| quadratic_analytic_none | 1.6450881968e-07 | 1.3536877108e-07 | 3/3 |
| quadratic_smooth_none | 6.3730345832e-05 | 6.3730345832e-05 | 0/3 |
| uniform_add1 | 5.4836273300e-09 | 5.4836273300e-09 | 3/3 |
| uniform_add2 | 1.0967254660e-08 | 1.0967254660e-08 | 3/3 |
| uniform_none | 5.4836273300e-09 | 5.4836273300e-09 | 3/3 |

Las constantes, atributos constantes y suma aditiva pasan; las coordenadas smooth y sus cuadrados fallan en las tres resoluciones de ambos backends. Las coordenadas analíticas del fragment shader y sus cuadrados pasan. Esto aísla una discrepancia en la ruta de interpolación para estas marcas y respalda estudiar una representación analítica prospectiva. No demuestra una causa única de R2 ni valida retroactivamente sus campos. Vulkan no resuelve la discrepancia smooth en este banco.

| Coste total, segundos | OpenGL | Vulkan |
|---|---:|---:|
| Hijo con arranque | 2.801133900 | 3.348305300 |
| Supervisor | 3.384355500 | 3.986085900 |
| Trabajador | 0.738696000 | 1.719052400 |
| Shader y batches | 0.047073700 | 1.020156700 |

Todos los tiempos por marca se conservan en los informes y el resumen; incluyen uniforms/dibujo/readback/copia. No se deriva speedup de una salida que falla precisión ni de estos dos arranques individuales. No se mide energía ni se demuestra RT, propagación, entrenamiento, red funcional o validación física.

![Calibración GPU auditada](../assets/12_gpu_pipeline_opengl_vulkan.gif)

GIF generado en CPU a partir de auditorías y píxeles ya calculados; todas las escalas son fijas. Muestra instrumento gráfico, no actividad de neuronas. El generador, entradas y seis frames están registrados por SHA.

F1 sigue sin resultados finales recuperados: Chrome se reconectó, pero el entorno asignado contiene sólo sample_data. No se repitieron celdas/campos ni presupuestos. S16 y dominio permanecen pendientes, tarea 1 abierta; JEV fallback local.
