# Respuesta a la revisión independiente — 13/10/2026

La revisión F6 de un único agente independiente queda retenida sin modificaciones junto a su código y registro316/190. No fue la reproducción completa de F8 ni se invocaron modelos Sonnet/Opus: se usó el revisor Codex disponible. No reentrenó ni abrió test_X o la bóveda.

| Hallazgo | Respuesta / estado |
|---|---|
| B1: separación/coherencia | Aceptado. DRCv2 FAIL, auditado mecánicamente como FAIL; ninguna bandera eliminada ni umbral relajado. Las316infracciones de polilínea y190alertas conservadoras se distinguen. Requiere otro layout antes de Blender final. |
| B2: descartes/cupones | Aceptado. N2/N3 no llegan a una cara exterior y no hay región de dispersión modelada; K1/K2 necesitan puertos ópticos. Especificación/plano/estado dicen que no está listo. |
| B3: modelo incompleto | Aceptado. F6_passed=false; 3,7mW es requisito condicional a NEP/eficiencias, no presupuesto certificado. κ20% da84,95%, por debajo del objetivo85%; no se declara que pase. No hay ventaja física de energía/latencia. |
| B4: liberación | Se añadieron release_guard.py, final_eval.py y reveal_v2.py aparte del custodio congelado. El guard verifica hashes y enlaces de F0/F3/F4/F5/F6/geometry; rechaza un simple ready=true, archivos cambiados, otra geometría, una sola polarización y presupuesto incompleto. El marcador O_EXCL+fsync se consume antes de exportar etiquetas. Tests únicamente sintéticos; la bóveda real no se tocó. La custodia sigue siendo procedural, no una garantía contra el titular del mismo equipo. |

18tests pasan, incluidos8 del guard/marcador con datos sintéticos. No se ejecutó liberación real; no hay recibo ni marcador de intento en la bóveda. El estado por fases, el candidato de revisión y los fallos se conservan. El envío técnico final y propuesta contractual siguen dependiendo de las puertas F0–F8 y aprobación expresa del titular.
