# Estado de novedad del proyecto · 2026-10-10

**Proyecto:** Silice-Neuro3D-Cube. Modelos numéricos y documentación; no es un dispositivo.
**Fecha de corte de las fuentes:** 2026-10-10.
**Alcance:** afirmaciones de novedad (a) a (e), y su efecto en T19 y T20. No es una revisión bibliográfica exhaustiva.
**Estado general:** ninguna afirmación de novedad queda establecida. No hay medida experimental en el repositorio (`Docs/F2-PROTOCOLO-MEDIDA.md`, encabezado de estado).

## 0. Convenciones y fuentes

Etiquetas usadas en el texto:

- **V**: verificado en texto completo leído, o en resumen leído directamente. Se indica la fuente.
- **C**: resultado de cálculo del modelo. No es medida.
- **M**: requiere medida. No existe hoy.
- **NV**: no verificado. Incluye fragmentos de búsqueda, prensa y cifras citadas en otro documento sin releer.

Abreviaturas de fuentes (rutas dentro del repositorio):

| Abrev. | Ruta | Uso en este documento |
|---|---|---|
| LIT | `Docs/LITERATURA-NOVEDAD.md` | Secciones 1, 2 y 4 (base); 6 y 7 (superadas en lo referente a HUST/SJTU); 8 (vigente) |
| V5 | `experimentos/verificacion_claude/VERIFICACION-V5-literatura.md` | Texto completo de HUST/SJTU y Lee et al.; índices de SK-1310; correcciones propuestas (§5) |
| SK | `Docs/SK1310-FUENTES.md` | Estado del artículo SK1310 e índices del fabricante |
| T20 | `Docs/CONTRIBUCION-CENTRAL-T20.md` | H1, criterios F1 y F2, test decisivo |
| F2 | `Docs/F2-PROTOCOLO-MEDIDA.md` | Protocolo de corte, predicciones P-F2a y P-F2b, recursos |
| VEC-GEO | `experimentos/vectorial_claude/RESULTADOS-VECTORIAL-GEOMETRIA.md` | Trinchera: fuga y modos (C) |
| VEC-SALTO | `Docs/VECTORIAL-RESULTADOS.md` | Guía de salto ideal: contraste escalar-vectorial (C) |
| PLAN | `coordinacion/tareas/PLAN-22-TAREAS-20261010.md` | Estado de T6, T8, T9, T12, T13, T14, T19 y T20 |

Enlaces externos usados: HUST/SJTU, DOI 10.1038/s41467-026-72316-9, texto en https://pmc.ncbi.nlm.nih.gov/articles/PMC13284361/ · SK1310, metadatos en https://api.crossref.org/works/10.1016/j.optmat.2025.116651 · Lee et al., https://pmc.ncbi.nlm.nih.gov/articles/PMC8660921/ · Kondratyev et al., https://arxiv.org/abs/2308.13452.

## 1. Resumen

- **(a) Red 3D multicapa escrita con fs en vidrio:** cubierta por un antecedente publicado (HUST/SJTU, 2026, texto completo verificado). **No puede presentarse como novedad.**
- **(c) Guías de camisa deprimida en trinchera a 1550 nm:** **riesgo alto.** Del artículo SK1310 (2025) está verificado el título, que habla de guías de camisa deprimida en banda de telecomunicaciones. La geometría de trinchera y la longitud de onda no están verificadas.
- **(b) Operación a 1550 nm en la red** y **(d) cutback propio con acoplo y propagación separados:** **no establecidas.** No hay medida. El protocolo F2 está publicado, y el laboratorio no está disponible.
- **(e) Contraste con el modelo vectorial:** **en curso.** Hay contraste calculado para una guía de salto ideal. Para la trinchera falta el contraste con un FD vectorial independiente.
- **T19:** parcial, no cerrada. **T20:** abierta, sin datos. **H1 no cambia en este documento.** Hay cinco puntos de definición que deben declararse como enmienda antes de medir (sección 5).

## 2. Tabla de afirmaciones de novedad

| Id | Afirmación | Estado | Fuentes |
|---|---|---|---|
| a | Red 3D multicapa escrita con fs en vidrio | **Cubierta por antecedente publicado. No sostenible como novedad.** | V5 §2; LIT §8 |
| a' | Variante: red 3D en **sílice**, escrita **desde varias caras** | **No establecida (M).** El antecedente usa borosilicato. La escritura desde varias caras no se evaluó en V5 (NV). | V5 §2; PLAN, fila 9 |
| b | Operación a **1550 nm** en la red | **No establecida (M).** El antecedente no declara longitud de onda de operación. No hay red medida. | V5 §2 (P1c); F2 §3 |
| c | Guías de camisa deprimida en trinchera a 1550 nm | **Riesgo alto de solapamiento. No establecida.** | SK; LIT §8; T20 §1 |
| d | Cutback propio a 1550 nm con pérdidas de acoplo y propagación separadas | **No establecida (M).** Protocolo publicado; ninguna medida. | F2 §3; T20 §2 |
| e | Contraste con el modelo vectorial | **En curso.** Calculado (C) para la guía de salto ideal. Para la trinchera falta el FD vectorial independiente. | VEC-SALTO; VEC-GEO; PLAN, fila 6 |

Resultados propios calculados (C), que no son novedad frente a la literatura: fuga ideal de la trinchera de referencia, 0,044 dB/cm en HE11 (VEC-GEO); contraste escalar-vectorial de la guía de salto (VEC-SALTO); la red F3-b no cumple H-F1 ni H-F2 (PLAN, fila 12).

## 3. Detalle por afirmación

### (a) Red 3D multicapa escrita con fs en vidrio

- **V.** HUST/SJTU, *Nature Communications*, publicado el 2026-04-21 (Crossref; V5 P1a). Texto completo en PMC13284361 (V5 §2). Chip escrito por escritura directa con láser fs en **vidrio borosilicato**. Dispositivo de **8 capas**, 8 × 8, con microcalentadores para programar (V5 P1b).
- **V.** Precisión: **93 % en entrenamiento** y **91,7 % en prueba** (48 imágenes) (V5 P1d y P1e). 6554 TOPS, que los autores describen como **teóricos** (V5 P1f).
- **Contradice.** La parte 3D multicapa escrita con fs en vidrio tiene antecedente publicado (V5 §8; LIT §8). El material del antecedente no es sílice.
- **C, limitación propia.** La función de la red del proyecto no está demostrada. F3-b no cumple H-F1 ni H-F2, y ningún punto de la rejilla alcanza 0,70 (PLAN, fila 12 y su actualización de T12).
- **Falta.** Escritura desde varias caras con registro entre caras medido (T9, bloqueada; `Docs/PROTOCOLOS-BLOQUEADOS-22-TAREAS.md`). Confirmar si el antecedente escribe desde una o varias caras (NV: V5 no lo evaluó). Material suplementario del antecedente, si existe (NV, no revisado).
- **Medida que la establecería.** Una red multicapa en sílice escrita desde varias caras, con registro entre caras medido y transmisión a 1550 nm (T9 y T14). El número de capas y el criterio se fijarían en un contrato previo a la medida.

### (b) Operación a 1550 nm en la red

- **V.** El cuerpo del texto de HUST/SJTU no contiene «1550», «1,55 µm», «1310», «telecom», «C-band» ni «O-band». Las longitudes de onda que aparecen son 515 nm (escritura), 800 nm (entrenamiento in situ) y 500 nm (parámetro de una estimación de escalado) (V5 P1c).
- **V (resumen).** El interferómetro programable de 8 puertos de Kondratyev et al. opera de 920 a 980 nm (LIT §6).
- **C.** Los modelos usan λ = 1550 nm y n0 = 1,444 como supuesto de contrato (por ejemplo, `Docs/GLASS-003-V2-CONTRACT.md` y `Docs/GLASS-GPU-002-CONTRACT.md`). Es un supuesto de modelo, no una medida.
- **Contradice o limita.** Nada verificado contradice la operación a 1550 nm. Pero que un texto no declare una longitud de onda no prueba que opere en otra. El argumento posible es que no está declarada, no que esté excluida.
- **Falta.** Cualquier medida de red en 1550 nm. Muestras de calibración (T13) y medidas ópticas calibradas (T14), ambas bloqueadas (PLAN, filas 13 y 14).
- **Medida que la establecería.** Transmisión a 1550 nm de un elemento de red (acoplador o interferómetro) con fuente calibrada y potencia de salida medida, sobre la misma muestra que la guía de (d).

### (c) Guías de camisa deprimida en trinchera a 1550 nm

- **V (título y metadatos).** *Optical Materials* 159, artículo 116651, 2025; DOI 10.1016/j.optmat.2025.116651. Título: «Femtosecond laser writing of telecom-band depressed-cladding waveguides and mode modulation in SK1310 glass» (V5 P3a; SK, sección de corrección).
- **NV (resumen visto en búsqueda).** Guías de camisa deprimida escritas con fs en banda de telecomunicaciones. El modo pasa de monomodo a multimodo al subir la energía de pulso. No se vieron pérdidas, dimensiones ni perfiles modales (V5 §4). No se sabe si la geometría es de trinchera ni si hay medida a 1550 nm.
- **V (acceso).** ScienceDirect devuelve 403 y Crossref no indica licencia abierta (V5 P3c). El acceso restringido es una inferencia de V5, no un hecho verificado.
- **NV (referencia de pérdidas).** Springer, DOI 10.1007/s00339-015-8990-x: unos 0,3 dB/cm en guía tubular, longitud de onda no confirmada (LIT §1, fragmento). Es la base del umbral de H1 (T20 §2).
- **V (curvatura, otra geometría).** Lee et al. 2021: 1 dB/cm con radio de 10 mm a 1550 nm, en ambas polarizaciones, con microgrieta y no con camisa deprimida. A 6 mm, 3 dB/cm en polarización x (V5 P2a y §3).
- **C.** Fuga ideal de la trinchera de referencia (δn = −0,005; t = 12 µm; a = 6 µm): 0,044 dB/cm en HE11 (VEC-GEO). Es un límite de fuga, no la pérdida total.
- **Contradice o limita.** La formulación «primera trinchera a 1550 nm» queda superada si el artículo SK1310 cubre trinchera en telecomunicaciones. Eso no está verificado. El índice de SK-1310 a 1550 nm (1,44463) es un supuesto (SK). Afecta a la fase absoluta, no al contraste Δn.
- **Falta.** Texto del artículo SK1310, que debe subir el titular o un acceso institucional (PLAN, fila 5). Geometría, longitud de onda y método de pérdidas del artículo. Medida propia.
- **Medida que la establecería.** H1 de T20 medida por cutback a 1550 nm según F2. La comparación con SK1310 solo es posible con el texto del artículo. Sin él, (c) no queda establecida aunque se mida.

### (d) Cutback propio a 1550 nm con pérdidas de acoplo y propagación separadas

- **V (protocolo).** F2 §3: longitudes de 1, 2, 3 y 4 cm en el mismo chip; tres chips por geometría; dos polarizaciones; pendiente de la regresión lineal de dB frente a L; pérdidas de acoplo como ordenada en el origen. El protocolo está publicado antes de cualquier medida (F2, encabezado).
- **V (estado).** Ninguna medida. Faltan láser fs de escritura, fuente a 1550 nm, banco de corte, cámara InGaAs y microscopio de fase cuantitativa (F2, «Recursos necesarios»).
- **V (resumen, otra familia).** Skryabin et al. (arXiv:2408.06688): 0,07 dB/cm en guías multiscan y 0,2 dB por faceta. La longitud de onda no está en el resumen (LIT §1; F2 §4). No son camisas deprimidas.
- **NV (métodos en fragmentos).** arXiv:2409.13110 (zafiro, fs): pérdida por diferencia de inserción entre muestras de 10, 40 y 100 mm. Según el fragmento, no es un cutback de una sola muestra (LIT §7). arXiv:1605.06580 (niobato de litio): pérdida combinada de inserción y propagación, 2,15 dB (s) y 6,04 dB (p), sin separar (LIT §1). Muestran que el problema de separar acoplo y propagación aparece en la literatura, pero no establecen un método estándar.
- **Contradice o limita.**
  - **Modo no especificado.** H1 habla de «pérdida total de propagación» sin modo. En la misma geometría, el modelo da 0,044 dB/cm para HE11 y 2,75–2,79 dB/cm para HE21, TE01 y TM01 (VEC-GEO, δn = −0,005, t = 12 µm). Si la medida excita modos superiores, el α medido puede reflejarlos. En la guía de salto análoga, V = 2,92 supera el corte de HE21/LP11 (V ≈ 2,41; VEC-SALTO, controles).
  - **Excitación no especificada.** F2 §3.2 no define cómo se excita el modo ni si se filtran modos en la medida de corte.
  - **Cota ideal.** 0,044 dB/cm supone camisa continua, sin dispersión ni defectos de escritura (F2 §1).
  - **Cálculo directo (C).** 0,044 dB/cm × 3 cm ≈ 0,13 dB de diferencia entre los extremos del intervalo de longitudes. El criterio de incertidumbre de pendiente, ≤ 0,01 dB/cm (F2 §3.2), exige que el acoplo sea estable entre chips. Es una comprobación de diseño, no un resultado.
- **Falta.** Laboratorio. Control y declaración de la excitación modal. Perfil de índice medido (F2 §3.1, incertidumbre objetivo ≤ 5·10⁻⁵ en δn). Birrefringencia de escritura, no caracterizada (F2 §6; SK).
- **Medida que la establecería.** F2 ejecutado con el perfil de índice medido, excitación modal declarada y las dos polarizaciones. Las pérdidas de acoplo y de propagación se separan por ordenada en el origen y pendiente.

### (e) Contraste con el modelo vectorial

- **C, guía de salto ideal.** El solver vectorial analítico de capas reproduce los n_eff de la fibra de salto analítica con diferencia de 10⁻¹⁶ (VEC-GEO, validación). Para el modo fundamental, el escalar difiere del vectorial en 2·10⁻⁶ relativo. La dispersión de polarización en LP11 es 2,6·10⁻⁶; el criterio H2 de VEC-SALTO exigía ≥ 10⁻⁴ y no se cumple. Esos H1 y H2 son los de VEC-SALTO, no los de T20.
- **C, trinchera.** HE11 vectorial frente al escalar (GLASS-006a): pérdidas dentro de 0,5–2,5 % y Δn_eff ≤ 6·10⁻⁶ (VEC-GEO). Separación TE01–TM01 en δn = −0,005: 3,1–3,2·10⁻⁶ (VEC-GEO).
- **V (limitación medida).** Un FD escalar estándar converge con orden observado 1,4. Con h = 0,125 µm el error es 4,2·10⁻⁶, del mismo orden que la separación TE/TM (VEC-GEO, convergencia). El FD vectorial independiente sigue pendiente (PLAN, fila 6).
- **Contradice o limita.**
  - T20 §4 dice «validado contra fibra analítica (1e-16)». Es la validación de n_eff de la fibra de salto. La pérdida de la trinchera de 0,044 dB/cm no tiene validación analítica; se compara con el escalar (−0,47 %).
  - Para δn = −0,003, TE01, TM01 y HE21 quedan fuera de validez. Solo HE11 es válido en todas las geometrías (VEC-GEO).
  - Geometría circular y capas uniformes. Sin no circularidad, tensión de escritura ni birrefringencia inducida. No es un solver FD o FE independiente (VEC-GEO, «Lo que no afirma»; VEC-SALTO, limitaciones).
  - Hay archivos de T6 modificados el 2026-10-10 entre las 12:25 y las 12:29 UTC (`experimentos/vectorial_claude/fd_vectorial_gate.py`, `fd_vectorial_run.py` y `CONTRATO-T6-r5.md`). No hay informe de resultados en el repositorio al redactar este documento. No se han leído y no se cuentan como evidencia.
- **Falta.** FD o FE vectorial validado frente a la fibra analítica y frente a 0,044 dB/cm. Auditoría independiente (Codex, PLAN, fila 6). Perfil de índice medido (F2).
- **Medida que la establecería.** Acuerdo del modelo vectorial con el campo modal medido (F2, P-F2b, acuerdo del 5 %) y con la pérdida medida en (d) (F2, P-F2a).

## 4. Afirmaciones de los documentos que hay que matizar

Estos documentos no son parte de este encargo y no se han editado. Las correcciones se proponen al coordinador.

| Documento | Afirmación | Estado real | Corrección propuesta |
|---|---|---|---|
| T20 §1 (línea 12) | HUST/SJTU «no está verificado en texto completo» | Superada: texto completo leído (V5 §2) | Actualizar |
| T20, actualización de novedad (línea 60) | SK1310 «ya la publica» la trinchera a 1550 nm | Solo el título está verificado; geometría y λ no verificadas | Decir que publica guías de camisa deprimida en banda de telecomunicaciones, según el título |
| T20 §4 | 0,044 «validado contra fibra analítica (1e-16)» | La validación es de n_eff; la pérdida se compara con el escalar (−0,47 %) | Separar ambas validaciones |
| T20 §4 y VEC-SALTO | «H1 cumple, H2 no cumple» | Son H1 y H2 del contraste vectorial de la guía de salto, no las de T20 | Renombrar (por ejemplo VH1 y VH2) y citar rutas exactas |
| LIT §4 | «Un resultado negativo medido» (F3) | Es cálculo del modelo (C), no medida | Escribir «calculado» |
| LIT §4 | «Un contraste escalar-vectorial cuantificado» como aporte | Calculado para la guía de salto ideal, no para la trinchera | Precisar el alcance |
| LIT §6 y §7 | HUST/SJTU «[B] solo prensa» y «mayo de 2026» | Superado por LIT §8: publicado el 2026-04-21, texto completo | Aplicar V5 §5, punto 1 |
| SK, tabla inicial | «la búsqueda no lo localiza ni por título ni por SK1310» | Incorrecta. La sección «Corrección» del final la reconoce, pero la tabla no se ha actualizado | Actualizar la tabla y añadir el DOI (V5 §5, punto 2) |
| PLAN, tabla de cierre, fila 19 | «el de 2026 no» está verificado | Desfasado: V5 lo verificó en texto completo | Actualizar la fila |

## 5. Cierre: T19 y T20

### T19 · Novedad científica con antecedentes verificados

- **Estado: parcial. No se cierra.** El plan define T19 por antecedentes verificados (PLAN, fila 19). Hoy hay texto completo verificado para HUST/SJTU y Lee et al. (V5). Hay resúmenes verificados para Kondratyev et al., Shen et al. y Skryabin et al. (LIT §1, §2 y §6). Hay fragmentos o prensa para Springer, Amorim, niobato de litio, zafiro, Okhrimchuk y Ross-Adams. De SK1310 solo está verificado el título.
- **Qué cambia hoy.** (1) HUST/SJTU pasa de prensa a texto completo, y la afirmación (a) queda cubierta por antecedente. (2) La afirmación (c) pasa a riesgo alto con el título verificado.
- **Qué sigue pendiente.** Texto de SK1310. Método y longitud de onda de Skryabin et al. Texto de Springer y de Amorim. Método de la no linealidad en Shen et al. Material suplementario de HUST/SJTU. Si el antecedente escribe desde varias caras. Mientras esos puntos estén abiertos, T19 no cumple su criterio.

### T20 · Contribución central con hipótesis falsable

- **Estado: abierta.** T20 se cierra «cuando el test decisivo tenga datos» (T20, encabezado). No hay datos. El estado de PLAN, fila 20 («documento preregistrado; test pendiente de medida»), es correcto.
- **Qué cambia en T20 con este documento, sin cambiar H1.**
  1. Reformular la frase sobre SK1310 (T20, línea 60) y la que dice que HUST/SJTU no está verificado (T20 §1), según la sección 4.
  2. Acotar «validado contra fibra analítica» a n_eff (T20 §4).
  3. Renombrar las H1 y H2 del contraste vectorial de la guía de salto (VEC-SALTO).
  4. Declarar el modo de la pérdida en el test (punto i, abajo).
- **H1 no se propone cambiar en este documento.** Los puntos siguientes son ambigüedades de definición o de regla de decisión. Deben declararse como enmienda con fecha antes de medir:
  - **(i) Modo y excitación.** H1 no declara modo ni excitación. Según VEC-GEO, HE11 da 0,044 dB/cm y los modos superiores 2,75–2,79 dB/cm en la misma geometría. Sin modo declarado, la prueba puede fallar por modos superiores aunque el fundamental cumpla.
  - **(ii) Regla de decisión incompleta.** T20 falsa H1 (F1) si el límite inferior del IC 95 % supera 0,3 dB/cm. T20 la confirma si el límite superior es ≤ 0,3 dB/cm y el inferior ≥ 0,044 dB/cm. Quedan sin resolver dos zonas: el IC que contiene 0,3 dB/cm, y el IC que contiene 0,044 dB/cm. Además, F2 P-F2a usa 0,044 − 3σ en lugar del IC 95 %. Son dos reglas en el mismo preregistro.
  - **(iii) Base del umbral de 0,3 dB/cm.** Procede de Springer 2015: guía tubular, longitud de onda no confirmada y sin verificar (NV). T20 §2 lo usa como referencia de competitividad. Si se mantiene, su origen debe declararse como no verificado. Si se cambia, es una enmienda.
  - **(iv) Definición de «pérdida total de propagación».** Conviene fijar qué incluye (fuga, dispersión y absorción) y que excluye el acoplo, como separa F2 §3.3.
  - **(v) Referencia de fuga.** F2 usa 0,0443 dB/cm (escalar, F2 §1) y T20 usa 0,044 (vectorial, 0,044044; VEC-GEO). Conviene citar una sola fuente.
- **Viabilidad (C).** Véase (d): 0,044 dB/cm sobre 3 cm son unos 0,13 dB.

## 6. Pendientes

- **Titular:** subir el PDF de SK1310 o dar acceso institucional (PLAN, fila 5). Decidir el socio experimental para T14 (T20 §6). Decidir si H1 se enmienda antes de medir.
- **Coordinador:** aplicar V5 §5 (puntos 1 a 4) y las correcciones de la sección 4. Actualizar la fila 19 de PLAN.
- **Codex y T6:** FD vectorial validado frente a la fibra analítica y frente a 0,044 dB/cm.
- **Medidas (laboratorio):** F2 completo (T14); red y registro entre caras (T9); muestras de calibración (T13).

## 7. Límites

- Fuentes leídas completas: LIT, T20, SK, V5, F2, VEC-GEO, VEC-SALTO y PLAN. Citadas solo a través de otro documento: `experimentos/f3_red_pequena` (vía PLAN), `experimentos/acoplo_claude/RESULTADOS-ACOPLO.md` (vía T20), `Docs/PROTOCOLOS-BLOQUEADOS-22-TAREAS.md` (solo líneas localizadas por búsqueda) y los contratos GLASS (solo la línea de longitud de onda).
- El texto de HUST/SJTU lo leyó V5 mediante extracción de PMC. No se ha releído aquí. Las citas literales deben comprobarse en el PDF antes de usarlas fuera del repositorio (V5 §6).
- La ficha OHARA se leyó visualmente (V5 §6).
- Este documento no es una búsqueda exhaustiva de novedad. Cubre las búsquedas de LIT §6 a §8.
- Las cifras de cálculo directo (0,13 dB sobre 3 cm) se derivan de F2 y están marcadas como (C).
- JEV: no se consultó `router.py` para esta redacción, porque el documento no contiene decisiones sustanciales. Ninguna decisión de JEV se atribuye a este documento.
- V5 señala copias automáticas de los PDF de OHARA en `C:\Users\...\tool-results\` (1,9 MB y 2 MB), no creadas en esta tarea. Conviene revisarlas, dado el poco espacio libre en C:.
- Este encargo escribe solo `Docs/NOVEDAD-ESTADO-20261011.md`. No se han hecho `git add`, commit ni push.
