# P0: calibración del Buffer, reloj y cierre antes de nuevos campos P2

Prerregistro posterior al negativo R1run02 publicado2e6444f. R1run01/run02,
sus84crudos y sus fallos permanecen intactos; ninguna transformación se
adopta como nuevo resultado. F1/S16 y sus fuentes/límites no se modifican.
P0 sólo calibra el instrumento gráfico: no propaga ondas ni inicia tareas2–22.

## Diagnóstico primario y pregunta

El código oficial Blenderv4.5.14 crea Buffer de lectura con forma(h,w,canales),
pero exporta strides que crecen desde el primer índice. NumPy interpreta
esa forma con orden de memoria F aunque los píxeles RGBA están intercalados.
La lectura previa usó directamente ese export multidimensional. Se registra
una lectura nueva que declara Buffer unidimensional antes de copiarlo y
darle forma(h,w,4). No se ajusta orientación o fase a resultados ópticos.

Fuentes primarias verificadas y descargadas como datos de inspección:
[gpu_py_buffer.cc v4.5.14](https://github.com/blender/blender/blob/v4.5.14/source/blender/python/gpu/gpu_py_buffer.cc),
SHA8ec78410234d15714d837f30e880aa4d654b93f0c7a8faffa3bd890b226ba215;
[gpu_py_framebuffer.cc v4.5.14](https://github.com/blender/blender/blob/v4.5.14/source/blender/python/gpu/gpu_py_framebuffer.cc),
SHA46714770502ca049c77f56e3e9b5bcf01ed5bcc2197b482158f7ea8cd74fe389.
El acceso a docs4.5 volvió a fallar402; el código fijado sí se recuperó.
La causa se contrasta prospectivamente con marcas nuevas; no sólo con R1.

## Marcas fijadas antes de GPU

Dos casos y tres tamaños no cuadrados: ancho/alto(8,5),(13,7),(32,16).
Pantalla completa formada por dos triángulos3D, blendNONE, framebufferRGBA32F.
ConstanteRGBA=(0,125;0,375;0,625;0,875), y coordenadas de centros de píxel:
R=(columna+0,5)/ancho, G=(fila+0,5)/alto,
B=0,125+0,25R+0,5G, A=1, origen inferior izquierdo.
ReferenciaCPU analítica float64; no lee campos P2 ni resultados R1.

Se guardan ambos exports del mismo Buffer: método anterior y copia nueva
unidimensional. Sólo la copia nueva se evalúa como instrumento. Gate en
todos los píxeles/canales: error absoluto máximo<=1e-6, finitud y forma/dtype
correctos. La predicción C/F fija para el método anterior debe coincidir<=1e-6;
su error se conserva, sin seleccionar transformaciones. Se guardan forma y
strides observados. Son seis marcas, no una tanda P2 de84campos.

CPU: seis grupos de marcas, rechazo de lectura anterior/mirrors/canales y
cinco grupos inválidos, con salida nueva y exclusiva. Publicar/verificar
contrato, seis fuentes necesarias y perfil antes de GPU; el perfil incluye
también el contrato R1 original para conservar sus límites.

## Reloj, salida y límites

Usar perf_counter_ns: guardar ns enteros positivos de clear/uniforms/dibujo,
lectura de ambos métodos y copia; guardar resolución de ambos relojes.
Esto calibra medición y no demuestra speedup. Versiones Python/NumPy/Blender,
renderer/backend y capsBLAS=1 se guardan. Shader/preparación/arranque separados.

El worker cierra únicamente su propio factory-startup mediante os._exit
después de liberar todos los offscreens y cerrar/sincronizar el informe.
Así se evita depender del evento de cierre GUI que no terminó R1run02.
No se abre escena del usuario ni se cierra proceso ajeno.

Misma cola FIFO: RAM>=8GiB antes, floor>=6, VRAMtotal<=4GiB, temperatura<=80C,
RSS propio<=1,5GiB, un hilo, espera<=1min, hijo<=120s/timer115, worker110s,
deadline13:45UTC9oct. Runtime directoC:/Python313/python.exe para supervisor;
cola desde entorno científico; no PYTHONPATH al motor. No compras/instalaciones.
Nuevos supervisor/perfil/carpeta; fuentes congeladas durante ejecución.

Auditor independiente exige fuentes/hashes/seis marcas/strides/recursos,
cierre normal del hijo y tiempos positivos. Incluso si P0aprueba, R1P2 no
se valida retroactivamente. Una nueva tanda P2 requiere protocolo/fuentes/
controles/perfil publicados antes de calcularla, mismos gates científicos,
y resolución explícita del desacuerdo de métricas; no ampliar tolerancias
por conveniencia. T96/Q4 permanece abierta. JEV fallback local.
