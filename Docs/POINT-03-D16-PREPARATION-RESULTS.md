# D16-C1: preparación verificada, resultado óptico pendiente

Tarea1/punto3 T96/Q4 sigue abierta. Los contratos históricos y sus resultados
negativos se preservan. D16-C1 tiene un operador distinto, con K Duffy16
validada antes de cualquier nueva potencia óptica. Contrato e2f3cb9 y
adaptaciones portables3f6e5ad. No se ha lanzado el ensayo completo.

## Controles ejecutados

Los métodos, en un sistema manufacturado de tres grados de libertad,
coinciden con la exponencial matricial densa: errores1,214e-14 para Padé6
y2,610e-15 para Radau5. El evaluador acepta campos idénticos y rechaza
errores de amplitud y un error de fase de0,02rad aunque la potencia coincida.

El trabajador real se probó con ese sistema manufacturado mediante dos
tramos consecutivos por familia: error máximo2,741e-13, límite1e-10.
También rechaza en ambas familias un hash del campo anterior corrupto.
Sólo en este test de software se simulan los recursos y se sustituye la
matriz por la pequeña manufacturada. No es una trayectoria T96 ni evidencia
de memoria física disponible. Los datos de prueba quedan identificados
en point03_d16_worker_controls_20261008.

Comprobación de las entradas reales: veinte archivos del paquete coinciden
con sus hashes; masa, camisa, detector, entrada y amortiguación coinciden
con los informes anteriores. K16 coincide con51a273ef…;31077 grados libres,
norma de potencia de entrada1,0000000000000004. No se propaga el campo.

## Paquete revisable

Silice_D16_C1_20261008.zip,6081913bytes,20archivos.
SHA256:cebaeac0f2952360f319acd9081f0f6149e0fbda7112258ac738aafc6d0a3ea1.
CRC aprobado. Cuaderno acompañante validado por nbformat y sus celdas
analizadas sintácticamente; no ejecutado con datos del proyecto.
Primer empaquetado: error ValueError al construir una celda con f-string.
Se corrigió y se generó una carpeta nueva; el producto anterior incompleto
se conserva y no es el paquete propuesto para transferir.

Los registros del nuevo trabajador usan rutas relativas, permitiendo
recuperar resultados desde Linux a Windows sin reescribir informes
originales ni invalidar sus hashes. El auditor recalcula todos los tramos
y observables independientemente del evaluador de producción.

## Recursos y siguiente acción

La memoria local bajó hasta1,676GiB disponibles, insuficiente para el
guard3GiB y la reserva4,5GiB del contrato nuevo. No se modifican trabajos
de otros proyectos ni se relajan límites para forzar un lanzamiento.

El cuaderno privado Colab se reconectó tras su desconexión por inactividad.
Una comprobación genérica de recursos mostró12,671GiB totales y11,593GiB
disponibles, Linux/Python3.13.16. Sólo se ejecutó esa prueba genérica:
sin archivos científicos transferidos ni resultados ópticos remotos.
El ensayo requiere dependencias fijadasNumPy2.2.6/SciPy1.15.1/psutil6.1.1,
integridad de entradas y los mismos criterios físicos y de recursos.

Está solicitada autorización específica para subir el ZIP y el cuaderno
al Colab privado y ejecutar CPU estándar. Sin contratar recursos de pago.
Alternativa: esperar disponibilidad local suficiente. No hay proceso
numérico activo ni se inicia la tarea siguiente. JEV: fallback local por
el bloqueo de seguridad heredado; sin recomendaciones remotas atribuidas.

Un aprobado temporal sólo permitiría registrar el ensayo de la malla
intermedia. Todavía faltan las tres referencias temporales con K16,
predicción espacial previa a la malla fina, control de esa malla y dominio.
La importación real Blender requiere su ventana/reserva vigente; las
herramientas auxiliares ya verificadas no sustituyen estas pruebas.
