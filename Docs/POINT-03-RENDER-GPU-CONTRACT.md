# R1: campo complejo mediante rasterización en Blender

Prerregistro de preparación del 9 de octubre de 2026, posterior a la
petición explícita del usuario de investigar las ventajas del motor 3D.
Pertenece al banco auxiliar de representación de campos de la tarea 1.
No cambia F1, sus entradas, sus fuentes, su presupuesto ni S16. No inicia
el barrido modal, una nueva propagación T96 ni una red física.

## Pregunta y mecanismo

¿Puede el pipeline gráfico de Blender conservar la interpolación P2 y la
superposición coherente en un framebuffer de coma flotante, y con qué
coste completo frente a la misma evaluación CPU?

Se usan triángulos 3D, atributos por vértice, rasterización, interpolación
baricéntrica y un fragment shader propio. Sus canales R/G almacenan las
partes real/imaginaria del campo; no son colores sujetos a exposición o
tonemapping. La suma aditiva conserva amplitudes antes de formar |E|².
Se desactiva profundidad: una oclusión visual no justifica eliminar una
contribución coherente. Esto es un componente de lectura/representación,
no un integrador de ondas ni un trazador RT.

No hay pesos entrenados, GEMM, matriz de transferencia precompilada,
Tensor Cores ni FFT en este ensayo. La GPU ejecuta los shaders y el
pipeline de triángulos. El uso de aritmética dentro del shader es explícito.

## Entradas y controles, fijados antes de GPU

Un triángulo de coordenadas normalizadas (-0,8;-0,7), (0,8;-0,7), (0;0,8),
con seis valores nodales complejos P2; las copias tienen z=0 y z=0,25.
Coordenadas adimensionales de calibración, no una muestra de sílice.
Casos fijos: una contribución; dos iguales con fases 0/0, 0/pi y 0/pi/2.
Resoluciones 64, 128 y 256; centros de píxel, origen inferior izquierdo.
Referencia CPU float64 independiente, baricéntricas calculadas desde
las coordenadas, con las seis funciones de Lagrange cuadráticas.

Se excluyen de la comparación sólo centros a distancia baricéntrica
<=2e-6 de un borde matemático, para explicitar la regla de cobertura del
rasterizador. Se guardan cantidad y máscara excluidas, no se seleccionan
píxeles por su resultado. El exterior restante debe permanecer a cero.

Gates simultáneos: error complejo absoluto máximo <=5e-6; error relativo
L2 <=5e-6 salvo el caso oscuro (norma de referencia casi cero); diferencia
absoluta de potencia integrada <=5e-6; campo exterior <=1e-7. En el caso
oscuro, potencia/ potencia de una contribución <=1e-10. Todos los casos
se conservan; no renormalizar ni alinear fase después. Estos umbrales
son propios de la calibración gráfica; no sustituyen los gates T96/S16.

Controles CPU: reproducción de un polinomio complejo de grado 2,
partición de unidad y propiedad nodal; coherencia 0/4/2; rechazo de
NaN/Inf, formas inválidas, resoluciones inválidas y geometría degenerada.
La compilación Python no confirma compilación GLSL ni un resultado GPU.

## Costes y recursos

Publicar y verificar contrato, código y controles antes de GPU. Blender
instalado 4.5.14; factory-startup, sin complementos de otros proyectos.
RTX 3090 real exigida en gpu.platform.renderer_get, framebuffer RGBA32F.
Guardar versión/backend/controlador y hash del ejecutable y fuentes.

Reserva FIFO gpuq: RAM disponible >=8 GiB antes del arranque, solicitud
VRAM 2 GiB más margen de la cola; floor RAM >=6 GiB durante el hijo,
VRAM total <=4 GiB, temperatura <=80 C, RSS propio <=1,5 GiB.
Un hilo CPU, hijo <=120 s, espera de cola <=1 minuto, deadline absoluto
2026-10-09T13:45UTC. No reducir reservas para lanzar; no parar procesos
de otros proyectos. Si falla un recurso, conservar el bloqueo y no GPU.

Siete pares por caso/resolución, orden CPU/GPU alternado. Los valores
nodales cambian por repetición k=0..6 mediante la función fijada
nodal_for_repeat: a_k=a_0*(1+0,01*k)+0,001*k*v, con vector v explícito
en la fuente. No reutilizar salidas ya calculadas. Ambos caminos pueden
preparar la geometría una vez; CPU conserva las funciones P2 por píxel,
GPU conserva el batch de triángulos. GPU actualiza seis uniforms complejos
por dibujo; ese coste se incluye en el tiempo. Guardar muestras
sin escoger la más rápida. CPU evalúa la misma malla/píxeles/suma; GPU
incluye clear, dibujo y readback sincrónico. Separar compilación, upload,
arranque Blender y coste total del hijo; informar el total junto al núcleo.
Un único ensayo compartido no establece una ventaja general o energética.

## Integración posterior

Sólo tras F1 auditada localmente puede registrarse un ensayo nuevo sobre
su malla P2 y campos exactos por hash. Deberá incluir ambos detectores,
muestreo espacial y error de conversión de precisión; nunca reemplazar
primarias o cuadraturas de F1/S16 por una imagen. La investigación de BVH,
ray tracing, caminos ópticos, fase y red funcional seguirá el orden fijado
una vez cerrada la tarea 1. R1 por sí solo no prueba esas capacidades.

Fuentes primarias consultadas: ejemplos de triángulo/shader de
[Blender GPU API](https://docs.blender.org/UATEST/api/current/gpu.html) y
[arquitectura de shaders](https://developer.blender.org/docs/features/gpu/overview/).
El acceso completo a API 4.5 devolvió 403; por tanto la compatibilidad se
comprobará en el ejecutable fijado y cualquier fallo se conservará.
JEV: fallback local explícito por el bloqueo remoto heredado.
