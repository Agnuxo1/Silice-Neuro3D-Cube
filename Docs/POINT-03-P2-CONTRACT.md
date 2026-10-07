# P2: estudio prospectivo T96 con dominio Dirichlet fijo

Registrar contrato, controlador, auditor y prueba de coste antes de óptica
P2. Reutilizar P1 N399 sólo tras su auditoría de integridad y precisión,
sea favorable o negativa su hipótesis de cambio de frontera. Conservar
E/G/H/K/L/M1/N1/P1 y no ajustar criterios después de datos nuevos.

Pregunta: con fantasmas fijos±64µm y el muestreo/entrada/detector físicos
constantes, ¿pasa un nuevo punto de refinamiento la predicción y estabilidad
de orden para la potencia T96 del núcleo? Mismas96circunferencias ideales,
dn=-0,003,1550nm,2mm, cintura/radio6µm; ecuación escalar fija.

Serie fijada por espaciado: M320/400/500/640/800 intervalos, nodos
interiores N=M-1 y dx=128µm/M. Todos los nodos/centros y fantasmas siguen
la misma fórmula física simétrica. El factor fino800/640=1,25 prolonga
el refinamiento nominal y se elige antes de generar su geometría.

Para M320/500/640 usar los arrays geométricos/entrada guardados y quitar
sólo su primera fila/columna; comprobar igualdad exacta interior, energía
de entrada retirada<=1e-12 y área de cladding constante<=1e-12 relativa.
No reutilizar sus propagaciones antiguas, cuyo dominio era distinto.
M400 se reutiliza de P1 por hashes, sin repetir su propagación.

Referencias nuevas exponenciales: M320 particiones4/9;M5009/13;M64017/23.
Con P1 estas cuatro primarias deben pasar referencia campo<=1e-9,
potencias<=1e-8, cota por normas<=1e-6 y cuadratura16/32<=1e-10.
Órdenes positivos en[0,05;8], monotonía/incrementos>1e-12 para ternas
320/400/500 y400/500/640 y discrepancia<=20% en ambos detectores.
Si falla un prerrequisito, terminar P2 negativo sin calcular el punto fino.

Sólo tras aprobarlos, predecir M800 por la última terna. Guardar valores,
fuentes/hashes y hacer commit Git ANTES de su geometría. Generarla con
el método analítico G, adaptado únicamente a M800 y nombres; contrastar
48celdas y área global contra referencia independiente<=1e-12, calidad
<=1e-13. Recortar su primera fila/columna manteniendo interiores.

Punto fino: referencias29/41particiones, más FDST25600pasos de
0,078125µm,64tramos de400pasos. Kernel validado sin modificaciones.
Primero control sintético N799 de100pasos, sin geometría ni potenciaT96:
fase del seno de alta frecuencia con error<=1e-10; presupuesto200s.
Su coste previsto FDST completo debe ser<=12000s antes de iniciar P2.
Gaussianas analíticas y sus detectores se contrastan antes de óptica fina:
para fases transversales0/2e5/4e5m^-1, órdenes500/640/800 en[1,8;2,2]
y el indicador fino capado en2 debe cubrir el error conocido.

Criterios FINOS para ambos detectores:
1. Integridad/cadenas/recursos/finitos, geometría/entrada y controles PASS.
2. Referencias:campo<=1e-9,potencias<=1e-8,cota<=1e-6; cuadratura<=1e-10.
3. FDST frente referencia41:campo<=1e-4,potencias<=1e-6,
   cota por normas+consistencia+cuadratura<=1e-5; sin alinear/renormalizar.
4. Predicción:residuo<=10% de|P800-P640|. Orden500/640/800 positivo,
   monótono y estable20% frente400/500/640.
5. Indicador espacial=1,25*|P800-P640|/(1,25^min(p,2)-1).
   Añadir diferenciaFDST/referencia, consistencia, cuadratura y diferencia
   entre reconstrucciones. Total<=1e-3 y<=1%deP800. Es CONDICIONAL,
   no cota rigurosa ni cobertura probabilística.
6. Auditor separado antes de adoptar cierre local de potencia T96.

CPU un hilo por hijo, hijos360s/corte370s, RAM>1,5GiB y disco>2GiB.
GLOBAL36000s(10h) incluye preparaciones,primarias,fino y evaluación;
estimación basada en costes medidos anteriores, no garantía. Sin ampliar
presupuesto ni recuperación automática durante P2. Fallo operativo y
fallo científico se registran por separado. Este presupuesto sustituye
para este ensayo los límites exploratorios antiguos, sin modificarlos.

Campo/círculo se representa para el detector en una matriz MxM añadiendo
ceros en la fila/columna retirada: el detector reside íntegramente dentro
de las celdas no modificadas. No cambiar el observable para aprobar.

Cierre, si procede: sólo potencia escalar del núcleo para este caso y
dominio fijo. No cerrar frontera/fase general, Maxwell, material medido,
fabricación ni ventaja funcional. Todos los FAIL históricos permanecen.
JEVfallbacklocal por bloqueo heredado. Registro local Git, sin IPFS externo.
Fuente metodológica: https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html
