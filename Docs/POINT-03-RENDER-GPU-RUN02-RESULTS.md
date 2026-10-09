# R1run02: resultado gráfico negativo conservado

9 de octubre de 2026. Perfilv3 y fuentes publicadasa67c33a precedieron
al ensayo. El diagnóstico de identidad directa bajo FIFO aprobó, exit0,
sin GPU; luego se obtuvo una nueva reserva para run02.

## Ejecución real y dictamen

Blender4.5.14LTS ejecutó vertex/fragment shaders y rasterización de triángulos
con backendOPENGL en NVIDIA GeForceRTX3090. Se guardaron84 fotogramas
RGBAfloat32: cuatro casos, tres resoluciones y siete repeticiones. Esta
es evidencia de ejecución gráfica del banco manufacturado; no de
propagación óptica, una red neuronal funcional ni validación física.

El worker escribió completed, pero su accuracy_pass fueFalse:63/84 filas
fallan, todos los casos single/constructive/quarter en las tres resoluciones.
Las21 filas destructive satisfacen sus gates; eso no basta para validar
la superposición coherente del banco completo. Máximo error complejo
2,5664682513 frente al gate5e-6; máximo errorrelativo1,3318562176;
diferencia máxima de potencia0,1879463875; campo exterior máximo
2,3187420065 frente a1e-7. No se renormalizó ni alineó fase ni se cambió gate.

El proceso de Blender no cerró normalmente después del informe. El timer
independiente cortó el hijo; guard.status=failure_retained y reason=
independent own-child hard cutoff. Tiempo observado del hijo con arranque
115,5790023s, supervisor116,0498914s; máximo declarado120s. Todos los
samples de recursos aprueban: RAM mínima10,106743GiB, VRAM máxima
0,729492GiB, temperatura máxima30C y RSS propio máximo0,344334GiB.
No se prolongó el ensayo ni se interfirió con procesos ajenos.

Las84 filas contienen al menos una duración CPU/GPU igual a cero con el
reloj utilizado. Los tiempos no permiten calcular un speedup válido. El
elapsed_worker reportado1,718s tampoco representa el coste total del hijo.
El corte y el arranque forman parte del coste de este intento fallido.

## Auditoría y datos íntegros

El auditor completo congelado devolvió exit1 al exigir completed en el
supervisor. Se guardan stdout/stderr de esa excepción. La auditoría
independiente adicional verificó84 hashes, formas, dtype, finitud, casos,
orden de pares y fuentes; recalculó los gates originales y conserva el
negativo. full_integrity_pass=False, adopted=False, point03_closed=False.

Una primera comparación estricta de métricas se detuvo: cinco errores L2
relativos difieren alrededor de1,3–1,5e-14 entre runtimes, sobre la tolerancia
original1e-14*max(1,valor). Se conserva metric_mismatch_diagnostic.json;
la tolerancia no se amplió. Los grandes fallos de precisión permanecen
también en el cálculo local. failed_frame_audit.json distingue integridad
de bytes/forma/fuentes, desacuerdo de métricas y validez del ensayo completo.

Los diagnósticos de coordenadas/canales son sólo diagnósticos: la lectura
RGBA presenta valores B no nulos aunque el shader escribe B=0; la máscara
espacial tampoco coincide. Transponer ejes por sí solo no resuelve el error.
No se adopta ningún fotograma transformado ni se concluye todavía una causa
única. La API primaria documenta read_color como lectura de píxeles desde
la esquina inferior izquierda a un Buffer; la conversión concreta debe
calibrarse en este ejecutable antes de registrar otra tanda P2:
[Blender4.5 GPUFrameBuffer](https://docs.blender.org/api/4.5/gpu.types.html).
La búsqueda consultó la documentación indexada; no prueba el orden del
buffer NumPy en este ensayo.

## Continuación condicionada

Registrar una nueva versión sólo después de conservar y publicar estos
fallos. Primero calibrar layout/canales/coordenadas con marcas conocidas,
registrar reloj de alta resolución y cierre del hijo propio, y guardar
versiones de Python/NumPy del motor. Cualquier fuente nueva exige perfil
y controles nuevos antes de GPU. No editar run02 ni repetir sus salidas
como si fueran un ensayo válido. Preservar reservas/límites/deadline.

F1 permanece separada e intacta. Chrome sigue sin aparecer conectado;
última lectura confirmada07:45UTC,96/192 campos reportados. No se afirma
progreso posterior, no se relanzan celdas y S16 requiereF1 localPASS.
Tarea1 abierta. JEV fallback local; no adopción de resultados de Neuro3D.
