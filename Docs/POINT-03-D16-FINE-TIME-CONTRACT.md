# D16-F1: referencia temporal h=0,35 antes del contraste espacial

Protocolo anterior a nuevos campos K16 de esta malla. La propagación
requiere M2-R1 completa, transportada y auditada **localmente**, con
integridad y los cinco criterios temporales aprobados. Preparar software
y comprobar archivos no sustituye esa condición. Si M2-R1 no aprueba,
F1 no empieza. C1 negativo, M2 fallida, recuperaciones y campos K8 históricos
permanecen intactos y no se usan como campos K16.

Pregunta: ¿la pareja temporal registrada en las mallas previas satisface
los mismos cinco criterios en la malla conforme existente h=0,35 µm?
Hipótesis y umbrales simultáneos: diferencia relativa del campo en norma
de masa <=1e-4; diferencias de los dos observables de potencia <=1e-6;
cotas de discrepancia de ambos operadores PSD <=1e-5. Conservar resultados
positivos y negativos. No escoger sólo el detector favorable, alinear fase
ni renormalizar salidas. La comparación no certifica error continuo.

Modelo escalar ideal y datos físicos originales: longitud2mm, dominio±64µm,
lambda1550nm, n0=1,444, contraste deprimido0,003, entrada gaussiana q16,
detector de campo q32 e intensidad q32, camisa/masa y amortiguación q12.
Reutilizar sin regenerar la geometría P4C y sus matrices, detector P4F,
amortiguación P4G y regla Duffy16 validada contra Duffy24. K16 SHA-256:
f251ae68f374cb6ae98288caed1984d528a6147c7b74ada3229e7aa98771074f.
El informe de geometría recuperado se acepta sólo con integridad y
controles geométricos/de ensamblaje aprobados; su fallo original se conserva.

Padé[3/3]32768pasos es la primaria; Radau[2/3]65536pasos es el control.
Tramos de512pasos:64Padé y128Radau,192campos. La partición menor se fija
antes de nuevos campos para acotar el tiempo de cada hijo en la malla
mayor. No cambia los pasos totales, coeficientes, matrices, observables o
criterios. Se generan fuentes diferenciadas a partir de M2, con registros
de sustituciones y hashes, sin editar ningún archivo usado por M2-R1.

Antes de campos: siete archivos numéricos comprobados por hashes; potencia
de entrada uno dentro de1e-12; evaluador positivo, error de fase y amplitud;
trabajador con dos tramos por familia en sistema manufacturado de3DOF
frente a exponencial densa(error<=1e-10), y rechazo de hash previo corrupto.
Los recursos simulados se permiten sólo en esos controles de software.

CPU estándar, un hilo; reserva previa>6GiB, guardia inicial/final>3GiB,
disco>2GiB. Hijo<=360s/corte370s. Este ensayo nuevo tiene presupuesto
global32000s desde su propio inicio, incluyendo interrupciones y recuperación,
y espera acumulada<=900s. El límite absoluto de la ventana del usuario
2026-10-09T13:45UTC prevalece; no se amplía ningún límite ya iniciado.
Comprobarlo antes de cada hijo y al finalizar; el corte externo se reduce
al tiempo restante si cualquiera de los dos límites llega antes.
No ejecutar a la vez otra propagación en el mismo recurso.

La expectativa de coste es una estimación, no garantía de completar el
ensayo dentro de la ventana. Un hijo o recurso insuficiente produce un
fallo conservado; nunca un aprobado parcial. Antes de recuperar, auditar
campos existentes y registrar una operación nueva sin repetirlos ni
reiniciar tiempo o espera. Se conserva el entorno fijo NumPy2.2.6,
SciPy1.15.1/psutil6.1.1 y las versiones de Python/plataforma reales.

Registrar el protocolo, controles y ejecutor/auditor en Git y verificar la
publicación antes de campos. El auditor independiente recalcula los192
campos, cadenas, hashes, potencias, recursos y cinco criterios; comprueba
el presupuesto y la hora final. Transportar con SHA/CRC antes de repetir
la auditoría local. No adoptar un aprobado del controlador sin auditoría.

Después de una aprobación F1: registrar explícitamente la serie espacial
K16, sus tres primarias y las dependencias actualizadas antes de evaluar
la predicción reservada. El protocolo P5D histórico aludía a campos K8:
no autoriza mezclarlos con K16. No generar h=0,28 antes de registrar la
predicción. Dominio sigue pendiente. Tarea1 abierta; tareas2–22 sin iniciar.
JEV: bloqueo remoto retenido y fallback local explícito.
