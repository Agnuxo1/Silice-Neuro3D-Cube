# P0: seis marcas GPU auditadas, antes de nuevos campos P2

9 de octubre de2026. Contrato, fuentes y perfilv2 publicadosf02c2ad77b43ac6d585ad12c6e99f68cb9f4b16f
antes de ejecutar GPU; hashes de fuentes/controles/perfil coincidieron conGit.
Preparaciónv1 conservada. Un preflight de publicación detectó diferencias
CRLF/LF en el guard nuevo; se archivaron sus bytes originales y se fijó
versiónLF/controles portables iguales porJSON antes de GPU. No se cambiaron
gates ni se reejecutaron controles exclusivos.

Blender4.5.14LTS/OpenGL/RTX3090 generó seis marcas, dos casos por tamaño
no cuadrado(8x5,13x7,32x16). Ambas copias del mismoBuffer se guardan: lectura
multidimensional anterior y copia unidimensional con reshapeC explícito.
ReferenciaCPU analítica independiente; no se leyó ni adoptó un campo R1/F1.

Auditoría local: integridad, precisión de la copia nueva, predicción de
stridesC/F y rechazo del método anterior PASS en las seis marcas. El error
máximo nuevo y todos los tiempos se guardan en calibration_summary.json.
Las formas(h,w,4) y strides(4,4h,4hw) observados confirman el diagnóstico
para este ejecutable. Los fotogramas R1run02 siguen negativos y no adoptados;
no se transforman para convertirlos en nuevos resultados.

El motor registra Python3.11.15/NumPy1.26.4; capsBLAS=1. perf_counter tiene
resolución1e-7s, monotonic0,015625s. Todos los pares clear/uniform/dibujo,
doslecturas/copias tienen ns positivos. Esta resolución del reloj anterior
es compatible con sus duraciones cero; P0 no compara rendimiento CPU/GPU.

Cierre del hijo propio después de liberar offscreens/cerrar/fsync informe:
completed/exit0,2,2395457s de hijo con arranque y2,755621s del supervisor.
Las reservas y muestras de recursos originales aprobaron; ningún proceso
ajeno detenido ni ampliación de límites. Se conservan los seisNPZ, stdout,
stderr, guard, informe y auditoría. El cierre no depende del evento GUI.

Esto valida coordenadas/canales/lectura y medición del instrumento para
las marcas registradas. No valida campoP2, propagaciónT96, red funcional,
RT, energía o ventaja general, ni constituye medida física de sílice.

Siguiente: registrar y publicar una nueva tanda P2 con conversión/temporizador/
cierre calibrados y referencia original porhash. Mantener gates científicos,
todos los casos y coste total. Primero auditar de forma explícita las métricas
con ambos runtimes; no ampliar tolerancias para buscar un aprobado.
F1 permanece intacta; Chrome sigue desconectado, último dato96/192 a07:45.
S16/h0,28/dominio requieren F1localPASS. Tarea1 abierta; JEVfallbacklocal.

La causa de los strides se contrastó con el código primario fijado:
[Blenderv4.5.14 Buffer](https://github.com/blender/blender/blob/v4.5.14/source/blender/python/gpu/gpu_py_buffer.cc).
