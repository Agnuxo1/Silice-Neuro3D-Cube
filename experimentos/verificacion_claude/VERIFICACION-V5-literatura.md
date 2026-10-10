# VERIFICACIÓN V5: literatura (agente Claude)

- Fecha: 2026-10-10. Contrato previo: `CONTRATO-literatura-V5.md` (umbrales fijados antes de buscar).
- Estado: **done**. Se evaluaron todos los criterios del contrato. Dos resultados quedan **unverified** y una afirmación del proyecto queda **refuted**.
- Alcance: solo literatura y documentación. No hay cálculo de la red. Modelo, predicción y medida no se mezclan.
- Única comprobación numérica: tabla de índices de SK-1310 (script `comprobar_sk1310.py`, Python `-B`, biblioteca estándar).
- Terminología: en el esquema JSON, «verified» se corresponde con `confirmed`.
- Numeración: los identificadores P1 y P2 coinciden con el contrato, pero P1 tiene más subapartados (P1b se divide en material, longitud de onda y cifras). En P3 el contrato usa a = acceso, b = enlace, c = índices. Aquí: P3a = localización del artículo (adición), P3b = afirmación refutada del proyecto (adición), P3c = acceso (contrato P3a), P3d = enlace OHARA (contrato P3b), P3e = índices (contrato P3c).

## 1. Veredictos

| Punto | Afirmación del proyecto | Veredicto | Fuente principal |
|---|---|---|---|
| P1a | HUST/SJTU, *Nature Communications* 2026, existe | **confirmed** | Crossref y PMC13284361 |
| P1b | Red en vidrio escrita con láser fs | **confirmed**, con matiz: el vidrio es **borosilicato**, no sílice | PMC13284361 (Abstract, Methods) |
| P1c | Longitud de onda de operación | **unverified**: el artículo no la declara (ni 1550 ni 1310 nm) | PMC13284361 |
| P1d | 93 % MNIST aparece en el artículo | **confirmed** (cifra presente) | PMC13284361 (Abstract) |
| P1e | 93 % es precisión de prueba | **refuted**: es de **entrenamiento**; la de prueba es 91,7 % | PMC13284361 (Results, Fig. 3c) |
| P1f | 6554 TOPS aparece en el artículo | **confirmed** (cifra presente), descrita por los autores como **teórica** | PMC13284361 (Abstract, Conclusion) |
| P2a | Lee et al., *Sci. Rep.* 2021: ~1 dB/cm, radio 10 mm, 1550 nm | **confirmed** | PMC8660921, Crossref |
| P2b | DOI y técnica de microgrietas | **confirmed** | Crossref 10.1038/s41598-021-03116-y, PMC8660921 |
| P3a | El artículo SK1310 existe y tiene DOI | **confirmed** | WebSearch, Crossref 10.1016/j.optmat.2025.116651 |
| P3b | `SK1310-FUENTES.md` dice que la búsqueda no lo localiza ni por título ni por SK1310 | **refuted** | WebSearch (primer resultado) |
| P3c | Acceso abierto del PDF del artículo SK1310 | **unverified** (ScienceDirect devuelve 403; no hay licencia CC en Crossref) | ScienceDirect, linkinghub, Crossref |
| P3d | El enlace OHARA del proyecto funciona | **confirmed** | oharacorp.com/wp-content/uploads/2025/02/SK1310.pdf |
| P3e | Índices de la ficha a 25 °C coherentes con la tabla del proyecto | **confirmed** (diferencia máxima 4,7·10⁻⁶ frente al umbral 10⁻⁴) | Ficha OHARA, página 2 |

## 2. P1: «Programmable Three-dimensional Photonic Neural Network Chip»

**Existencia y metadatos (P1a).** Crossref registra el título exacto, *Nature Communications*, DOI `10.1038/s41467-026-72316-9`, publicado el **2026-04-21**. Tiene 14 autores; entre ellos, Xinliang Zhang, Jianji Dong, Hao Tang y Xiao-Yun Xu, que coinciden con los nombres de la prensa. La licencia es CC BY-NC-ND 4.0. La fecha de «mayo de 2026» de `LITERATURA-NOVEDAD.md` es la de la prensa (36Kr); la fecha del artículo es abril.
- Enlaces: https://api.crossref.org/works/10.1038/s41467-026-72316-9 · https://pmc.ncbi.nlm.nih.gov/articles/PMC13284361/ · https://www.nature.com/articles/s41467-026-72316-9 (la página redirige a un inicio de sesión del editor; no se siguió la redirección y el texto se leyó desde PMC).

**Material y fabricación (P1b).** El resumen dice que el chip está «fabricated by femtosecond laser direct writing (FLDW) in glass». Los Methods precisan que los guiaondas y los microcalentadores van en un **sustrato de vidrio borosilicato**. El proyecto habla de «red en silice», así que la comparación debe anotar que el material es distinto.

**Longitud de onda (P1c, unverified).** El texto no declara la longitud de onda de operación de la red. No aparece «1550», «1,55 µm», «1310», «1,31», «telecom», «C-band» ni «O-band» en el cuerpo del artículo. Las longitudes de onda que sí aparecen:
- 515 nm: láser de escritura fs (Methods).
- 800 nm: láser de entrenamiento in situ (Methods, «An 800 nm laser beam»).
- 500 nm: parámetro de una estimación hipotética de escalado (Results), no una longitud de onda de operación.
Esto no refuta nada: el artículo simplemente no lo dice. Para el proyecto, la pregunta de si opera en 1550 nm queda abierta.

**93 % MNIST (P1d y P1e).** El resumen dice «93% accuracy on MNIST classification». El cuerpo lo aclara:
- «the training accuracy rises on average to 93% despite fluctuations» (Results).
- Pie de la figura 3c: «Confusion matrices for the training set (left, 93% accuracy) and the testing set (right, 91.67% accuracy)».
- Conjunto de entrenamiento: «a dataset of 200 images (50 per class)». Conjunto de prueba: «a test dataset of 48 images, which yields an accuracy of 91.7%».
Conclusión: la cifra de 93 % es **precisión de entrenamiento**, y la de prueba es 91,7 % con 48 imágenes. El proyecto debe citar 91,7 % si quiere hablar de generalización. (Este matiz coincide con lo que ya anotaba `coordinacion/respuestas/GLASS-001-CLAUDE.md`: «93 % (entrenamiento) / 91,7 % (prueba)».)

**6554 TOPS (P1f).** Aparece en el resumen: «An 8-layer 8 × 8 device achieves a computing throughput of 6554 TOPS». La conclusión la califica de «detector-limited theoretical computing throughput». No es un rendimiento medido.

**Otros datos del mismo artículo.** El resumen también da «94% fidelity in optical pattern generation» (similitud coseno media >94 %). No se evaluó más allá de esa cifra.

## 3. P2: Lee et al., *Scientific Reports* 2021

- Título: «Low bend loss femtosecond laser written waveguides exploiting integrated microcrack». Autores (según PMC): Timothy Lee, Qi Sun, Martynas Beresna, Gilberto Brambilla. *Sci. Rep.* 11, 23770 (2021), publicado el 2021-12-09. DOI `10.1038/s41598-021-03116-y`. Licencia CC BY 4.0.
- Enlaces: https://pmc.ncbi.nlm.nih.gov/articles/PMC8660921/ · https://api.crossref.org/works/10.1038/s41598-021-03116-y

**Valor de pérdida (P2a, confirmed).** El texto dice: «For λ=1.55 μm, 1 dB/cm is measured at a very tight radius of rb=10 mm for both polarizations». Cumple el criterio: 1 dB/cm en [0,5; 2], radio 10 mm y λ 1550 nm.

**Contexto para la curva de T8 (no es una verificación nueva).**
- El punto de 1 dB/cm es el mejor caso, a 10 mm y para ambas polarizaciones. A 1550 nm con 6 mm, el texto da 3 dB/cm (polarización x).
- A 1310 nm se da 1 dB/cm a 8,5 mm.
- El artículo compara con SMF-28 (3,2 dB/cm frente a 2 dB/cm para la guía, a 7 mm). La longitud de onda de esa comparación no se especifica en la frase leída.
- La técnica consiste en crear una microgrieta por tensión asimétrica en el borde exterior de la curva, escrita en la misma pasada multiscan. Sección estimada de la grieta: 15 µm de alto y 30 nm de ancho. Guía de 10 × 10 µm.
- Un trabajo de 2024 (Ross-Adams et al., *Light: Advanced Manufacturing*) menciona un radio de corte de 4 mm para 1 dB/cm a 1550 nm. Lo vi solo en un resumen de búsqueda; **no está verificado** y queda como pista.

## 4. P3: SK1310

**Localización del artículo (P3a, confirmed).** La búsqueda por título devuelve el registro de ScienceDirect (PII `S0925346725000102`): «Femtosecond laser writing of telecom-band depressed-cladding waveguides and mode modulation in SK1310 glass». Crossref lo confirma: *Optical Materials*, volumen 159, artículo 116651, 2025-02, DOI `10.1016/j.optmat.2025.116651`. Autores: J. Zhou, W. Liu, W. Cheng, H. Du, B. Wu, L. Wang, Q. Lu, B. Zhang, F. Chen.
- Enlace: https://api.crossref.org/works/10.1016/j.optmat.2025.116651
- Según el resumen visto en búsqueda, el artículo trata guías con camisa deprimida en SK1310 escritas con fs, y el modo pasa de monomodo a multimodo al subir la energía de pulso, en la banda de telecomunicaciones. No vi cifras de pérdidas, dimensiones ni perfiles modales.

**Afirmación refutada (P3b).** `Docs/SK1310-FUENTES.md` dice que «la búsqueda no lo localiza por título ni por SK1310». La búsqueda de hoy lo localiza en el primer resultado. Corrección propuesta: el artículo está localizado; lo que falta es el PDF.

**Acceso abierto (P3c, unverified).** Ni ScienceDirect ni el editor dejan leer la página: `sciencedirect.com/…/abs/pii/S0925346725000102` devuelve **403**, y `doi.org/10.1016/j.optmat.2025.116651` redirige a `linkinghub.elsevier.com`, que devuelve solo «Redirecting» sin etiqueta de acceso. Crossref tiene 7 entradas de licencia, todas de TDM y de políticas `stm-asf` de Elsevier. **No hay ninguna licencia Creative Commons**, que sí aparece en los artículos de Elsevier con acceso abierto. Eso apunta a acceso restringido, pero es una inferencia y no está verificado. La herramienta de lectura de Crossref interpretó esas entradas como acceso abierto; no lo acepto como prueba.

**Enlace OHARA (P3d, confirmed).** `https://oharacorp.com/wp-content/uploads/2025/02/SK1310.pdf` devuelve el PDF (dos páginas, creado con Canva el 2025-02-06). Las tablas son imágenes, no texto; las leí visualmente de la página 2. Hay un segundo PDF, `SK1310-fused-silica.pdf`, que también responde (solo imagen).

**Índices a 25 °C (P3e, confirmed).** La ficha da, en aire a 25 °C, los siguientes índices. Los comparé con los del proyecto (`Docs/SK1310-FUENTES.md`, en vacío) dividiendo entre el factor 1,000277 que usa el proyecto:

| λ (µm) | Línea | Ficha, aire, 25 °C | Proyecto, vacío | Proyecto → aire | Diferencia |
|---|---|---|---|---|---|
| 0,365015 | i | 1,47475 | 1,47516 | 1,474751 | +1,5·10⁻⁶ |
| 0,404656 | h | 1,46982 | 1,47023 | 1,469823 | +2,9·10⁻⁶ |
| 0,435835 | g | 1,46689 | 1,46730 | 1,466894 | +3,7·10⁻⁶ |
| 0,486133 | F | 1,46333 | 1,46374 | 1,463335 | +4,7·10⁻⁶ |
| 0,546075 | e | 1,46028 | 1,46068 | 1,460276 | −4,5·10⁻⁶ |
| 0,587562 | d | 1,45866 | 1,45906 | 1,458656 | −4,1·10⁻⁶ |
| 0,656273 | C | 1,45657 | 1,45697 | 1,456567 | −3,5·10⁻⁶ |

- Máxima diferencia: 4,7·10⁻⁶, dentro del umbral 10⁻⁴ del contrato. Es del orden de la precisión de medida de la ficha (±5·10⁻⁶).
- Otros datos de la misma ficha: dn/dT 10,2–11,5·10⁻⁶ /°C (intervalo 20–5 °C), densidad 2,2 g/cm³, birrefringencia de deformación ≤ 20 nm/cm, OH < 1 ppm, Cl < 2000 ppm. Todos coinciden con la sección «fuentes» del proyecto.
- Límite: el factor 1,000277 aire→vacío **no está verificado de forma independiente**; la ficha no lo da. Lo que sí se verifica es que la tabla del proyecto es la de la ficha multiplicada por ese factor.
- Límite: la ficha llega solo a 656 nm. El índice a 1550 nm (1,44463) sigue siendo una suposición, como dice el proyecto.

## 5. Correcciones propuestas al coordinador (no aplicadas; `Docs/` es del coordinador)

1. `Docs/LITERATURA-NOVEDAD.md`, §6 y §7: pasar la entrada HUST/SJTU de «[B] solo prensa» a «[V] texto completo vía PMC». Añadir DOI `10.1038/s41467-026-72316-9`, fecha 2026-04-21, vidrio **borosilicato**, longitud de onda de operación **no declarada**, 93 % = entrenamiento, 91,7 % = prueba (48 imágenes), 6554 TOPS = teórico.
2. `Docs/SK1310-FUENTES.md`: corregir la afirmación de que la búsqueda no localiza el artículo. Añadir DOI `10.1016/j.optmat.2025.116651`. Mantener «acceso no determinado».
3. Nota sobre la contribución 3D: el artículo de HUST/SJTU sí es una red 3D escrita con fs en vidrio, con 8 capas. Lo que no cubre, según el texto leído, es operación en telecomunicaciones (no declarada). Si el proyecto quiere afirmar «1550 nm» como diferencia, ya tiene una base documental. No busqué «cutback» en el texto ni afirmo nada sobre pérdidas por cutback.
4. T8 (`coordinacion/tareas/PLAN-22-TAREAS-20261010.md`): la referencia de Lee et al. queda verificada en su punto de 1 dB/cm a 10 mm y 1550 nm. Añadir la nota de que es el mejor caso y de que a 6 mm son 3 dB/cm.

## 6. Límites

- Las citas textuales vienen de la herramienta de extracción (WebFetch), que procesa el texto con un modelo. Pedí citas literales, pero el coordinador debe comprobar las frases clave en el PDF antes de citarlas en un documento.
- La ficha OHARA se leyó visualmente de una imagen. Un error de transcripción en la última cifra es posible. La coincidencia de las siete líneas con la tabla del proyecto reduce ese riesgo.
- No se siguió ninguna redirección a un proveedor de identidad (idp.nature.com).
- No se descargó ningún PDF al repositorio ni a D:. WebFetch dejó copias automáticas de los dos PDF de OHARA en `C:\Users\Windows-500GB\.claude\projects\…\tool-results\` (1,9 MB y 2 MB). No las creé yo; el coordinador puede borrarlas si quiere liberar espacio en C:.
- Plan JEV (`router.py plan`, id `1791605554-research`): ejecutor `main_agent`, esfuerzo bajo, sin segunda opinión. La salida no trae `provenance`, así que la decisión se registra como local. No se hizo una consulta `jev` con `provenance=jev`.
- La carpeta `experimentos/verificacion_claude/` es compartida con otros trabajos del mismo flujo. Contiene archivos como `CONTRATO-V1.md`, `CONTRATO-V4.md`, `v1_*`, `v4_*`, `verif_*` y `log_bpm_*`, creados entre 04:13 y 04:19 UTC. No los he leído ni modificado. Mis archivos son `CONTRATO-literatura-V5.md`, `VERIFICACION-V5-literatura.md` y `comprobar_sk1310.py`.
- No se leyó ni se imprimió ninguna clave. No se abrió `Desktop/UTILIDADES_HERRAMIENTAS_APIs.txt`. No se hizo `git add`, commit ni push. No se tocó `src/silice/`, `tests/`, `scripts/`, `coordinacion/` ni `Docs/`.

## 7. Enlaces usados

- https://api.crossref.org/works/10.1038/s41467-026-72316-9
- https://pmc.ncbi.nlm.nih.gov/articles/PMC13284361/
- https://www.nature.com/articles/s41467-026-72316-9 (redirige al inicio de sesión del editor; no leído)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC8660921/
- https://api.crossref.org/works/10.1038/s41598-021-03116-y
- https://www.nature.com/articles/s41598-021-03116-y (redirige al inicio de sesión del editor; no leído)
- https://api.crossref.org/works/10.1016/j.optmat.2025.116651
- https://www.sciencedirect.com/science/article/abs/pii/S0925346725000102 (403)
- https://doi.org/10.1016/j.optmat.2025.116651 → https://linkinghub.elsevier.com/retrieve/pii/S0925346725000102 («Redirecting»)
- https://oharacorp.com/wp-content/uploads/2025/02/SK1310.pdf (datos en la página 2)
- https://oharacorp.com/wp-content/uploads/2025/02/SK1310-fused-silica.pdf (solo imagen)
- https://oharacorp.com/glass/sk-1310/ (página de producto; solo cuatro líneas en la extracción; la ficha PDF es la fuente completa)
- Script: `experimentos/verificacion_claude/comprobar_sk1310.py`
