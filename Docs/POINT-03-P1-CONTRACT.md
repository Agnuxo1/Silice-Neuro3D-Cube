# P1: aislar el cambio de bordes discretos en T96

Registrar controlador, auditor y contrato en Git antes de preparar entradas
y calcular campos. No modificar E/M1 ni sus fuentes/umbrales. Punto3 abierto.

Pregunta: al fijar los fantasmas Dirichlet en ±64µm manteniendo dx=0,32µm
y el mismo muestreo interior T96, ¿cambia la potencia del núcleo más de1e-6?
Hipótesis prospectiva: ambas reconstrucciones cambian <=1e-6 frente a la
referencia H2 N400, valor ligado al presupuesto de precisión práctica L2.
Si falla, conservar FAIL; si pasa, sólo descarta una contribución dominante
de este cambio en este caso N400, no en otras mallas ni en frontera general.

Entrada H/L2 N400 exacta: comprobar el SHA del manifiesto L2 y congelarlo
en el manifiesto P1 antes de propagar. No generar otra geometría interior.
Eliminar sólo la primera fila/columna de A0/dn/sigma/weights:399²nodos.
Antes: nodos[-64;63,68]µm, fantasmas[-64,32;64]µm en ambos ejes.
Después: nodos[-63,68;63,68]µm, fantasmas[-64;64]µm. dx permanece0,32µm.
No mover trazos, detector, amortiguador o coordenadas interiores ni
renormalizar entrada/salida. Verificar energía de entrada retirada<=1e-12
y conservación de los datos interiores por igualdad exacta de arrays.

Stencil FD y acción exponencial H sin modificar: usar su función operator
con la dimensión399 y dx explícito128µm/400. Referencias nuevas con5/7
particiones,12tramos totales hasta2mm. Semilla0/un hilo. Guardar recursos,
fuentes, cadena, arrays y hashes; hijos360s/corte370s, total2400s,
RAM>1,5GiB, disco>2GiB. Sin recuperación/ampliación automática durante P1.
No ejecutar de nuevo la trayectoria histórica N400.

Control previo pequeño: el operador recortado es exactamente la submatriz
principal del original; espectro de seno y amortiguación uniforme contrastan
con fase/potencia analíticas a2mm, error de campo<=1e-9/potencia<=1e-10.
Guardar la prueba previa separada antes de óptica T96.

Para medir el núcleo, rellenar con ceros la fila/columna retiradas y usar
el detector bilineal validado N400: el disco está en las celdas interiores
no modificadas. Esa representación no reconstruye el campo de los bordes.
Verificar cuadratura16/32<=1e-10 y concordancia de referencias: campo
relativo<=1e-9, ambas potencias<=1e-8, cota por normas<=1e-6.
La cota incluye dx²(||A||+||B||)||A-B||/Pentrada, sin alinear fases.

Auditor separado relee12campos, entradas y baseline, comprueba hashes,
arrays/recursos/pasivo/balance, remide observables y reproduce el dictamen.
Toda conclusión requiere controles e integridad aprobados. Fallo de la
hipótesis no convierte una ejecución completa en fallo operativo.

P1 es diagnóstico de la primera tarea, no cierre del hito posterior de
frontera/campo/fase. No demuestra Maxwell ni fabricación. JEVfallbacklocal
por bloqueo heredado; registro local Git, sin identificador externo/IPFS.
NASA recomienda mantener parámetros de generación en el refinamiento:
https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html
