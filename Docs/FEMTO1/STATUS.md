# FEMTO-1 — estado verificable, 13/10/2026

Se ha ejecutado la preparación prospectiva, entrenamiento, simulación de tolerancias, compilación de cuatro zonas, DRC, revisión independiente y exportación preliminar. **No hay chip fabricado ni paquete listo para fabricación.** Las fases siguientes no se sustituyen por simulaciones incompletas.

| Fase | Estado | Evidencia / trabajo restante |
|---|---|---|
| F0 | Contacto enviado; puerta pendiente | Gmail 1a134b2ae1501c9f, info@femtoprint.ch. Nota conceptual adjunta, formatos/DFM/cupons/coste/plazo y vía de colaboración solicitados. Última búsqueda sin respuesta. No hay confirmación de entrega/lectura. |
| F1 | Ejecutada | Protocolo 2df24924 publicado y consultado contra servidor con ref explícito; manifiesto 3c08b9b antes de entrenar. 11882 fit, 2968 calibración, 4949 validación y 4955 test. Uso previo exploratorio declarado. |
| F2 | Modelo/MC ejecutados; ruido alto falla | Nominal 87,31% validación; prototipo79,39%. MC200 a κ10%: ocho parámetros88,12%. TIA5% con calibración sin ruido50,12%. Variante robusta no convergió y no fue seleccionada; fallo conservado. |
| F3 | FAIL | 192 acopladores (48 por N1–N4); transferencia bajo modelo provisional error<=1,11e-16. Radios25mm; DRC18entradas con506parejas conservadoras. Revisor confirma316infracciones reales. Coherencia falla16haces. Descartes/cupones incompletos. |
| F4 | Preparada, no ejecutada | blender_twin.py, final_eval.py, release_guard.py y reveal_v2.py. Bloqueo de DRC/validación física; GPU con prioridad VillaAnzuelo. No Blender ejecutado, .blend, render, vídeo ni benchmark sellado. |
| F5 | Protocolo preparado, no ejecutada | F5-SOLVER-AND-BENCH-PLAN.md; faltan perfil/tolerancias y simulación física independiente del chip con curvas, modos, banda y dos polarizaciones. |
| F6 | Parcial | MC200 por siete niveles de ruido (pareado), más cinco niveles de κ de F2. Calibración ruidosa: TIA0,5%86,85%, TIA1%83,51%. Presupuesto3,7mW es condicional a NEP10pW/sqrtHz y eficiencias supuestas. Disparo/error completo/peor polarización y latencia/energía física pendientes. Crítica independiente realizada. |
| F7 | Paquete de revisión preliminar | JSON SI y um, CSV896446puntos, DXF de ejes, tabla de acopladores, plano e informe PDF. CSVreimport error<=6,94e-12um y W<=4,86e-14. Falta STEP/STL completo, Blender como fuente verificada, CADreimport independiente, formatos confirmados y firma del titular. |
| F8 | No congelada/liberada | Auditoría F1/F2 mecánica PASS; layout FAIL. Revisión crítica conservada, pero no reproducción/revisión final desde cero ni etiqueta femto1-fab-v1. Aprobación/envío final pendientes; no se pide aprobación de fabricación con estas puertas abiertas. |
| F9 | Plan preparado; requiere fabricar | Cupones/medidas raw/C1–C4 y prueba de banco descritos; ningún dato de dispositivo inventado. |

## Artefactos

- Repositorio de trabajo: `D:/PROJECTS/Silice-FEMTO1-20261013`, rama `codex/femto1-20261013`. No se modificó main ni los cambios de los otros checkouts.
- Modelo y MC: `resultados/codex/femto1_20261013/`; layout: `resultados/codex/femto1_layout_20261013_v2/`; ruido/potencia: `resultados/codex/femto1_noise_20261013/`.
- Geometría grande y paquete preliminar: `D:/PROJECTS/.cognition/femto1/geometry_FEMTO1_candidate_v2.json`, `review-package-v2/`. No subidos ni enviados a FEMTOPRINT.
- Revisor: `Docs/FEMTO1/INDEPENDENT-REVIEW.md` y `review-evidence/`. El JSON316/190 es reconstrucción declarada del registro del revisor; código retenido para reejecución. No una segunda nueva ejecución posterior.
- Contacto/copia/recibo: `D:/PROJECTS/.cognition/silice-femtoprint/F0-REGLAS-FEMTOPRINT.md`.
- Colaboración: `COLLABORATION-PROPOSAL-DRAFT.md`, interna y no enviada. El correo inicial expresa el objetivo de desarrollo conjunto después del estudio de viabilidad.

## Qué hacer al reanudar

1. Leer este estado y `D:/PROJECTS/.cognition/femto1/CHECKPOINT.md`; verificar hashes con `python scripts/femto1/run_pipeline.py femto1 verify`. No repetir entrenamiento ni MC ya completos por defecto.
2. Leer y registrar las respuestas escritas de FEMTOPRINT; reemplazar supuestos por reglas/perfil reales. Priorizar cupones accesibles K1–K3 si no entregan un modelo calibrado.
3. Nuevo layout con rutas 3D separadas, accesos a cupones y terminaciones T reales; resolver coherencia con el espectro y colección previstos. Congelar nueva versión antes de medir; conservar v2 FAIL y umbrales.
4. Ejecutar F5 independiente y F6 completo. Solo después F4 definitivo, con evidencia enlazada por hashes, predicciones congeladas y una liberación atómica de etiquetas. Usar reveal_v2.py, no el reveal directo de custodian.pyv1.
5. Validar STEP/DXF/STL/CSV en los formatos confirmados; revisión final, manifiesto/firma y aprobación expresa del titular. Enviar después el paquete junto a la propuesta de colaboración revisada. Ningún pedido, NDA o pago está autorizado incidentalmente.

Verificaciones actuales: 18 tests de invariantes/geometría/serialización/custodia procedural; hashes de datos y resultados; equivalencia algebraica; CSVreimport; PDFs inspeccionados visualmente. El sello en el mismo host no es un custodio independiente. Los recibos Git/servidor no constituyen un sello externo firmado de tiempo histórico.
