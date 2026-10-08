# Control previo del evaluador espacial P5D

Registrar fuente, controles y este documento antes de ejecutarlos y
antes de datos P5C. Los controles no usan resultados ópticos T96.

Cinco leyes conocidas P(h)=0,32+1e-4*h^p, p=0,75/1/2/3/5, con los
cuatro tamaños nominales registrados, permiten contrastar una predicción
cuya cuarta potencia se calcula directamente desde la ley conocida.
Exigir recuperación del orden dentro de 1e-7 y predicción dentro de 1e-12,
aprobación prospectiva y un indicador que cubra el error continuo conocido.
Las discrepancias temporales sintéticas son 1e-15; cota PSD 1e-12,
cuadratura 1e-14 y discrepancia de reconstrucción cero.

Controles negativos: cuarta potencia alterada, incrementos oscilatorios,
orden 0,1 y 7 fuera del intervalo, señal inferior al límite de discrepancia
temporal y componente de cuadratura 0,002 que impide aprobar el total.
Cada uno debe ser rechazado por su condición correspondiente, sin cambiar
las cinco leyes válidas ni los umbrales del contrato P5D.

Guardar cada entrada y resultado, hashes, fecha y ausencia de datos T96.
Son pruebas del evaluador y su manejo de rechazos, no pruebas físicas
de convergencia del proyecto.
