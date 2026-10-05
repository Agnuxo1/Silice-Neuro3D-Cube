# Geometría masiva para Silice-Neuro3D-Cube

Fecha: 2026-10-05. Investigación de fuentes primarias, diagnóstico local y
experimento analítico pequeño. No benchmark de capacidad neuronal ni ejecución RT.
JEV bloqueado por seguridad: análisis local sin atribuir aval remoto.

## Qué anunció cada fabricante

AMD comunica unos 500 millones de triángulos tras seleccionar LOD, con rayos
primarios y de sombra, a 1080p y más de 60 FPS en RX 9070 XT. Sus jaulas
tetraédricas mantienen geometría/BVH de referencia reutilizables y animan
la envolvente. Reporta ~1.7 GB de BVH y ~3.3 ms de actualización. Son cifras
de su escena animada, no de una RTX 3090 ni de inferencia coherente.
[Fuente AMD, 17/09/2026](https://gpuopen.com/learn/how-tetrahedral-cages-significantly-reduce-bvh-memory-usage/).

La deformación por jaula es lineal por partes y no equivale a animación
independiente de cada vértice. AMD indica que prepara ejemplos DXR y biblioteca;
no asumimos implementación llave en mano disponible.
[Explicación técnica AMD](https://gpuopen.com/learn/ray-tracing-massive-amounts-animated-geometry/).
El PDF de autores se localizó, pero la lectura web falló por su tamaño: este
informe NO pretende haber auditado su artículo completo o sus tablas.

RTX Mega Geometry es una línea distinta de NVIDIA: clusters de triángulos y
estructuras de aceleración, con APIs DXR, Vulkan y OptiX 9. NVIDIA declara
soporte desde Turing; Blackwell añade hardware específico que Ampere no tiene.
[Documento de arquitectura, página impresa 22](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf).

Hay ejemplos oficiales [clusters animados](https://github.com/nvpro-samples/vk_animated_clusters)
y [clusters con LOD](https://github.com/nvpro-samples/vk_lod_clusters).
El primero incluye preparación y readbacks CPU: copiarlo no prueba recorrido
íntegramente GPU. El segundo simplifica/selecciona geometría para imagen:
la selección por cámara no certifica exactitud óptica.

## Comprobación real del equipo

Informe retenido: `resultados/codex/megageometry_analytic_20261005_v1.json`.
Contrato fijado en commit `f4e9dcd`, antes de la ejecución.

- RTX 3090, 24576 MiB, controlador 581.29.
- `vulkaninfo`, rc0: `VK_KHR_acceleration_structure` rev13,
  `VK_KHR_ray_tracing_pipeline` rev1, `VK_NV_cluster_acceleration_structure`
  rev2 y `VK_NV_partitioned_acceleration_structure` rev1 expuestas.
- Esto prueba enumeración de extensiones, NO activación de features, creación
  de estructuras, compilación de un pipeline o rendimiento.
- Consulta de metadatos, no carga GPU. Se omitieron advertencias de overlays
  ajenos y rutas personales; no se modificó su instalación.
- Ventana GPU anterior cerrada a 13:13:06 UTC de hoy; no se lanzó carga nueva.

## Qué puede ayudarnos (hipótesis de ingeniería)

| Camino | Beneficio que medir | Riesgo y control necesario |
|---|---|---|
| Instancias exactas de componentes repetidos | Compartir geometría y BVH, no estados ópticos | Cada instancia conserva fase, índice, polarización/modo y parámetros propios |
| CLAS / PTLAS | Menor memoria o coste al cambiar solo partes de escena | Comparar también con BVH estático residente; no reconstruirlo inútilmente por inferencia |
| Jaulas tetraédricas | Reutilizar geometría durante deformaciones | Recuperar longitudes físicas por segmento y normales; no usar longitud de referencia |
| Wavefront, compactación y lotes | Reducir rayos inactivos y costes de lanzamientos | Claves completas de coherencia; no fusionar estados solo por hash o cercanía |
| LOD basado en error óptico | Menos primitivas con un error acotado | Gates de fase/campos/detectores, no parecido de la imagen o visibilidad por cámara |

El cubo entrenado se concibe estático: la gran ventaja de AMD en reconstrucción
de geometría animada puede ser pequeña aquí. La reutilización exacta es una
hipótesis más inmediata que deformar todo el dispositivo.

Nuestros ensayos GLASS actuales propagan campos por SSFM/FFT en GPU, con perfiles
de índice; no recorren triángulos ni usan BVH. Una camisa de guía requiere
difracción, fuga y acoplamiento: cambiarla a rayos geométricos cambia el modelo
físico. RT podría acelerar consultas de geometría en un nuevo solver híbrido,
pero la interferencia/fase necesita kernels propios y validación contra ondas.
Un motor renderizador no convierte automáticamente RGB en campo complejo.

## Por qué triángulos no son neuronas

Un BVH evita visitar muchos triángulos. Una escena puede contener gran geometría
que ningún rayo útil recorra. Hay que contar componentes realmente alcanzados,
estados de campo, conexiones, frecuencia, profundidad y muestras inferidas.
No existe aquí evidencia de una red de 80 o 500 millones de neuronas.

Ejemplos calculados, NO mediciones de capacidad:

- 500 millones de registros de 16 bytes: 7.451 GiB; de 32 bytes: 14.901 GiB.
  Con ocho conexiones de 16 bytes por nodo: otros 59.605 GiB, antes de BVH y
  temporales. Son formatos hipotéticos, no costes universales ni cota mínima.
- 1920x1080 con hasta dos rayos iniciales por píxel: 4,147,200 rayos/frame,
  248,832,000 a 60 FPS. Esto NO cuenta rayos reales del demo, rebotes, muestras
  adicionales o sombras omitidas. No dividir triángulos/frame por rayos para
  deducir cómputo neuronal.

## Diagnóstico óptico realizado (analítico, CPU)

Seis transformaciones afines x cuatro rayos: 24 impactos conservados, error
máximo 1.90e-21 m en estos casos idealizados float64. Normales mediante inversa
transpuesta y parámetro mundial conservado con dirección local no normalizada.

Adversario: una escala de 1.001 conserva el impacto de la geometría deformada
mediante referencia, pero usar la longitud de referencia produce error de fase
0.023414 rad en un tramo de 4 um. Es un error detectado, no aprobación de una
jaula ni demostración de precisión del hardware RT.

Con lambda=1550 nm y n=1.444:

`delta_fase = 2*pi*delta_camino_optico/lambda`.

Presupuesto ilustrativo de 0.01 rad -> error OPL <=2.4669 nm, o error de longitud
<=1.7084 nm en material uniforme. No es un gate heredado del proyecto.
Un error de 200 nm da 1.1707 rad: un puerto idealmente oscuro recibe 30.52%
de potencia en el ejemplo de dos brazos. Una desviación visual pequeña puede
ser un error de inferencia grande.

Espaciado float32 a 10 mm: 0.9313 nm, equivalente a 0.00545 rad por esa
diferencia de longitud uniforme. No demuestra el error total de RT ni obliga
a precisión doble en todos los buffers: sugiere coordenadas locales y contabilidad
de camino de precisión superior, incluyendo longitud/bias entre segmentos.

Cuatro gates analíticos PASS, seis tests nuevos PASS; consultas + ensayo 0.374 s.
Suite total: 51 tests CPU PASS en 1.195 s con `PYTHONPATH=src`. Se retiene
incidente de invocación: la primera ejecución de la suite sin ese entorno tuvo
tres errores de importación `silice` (32 tests contabilizados); se corrigió solo
la invocación, no el solver ni los gates.
SHA256 del JSON:
`7dd0fa2ad5f84065e5a39bf50da232bcf0d5c66c1d6e873fa2e5a075aa75ca3f`.
No solver independiente de Maxwell, dispositivo ni ventaja demostrada.

## Experimentos siguientes: preparación, NO contrato GPU congelado

1. **MEGA-002, acceso RT mínimo.** Revisar features y crear una estructura de
   triángulos mínima, con queries conocidas. No usar los grandes assets de
   NVIDIA/AMD. Retener API real, driver, shaders y salida; no inferir soporte
   completo solo de enumerar extensiones.
2. **MEGA-003, precisión antes de rendimiento.** BVH convencional contra
   instanciado: coordenadas locales/globales, escala/cizalla, fronteras entre
   jaulas, superficies casi coincidentes, negativos de fase y salida oscura.
   Medir distancia/OPL/campo complejo, sesgo de origen compensado y modo.
   Congelar tolerancias justificadas por tarea antes de ejecutar.
3. **MEGA-004, memoria y tiempo pareados.** 64/256/1024 componentes con misma
   geometría, entradas y detectores: residente convencional vs instancias, y
   clusters si ya funciona. Registrar build/transfer/recorrido/reducción/readback
   y extremo a extremo, mediana+p95 en AB/BA, memoria máxima y energía si hay
   telemetría válida. Casos dinámicos separados de estáticos.
4. **MEGA-005, límite de validez física.** Calibrar el componente geométrico
   contra campos GLASS retenidos y ADI independiente: fuga/difracción/coupling.
   Si falla, mantener SSFM como solver o declarar dominio geométrico restringido;
   no promocionar un render bonito como red del cubo.
5. **MEGA-006, escalado seguro.** Solo tras 002-005: límite de capacidad por
   inferencia completa a precisión/tarea fijas; contar modos/componentes y
   conexiones, NO convertir triángulos a neuronas. Parar por presupuesto, no
   provocar OOM/reinicio. Red convencional con función/calidad comparables.

GPU solo con nueva ventana vigente, gpuq y exclusividad por job; RAM libre
>=4 GiB tras presupuesto, VRAM total<=18 GiB, <=80 C, pilotos<=120 s y guard
fail-closed. Estimación conservadora y deadline real; no MLP32768 ni aumentar
bounds para rellenar ocupación. No instalar SDKs/dependencias incidentalmente.

## Núcleo gráfico: candidato, no ganador

Mantener Blender como editor/visor y un núcleo mínimo medible. Vulkan facilita
probar CLAS/PTLAS expuestos; OptiX/CUDA es candidato para RT más campos propios.
Para GLASS actual, CUDA/FFT ya resuelve ondas y seguirá siendo referencia.
Unreal puede aportar herramientas, pero no suprime la obligación de calcular
fase/difracción. Elegir después de medir coste completo y precisión, no por FPS.
DLSS/FSR e interpolación de fotogramas se limitan al visor o a una aproximación
evaluada aparte: imágenes sintéticas no son inferencias ópticas exactas nuevas.

Encargo independiente preparado para Claude:
`coordinacion/tareas/MEGAGEOMETRY-CLAUDE.md`. No respuesta recibida todavía;
ni consulta válida a JEV ni publicación externa de esta entrega.
