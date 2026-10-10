# VERIFICACION-V9: verificacion independiente de I3 (curvas, ronda 3) y D3 (009c vacio, ronda 3)

Verificador adversarial. Hora de entrega: 08:10 UTC aprox. (limite 08:40). Todo es modelo numerico; ninguna cifra es medida. No se ha modificado ningun fichero ajeno; solo se escribio en esta carpeta (codigo `v9_i3.py`, `v9_d3_run.py`, `v9_d3_analisis.py`, salidas `v9_i3_*.json/log`, `v9_d3_out/`, `v9_d3_resumen.json`). CPU, `python -B`, OMP_NUM_THREADS=1, temporales en D:.

## Resumen

| Paso del encargo | Resultado |
|---|---|
| 1. Leer contratos -r3 y JSON | HECHO. Cifras de los JSON coinciden con los RESULTADOS (n_pass I3 = 2/3 evaluados; D3 = 7/19) |
| 2. Contrato anterior a resultados (mtime) | PASA en I3 y D3 (con una incoherencia menor de hora en el encabezado de D3) |
| 3. Recalcular n_eff de I3.1 en R = 10 mm, L = 80 y 100, y solape con el recto | PASA: reproduce las cifras a 12 decimales; S_rec = 0,968 y 0,961. Matiz: la convergencia en L oscila a ~1e-7 y el 1,2e-8 del par 80-100 es en parte suerte |
| 4. Factor dominante de D3 con otra semilla del dato inicial | SE SOSTIENE con la metrica pre-declarada (A = w0 en 2 de 2 variantes con >= 2x consistente), PERO el dominio cambia a B (dominio) con la cola tardia en las tres familias de datos; la dominancia depende de la metrica |
| 5. Ninguna variante se presenta como validacion del criterio original | PASA con reservas (ver seccion 5) |

## 1. Lectura de contratos y JSON

- `curvas_claude/CONTRATO-curvas-r3.md`, `RESULTADOS-curvas-r3.md`, `resultados_curvas_r3.json`: estado "done"; I3.0 true, I3.1 true, I3.2 null (observado "crece al bajar R"), I3.3 false (sin cruce P_out = 1 % en [10; 50] mm). n_pass = 2 de 3 evaluados, 4 criterios.
- `glass009c_claude/CONTRATO-VACIO-D3.md`, `resultados009c_D3.json`: estado "done"; n_pass 7 de 19. Los 7 son K0a-K0e (5), K2 (existe un factor "fuerte") y K4_w2_d256 (q = 3,01). Los 8 K1 fallan (M entre 2,0e-2 y 3,6e-3 frente a umbral 1e-4), K3 falla, K4_w2_d128 es "indeterminado" (q = 2,24), K4_w4_d128 "independiente de la malla" (q = 1,09), K5 falla (23,5 % > 10 %).

## 2. Orden temporal (ls -l --time-style=full-iso, hora local +0200; UTC = local - 2 h)

- I3: CONTRATO 09:17:05 (07:17:05 UTC) < curvas_r3.py 09:18:18 < ckpt L40 09:20:39 < resultados_curvas_r3.json 09:32:23 < RESULTADOS 09:33:11. PASA.
- D3: CONTRATO-VACIO-D3.md 09:16:30 (07:16:30 UTC) < runner 09:16:39 < trabajos.txt 09:17:07 < primeras salidas D3_out 09:18:30 < resultados009c_D3.json 09:33:58. PASA.
- Incoherencia menor: el encabezado del contrato D3 dice "Redactado ~07:20 UTC" pero el mtime es 07:16:30 UTC (4 min antes de lo declarado). No afecta al orden (el contrato sigue anterior a todo calculo), pero la hora declarada no es exacta. Ademas el lote se edito a las 09:24:41 para corregir G3 (declarado en limites del JSON); el runner no cambio tras las primeras salidas (09:16:39).
- Los mtimes de ficheros no demuestran inmutabilidad del contrato: no hay hash ni git. El JSON de D3 si guarda sha256 de adi2d, analisis y runner; el de I3 no guarda hash de contrato.

## 3. Recalculo independiente de I3.1 (R = 10 mm, L = 80 y 100, h = 0,25)

Implementacion propia (`v9_i3.py`): no importa curvas_r3 ni solver2d; construye el operador de 5 puntos, el promedio subpixel s = 8 y el analitico LP01 por su cuenta.

- Analitico y recto: n_recto = 1,442191871838 (error -2,936e-07 respecto de la analitica), identico a su valor en L = 80 y 100.
- Cadena 50, 30, 20, 15, 10 mm con seguimiento por solape (mismo metodo del contrato):

| L | n_eff (R = 10) mio | n_eff r3 | S_prev | S_rec (con el recto) | segundo mejor S_rec | P_out |
|---|---|---|---|---|---|---|
| 80 | 1,442266315212 | 1,442266315212 | 0,9953 | 0,9680 | 0,0006 | 8,33e-4 |
| 100 | 1,442266302764 | 1,442266302764 | 0,9879 | 0,9611 | 0,0073 | 7,75e-3 |

  Diferencia mia 80-100: 1,2448e-8 (r3: 1,2448e-8). Los 5 radios de la cadena coinciden con r3 a 12 decimales en ambos L (p. ej. R = 50: 1,442194819527; R = 20: ...528 y ...527).
- Ruta alternativa (sin cadena): un solo `eigsh` desde el recto (sigma en n_recto, 12 modos) a R = 10 mm da el mismo modo con el mismo n_eff y S_rec (0,968 y 0,961) en L = 80, 90, 100, 110, 120(*), 140(*). (*) Con sigma en n_recto, a L = 120 el nucleo NO aparece entre los 12 modos (mejor S_rec = 0,0021): es el mismo fallo de ventana que sufrio la ronda 2. Con sigma en 1,4422663 aparece (S_rec = 0,964). Es decir, el seguimiento por cadena es necesario, la busqueda directa desde el recto no es robusta a L grande.
- Barrido extra en L (R = 10 mm, h = 0,25, ruta directa/cadena):

| L (um) | n_eff | S_rec | n_eff - 1,4422660 (1e-7) |
|---|---|---|---|
| 80 | 1,442266315212 | 0,9680 | 3,15 |
| 90 | 1,442266372037 | 0,9663 | 3,72 |
| 100 | 1,442266302764 | 0,9611 | 3,03 |
| 110 | 1,442266299728 | 0,9628 | 3,00 |
| 120 | 1,442266201 | 0,9639 | 2,01 |
| 140 | 1,442266259 | 0,9682 | 2,59 |

  Todas las diferencias entre L consecutivos son < 1e-6 (maxima 1,0e-7 entre 100 y 120, 5,7e-8 entre 80 y 90). Conclusion: I3.1 se sostiene tambien con mas L. Pero la sucesion no es monotona (oscila ~ +-1e-7) y el 1,24e-8 del par 80-100 es mas pequeno que la oscilacion tipica; el criterio de 1e-6 es holgado respecto de esa oscilacion. La afirmacion "converge" es cierta al nivel 1e-6, no a 1e-8.
- Solape con el modo recto: S_rec >= 0,961 en todos los L probados (umbral 0,9). PASA. Hay un modo de caja vecino (segundo S_rec 0,0006 a L = 80; 0,0073 a L = 100; 0,006 a L = 110) cuyo n_eff se acerca al del nucleo (1,442251 a L = 100, 1,442258 a L = 110): hibridacion incipiente, coherente con el salto de P_out (8,3e-4 a 7,7e-3) y del centroide (1,08 a 1,43 um) entre L = 80 y 100.
- Lo que NO se refuta: I3.0, I3.1, la cifra de I3.2 (signo creciente) ni I3.3 = false (P_out a L = 100: 7,75e-3 < 1 %; mi calculo da el mismo valor). Lo que si se matiza: R_c "no establecido" depende de L (P_out crece 9x entre L = 80 y 100); no he re-evaluado P_out a otros L ademas de lo anterior.

## 4. D3: factor dominante con otro dato inicial

El dato inicial de D3 es una gaussiana determinista (no hay semilla aleatoria). "Otra semilla" se interpreto como otro dato inicial: familia S1 = w0 en {3; 5} um (centrada) y familia S2 = w0 en {2; 4} um con el centro desplazado (3,3; 1,7) um, que no cae en nodos de malla (dx = 0,5). Cada familia es un diseno 2 x 2 x 2 completo (dominio 128/256, absorbente base/ancho), mismo solver `adi2d.py`, mismos dx, dz, 800 pasos, misma ventana, mismo K2. Control: mi runner reproduce `D3_out/w2_d128_base.json` con diferencia maxima de dP 3,4e-14. Mi K2 sobre los datos originales reproduce sus GM (A 0,2158; B 0,8039; C 0,9992).

K2 con la metrica pre-declarada M (maximo en ventana W):

| Familia | A (w0) GM | B (dominio) GM | C (absorbente) GM | Dominante |
|---|---|---|---|---|
| original w0 = 2 / 4 | 0,216 (fuerte, 4/4 consistentes) | 0,804 (no) | 0,999 (no) | A |
| S1: w0 = 3 / 5 | 0,417 (fuerte, 4/4 consistentes, razones 0,71 a 0,32) | 0,691 (no, no consistente) | 0,974 (no) | A |
| S2: w0 = 2 / 4 desplazado | 0,221 (fuerte, 4/4) | 0,791 (no, consistente) | 0,975 (no) | A |

Veredicto: la afirmacion del contrato (con M pre-declarada, A es el unico factor fuerte) se sostiene con otro dato inicial, con dos matices: en S1 el efecto de A es mas flojo (una razon 0,71, GM 0,42 cerca del limite 0,5) y en S1 el absorbente si importa a w0 = 5 um (M 5,5e-3 con base frente a 2,8e-3 con ancho a 128 um; razon C hasta 1,44 y 0,51: C inconsistente).

Pero la dominancia NO es robusta a la eleccion de metrica. Con el maximo solo en la cola z >= 1 mm (descriptivo, mismas formulas, no pre-declarado, tambien presente en `resultados009c_D3.json`), el factor fuerte pasa a ser B (dominio) en las tres familias:

| Familia | A GM | B GM | C GM | Dominante (cola) |
|---|---|---|---|---|
| original | 1,54 (no) | 0,205 (fuerte) | 0,572 (no) | B |
| S1 | 1,65 (no) | 0,329 (fuerte) | 0,623 (no) | B |
| S2 | 1,73 (no) | 0,218 (fuerte) | 0,548 (no) | B |

Y el M pre-declarado en w0 = 2 es el valor en el primer instante de la ventana (z_arr = 0,2 o 0,3 mm), identico en 128 y 256 um y con ambos absorbentes (0,0205968489 en las cuatro celdas con z comun 0,2 mm; en S2 0,020213): ese numero no depende de la frontera ni del absorbente, es la diferencia entre el esquema discreto y el analitico antes de que el haz toque la banda. Es decir, el "retorno" de w0 = 2 um es en gran parte error del esquema (dx = 0,5 um, unos 4 puntos por radio, dz con K5 en 23,5 %), no retorno desde el borde. El propio contrato lo reconoce de forma parcial (atribucion "mezclado, no separado") y K4 da q = 2,24 (indeterminado) a 128 um frente a 3,01 a 256 um para el mismo w0 (el z de M difiere: 0,2 frente a 0,3 mm). Conclusion: "A domina" es cierto como enunciado sobre la metrica M, pero no autoriza a decir que la causa fisica del retorno sea el contenido de frecuencias altas del dato inicial; el contrato no lo afirma (K3 falla), y el resultado debe leerse asi.

## 5. Ninguna variante como validacion del criterio original

- D3: los 8 K1 fallan; ninguna celda alcanza 1e-4 (minimo 2,0e-3 con w5 en mis familias; 3,57e-3 en las originales), asi que no hay ninguna celda "cambio de protocolo" que presentar como exito. El `n_pass` 7/19 puede leerse como exito parcial pero no lo es: incluye K0 (herramienta) y K2 (que solo dice que hay un factor, no que el retorno cumpla). Riesgo de lectura, no de falsedad.
- I3.1 PASS frente al FAIL de I2.1: el umbral es el mismo (1e-6, par 80-100, S > 0,9). Lo que cambio es la identificacion del modo (seguimiento por solape en vez de sigma fijo); lo que fallaba en la ronda 2 era un artefacto declarado. No es una relajacion del criterio. Pero:
  1. I2.2 (12 pares con S > 0,9 y "sin marca de corte espectral") no tiene equivalente exacto en I3; la condicion de corte espectral se perdio. Es un cambio de criterio no destacado.
  2. I2.3 (tendencia con incertidumbre u) pasa a ser I3.2 informativo con pass = null. Con los datos de r3, I2.3 habria dado FAIL (n(50) - n(20) < 0), y C2 de la ronda 1 es un FAIL real. Se documenta en el texto ("C2 queda no cumplido") pero el JSON lo deja como null; quien lea solo `pass` no vera el fallo.
  3. I3.3 sustituye el C7 de la ronda 1 (cociente con R_c,A en [0,67; 1,5] y ambos en [2; 5] mm) por una regla mas debil (cruce de P_out = 1 % en [10; 50] mm). Falla igual, asi que no hay sesgo favorable, pero tampoco evalua el C7 original.
- Ninguno de los dos documentos presenta una variante como validacion del criterio original. PASA.

## 6. Riesgos no cubiertos por los criterios

- I3: la caja de Dirichlet no tiene radiacion; la convergencia en L mide la interaccion con estados de caja, no un limite fisico. Con L creciente, un modo de caja vecino se acerca al nucleo (hibridacion); P_out y el centroide no estan convergidos en L (P_out 8,3e-4 a 7,7e-3). R_c y cualquier lectura de P_out son cifras de la caja.
- I3: oscilacion de n_eff con L de ~1e-7; si algun dia se endurece el umbral a 1e-7, el resultado puede cambiar.
- I3: sin h = 0,125 (pendiente declarado). La malla 0,25 da un error de discretizacion de -2,9e-7 en el recto; ese error es del mismo orden que la oscilacion en L.
- I3: la busqueda directa desde el recto falla a L = 120 (nucleo fuera de los 12 modos): el metodo depende del seguimiento por cadena y de n_modes = 12.
- D3: la metrica M mezcla error de esquema temprano y retorno; el contrato lo reconoce. Con la cola tardia manda el dominio, no w0. Hay que decidir cual es el observable fisico antes de atribuir causas.
- D3: muestreo cada 0,1 mm; K5 falla (el paso dz importa 23,5 %); malla solo dos niveles; un solo exponente p; solo theta = 0.
- Los mtimes y las horas declaradas dependen de que los autores no hayan retocado el reloj; no hay hash de contrato ni git.

## Ficheros

- Esta carpeta: `D:/PROJECTS/.cognition/audit/silice-origin-main/experimentos/verificacion_claude/`: `VERIFICACION-V9.md`, `v9_i3.py`, `v9_i3_L{80,100}_h0.25.json`, `v9_i3_L{90,110,120,140}_h0.25_direct*.json`, `v9_d3_run.py`, `v9_d3_analisis.py`, `v9_d3_jobs.txt`, `v9_d3_out/`, `v9_d3_resumen.json`.
