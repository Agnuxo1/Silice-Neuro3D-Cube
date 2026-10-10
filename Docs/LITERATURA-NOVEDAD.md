# Literatura y novedad: mapa de antecedentes (2026-10-09)

Mapa de antecedentes para situar el proyecto frente a la camisa deprimida, las redes ópticas lineales y las herramientas de simulación. **Etiquetas:** [V] = verificado en el texto o en el resumen con una lectura directa; [B] = solo en fragmentos de búsqueda, pendiente de leer el artículo completo.

## 1 · Pérdidas en sílice escrita con láser fs

| Referencia | Resultado | Longitud de onda | Estado |
|---|---|---|---|
| Skryabin et al., [arXiv:2408.06688](https://arxiv.org/abs/2408.06688) (2024) | Pérdida de propagación **0,07 dB/cm**; acoplamiento 0,2 dB por faceta; solapamiento > 98,8 % con fibra SMF-28 | No indicada en el resumen (una búsqueda secundaria la sitúa en 920 nm) | [V] resumen. Guías multiscan, **no** camisa deprimida |
| Springer, [DOI 10.1007/s00339-015-8990-x](https://link.springer.com/10.1007/s00339-015-8990-x) (2015) | Guía tubular de camisa deprimida en sílice fundida, unos **0,3 dB/cm**; diferencia entre polarizaciones de unos 0,1 dB/cm | No confirmada | [B] fragmento de búsqueda |
| Amorim et al., Journal of Lightwave Technology (2019) | Mapa de pérdidas de guías fs en sílice entre 350 y 1750 nm; la escritura rápida empeora la dispersión de Rayleigh y la pérdida de acoplamiento a larga longitud de onda | Barrido 350–1750 nm | [B] fragmento de búsqueda; no es arXiv |
| Lithium niobate, [arXiv:1605.06580](https://arxiv.org/pdf/1605.06580) (2016) | Camisa deprimida enterrada a 1550 nm: pérdida combinada de inserción y propagación de unos **2,15 dB** (s) y **6,04 dB** (p) en una guía de unos 13 µm | 1550 nm | [B] fragmento. Cota superior de pérdida de propagación, no medida separada |

**Lectura para el proyecto.** En sílice a 1550 nm, el valor más cercano a camisa deprimida que aparece es el de 0,3 dB/cm en guía tubular, y su longitud de onda no está confirmada. El límite de fuga ideal de [F2](F2-PROTOCOLO-MEDIDA.md) (0,044 dB/cm para t = 12 µm) queda por debajo de todas las pérdidas reportadas, lo que es coherente con que la fuga sea solo una parte de la pérdida total.

## 2 · Redes ópticas lineales con detección

- **Shen et al., [arXiv:1610.02365](https://arxiv.org/abs/1610.02365)** y **Nature Photonics 11, 441 (2017)**, [DOI 10.1038/nphoton.2017.93](https://doi.org/10.1038/nphoton.2017.93) [V, resumen y metadatos]. Una malla de interferómetros con 56 elementos ajustables en chip de silicio, con una etapa no lineal, probada con reconocimiento de vocales. Los resúmenes difieren en la fuerza con que afirman las ganancias de velocidad y eficiencia. **No se ha confirmado cómo se implementa la no linealidad experimental** (puramente óptica u optoelectrónica).
- **Revisión** [arXiv:2509.01262](https://arxiv.org/pdf/2509.01262) [B]. Tabula ese trabajo como malla 4×4 con 76,7 % en la tarea de vocales. La cifra de 56 elementos y la etiqueta 4×4 pueden referirse a cosas distintas. Verificar antes de citar.
- **Resultado propio** (F3, [RESULTADOS-F3](../experimentos/f3_red_pequena/RESULTADOS-F3.md)): una malla unitaria 4×4 con lectura de intensidad llega al 59 % en una tarea cuadrática congelada. Ese resultado es una cota de la familia unitaria con esa lectura; no contradice a Shen et al., que usa otra tarea y otra arquitectura.

## 3 · Herramientas de simulación (Python y GitHub)

Búsqueda [B]: ninguna herramienta abierta encontrada cubre a la vez BPM vectorial, solver de modos vectorial y guías escritas con fs. Candidatos, sin verificar licencia ni mantenimiento salvo indicación:

| Herramienta | Tipo | Notas de la búsqueda |
|---|---|---|
| Murphy `modesolver` ([GitHub](https://github.com/thomas-e-murphy/modesolver)) | Solver de modos escalar, semivectorial y vectorial completo | Malla no uniforme, PML con coordenadas complejas; actualización reciente indicada |
| `philsol` ([PyPI](https://pypi.org/project/philsol)) | Diferencias finitas vectoriales (Zhu y Brown) | Advierte que no está bien probado; último push 2021 |
| `modesolverpy` / `modes` ([GitHub](https://github.com/joamatab/modesolverpy)) | Semivectorial y vectorial completo | Pruebas diarias indicadas |
| `femwell` ([GitHub](https://github.com/HelgeGehring/femwell)) | Elementos finitos de modos | Licencia GPL-3.0 indicada en el README; la vectorialidad no está confirmada |
| `Beampy` ([PyPI](https://pypi.org/project/beampy)) | BPM para guías | Última actualización indicada 2020; no está claro si es vectorial |
| `Diffractio` ([PyPI](https://pypi.org/project/diffractio)) | Óptica escalar y vectorial, BPM y WPM | Licencia MIT indicada; las rutinas vectoriales no son BPM |
| `cbeam` ([GitHub](https://github.com/jw-lin/cbeam)) | Acoplo de modos en guías de pocos modos | Alternativa sin BPM |
| `femto` ([GitHub](https://github.com/ricalbr/femto)) | Diseño de circuitos fs y exportación | No simula propagación |

**Implicación.** El solver exacto de fibra de salto de [VECTORIAL-RESULTADOS](VECTORIAL-RESULTADOS.md) es una referencia analítica, no un solver general. Un solver FD vectorial independiente, como el de Zhu y Brown que implementa `philsol`, sería el siguiente paso para validar la trinchera con fuga. Antes de usarlo, habría que probarlo contra el mismo caso analítico.

## 4 · Novedad: qué se puede y qué no se puede afirmar

**No establecido:**
- Que una red o un acoplador lineal escrito en 3D con láser fs en sílice sea nuevo. Las redes lineales están demostradas en silicio (Shen et al.), y las guías de camisa deprimida son conocidas desde hace años.
- Que la pérdida de camisa deprimida en sílice a 1550 nm sea mejor o peor que la publicada. No hay medida comparable con el mismo diseño.
- Que la escritura desde seis caras o la red 3D sean factibles. Son hipótesis del proyecto.

**Lo que el proyecto sí aporta, con evidencia:**
- Un límite de fuga ideal explícito y su convergencia numérica (GLASS-006a, con la nota sobre no monotonía de Re γ).
- Un contraste escalar-vectorial cuantificado para una guía de salto análoga (H1 cumplida, H2 no cumplida).
- Un resultado negativo medido para la familia unitaria con lectura de intensidad (F3).

**Pendiente para establecer novedad:** comparar un diseño concreto con el estado del arte en el mismo régimen de longitud de onda, con una medida real. Eso depende de [F2](F2-PROTOCOLO-MEDIDA.md) y de un socio experimental.

## 5 · Lo que queda sin verificar

- Texto completo de Skryabin et al. (método de medida de pérdidas y longitud de onda).
- Texto completo del artículo de 2015 en Springer (longitud de onda, geometría).
- Texto completo de Shen et al. (método de la no linealidad).
- Licencias y estado de mantenimiento de las herramientas de la tabla 3.

## 6 · Actualización del 2026-10-10 (tarea 19)

Competidores directos que cambian la evaluación de novedad:

| Referencia | Qué afirma | Estado |
|---|---|---|
| Kondratyev et al., [arXiv:2308.13452](https://arxiv.org/abs/2308.13452) (2023) | Interferómetro **programable de 8 puertos** escrito con láser fs; funciona de 920 a 980 nm. Mismo grupo que [arXiv:2408.06688](https://arxiv.org/abs/2408.06688). | [V] resumen leído. No da pérdidas, número de MZI, vidrio ni fidelidad en el resumen |
| Prensa, mayo de 2026 (HUST y SJTU, Nature Communications, «Programmable Three-dimensional Photonic Neural Network Chip») | Chip fotónico neuronal **tridimensional y programable**: 93 % en MNIST, 6554 TOPS teóricos | [B] solo noticia secundaria. **Hay que leer el artículo antes de citarlo.** Si el enfoque es 3D programable, es el competidor más directo del proyecto |
| Shen et al., [arXiv:1610.02365](https://arxiv.org/abs/1610.02365) (2016/2017) | Red de interferómetros en silicio con etapa no lineal | [V] resumen |
| Skryabin et al., [arXiv:2408.06688](https://arxiv.org/abs/2408.06688) (2024) | Guías multiscan en sílice con 0,07 dB/cm y 0,2 dB por faceta | [V] resumen; longitud de onda no indicada en el resumen |
| Kondratyev et al. (arXiv:2308.13452) y Skryabin et al. (arXiv:2408.06688) | Mismo grupo, dos trabajos seguidos | — |

**Conclusión de novedad (actualizada).**
- **No es novedad:** una malla programable escrita con fs en vidrio (8 puertos, 2023), ni las guías multiscan de bajas pérdidas en sílice (2024).
- **Posible novedad, no establecida:** (a) red **tridimensional** de múltiples capas escrita desde varias caras; (b) operación y medida a **1550 nm**; (c) guías con **camisa deprimida en trinchera** caracterizadas con cutback a 1550 nm. Ninguna está demostrada en la literatura consultada.
- **Riesgo:** el trabajo de 2026 con chip neuronal 3D programable puede cubrir la idea de 3D antes que el proyecto. Hay que leer el artículo original.

**Fuentes que no se han verificado en texto completo:** Amorim et al., JLT 2019 (pérdidas 350–1750 nm); Springer DOI 10.1007/s00339-015-8990-x (guía tubular, 0,3 dB/cm); sapphire arXiv:2405.08840 (1,9 dB/cm propagación y 4,3 dB de acoplamiento, según fragmento); arXiv:1912.08203 (interconexiones 3D para PNN, no verificado en detalle).

## 7 · Segunda búsqueda del 2026-10-10 (tarea 19)

Búsqueda web en modo estándar. Todo lo de esta sección viene de resúmenes o prensa, no de texto completo.

| Referencia | Qué dice | Estado |
|---|---|---|
| HUST y SJTU, «Programmable Three-dimensional Photonic Neural Network Chip», *Nature Communications* (mayo de 2026, según 36Kr) | Red fotónica neuronal programable **dentro del vidrio**, núcleo de cómputo óptico 3D; 93 % en MNIST; 94 % de fidelidad en generación de patrones; 6554 TOPS teóricos. Autores: Zhang Xinliang y Dong Jianji (HUST), Tang Hao y Xu Xiaoyun (SJTU). | [B] solo prensa secundaria (36Kr, 28-05-2026, sin DOI). **Riesgo alto de solapamiento con la hipótesis 3D.** Longitud de onda no conocida. |
| arXiv:2409.13110 (zafiro, láser fs) | Núcleo de 10 µm en un revestimiento de unos 40 µm, 88 pistas; unos 0,7 dB/cm en TE y TM, obtenido por diferencia de inserción entre muestras de 10, 40 y 100 mm; una simulación de modo con fuga da 0,015 dB/cm. | [B] fragmento. Según el fragmento, no es un cutback de una sola muestra. Longitud de onda por confirmar. |
| Lee et al., *Scientific Reports* (2021) | Pérdida de curva en sílice escrita con fs, con técnica de microgrietas: unos 1 dB/cm con radio de 10 mm a 1550 nm. | [B] fragmento. **Referencia para la curva de T8** (pendiente). |
| Okhrimchuk et al., *Optics Express* (2012) | Guía con camisa deprimida en Nd:YAG: 0,12 dB/cm a 1064 nm. | [B] no es sílice ni 1550 nm; solo referencia de orden de magnitud. |

**Conclusión actualizada.**
- No se ha encontrado un cutback a 1550 nm en camisa deprimida de sílice escrita con fs. La brecha que describen los autores del niobato de litio sigue abierta, lo que mantiene la candidatura de (c), sin establecerla.
- La contribución (a), «red 3D multicapa escrita desde varias caras», **queda en riesgo** por el trabajo de HUST/SJTU de 2026, que no hemos podido leer. Hasta leer el artículo original, no afirmamos novedad en 3D.
- La fuente de 2026 se conoce solo por prensa. Su metodología, longitud de onda y medidas no están verificadas.

## 8 · Verificación en texto completo (2026-10-10, informe V5)

Fuente del informe: `experimentos/verificacion_claude/VERIFICACION-V5-literatura.md`. «Texto completo» indica que se leyó el artículo completo.

| Referencia | Qué confirma el texto | Consecuencia |
|---|---|---|
| HUST/SJTU, «Programmable Three-dimensional Photonic Neural Network Chip», *Nature Communications*, DOI 10.1038/s41467-026-72316-9 (2026-04-21); texto en PMC13284361 | Chip fabricado por escritura directa con láser fs en **vidrio borosilicato**; red 3D de **8 capas**; microcalentadores para programar; entrenamiento con láser de 800 nm; **93 % en entrenamiento y 91,7 % en prueba** (48 imágenes); **no declara longitud de onda de operación**. | **La parte 3D multicapa escrita con fs en vidrio tiene antecedente publicado.** No se puede afirmar novedad en red 3D. |
| Lee et al., *Scientific Reports* 11, 23770 (2021), DOI 10.1038/s41598-021-03116-y; texto en PMC8660921 | Guías con fs y microgrietas integradas: **1 dB/cm con radio de 10 mm a 1550 nm** (ambas polarizaciones); con 6 mm, 3 dB/cm (polarización x); a 1310 nm, 1 dB/cm con 8,5 mm. | Referencia de curvatura **verificada** para T8. |
| Artículo SK1310: «Femtosecond laser writing of telecom-band depressed-cladding waveguides and mode modulation in SK1310 glass», *Optical Materials*, 2025 (PII S0925346725000102) | **Solo el título, verificado** (Crossref y búsqueda). El texto completo devuelve 403 y no hay licencia abierta. | **Las guías de camisa deprimida en banda de telecomunicaciones en SK1310 ya tienen publicación previa.** La contribución «trinchera a 1550 nm» no puede afirmarse como nueva sin leer ese artículo. La longitud de onda concreta no está verificada. |

**Conclusión de novedad revisada.**
- Riesgo alto en (a), red 3D multicapa escrita con fs en vidrio (HUST/SJTU), y en (c), guías de camisa deprimida en telecom en SK1310.
- Lo que el texto leído no cubre: un cutback propio a 1550 nm en trinchera, con pérdidas de acoplo y de propagación separadas, y su contraste con el modelo vectorial. Esa es la candidata a contribución, y sigue sin medir.
- Acción inmediata: leer el artículo de SK1310 (acceso institucional de Fran o de los autores) antes de cualquier afirmación de novedad.
