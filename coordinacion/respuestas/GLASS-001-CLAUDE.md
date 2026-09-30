# GLASS-001 — Viabilidad del cubo óptico de sílice (informe de Claude)

Fecha: 2026-09-30 · Autor: Claude (Sonnet 5.5) · Estado: **v1, primera pasada de investigación**
Decisiones: **análisis local de Claude, sin aval de JEV** (canal bloqueado; no se reintentó).
Recursos usados: solo web + CPU. Sin GPU, sin Blender, sin instalaciones, sin escritura fuera de este archivo y su JSON.

> Nota de proceso: `D:\PROJECTS\Silice-Neuro3D-Cube` no existía. He creado únicamente `coordinacion/respuestas/` para estos dos entregables. Codex debe crear el resto de la estructura; si prefiere mover o rehacer esta carpeta, no hay conflicto.

## 0. Nivel de evidencia de este informe

- **[LEÍDO]** = abrí el texto y extraje el dato.
- **[SNIPPET]** = solo resumen de buscador o abstract; hay que verificar en el artículo.
- **[ESTIMACIÓN]** = cálculo mío con fórmula explícita; no es medición.
- **[CONOCIMIENTO PREVIO]** = de memoria, sin fuente abierta hoy; **no usar como dato** hasta verificar.

No he abierto el artículo de Nature de Project Silica ni la página de Microsoft Research (solo prensa secundaria). Eso es una laguna que debe cerrar la segunda pasada.

## 1. Veredicto corto

**La idea tal como está formulada ("escribir el recubrimiento, núcleo sin tocar, acopladores y elementos de fase dentro del cubo, entrenar una red y convertirla a geometría") no está demostrada, pero la parte central sí tiene precedente**:

| Componente | Estado | Evidencia |
|---|---|---|
| Guías de onda 3D en sílice fundida por fs-láser | Demostrado, baja pérdida | 0,07 dB/cm, 0,2 dB/faceta [SNIPPET, arXiv 2408.06688] |
| Acopladores direccionales, MZI, circuitos 3D multipuerto | Demostrado en varios vidrios | [SNIPPET] revisiones y arXiv 2604.12017 |
| Red neuronal óptica 3D escrita por fs-láser | Demostrada, **en borosilicato, con calefactores térmicos y sin no linealidad** | Nat. Commun. s41467-026-72316-9 [LEÍDO vía PMC13284361] |
| Cubo con acceso desde 6 caras, red "fijada" solo por geometría | **No encontrado** en esta pasada | — |
| Project Silica como procesamiento óptico | **No**: es almacenamiento | [SNIPPET] |

La parte que no se sostiene sin cambios: **fases y divisiones fijadas solo por geometría con la precisión que exige una malla interferométrica** (sección 5), y **"espejos internos" ideales** (sección 4).

## 2. Qué demuestra y qué NO demuestra Project Silica

Demuestra (prensa sobre el artículo de Nature, 18 feb 2026; **verificar en el original**) [SNIPPET/secundaria]:
- Escritura de datos por fs-láser: vóxeles birrefringentes en sílice fundida (varios pulsos) y vóxeles de fase en borosilicato (un pulso, o régimen pseudo-un-pulso con dos).
- Placas 75×75×2 mm (sílice, 5,15 TB) y 120×120×2 mm (borosilicato, 2,02 TB). Escritura ~66 Mbit/s con 4 haces. Lectura con microscopía de campo ancho + CNN que corrige crosstalk entre vóxeles.

No demuestra:
- Ningún procesamiento óptico, guiado de luz ni interferometría dentro del vidrio.
- Nada sobre cubos gruesos: el medio es una placa de 2 mm.
- Nada sobre pérdidas de propagación en guías: los vóxeles son elementos dispersivos/de fase para lectura con microscopio, no guías.

Consecuencia: Silica sirve como **prueba de que la escritura volumétrica, multicapa y de alta densidad es industrializable**, no de que una red óptica lo sea. No debe citarse como evidencia de cómputo.

## 3. Guías de onda en sílice: recubrimiento deprimido vs. alternativas

- **Sílice fundida, multiscan cuadrado**: 0,07 dB/cm de propagación, 0,2 dB/faceta, solape con fibra monomodo >98,8 %, interferómetro de 25 canales con pérdida total <1 dB [SNIPPET, PRApplied 22, 064079 / arXiv 2408.06688]. Faltan: longitud de onda, Δn, tamaño de modo, profundidad, radio de curvatura.
- **Contraste**: se cita Δn hasta 1,0×10⁻² a 522 nm y 9×10⁻³ en Heraeus F300 [SNIPPET]. **Ojo**: no sé si es contraste positivo (núcleo escrito) o el de un recubrimiento; **no extrapolar a "recubrimiento deprimido en sílice"** sin leer el artículo.
- **Recubrimiento deprimido ("depressed cladding")**: la referencia que aparece es en cristal Tm³⁺:YAG [SNIPPET, PMC7019769]; **no** es sílice. El régimen de núcleo intacto rodeado de trazos de índice reducido es conocido, pero **no tengo hoy una fuente primaria de pérdidas/Δn para sílice fundida con este esquema**. Marcado como hueco.
- Ventaja de núcleo intacto: hereda la homogeneidad del sílice (baja dispersión, sin tensión inducida en el núcleo). Coste: modo débilmente guiado, curvas amplias, sensible a desalineación de los trazos.

**Estimación de apertura** [ESTIMACIÓN]: para Δn_clad = 1×10⁻³ sobre n≈1,444, NA ≈ √(2·n·Δn) ≈ 0,054. Modo débil ⇒ radios de curvatura esperables de decenas de mm. Para Δn = 5×10⁻³, NA ≈ 0,12. Por eso el tamaño del cubo limita cuántas curvas caben; hay que medir, no suponer.

## 4. Alternativas a "espejos internos" ideales

No existe un espejo ideal dentro de un bloque homogéneo: no hay interfaz de índice controlable sin escribirla.

| Opción | Cómo funciona | Coste/restricción | Estado |
|---|---|---|---|
| Curva de guía | Doblar la propagación con radio suficiente | Radio mínimo grande si Δn pequeño; pérdida por curvatura | Demostrado en vidrios; ver "low bend loss" [SNIPPET, Sci. Rep. s41598-021-03116-y] |
| Reflexión interna total en cara pulida | Usar caras del cubo | Solo en superficies, no en interior | Física estándar |
| Rejilla/nanoestructura escrita como reflector | Rejilla de Bragg o planos de nanograting | Pérdidas por dispersión, banda estrecha, sensibilidad a polarización | [CONOCIMIENTO PREVIO]: verificar |
| Vacíos/cavidades | Interfaz sílice–aire | Dispersión, daño, difícil de repetir | Sin fuente |

**Recomendación**: diseñar sin espejos internos. Usar guías con curvas suaves y, si hace falta cambiar de dirección, reflexión en las caras del cubo.

## 5. Acopladores, interferómetros, retardos de fase y filtros

- Acopladores direccionales, MZI y redes multipuerto 3D: demostrados en vidrio [SNIPPET]. Régimen de un solo barrido con esfuerzo asistido a 30 mm/s [SNIPPET].
- Control del cociente de división: arXiv 2604.12017 ("scan-engineered index control"). El PDF no se pudo leer; **sin cifras de tolerancia**.
- Filtros: interleaver plano con MZI en cascada en sílice fundida (0,5 dB: 10 nm, extinción 15 dB) [SNIPPET, 2013-14].
- Birrefringencia de guías multiscan ajustable [SNIPPET, arXiv 2603.25142].

**Punto crítico — fases pasivas** [ESTIMACIÓN]: el error de fase es φ = 2π·δn·L/λ.
Con δn = 1×10⁻⁵, L = 10 mm y λ = 1550 nm: φ ≈ 0,41 rad (≈ 23°).
Una malla interferométrica que necesite fases con error <0,1 rad requiere δn ≤ 0,1·λ/(2π·L) ≈ 2,5×10⁻⁶ [ESTIMACIÓN] en 10 mm a 1550 nm. Eso es exigente para escritura fija.
Por eso el trabajo publicado de red 3D usa **calefactores termo-ópticos** (74 microcalentadores, potencia de media onda 146–161 mW, entrenamiento in situ con SPSA) [LEÍDO]. Una versión puramente geométrica necesitaría o bien **recalibración por post-escritura** (medir cada camino y recortar con más pulsos), o aceptar una red robusta a errores de fase.

## 6. Límites de escritura volumétrica

Datos **no verificados hoy** (marcar como pendientes de fuente primaria):
- Profundidad frente a apertura numérica: los objetivos de alta NA tienen distancias de trabajo cortas; con inmersión en aceite, décimas de mm. Para atravesar mm–cm hay que usar NA menor o corrección de aberración esférica con SLM [CONOCIMIENTO PREVIO].
- Al escribir a más profundidad el voxel se alarga (aberración), y el contraste y la reproducibilidad cambian con la profundidad.
- Separación mínima entre estructuras: hay acoplamiento evanescente si la separación es de µm; la red publicada usó paso de 15 µm en borosilicato para acoplar deliberadamente [LEÍDO].
- Registro entre caras: para escribir "desde las seis caras" hay que girar el cubo y volver a registrar. Cada reposicionamiento añade error de posición que se suma como error de fase y de alineación de modo. **No he encontrado una demostración de escritura en seis caras** con registro sub-micrométrico.
- Daño: umbral y acumulación térmica dependen de repetición y energía; no extrapolar de otros vidrios.

## 7. De la red entrenada a parámetros fabricables

Pipeline propuesto (todo verificable por separado):
1. Red de referencia (matriz compleja) entrenada en software con restricciones físicas (unitariedad con pérdidas, fase cuantizada, tolerancias).
2. Compilación a una **malla de MZI / acopladores + fases** (descomposición tipo Reck/Clements para la parte unitaria) — este es un **backend a matriz**; debe etiquetarse como tal.
3. Traducción a geometría: cada acoplador ⇒ (separación, longitud de interacción) usando una tabla de calibración medida; cada fase ⇒ (longitud de camino, o Δn por barrido).
4. Simulación de propagación (BPM o modos acoplados) con tolerancias para confirmar que la geometría reproduce la matriz de referencia.
5. Fabricación de piezas de calibración antes del dispositivo.

Cuello de botella: el paso 3 necesita **curvas medidas de acoplamiento y Δn frente a parámetros de escritura para el sílice y láser concretos**. Sin ellas, cualquier geometría es una promesa.

## 8. Qué necesita detección, electrónica o no linealidad

- La malla pasiva es **lineal** (en campo). Sola no ofrece clasificación general.
- La red publicada de 8 capas **no tiene no linealidad en el chip**; la detección de intensidad en la salida introduce cuadrado del módulo; los autores señalan que se pueden integrar elementos no lineales en las facetas de salida [LEÍDO].
- Resultados: MNIST 93 % (entrenamiento) / 91,7 % (prueba) con 200 imágenes de entrenamiento; similitud coseno >94 % en generación de patrones [LEÍDO]. La cifra de 6 554 TOPS es **teórica**, limitada por detector, no medida. Precaución con lo de "velocidad".
- Necesitan electrónica: detección, cualquier no linealidad de activación (a menos que sea óptica), realimentación para calibración de fase, lectura de resultados.

## 9. Si la idea no es fabricable tal cual: alternativa más cercana

**Lo que no se sostiene**: fijar por geometría fases interferométricas con error <0,1 rad en trayectos de cm, y depender de espejos internos.
**Alternativa más cercana** (sin cambiar de proyecto): mismo cubo de sílice, guías escritas, pero:
1. Red **poco profunda** (2–3 capas de mezcla), diseñada con **robustez a errores de fase** (entrenar con ruido de fabricación).
2. **Referencias de fase medibles** en el cubo (caminos de referencia) y **recorte post-escritura**.
3. Sin espejos internos; giros mediante curvas suaves o reflexión en caras.
4. Detección y no linealidad **fuera** del cubo, declaradas como tales.

## 10. Propuesta mínima (GLASS-MIN-1)

**Objetivo falsable**: comprobar que la geometría escrita reproduce una matriz de transferencia 4×4 conocida, no trivial, a partir de acopladores y caminos.

- **Entradas**: 4 modos (una fuente láser coherente dividida, o 4 fibras).
- **Salidas**: 4 modos; se mide intensidad |y|² con cámara/fotodiodos (la fase no se mide directamente).
- **Función objetivo**: y = U·x con U = DFT de 4 puntos (o Hadamard 4×4), realizada como 2 etapas de acopladores 50/50 con retardos de fase fijos (0, π/2 según caminos).
- **Material y parámetros [a fijar por Codex y medidas]**: sílice fundida de alta pureza; λ a elegir (p. ej. 1550 nm o 800 nm; **decisión pendiente** según láser de caracterización); guías monomodo; tolerancia de fase objetivo <0,2 rad.
- **Referencias de fase**: un camino de referencia sin acoplador y un MZI de calibración para medir δn·L de cada brazo.
- **Pérdidas**: presupuesto = 4 caras acopladoras × 0,2 dB [SNIPPET] + propagación 0,07 dB/cm [SNIPPET] × L. Debe medirse en la pieza real; los valores citados no son garantía.
- **Qué calcula el simulador**: propagación (BPM/modos acoplados) con geometría, con y sin errores; la matriz U teórica.
- **Qué existiría físicamente**: la pieza escrita, fuente, cámara. La red no "razona": mide una matriz.
- **Oráculo independiente**: cálculo numérico de U con álgebra lineal pura (sin código del simulador de propagación) comparado con |Ux|² medido/simulado.
- **Controles negativos**: (i) sustituir un acoplador por sección sin acoplamiento ⇒ salida distinta a la prevista; (ii) perturbar una fase en π ⇒ salida distinta; (iii) guía sin cladding ⇒ pérdidas altas; (iv) polarización rotada 90° ⇒ resultados dependientes (para detectar birrefringencia).
- **Criterios de aceptación**: error relativo por salida <10 % sobre 8 estados de entrada (coherencia mínima), conservación de energía cerrada con las pérdidas medidas (±5 %), y **el simulador de propagación coincide con el oráculo matricial** dentro de la tolerancia declarada.
- **Rechazo**: si tras recorte la dispersión de fase entre piezas supera 0,5 rad, o si las pérdidas por acoplador superan el presupuesto en más de 3 dB, el diseño se rechaza.

## 11. Obstáculos principales (orden de gravedad)

1. Precisión de fase de la escritura pasiva (§5): puede exigir recorte o calefactores.
2. Falta de datos primarios de **recubrimiento deprimido en sílice**: Δn, pérdida, radio de curva (§3).
3. **Escritura desde seis caras** sin demostración encontrada y con registro sub-µm (§6).
4. Aberración a profundidad y NA (§6).
5. No linealidad y detección obligatoriamente externas (§8).
6. Confusión de niveles: Project Silica ≠ cómputo (§2).

## 12. Petición concreta de revisión para Codex

1. **Confirmar** si acepta acotar GLASS-MIN-1 a una matriz 4×4 con detección de intensidad, y elegir λ.
2. **Decidir** quién escribe el oráculo de álgebra lineal (propongo Claude) y quién el simulador de propagación (Codex), sin compartir código entre ambos.
3. **Autorizar** una segunda pasada de investigación: leer el artículo de Nature de Silica y el PRApplied 22, 064079 completos, y buscar fuente primaria de recubrimiento deprimido en sílice.
4. **Responder** en `coordinacion/TABLON.md` cuando exista, con acuse y dudas sobre el JSON adjunto.
