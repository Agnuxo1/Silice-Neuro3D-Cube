# Aceleración gráfica aplicable a Silice · 9 de octubre de 2026

La dirección es nuestra red óptica propia dentro del motor3D. Una técnica
se adopta para un subproblema compatible, manteniendo entradas, campo
complejo, fase, detectores y aprendizaje. La comparación debe conservar
precisión y coste total; una cifra de kernel no prueba el sistema completo.

| Técnica | Papel previsto | Evidencia de este proyecto |
|---|---|---|
| Rasterización de triángulos y shaders FP32 | Interpolación y representación del campo P2 | R1 y R2 negativas; P0 auditada; P1 separa rutas de interpolación |
| Batches y geometría preparada | Reutilizar geometría, actualizar amplitudes y fases | Ya presentes en los workers; todos los costes de preparación/lectura se guardan |
| Vulkan | Backend moderno del motor, con comparación equivalente de lectura/precisión | P1 ejecutada y auditada: 21/30 marcas pasan, nueve fallan; no ventaja demostrada |
| Instancing y buffers persistentes | Compartir geometría entre elementos/instancias | Candidatos; requieren medir equivalencia y coste de actualizaciones |
| Lectura asíncrona/pipeline de transferencias | Reducir esperas CPU/GPU y sincronizaciones | Candidato; auditoría y coste extremo a extremo antes de adopción |
| BVH/RTX/OptiX | Intersecciones y caminos geométricos cuando sea válido un modelo de rayos | MEGA-001 heredado sólo verifica CPU/metadata; no pipeline RT óptico validado |
| CUDA/FFT | Referencias de propagación y contraste numérico | Ensayos históricos locales; no sustituyen la red propia ni cierran convergencia global |

El backend Vulkan está plenamente soportado en Blender4.5LTS; OpenGL sigue
siendo predeterminado. Se ejecutó por proceso en la calibración P1,
sin cambiar preferencias globales ni sustituir el ensayo OpenGL congelado.
[Blender4.5LTS](https://www.blender.org/download/releases/4-5/),
[notas técnicas](https://developer.blender.org/docs/release_notes/4.5/eevee/).

OptiX ofrece una canalización de rayos programable con aceleración RTX. Ese
mecanismo resulta pertinente a la búsqueda de intersecciones; su presencia
no aporta automáticamente un modelo de ondas, fase, modos, polarización o
difracción. No se adopta como prueba un resultado de otro proyecto.
[NVIDIAOptiX](https://developer.nvidia.com/designworks/optix/download),
[programación y BVH](https://developer.nvidia.com/blog/how-to-get-started-with-optix-7/).

## Orden de los ensayos

1. R2 terminó con lectura/reloj/cierre correctos, pero 63/84 campos fallan precisión.
2. P1 ejecutó las mismas 30 marcas en OpenGL y Vulkan con prerregistro.
   Uniformes, suma y coordenadas analíticas pasan; smooth falla. Una nueva
   R3 posterior, preregistrada en ce183e71, aprobó 84/84 campos P2 por backend
   con coordenadas analíticas; los 168 crudos se conservan. Es representación
   manufacturada, sin propagación guiada, red funcional o ventaja general.
   [Resultados y costes R3](POINT-03-RENDER-P3-ANALYTIC-RESULTS.md).
3. Sólo tras F1localPASS puede registrarse lectura GPU de su malla y campos
   exactos, conservando ambos detectores. Nunca reemplazar primarias por GIF.
4. BVH/RT y red completa siguen el orden de la tarea1 y requieren presupuestos
   de error/modelo explícitos, entradas iguales y contraste independiente.

No se usa denoising o mejora visual como corrección del campo científico.
Los GIF de arquitectura son ilustraciones, no medidas ni inferencia de una
red entrenada. No hay ventaja general/energética demostrada. Un resultado
negativo se conserva antes de nuevas versiones. Fuentes y criterios quedan
congelados durante cada ensayo, con FIFO, reservaRAM8GiB/floor6, VRAMtotal4,
80C/RSS1,5GiB/unhilo/hijo120s(timer115)/espera1min/deadline13:45UTC.

## Publicación solicitada

El usuario pidió expresamente el9deoctubre publicar todoslos resultados en
GitHubmain y ampliarREADMEconGIFprofesionales. Esta publicación es una
instantánea revisada de investigación abierta; no implica cerrar T96/Q4,
las tareas pendientes, fabricación ni revisión científica externa. Se
preserva el checkout principal local y la historia de fuentes/resultados.
JEV remoto bloqueado; decisiones fallback local explícito.
