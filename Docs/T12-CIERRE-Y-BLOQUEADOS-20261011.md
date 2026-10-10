# T12 · Cierre de la red funcional y estado de las tareas bloqueadas

- **Fecha de redacción:** 2026-10-10, 10:33 UTC.
- **Repositorio:** `D:/PROJECTS/.cognition/audit/silice-origin-main`, rama `auditoria-20261009`.
- **Naturaleza:** modelo numérico y documentación. No es un dispositivo. Ninguna cifra de este documento es una medida.

**Etiquetas usadas:**

- **[V]** verificado al leer la fuente citada.
- **[C]** cifra calculada por el código del repositorio y reportada en la fuente. No se reejecutó el código en este documento.
- **[M]** requiere medida de laboratorio. No hay dato.
- **[NV]** no verificado.

---

## 1. Resultado de T12

**T12 no se cierra como éxito.** Se cierra como **resultado negativo preregistrado**. En la taxonomía de [PLAN-FINAL-20261011](PLAN-FINAL-20261011.md) su estado es **fallido**: criterio no cumplido, publicado tal cual. [V]

El criterio de funcionalidad, H-F1 (exactitud de prueba ≥ 0,70), no se cumple. H-F2 (no perder más de 2 puntos frente a la electrónica con la misma topología) tampoco. H-F3 sí se cumple, pero la ablación muestra que esa ganancia no viene de la activación. Es la suma de un aporte grande de la detección intermedia y una pérdida grande de la activación MZM en el punto de control. [C]

**Red funcional, F3-b** ([RESULTADOS-F3-B](../experimentos/f3_red_pequena/RESULTADOS-F3-B.md), [f3b_aggregate.json](../experimentos/f3_red_pequena/f3b_aggregate.json)):

| Hipótesis | Criterio fijado en el contrato | Resultado | Veredicto |
|---|---|---|---|
| H-F1 exactitud de A | ≥ 0,70 | 0,6425 | **No cumple** |
| H-F2 frente a B (misma topología) | A ≥ B − 0,02 | A = 0,6425; B = 0,8455; diferencia emparejada −0,2024, IC 95 % [−0,2200; −0,1840] | **No cumple** |
| H-F3 frente a una capa (F3 M1 = 0,5905) | diferencia > 0, IC 95 % excluye 0 | +0,0524, IC 95 % [+0,0190; +0,0840] | **Cumple** |

**Ablación** ([RESULTADOS-ABLACION](../experimentos/f3_red_pequena/RESULTADOS-ABLACION.md)):

| Hipótesis | Criterio | Δ puntual | IC 95 % | Veredicto |
|---|---|---|---|---|
| H-A1 aporte de la activación MZM (M_full − M_nonlin_off) | IC inferior > 0 | −0,2195 | [−0,2385; −0,1980] | **No cumple**, con signo contrario al previsto |
| H-A2 aporte de la detección intermedia (M_nonlin_off − M_det_off) | IC inferior > 0 | +0,2715 | [+0,2440; +0,2990] | **Cumple** |
| H-A3 M_det_off frente a M1 | IC contiene 0 | 0,0000 | [0,0000; 0,0000] | **Cumple** (predicción analítica V2) |

**Sensibilidad a V_π y θ_b** ([RESULTADOS-F3-SENSIBILIDAD](../experimentos/f3_red_pequena/RESULTADOS-F3-SENSIBILIDAD.md)):

- S1 (reproducción en V_π = 1, θ_b = 0): cumple, diferencia 0,0.
- S2 (rango de exactitud de prueba en la rejilla): **0,1485**, de 0,535 a 0,6835. Es sensible (umbral descriptivo 0,05).
- Ningún punto de la rejilla alcanza 0,70. El máximo es 0,6835, en V_π = 2, θ_b = 0.

**Controles y verificaciones:** E0, E1 y E2 pasan. Las verificaciones V1, V2, V2b, V3, V4 y V5 pasan. El criterio de convergencia C-CONV **no pasa** para M_real: 7 de sus 8 reinicios agotan las 300 iteraciones. [C]

**Lo que no queda cerrado con este resultado:**

- La red funcional como éxito.
- La neurona completa como sistema físico.
- El control en lazo cerrado. Es la tarea T15, bloqueada. [V]
- Cualquier cifra de energía o rendimiento. El balance de F3 es paramétrico y no incluye energía medida. [V]

---

## 2. Qué pedía T12 y qué cubre el modelo

En el plan de 22 tareas, T12 es «Neurona y red funcional completas (detección, activación, entrenamiento, control)». Ejecuta Claude y audita Codex. [V: [PLAN-22-TAREAS-20261010](../coordinacion/tareas/PLAN-22-TAREAS-20261010.md)]

El contrato [CONTRATO-F3-RED-FUNCIONAL](../experimentos/f3_red_pequena/CONTRATO-F3-RED-FUNCIONAL.md) fija los umbrales antes de entrenar. [V]

| Componente de T12 | Qué hay en el modelo | Veredicto |
|---|---|---|
| Detección | Intensidad |·|² con reemisión de amplitud. Aporta +0,2715 (H-A2). | Cumple como aporte [C] |
| Activación | MZM con V_π = 1 y θ_b = 0 fijos. Resta 0,2195 frente a no activar (H-A1). | No aporta en el punto de control [C] |
| Entrenamiento | L-BFGS-B, 8 reinicios, selección por pérdida de entrenamiento. La referencia M_real no converge. | Procedimiento correcto. Referencia no convergida [C] |
| Control | V_π y θ_b solo en análisis de sensibilidad, sin reentrenar. | Sensible. No hay control en lazo cerrado [C] [M] |
| Red funcional | H-F1 y H-F2. | **No cumple** [C] |

---

## 3. Ablación: qué aporta cada parte

Fuente: [RESULTADOS-ABLACION](../experimentos/f3_red_pequena/RESULTADOS-ABLACION.md). Todos los modelos tienen 32 parámetros, salvo M1 con 16. Exactitudes sobre las 2000 muestras de prueba. [C]

| Modelo | Qué contiene | Exactitud prueba | Exactitud entrenamiento | Reinicio seleccionado | Convergencia del seleccionado |
|---|---|---|---|---|---|
| M_full (A de F3-b) | U₁, MZM con V_π = 1 y θ_b = 0, U₂ | 0,6425 | 0,6530 | 5 | sí (131 it.) |
| M_nonlin_off | Detección |·|² y reemisión √I₁ con fase cero. Sin MZM. | 0,8620 | 0,8490 | 2 | sí (55 it.) |
| M_det_off | Dos mallas en cascada en amplitud compleja. Sin detección ni MZM. | 0,5905 | 0,5795 | 7 | sí (21 it.) |
| M_real (B de F3-b) | Pesos reales, misma activación MZM. Referencia electrónica. | 0,8455 | 0,8470 | 7 | **no** (300 it.) |
| M1 (F3) | Malla unitaria de una capa. | 0,5905 | 0,5795 | 8 | — |

**Lectura** (todo [C], salvo que se indique otra cosa):

1. **La activación MZM, con los parámetros de control, resta capacidad.** M_full pierde 21,95 puntos frente a M_nonlin_off. La pérdida también aparece en entrenamiento: exactitud 65,3 % frente a 84,9 %, y pérdida 0,962 frente a 0,690. No es sobreajuste, porque la red con activación no ajusta ni los datos de entrenamiento.
2. **La ganancia viene de la detección intermedia.** Con la misma cascada de dos mallas, la detección |·|² aporta +27,15 puntos (M_nonlin_off frente a M_det_off).
3. **La segunda malla sin detección no añade clase de funciones.** U₂U₁ pertenece a U(4), así que M_det_off equivale a una malla unitaria. V2 y V2b lo comprueban numéricamente. Sus predicciones de prueba coinciden con las de M1 (0 discrepancias). Los 32 parámetros de M_det_off son redundantes.
4. **Descomposición de F3-b.** La ganancia A − M1 es (A − M_nonlin_off) + (M_nonlin_off − M1) = −0,2195 + 0,2715 = +0,052. Es una identidad sobre diferencias puntuales.
5. **Corrección necesaria a F3-b.** La frase «La segunda capa y la activación aportan capacidad», de [RESULTADOS-F3-B](../experimentos/f3_red_pequena/RESULTADOS-F3-B.md) (sección Lectura, primer punto), no queda respaldada por la ablación. La ablación no modifica archivos existentes, así que la corrección queda para el coordinador. [V]
6. **Referencia no convergida.** M_real agota 300 iteraciones en 7 de 8 reinicios. Su 84,55 % no es un óptimo verificado. Por eso la brecha de H-F2 (−20 puntos) no puede atribuirse a la restricción unitaria. Tampoco es concluyente que M_nonlin_off (86,2 %) supere a M_real (84,55 %).
7. **Hipótesis, no probada.** T(I) = (1 + cos(πI))/2 tiene periodo 2 en I. Con V_π = 1, el 31,6 % de las intensidades de entrenamiento es ≥ 1. En el intervalo [1, 2] la transmisión vuelve a subir, así que intensidades distintas pueden dar la misma transmisión. La explicación es plausible, pero no está contrastada. [NV]
8. **Realizabilidad.** M_nonlin_off descarta la fase en la detección y reemite la amplitud con fase cero. Eso exige detección y reemisión coherente con fase conocida, es decir, electrónica. Es una red optoelectrónica, como A, no una red fotónica pasiva.

---

## 4. Sensibilidad a V_π y θ_b

Fuente: [RESULTADOS-F3-SENSIBILIDAD](../experimentos/f3_red_pequena/RESULTADOS-F3-SENSIBILIDAD.md). Se evalúa el mismo vector entrenado en V_π = 1 y θ_b = 0, sin reentrenar. [C]

| V_π | θ_b (rad) | Exactitud entrenamiento | Exactitud prueba |
|---|---|---|---|
| 0,5 | −π/4 | 0,6175 | 0,6185 |
| 0,5 | 0 | 0,5845 | 0,5930 |
| 0,5 | +π/4 | 0,5250 | 0,5350 |
| 1,0 | −π/4 | 0,6640 | 0,6595 |
| **1,0** | **0 (entrenado)** | 0,6530 | **0,6425** |
| 1,0 | +π/4 | 0,6045 | 0,5950 |
| 2,0 | −π/4 | 0,6505 | 0,6515 |
| 2,0 | 0 | 0,6735 | 0,6835 |
| 2,0 | +π/4 | 0,6565 | 0,6740 |

- El rango de exactitud de prueba es 0,1485, así que la red es **sensible** a los parámetros de control. [C]
- **Ningún punto llega a 0,70.** H-F1 sigue sin cumplirse para cualquier punto de control de la rejilla. [C]
- El máximo (V_π = 2, θ_b = 0; prueba 0,6835) **no se usa para elegir nada**. El contrato prohíbe seleccionar sobre prueba. Cambiar el punto de control exige reentrenar y seleccionar sobre entrenamiento o validación. [V]
- No es un control real de un modulador. No hay medida de V_π ni de θ_b. [M]

---

## 5. Referencia cruzada: tarea con datos reales (T16)

Fuente: [RESULTADOS-DIGITS](../experimentos/f3_red_pequena/RESULTADOS-DIGITS.md). Dígitos 0–3, 4 componentes PCA, partición 70/30. [V]

| Hipótesis | Resultado | Veredicto |
|---|---|---|
| H-D1 capacidad de M1 (≥ 0,70) | 0,7685 | Cumple |
| H-D2 referencia electrónica B (≥ 0,90) | 0,4074 | **No cumple** |
| H-D3 M1 frente a M2 (diferencia < −0,05, IC 95 % excluye 0) | −0,0700, IC 95 % [−0,1157; −0,0278] | Cumple. Ver §7 sobre la cifra puntual |

- El diagnóstico con entradas normalizadas (B = 0,8889, A = 0,5787) es **exploratorio y no preregistrado**. El propio documento lo declara y dice que no sustituye el veredicto. [V]
- Relación con T12: el fallo de la activación depende de la escala de entrada y de V_π fijo, según el documento. Es una hipótesis exploratoria. No hay contrato preregistrado para ella. [NV]

---

## 6. Qué cambiaría el resultado

**Con el contrato vigente, el resultado no cambia.** Los umbrales se fijaron antes de entrenar. El contrato de ablación establece que ningún criterio se modifica después de ver resultados. El plan final dice que los umbrales de rondas anteriores no cambian. [V]

No cambiarían el resultado ni reinterpretar la rejilla, que ya se ha visto y está sobre prueba, ni rebajar H-F1 a 0,68. Eso sería cerrar como éxito lo que no cumple el criterio. [V]

Lo que sí puede cambiar la conclusión es un **contrato nuevo, registrado antes de calcular**:

1. **Reentrenar M_full y M_nonlin_off en una rejilla de (V_π, θ_b)**, seleccionando por una partición de validación interna del entrenamiento, nunca por prueba. Es la propuesta (a) de [RESULTADOS-ABLACION](../experimentos/f3_red_pequena/RESULTADOS-ABLACION.md), sección «Siguiente paso propuesto (no ejecutado)». Respondería si la pérdida por activación es del punto de control o intrínseca a la MZM. [V]
2. **Reentrenar M_real hasta convergencia** (propuesta b). Sin esto, la brecha de H-F2 no puede atribuirse a la unitariedad. [V]
3. **Criterio de convergencia común** para todos los modelos (propuesta c). [V]
4. **Una activación distinta.** M_nonlin_off necesita electrónica para reemitir con fase conocida. Una red pasiva requeriría otra activación. Ningún documento revisado propone una. [NV]
5. **Medidas de V_π y θ_b en un dispositivo.** Sustituirían la rejilla por un valor medido. Requiere T13 y T14. [M]
6. **Otra tarea con entradas escaladas.** El diagnóstico de DIGITS es exploratorio y necesita su propio contrato. [NV]

---

## 7. Discrepancias numéricas y su origen

Verificado en el código: `paired_ci` en [run_f3b.py](../experimentos/f3_red_pequena/run_f3b.py) (línea 94) devuelve `d.mean()`, la **media de los remuestreos bootstrap**, no la diferencia puntual de las exactitudes. [V]

1. **F3-b.** H-F2 reporta −0,2024, y la diferencia puntual de las exactitudes que el mismo archivo lista es 0,6425 − 0,8455 = −0,2030. H-F3 reporta +0,0524, frente a 0,6425 − 0,5905 = +0,0520. Ningún veredicto cambia. [C]
2. **DIGITS.** H-D3 reporta −0,0700. La diferencia puntual 0,7685 − 0,8380 es −0,0694. [run_digits.py](../experimentos/f3_red_pequena/run_digits.py) usa `G.paired_ci`, es decir, `run_f3b.py`. Ningún veredicto cambia. [V]
3. **Ablación.** Sus Δ puntuales (−0,2195 y +0,2715) son diferencias exactas de exactitudes. Su descomposición es exacta sobre ellas: −0,2195 + 0,2715 = +0,0520. [C]

Propuesta: documentar en RESULTADOS-F3-B y RESULTADOS-DIGITS que la cifra «diferencia emparejada» es la media bootstrap. [NV: no se ha editado ningún archivo existente.]

---

## 8. Bloqueados: estado, dueño, criterio y decisión

**Ninguno de estos ítems se cierra en este documento.** No hay medida nueva.

Columnas: estado al cierre de la sesión del 2026-10-10 según [PLAN-22](../coordinacion/tareas/PLAN-22-TAREAS-20261010.md); dueño de ejecución, de auditoría y de decisión; criterio de aceptación de [PLAN-FINAL-20261011](PLAN-FINAL-20261011.md); criterio más específico de [PROTOCOLOS-BLOQUEADOS-22-TAREAS](PROTOCOLOS-BLOQUEADOS-22-TAREAS.md) cuando existe; y la decisión que lo desbloquea.

| Ítem | Estado | Dueño (ejecuta / audita / decide) | Criterio de aceptación (PLAN-FINAL) | Criterio más específico (PROTOCOLOS) | Decisión que lo desbloquea |
|---|---|---|---|---|---|
| **T1** · recuperar y auditar F1 (Colab) | Parcial en PLAN-22. PLAN-FINAL lo lista como bloqueado. F1 sin resultado final; Codex sin respuesta. | Ejecuta: Codex. Audita: Claude. Decide: Fran. | Recuperación de F1, o declaración formal de que no se recupera. | No tiene protocolo propio en PROTOCOLOS. | Fran accede a la sesión de Colab desde su navegador y decide si descarga algo ([ESTADO-ACTUAL](ESTADO-ACTUAL.md), decisión 4). Codex responde. |
| **T7** · GLASS-006b (fallos de dx, reducción gaussiana, base modal, contraste independiente) | Bloqueada, espera a Codex. Piloto entregado, fallos retenidos. | Ejecuta: Codex. Contrasta: Claude (ADI, solicitado). | Misma fila que T1. **No hay criterio científico propio.** [V] | No aplica. [NV] Falta un criterio preregistrado para base modal y contraste independiente. La carpeta `experimentos/glass006b_claude` no existe en el repositorio. [V] | Respuesta de Codex a la solicitud de coordinación. |
| **T9** · escritura profunda y registro entre caras | Bloqueada (protocolo). | Ejecuta: laboratorio. Sin socio asignado. Decide: Fran. | Al menos 3 muestras, IC 95 % de la pérdida, dos polarizaciones, registro entre caras < 1 µm (1σ). | Desplazamiento lateral < 1 µm (1σ) entre caras. Falsable: dispersión entre muestras > 3 µm. | Fran: socio o equipo para escribir 3 muestras en 2 profundidades. |
| **T13** · muestras de calibración y red 4×4 de 6 MZI | Bloqueada (fabricación). Depende de T9 y T14. No hay layout. | Ejecuta: laboratorio o taller con escritura fs. Decide: Fran. | Mismo criterio de cutback que T9 y T14. | Al menos 3 de 4 guías de calibración a 1550 nm dentro de la incertidumbre preregistrada. | Fran: fabricante o taller con escritura fs. |
| **T14** · medidas ópticas calibradas | Bloqueada (equipo y muestras). | Ejecuta: laboratorio. Decide: Fran. | IC 95 % de la pérdida, dos polarizaciones, al menos 3 muestras, registro < 1 µm (1σ). | Pérdida con IC 95 % (H1 de [CONTRIBUCION-CENTRAL-T20](CONTRIBUCION-CENTRAL-T20.md)) y δ con dispersión menor que 0,02. | Fran: equipo de medida y calibración del láser de 1550 nm. Protocolo en [F2-PROTOCOLO-MEDIDA](F2-PROTOCOLO-MEDIDA.md). |
| **T15** · integración óptica–electrónica–control | Bloqueada (hardware de control). | Ejecuta: laboratorio. Decide: Fran. | Error de transferencia < 10⁻² durante 1 h, con deriva medida. | Lazo de control de fase con la red de T13 y DAC de 8 bits. Medir la correlación antes de diseñar el control (H10b falla, cociente 1,68). | Fran: hardware de control y una planta de medida. |
| **T17** · rendimiento y consumo del sistema completo | Bloqueada (depende de T13 y T15). | Ejecuta: laboratorio. Decide: Fran. | Energía por operación del sistema completo con IC 95 %, frente a un baseline electrónico con los mismos datos. | Energía por operación menor que la del baseline T16, con IC 95 %. | Fran: equipo de medida eléctrica y tiempo de laboratorio. |
| **T18** · escalabilidad y reproducibilidad | Parcial: CI con hashes en Linux y Windows, y guardia de tamaño. Experimental bloqueado. | Ejecuta: laboratorio. Decide: Fran. | **Sin fila en PLAN-FINAL.** [V] | Diferencia de pérdida entre laboratorios menor que la incertidumbre combinada, reproduciendo dos muestras de T13. | Fran: un segundo laboratorio o socio. |
| **T21** · reproducción independiente y revisión externa | Externa. Requiere decisión de Fran. | Ejecuta: tercero externo. Decide: Fran. | Un tercero reproduce T2 y T11 con las mismas cifras, tolerancia 10⁻⁶ relativo en el modelo. | Código y datos con licencia y DOI de archivo. | Fran: licencia ([LICENCIA-PROPUESTA](LICENCIA-PROPUESTA.md)), confirmar que la visibilidad pública es intencionada, y depósito en Zenodo ([ARCHIVO-Y-TAMANO](ARCHIVO-Y-TAMANO.md)). |
| **T22** · impacto sostenido | Temporal. No cerrable hoy. | Ejecuta: tiempo (12 meses). Responsable de seguimiento: sin asignar. | Revisión con indicadores fijados hoy. | Citas, descargas del archivo, reproducciones independientes y decisiones de socios. **Sin umbral numérico** en la fuente. [V] | Fran: fecha de revisión y responsable del seguimiento. |
| **SK1310** · PDF del artículo (*Optical Materials*, 2025, S0925346725000102) | Parcial (F1d). El PDF no se obtuvo (403). Índice comprobado frente a Malitson. | Ejecuta: Fran sube el PDF con acceso institucional. Verifica: Claude (documental). | Texto completo leído. Permite fijar la novedad de la trinchera a 1550 nm. | No hay criterio numérico. Es una lectura, no una medida. | Fran sube el PDF ([ESTADO-ACTUAL](ESTADO-ACTUAL.md), decisión 5). Hasta entonces, cualquier afirmación sobre el artículo es [NV]. |
| **Fabricación** de muestras y red pequeña | Fuera de alcance actual según el punto 9 de la hoja de ruta en PLAN-22. Bloqueada en T13. | Ejecuta: fabricante externo con escritura fs. Decide: Fran. | **Sin fila en PLAN-FINAL.** [V] | Se aplica el de T13: al menos 3 de 4 guías dentro de la incertidumbre preregistrada. No hay protocolo de fabricación separado. [NV] | Fran: fabricante o taller. Antes hace falta un layout, que no existe. El compilador da la netlist, pero su fabricación no está comprobada. |

---

## 9. Observaciones para el coordinador

Estas observaciones están fuera del alcance de T12. Se anotan para decidir, no se aplican aquí.

1. **Corregir F3-b.** La frase «La segunda capa y la activación aportan capacidad» no está respaldada (§3, punto 5).
2. **Estado de T12 en PLAN-22.** Dice «parcial». Con H-F1 y H-F2 incumplidos, la taxonomía de PLAN-FINAL lo sitúa como **fallido**. Conviene actualizarlo.
3. **Cifras emparejadas.** Documentar la media bootstrap en F3-b y DIGITS (§7).
4. **Cierres «en modelo» a revisar.** PLAN-22 marca como «cerrada en modelo» T10 (H10b no cumple), T11 (C2 no cumple) y T16 (H-D2 no cumple). Según el principio de PLAN-FINAL, «hecho» requiere que el criterio preregistrado se cumpla. No he auditado los contratos de T10, T11 ni T16. Hay que decidir si su estado es cierre o parcial.
5. **T7 sin criterio propio.** PLAN-FINAL no define un criterio científico para GLASS-006b, y la carpeta `experimentos/glass006b_claude` no existe en el repositorio. [V]
6. **T1 con dos estados.** PLAN-FINAL lo lista como bloqueado. PLAN-22 lo marca como parcial. Conviene unificar.
7. **Filas ausentes en PLAN-FINAL.** T18 y fabricación no aparecen en su tabla. Sus criterios se han tomado de PROTOCOLOS.

---

## 10. Límites

- Modelo numérico con una tarea sintética congelada y una sola muestra de datos. El IC bootstrap solo recoge la variabilidad del muestreo de prueba. No recoge la variabilidad entre semillas de entrenamiento ni entre tareas. [V]
- V_π y θ_b se fijan en el punto de control (1, 0). No se ha buscado otro punto sobre prueba. [V]
- M_real no está convergida. Las comparaciones con ella son informativas, no concluyentes. [V]
- La activación usa electrónica de control y fotodetector. No es totalmente óptica. [V]
- No hay medidas, energía ni fabricación. No se afirma nada sobre un dispositivo. [V]
- No se afirma novedad científica. [V]
- Las cifras se toman de los archivos RESULTADOS, de los agregados JSON pequeños y del código de `run_f3b.py` y `run_digits.py`. No se reejecutó ningún experimento. No se ha leído el PDF de SK1310.
- Los criterios de T13, T14 y T9 se citan como aparecen en PROTOCOLOS. No se ha comprobado su coherencia con los contratos de origen, salvo lo indicado en §9.
