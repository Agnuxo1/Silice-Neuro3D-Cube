# Tarea 20 · contribución central con hipótesis falsable y test decisivo (2026-10-10)

Estado: **documento preregistrado, sin medidas**. Esta tarea se cierra cuando el test decisivo tenga datos. Hasta entonces queda abierta. Ninguna cifra de aquí es una medida del proyecto.

## 1. Qué es la contribución, si resulta cierta

El proyecto no es nuevo por las redes ópticas lineales ni por las guías escritas con láser fs, que ya existen (ver `Docs/LITERATURA-NOVEDAD.md`, sección 6). La contribución, si se sostiene, es esta combinación concreta:

1. Una guía de camisa deprimida en **trinchera** caracterizada a **1550 nm** con **cutback**, con el límite de fuga ideal calculado de antemano.
2. Una red programable **tridimensional** escrita desde varias caras, con su calibración medida.

Cada parte por separado tiene competidores (Kondratyev et al., arXiv:2308.13452, interferómetro programable de 8 puertos a 920–980 nm; Skryabin et al., arXiv:2408.06688, 0,07 dB/cm en guías multiscan). Un competidor 3D programable de 2026 (HUST/SJTU, Nature Communications) **no está verificado en texto completo**; hay que leerlo antes de afirmar nada.

## 2. Hipótesis principal (H1)

> **H1.** Una guía de trinchera (núcleo n = 1,444, trinchera δn = −0,005, t = 12 µm, a = 6 µm), escrita con láser fs en sílice, tiene a 1550 nm una pérdida total de propagación ≤ 0,3 dB/cm.

- **Umbral 0,3 dB/cm.** Es la cifra reportada para guías tubulares de camisa deprimida en sílice (Springer, DOI 10.1007/s00339-015-8990-x), **no verificada en texto completo**. Se usa como referencia de competitividad para redes, no como cota física.
- **Límite de fuga ideal.** El modelo vectorial da 0,044 dB/cm para esta geometría (`experimentos/vectorial_claude/RESULTADOS-VECTORIAL-GEOMETRIA.md`). La pérdida medida no puede ser sistemáticamente menor que esa fuga ideal.

### Test decisivo (T14 / F2)
- Medida por cutback a 1550 nm, según `Docs/F2-PROTOCOLO-MEDIDA.md`: al menos 4 longitudes, al menos 3 muestras, y las dos polarizaciones.
- Estadístico: pérdida media y su IC 95 % por regresión lineal de la potencia (dB) frente a la longitud.

### Qué la falsa
- **F1.** El límite inferior del IC 95 % es mayor que 0,3 dB/cm. Entonces H1 queda falsada para esta geometría y esta fabricación.
- **F2 (control del modelo).** La pérdida medida es menor que 0,044 dB/cm con IC 95 % que lo excluye. Eso no es un éxito: indica un error en el modelo o en la medida, y bloquea el uso de la fuga ideal como cota.

### Qué la confirma
- El límite superior del IC 95 % es ≤ 0,3 dB/cm y el límite inferior es ≥ 0,044 dB/cm.

## 3. Hipótesis secundarias

- **H2 (acoplo en red, modelo, ya calculado).** Con pasos ≥ 26 µm, las guías paralelas de esta familia no superan −30 dB de diafonía a 10 mm (`experimentos/acoplo_claude/RESULTADOS-ACOPLO.md`, H-T8-2). *Estado: predicción del modelo, cumple en el modelo; falta medida.* La H-T8-1 (20 µm) no se cumplió en el modelo: P₂ = 0,141.
- **H3 (calibración, modelo).** Con δ ~ N(0; 0,02) y DAC de 8 bits, el reajuste cumple a la vez ε₂ < 10⁻² y ε₂ < ε₁/3 en el 78 % de las realizaciones (28/36; `experimentos/compilador_claude/RESULTADOS-COMPILADOR.md`). *Estado: modelo; el valor real de δ no está medido (T14).*

## 4. Qué está establecido por cálculo y qué requiere medida

| Afirmación | Estado |
|---|---|
| Fuga ideal de trinchera, 0,044 dB/cm (t = 12 µm) | cálculo vectorial, validado contra fibra analítica (1e-16) |
| Contraste escalar–vectorial (H1 cumple, H2 no cumple) | cálculo, `experimentos/vectorial_claude/RESULTADOS-VECTORIAL*.md` |
| Diafonía de guías paralelas (H-T8-2) | modelo escalar, prefactor no verificado independientemente |
| Calibración a 8 bits, C3 en 78 % de realizaciones | modelo |
| Pérdida total de trinchera a 1550 nm | **no medida** |
| Tolerancia real de δ en la escritura | **no medida** |

## 5. Lo que este documento no afirma

- No afirma novedad. La novedad se establece con H1 medida frente al estado del arte en el mismo régimen (ver `Docs/LITERATURA-NOVEDAD.md`).
- No afirma que la red 3D funcione. Eso depende de T9, T13 y T14.
- No usa cifras de competidores que no estén verificadas en texto completo.

## 6. Decisión que necesita Fran

Un socio experimental con acceso a escritura fs y cutback a 1550 nm (ver `Docs/PROTOCOLOS-BLOQUEADOS-22-TAREAS.md`, bloque T14). Sin él, H1 queda como hipótesis preregistrada, sin test.

## Actualización de novedad (2026-10-10, tras la verificación en texto completo)

- H1 sigue siendo un test válido, pero la contribución ya no puede presentarse como «primera trinchera a 1550 nm»: el artículo de SK1310 en banda de telecomunicaciones (2025) ya la publica (`Docs/LITERATURA-NOVEDAD.md`, sección 8).
- La parte 3D multicapa escrita con fs está cubierta por HUST/SJTU (2026). El proyecto no debe presentarla como novedad.
- Queda pendiente la demostración propia: un cutback medido con pérdidas de acoplo y de propagación separadas, en el mismo lote de SK-1310, con contraste frente al modelo vectorial.
