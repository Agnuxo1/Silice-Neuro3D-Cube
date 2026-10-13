# Auditoría del README y conservación de resultados — 13 de octubre de 2026

**Conclusión:** no se encontró borrado ni conversión de resultados originales de Codex de PASS a FAIL. Sí se encontraron formulaciones demasiado generales y poca visibilidad de una aceleración de simulación realmente medida. Se corrige la presentación sin modificar datos, scripts, criterios ni veredictos.

## Alcance y versiones

Comparación completa del árbol publicado en b344dcf663a3e7c7399ae4172206d06e2eb81042 con c4710f6afb4357cd9c2873bf129c9255c8252083 (README de Claude del 13 de octubre). El primero es antecesor del segundo: su historial sigue accesible. Revisiones de datos guardados en CPU, un hilo; ninguna propagación, entrenamiento, carga GPU ni medida física nueva. JEV remoto mantiene el bloqueo heredado; fallback local explícito.

| Grupo original | Archivos comparados | Idénticos por blob Git | Modificados o borrados |
|---|---:|---:|---:|
| resultados/codex | 2715 | 2715 | 0 |
| scripts | 200 | 200 | 0 |
| src/silice | 7 | 7 | 0 |
| assets | 18 | 18 | 0 |
| Docs | 167 | 166 | 1: CPU-REPRODUCTION.md |

De los 3309 archivos originales, 3304 permanecen idénticos. No hay archivos borrados. Los cinco modificados son .gitattributes, Docs/CPU-REPRODUCTION.md, README.md, coordinacion/CHECKPOINT.md y pyproject.toml. Se añadieron 1487 archivos. Esto demuestra conservación del contenido versionado, no certifica toda la ciencia añadida.

## Qué resultados positivos se verificaron

- **CUDA128:** tres tiempos CPU (2.4329184, 2.4656332, 2.4527839 s) y tres GPU residentes (0.0998778, 0.1098203, 0.1101299 s). Cociente de medianas: **22.33452194**. El informe original ya distinguía este núcleo de simulación de inferencia completa y decía que no se midió energía. No fue eliminado ni cambiado.
- **GPU-001/GPU-002:** el auditor original, invocado sólo como función de lectura, reproduce 29 comprobaciones de consistencia de los campos y conserva los cuatro fallos complex64.
- **R3:** los 168 campos siguen aprobados. Recalculados desde los píxeles existentes: máximo complejo OpenGL 5.1366105143e-7 y Vulkan 5.8510303351e-7, ambos por debajo del umbral original 5e-6.
- **C2/M2:** los informes originales de aprobado temporal siguen intactos. Esta revisión comprueba su conservación; no repite las propagaciones ni sus auditores exclusivos.

Estos resultados prueban componentes numéricos concretos. No constituyen una medida de velocidad o energía de un procesador óptico fabricado.

## ¿Son ciertos los negativos?

| Ensayo | Comprobación de esta revisión | Conclusión |
|---|---|---|
| R1 | SHA de 84 píxeles y referencia P2 originales: 21 PASS / 63 FAIL | Negativo reproducido. Una métrica L2 difiere 1.31e-14 del registro; se conserva la discrepancia, sin cambiar tolerancias ni adoptar R1. |
| R2 | SHA de 84 píxeles; 21 PASS / 63 FAIL; error máximo 1.6208087841e-4 | Negativo reproducido frente a 5e-6; no era R3. |
| P1 OpenGL / Vulkan | 30 marcas por backend; 21 PASS / 9 FAIL en cada uno | Negativos smooth reproducidos. No cancelan las rutas analíticas aprobadas. |
| R3 OpenGL / Vulkan | 84 PASS / 0 FAIL en cada backend | Positivo reproducido; permanece en el README. |
| F3 | 2000 etiquetas regeneradas con las semillas fijadas y predicciones guardadas | M1 1181/2000 = 59.05%; M2 1696/2000 = 84.8%; M3 1983/2000 = 99.15%. Intervalo pareado reproducido [-0.2815, -0.2354875]. H1 y H2 negativas para esa tarea y familia. No se reentrenó ni se demuestra imposibilidad general de una red óptica. |
| T24 | Fórmula de ruido y presupuesto recalculada independientemente | La aritmética coincide. El resultado depende del tamaño, precisión, electrónica, referencia y arquitectura; es un presupuesto paramétrico, no una medida. |

F3 guarda predicciones, pero su archivo original no guarda los pesos ajustados; esta comprobación valida exactitud e intervalo desde las predicciones, no reproduce el entrenamiento.

## Límites de T24 y frases que requieren corrección

El punto registrado es una capa 64×64, objetivo de 8 bits y 1 GS/s con entrada/salida electrónica. Los valores optimistas implican 71.625 fJ/MAC de DAC, ADC y modulador: 4.462× la referencia digital elegida de 16.051 fJ/MAC. Esa conclusión es válida para esas cantidades y su comparación; no es un límite universal de todos los componentes, tamaños o arquitecturas.

El total de 101.586 pJ/MAC del caso optimista depende fuertemente de elegir dos mallas SVD, 128 etapas y 0.35 dB por etapa. El propio informe T30 identifica elecciones posteriores al compromiso y muestra que la comparación con la referencia de 2014 cambia de signo con pérdidas inferiores a aproximadamente 0.131 dB por etapa. El valor de 0.35 dB procede de interferómetros en boro-aluminosilicato EAGLE XG, no de nuestro dispositivo de sílice: [artículo primario](https://arxiv.org/pdf/2001.08144), páginas 6 y 20.

Por ello:

- «Energy saving ... at small size: Refuted» se acota al caso y parámetros registrados.
- «Depth advantage from 3D: Refuted» se acota a profundidad lógica de mallas universales de elementos de dos modos. Cruces, rutas, densidad y transformaciones estructuradas son otros mecanismos.
- La aceleración CUDA medida de 22.33× se incorpora al comienzo del README con su alcance.
- El README actual también contenía predicciones positivas de energía en fan-out (4–30× frente a RTX 3090 y 1.2–9× frente a H100), expresamente aproximadas y pendientes de comparación homogénea. No habían desaparecido; no se elevan aquí a medidas reales.

## Qué cambió Claude y qué no puede inferirse

El commit 75fc749 cambió el encuadre de «red neuronal» a «transformación óptica lineal», manteniendo la red como objetivo. El commit c4710f6 tradujo el README y añadió FEMTO-1. No cambiaron los datos originales de Codex. La pérdida de la sesión F1 en Colab ya estaba registrada antes de esas ediciones; no se atribuye a ellas.

La comparación de archivos no aporta evidencia de intención de sabotaje ni permite diagnosticar un efecto del arnés o de los guardrails de Claude. Sí permite señalar errores concretos de alcance editorial y corregirlos.

## Coordinación

Esta nota aporta a Claude una revisión reproducible: conservar los positivos aprobados, asociar cada negativo a su caso y contrato, no transferir pérdidas de otro vidrio como medida de sílice y no presentar un fallo de una arquitectura como fallo global del proyecto. Se preservan sus ensayos y críticas, incluidas sus correcciones de T24/T25.

## Evidencia de la auditoría

[Integridad del árbol](../resultados/codex/readme_claims_audit_20261013/tree_integrity_audit.json), [campos CUDA](../resultados/codex/readme_claims_audit_20261013/historical_gpu_raw_reaudit.json), [396 campos gráficos](../resultados/codex/readme_claims_audit_20261013/retained_graphics_raw_reaudit.json), [aritmética T24](../resultados/codex/readme_claims_audit_20261013/t24_arithmetic_audit.json), [predicciones F3](../resultados/codex/readme_claims_audit_20261013/f3_prediction_arithmetic_audit.json).
