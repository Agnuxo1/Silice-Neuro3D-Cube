# H: revisión previa de implementación

2026-10-07, antes de propagar H. Contrato/runner/evaluador congeladosc04558b.
No cambio a fuentes/criterios de G ni al historial E/B.

La matriz incluye cuatro vecinos y diagonal -4c+V. Los enlaces +/-1 se
anulan en cada borde de fila; +/-N corresponden a vecinos verticales.
La contribución potencial es completa, a diferencia de la mitad que usa
cada suboperador ADI. traceA suma la diagonal realcompleja y se escala con
la longitud del segmento. Cada solución R4/R8 comienza desde A0; no usa
la salida ADI ni el resultado de la otra partición.

Se contrastaron siete controles pequeños contra bucles independientes,
exponencial densa y eigenmodos discretos conocidos. Máximo error4.066e-16.
Cinco controles del evaluador incluyen rechazos de secuencias constantes,
oscilantes, órdenes negativos y predicción incorrecta; el caso fabricado
de segundo orden pasa. Estos resultados anteceden a campos ópticos H.

Contraste suplementario ADI/ref en perfil variable de9x9 y z10um:
errores relativos de campo2.4688e-7,6.1721e-8,1.5430e-8 para100/200/400
pasos. Órdenes1.9999888/1.9999970. Confirma aproximación a la misma ecuación
en ese control, sin validar T96 ni extender los criterios preregistrados.
JSON retenido point03_exponential_adi_manufactured_20261007.json.

Evaluación H vuelve a abrir cada checkpoint, contrasta hash/dtype/shape/
finitud/potencia cruda/cadena y los recursos muestreados. Compara métodos
de reconstrucción sin alinear fase ni normalizar salidas. Controla fecha
de predicción anterior al inicio H640. G640 ya disponible se declara:
esta predicción temporalmente prospectiva no es validación independiente.

Límites: CPUunhilo; presupuesto hijo360s, externo370s; parent7200s.
La memoria se muestrea antes/después de segmentos, no es un máximo global.
expm_multiply tiene redondeo/control algorítmico y usa estimación de normas;
R4/R8 comprueba partición, no elimina defectos comunes ni acredita cotas.
Referencia comparte ecuación/stencil/inputs/detector, por diseño: distingue
error temporal, no un defecto de modelo/fabricación. Los errores complejos
son diagnósticos, no aceptación de la posterior validación de campo/fase.

Un PASS H requiere todos sus criterios; G permanece FAIL. Un FAIL H conserva
punto3 abierto. El procedimiento no convierte un orden alto observado en
precisión formal elevada. Quedan expresamente fuera Maxwell, modos físicos,
frontera/dominio, metrología/fabricación y tolerancias de una red.

## Límite adicional observado durante H, sin cambiar sus criterios

En N256 yN400 la diferencia calculada entre R4/R8 es0; enN320 es1.22e-10
relativa. La fuente instalada SciPy1.15.1 `_expm_multiply_simple_core`
aplica un polinomio de Taylor en s subincrementos y una fase por trace shift.
Como inferencia de esa estructura, particiones externas relacionadas por2
pueden seleccionar el mismo grado y duplicar s, produciendo el mismo
incremento interno efectivo. No se midieron los m_star/s reales de esos
casos, así que no se afirma que ese mecanismo sea su causa comprobada.

Los PASS R4/R8 sólo acreditan consistencia de las particiones examinadas;
no equivalen a dos algoritmos independientes ni garantizan la exactitud de
la referencia. La matriz/stencil/bucles, exponencial densa y controles de
eigenmodos siguen siendo los contrastes independientes registrados. No se
modifica ningún umbral ni se alinea fase después de observar esta limitación.
