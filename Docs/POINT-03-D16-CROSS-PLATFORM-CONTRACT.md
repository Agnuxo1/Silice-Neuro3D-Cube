# D16-X1: reproducción limitada entre plataformas

El ensayo completo D16-C1 sigue activo en Linux/Python3.13.16. El entorno
local usa Windows/Python3.13.7, con NumPy2.2.6/SciPy1.15.1/psutil6.1.1.
Se fija este control antes de observar los campos remotos del primer tramo.
Es reproducción de una implementación definida, no un nuevo contraste
prospectivo del dispositivo ni un sustituto del ensayo completo.

Calcular localmente sólo1024pasos iniciales de P6_32768 y R5_32768:
62,5µm de los2mm. Misma entrada y matrices por los hashes del paquete,
misma fuente del trabajador intacta, mismos métodos y paso longitudinal.
No ajustar fase ni normalizar salida. Cada hijo≤360s/corte370s; un hilo,
reserva previa>6GiB, guard original>3GiB y disco>2GiB; global≤900s.
Conservar informes y ambos campos en carpeta propia, claramente parcial.

Cuando se recupere el ZIP remoto, verificar integridad de sus primeros
campos y comparar cada uno con el local: diferencia relativa en normaM
≤1e-10 y diferencia de potencia física≤1e-12. No exigir identidad de
bytes entre plataformas ni considerar un hash diferente como fallo físico.
Si falla, conservarlo e investigar antes de adoptar reproducibilidad.

Los recursos de estos dos tramos son reales; no se usan los recursos
simulados del test manufacturado3DOF. No se calcula otra trayectoria
completa ni se detiene el proceso remoto. Tarea1 sigue abierta.
