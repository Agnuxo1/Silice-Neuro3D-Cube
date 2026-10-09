# R3: representación compleja P2 aprobada en OpenGL y Vulkan

Los dos ensayos nuevos ejecutaron 84 campos por backend en Blender 4.5.14 LTS / RTX 3090. Las fuentes y perfiles publicados en ce183e71 preceden a los 168 campos. Los dos auditores locales aprueban integridad, precisión, fuentes, recursos, duraciones positivas, cierre normal y acuerdo de métricas a 1e-14 entre NumPy 1.26.4 del motor y 2.2.6 en Windows.

Se mantienen los cuatro casos, siete perturbaciones, tres resoluciones, nodos, fases, máscaras y umbrales originales. El cambio prospectivo calcula baricéntricas analíticas desde gl_FragCoord para el triángulo fijo w=1. R1, R2 y la ruta smooth negativa de P1 permanecen intactos; este aprobado no los transforma ni adopta retroactivamente.

| Criterio | OpenGL | Vulkan | Umbral registrado |
|---|---:|---:|---:|
| Error complejo máximo | 5.1366105143e-07 | 5.8510303351e-07 | 5e-6 |
| L2 relativo máximo | 1.2863053296e-07 | 1.3673972590e-07 | 5e-6 |
| Diferencia absoluta de potencia | 9.0718387913e-08 | 9.0073323022e-08 | 5e-6 |
| Exterior máximo | 0.0000000000e+00 | 0.0000000000e+00 | 1e-7 |
| Razón de potencia oscura | 0.0000000000e+00 | 0.0000000000e+00 | 1e-10 |

Cada backend aprueba 84/84 campos: 21 por caso (una fuente, suma constructiva, suma destructiva y desfase de un cuarto de vuelta). Los 168 NPZ completos se conservan con sus informes y hashes. El L2 relativo no es aplicable al campo oscuro de referencia nula; se conserva como null y se exige la razón de potencia oscura original. No se alinearon fases ni eligieron píxeles después del resultado.

| Coste medido, segundos | OpenGL | Vulkan |
|---|---:|---:|---:|
| Hijo con arranque | 14.693328700 | 6.904298600 |
| Supervisor | 17.707061700 | 7.711604000 |
| Trabajador | 4.366165300 | 3.805669000 |
| Shader y batches | 0.082854700 | 1.805288900 |
| Preparación de geometría CPU | 0.485567700 | 0.011250400 |
| Suma de las 84 evaluaciones CPU | 0.129677800 | 0.081200600 |
| Suma de 84 uniforms/dibujos/readback | 0.177901400 | 0.209987300 |

Las filas representan alcances distintos y algunos costes están incluidos en otros: no deben sumarse todos como costes independientes. El ensayo alterna CPU/GPU y GPU/CPU; todos los pares y siete observaciones por caso/resolución se publican. Son dos ensayos individuales en una máquina compartida, con compilación, arranque y lectura explícitos. No establecen ventaja general ni eficiencia energética del sistema completo.

![Campos P2 complejos auditados](../assets/13_gpu_p2_analytic_fields_v2.gif)

El GIF se genera en CPU desde los campos existentes y auditorías. Muestra, por regla fija, la repetición cero a resolución 256 de cada caso/backend, y el máximo error de todas las 21 muestras de cada caso. Escalas fijas, sin interpolar datos ni presentar actividad neuronal.

**Alcance:** representación y superposición coherente manufacturada P2 en un framebuffer FP32 rasterizado. No comprueba propagación guiada, T96/Q4, modos, entrenamiento, una red funcional, RT, un dispositivo ni validación física. F1 sigue sin copia final recuperada; S16, malla reservada y dominio permanecen bloqueados. Tarea 1 abierta. JEV: fallback local explícito.
