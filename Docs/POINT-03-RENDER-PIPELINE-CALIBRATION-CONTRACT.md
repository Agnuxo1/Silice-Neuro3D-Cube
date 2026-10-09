# P1: calibración prospectiva de interpolación, atributos y suma gráfica

Después de R2 negativo publicado en e2bd442. No transforma ni vuelve a
ejecutar R1, P0 o R2. No modifica F1, sus campos ni presupuestos. Es una
calibración manufacturada auxiliar de tarea 1, sin propagación ni red.
JEV remoto bloqueado; decisión mediante fallback local identificado.

La pregunta es qué etapas reproducen marcas analíticas con error <=1e-6.
Un fallo de interpolación no se presume causa única del error óptico R2.
Se registran las siguientes diez marcas, en 64, 128 y 256 píxeles:
uniform_none, uniform_add1, uniform_add2, attribute_none,
bary_smooth_none, bary_smooth_add1, bary_analytic_none,
bary_analytic_add1, quadratic_smooth_none, quadratic_analytic_none.

Todas usan el triángulo original (-0.8,-0.7),(0.8,-0.7),(0,0.8),
z=0/0.25, w=1, RGBA32F y centros de píxel con origen inferior izquierdo.
Uniformes RGB=(0.137,0.271,0.419), alfa fuente 1. Atributo constante:
mismo RGB en los tres vértices. Bary smooth: atributos unitarios en cada
vértice. Bary analytic: coordenadas calculadas desde gl_FragCoord,
l2=(y+0.7)/1.5; l1=(1-l2)/2+x/1.6; l0=1-l1-l2.
Quadratic: RGB=(l0^2,l1^2,l2^2). Ninguna fase, NODAL óptico o ajuste.

Blend NONE conserva alfa 1. ADDITIVE multiplica RGB por alfa fuente y
suma al destino; conserva alfa destino inicial 0, según código oficial
[OpenGL v4.5.14](https://github.com/blender/blender/blob/v4.5.14/source/blender/gpu/opengl/gl_state.cc).
Una y dos sumas tienen RGB esperado c y 2c, alfa 0. Profundidad/culling NONE.
Referencia CPU float64 independiente; máscara de comparación original
2e-6 en coordenadas baricéntricas, fijada antes de estos resultados. Se
conservan todos los píxeles crudos, incluidos los bordes excluidos del gate.
Máximo en todos los canales/píxeles incluidos <=1e-6, exterior <=1e-7.
Métricas de CPU/worker y auditor independiente deben coincidir a 1e-14.
Los gates ópticos de R2 permanecen intactos y R2 no se adopta.

Dos ensayos independientes registrados ahora: OpenGL y Vulkan, mismas
30 marcas/fuentes/criterios, carpetas nuevas. No reemplazar OpenGL por
Vulkan ni afirmar mejora por disponibilidad. Se fuerza backend con
--gpu-backend opengl/vulkan, opción de
[creator_args.cc v4.5.14](https://github.com/blender/blender/blob/v4.5.14/source/creator/creator_args.cc).
Exigir backend observado y RTX3090; incompatibilidad produce negativo
conservado, sin instalar ni cambiar el motor. No se afirma RT/OptiX.

P0 local PASS fijada por hash es prerrequisito; lector Buffer 1D/copia C,
perf_counter_ns positivo y cierre propio sincronizado. Tres controles
analíticos CPU (nodos/centro/partición) y diez grupos de marcas sintéticas,
rechazo de orientación/canales y entradas inválidas antes de publicación.
No leen T96 ni vuelven a generar controles exclusivos previos.

Publicar y verificar contrato, fuentes, controles y perfiles antes de GPU.
Misma reserva FIFO: RAM >=8 GiB antes/floor6, VRAM total<=4 GiB,80C,
RSS propio<=1.5 GiB, un hilo, espera<=1 min, child120/timer115/worker110 s,
deadline 2026-10-09T13:45UTC. Guard directo C:/Python313/python.exe; sin
PYTHONPATH a Blender, compras, instalación, cierres ajenos o límites nuevos.
Auditar integridad y precisión separadas, publicar también negativos y
todos los costes/30 crudos. No prueba red, propagación, física ni speedup.
