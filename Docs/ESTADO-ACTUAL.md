# Estado actual del repositorio · 2026-10-09

Documento de entrada. Resume qué está hecho, qué está parcial y qué depende de una decisión o de un laboratorio. El detalle científico sigue en [PROJECT-STATUS](PROJECT-STATUS.md) (reconciliado el 2026-10-06).

## Trabajo de la auditoría (2026-10-09)

Cada punto se cerró con un commit propio o con un contrato publicado antes de calcular. Los fallos y las hipótesis no cumplidas se conservan.

| Punto | Estado | Evidencia |
|---|---|---|
| D1 licencia | **Propuesta lista, sin publicar** (espera decisión del titular) | [LICENCIA-PROPUESTA](LICENCIA-PROPUESTA.md) |
| D2 visibilidad | Evidencia recogida: creado público el 2026-09-30. **Falta confirmación del titular** | Evento `PublicEvent` con la misma marca que `created_at` |
| D3 texto corrupto del README | Hecho | `e0af007` |
| D4 estructura del README | Hecho | `2b26c03`, `75fc749` |
| D5 CI Windows y Linux | Hecho. Verde en `windows-2022` y `ubuntu-24.04` | [cpu-tests.yml](../.github/workflows/cpu-tests.yml), `5854160`, `3c0c69d` |
| D6 autoría | Hecho: sin reescribir el historial | [CONTRIBUTORS](../CONTRIBUTORS.md), [CITATION.cff](../CITATION.cff), `b922b79` |
| D7 tamaño del repositorio | Auditoría y guardián en CI hechos. **Falta autorizar Zenodo para las evidencias pesadas** | [ARCHIVO-Y-TAMANO](ARCHIVO-Y-TAMANO.md), `5c4e450` |
| D8 F1 en Colab | **Bloqueado**: sin estado verificado. Procedimiento propuesto | [OPERACION-EJECUCIONES-LARGAS](OPERACION-EJECUCIONES-LARGAS.md), `cf853db` |
| F0 base y archivo | Hecho: bitácora archivada, CI y README | `c03f31d` |
| F1a reencuadre | Hecho: «transformación óptica lineal»; la red neuronal queda como objetivo | `75fc749` |
| F1b contraste vectorial | **Hecho**. H1 cumple, H2 no cumple, H3 cumple | [VECTORIAL-RESULTADOS](VECTORIAL-RESULTADOS.md), `544679f` |
| F1c G2 de GLASS-006a | **Diagnóstico y convergencia hechos**. Veredicto histórico intacto. Q4 de trazos sigue abierta | [RESULTADOS-G2-N](../experimentos/glass006a_claude/RESULTADOS-G2-N.md), `a70744f` |
| F1d PDF de SK1310 | **Parcial**: el artículo no se pudo obtener. Comprobación del índice hecha | [SK1310-FUENTES](SK1310-FUENTES.md), `ed74bfe` |
| F1e segunda máquina | Hecho: CI en Ubuntu, con la misma suite | `5854160` |
| F2 protocolo de medida | **Protocolo congelado; medida pendiente de laboratorio** | [F2-PROTOCOLO-MEDIDA](F2-PROTOCOLO-MEDIDA.md), `9a7eeab` |
| F3 red pequeña | **Hecho, resultado negativo**: H1 y H2 no cumplen. Balance energético paramétrico | [RESULTADOS-F3](../experimentos/f3_red_pequena/RESULTADOS-F3.md), `beafe0a` |
| Paralelo literatura | Hecho con etiquetas de verificación. **Novedad no establecida** | [LITERATURA-NOVEDAD](LITERATURA-NOVEDAD.md), `50cf595` |

## Resultados científicos de esta sesión

- **Contraste vectorial (F1b).** En una guía de salto ideal con el contraste del proyecto, el modelo escalar describe el índice modal a 2–3·10⁻⁶ relativo. Los efectos vectoriales escalan como Δn².
- **G2 a 10 µm (F1c).** Los fallos originales vienen de mallas gruesas (N ≤ 800). Con N ≥ 1400 Re γ varía ±0,8 %. El criterio de dos mallas consecutivas no basta para demostrar convergencia, porque Re γ no es monótona en N.
- **SK1310 (F1d).** La dispersión de la ficha coincide con la sílice de referencia más un desplazamiento constante de +6·10⁻⁴. El n₀ = 1,444 del proyecto es consistente con eso.
- **F3.** Una malla unitaria con lectura de intensidad no alcanza el umbral preregistrado (59 % frente a 60 %), y es peor que una línea base de igual número de parámetros (85 %).

## Decisiones pendientes del titular

1. **Licencia** (propuesta lista, sin publicar).
2. **Confirmar que la visibilidad pública es intencionada.**
3. **Autorizar Zenodo** para las evidencias pesadas (acción externa con DOI).
4. **Acceder a la sesión de Colab de F1** desde su navegador y decidir si descarga alguna parte.
5. **PDF del artículo de SK1310** (acceso institucional) para verificar el material.
6. **Decidir si se monta Drive** para persistir las partes en ejecuciones futuras.
7. **Socio experimental** para la fase de medida (F2). Sin él, el proyecto no pasa de simulación.

## Lo que no se ha hecho

- Ninguna medida de laboratorio. Ningún dispositivo fabricado.
- Ningún resultado de red funcional ni de ventaja energética.
- Ninguna reproducción externa ni revisión por pares.
- Ninguna escaneo DAST: no hay aplicación en ejecución y `HAWK_API_KEY` no está definida.
