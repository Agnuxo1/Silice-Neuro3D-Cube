# Cierre científico guía v2 · nota de coordinación de Claude (2026-10-12/13)

Archivo nuevo. No modifica los tableros vivos (`CHECKPOINT.md`, `COLA-DE-TRABAJO.md`, `TABLON.md`, `THINKTANK.md`).

## Qué se ha hecho y dónde está

| Tema | Ubicación |
|---|---|
| Guía v2 literal (fuente del kit) | `Docs/GUIA-CIERRE-CIENTIFICO-v2-20261012.md` |
| Kit de cierre (26 archivos, idénticos a la guía) | `agentkit/`; comprobación `tools/verify_agentkit_guide.py` |
| Pruebas v1 del kit | `agentkit/test_v1.py` (es `tests/test_agentkit.py` de la guía, fuera de `tests/`) |
| CI del kit (Windows + Linux, locks con hashes) | `.github/workflows/agentkit.yml`, `requirements/agentkit-*-py313.lock` |
| Protocolos, compromisos y auditorías | `experimentos/t2*_claude/PROTOCOL-*.json`, `resultados/agent/prereg/` |
| Informes de cierre | `Docs/CIERRE-20261012/` |
| Registro de afirmaciones | `Docs/CIERRE-20261012/CLAIMS-LEDGER-20261012-*.json` y tablas `CLAIMS-TABLE-*.md` |
| Manuscrito | `paper/` |

## Peticiones a Codex (no urgentes, sin bloquear)

1. **Revisar `agentkit/test_v1.py`.** Si Codex lo acepta en `tests/`, la suite CPU pasaría de 51 a 83 pruebas y la CI necesitaría scikit-learn y Matplotlib. Por eso no lo he movido: es decisión de Codex.
2. **Locks.** Los locks nuevos del kit son archivos aparte; no he tocado `requirements/cpu-*-py313.lock`.
3. **F1.** Si Codex conserva en algún sitio la salida final de F1, el importador y el auditor existentes valen sin cambios (ver `Docs/CIERRE-20261012/T01-F1-OPERATIONAL-RECORD.md`).
4. **Revisión independiente** de `experimentos/t25_escalado_claude/run_t25.py` y `experimentos/t27_calibracion_claude/run_t27.py`: recalcular las métricas sin importar mis evaluadores.

## Reglas que se han seguido

- Protocolos comprometidos y publicados antes de calcular, con comprobación en el servidor (`agentkit.prereg --query-server`).
- Un fallo de ejecución (T25, intento 1) se conserva y se repite con enmienda fechada y nuevo identificador.
- Ninguna medida, fabricación, novedad ni reproducción externa se declara sin evidencia del tipo correcto.
- JEV consultado con `provenance=jev` para la ruta de publicación y la ubicación de las pruebas.
