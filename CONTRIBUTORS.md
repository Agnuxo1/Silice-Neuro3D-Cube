# Autoría y colaboración

Este repositorio se desarrolla con dos agentes de IA bajo la dirección de su titular. Esta página registra quién hace qué. Las reglas de colaboración están en [AGENTS.md](AGENTS.md).

## Roles

| Participante | Tipo | Responsabilidad en el repositorio |
|---|---|---|
| Francisco Angulo de Lafuente | Persona (titular) | Dirección científica, decisiones de publicación, licencia y visibilidad. Es la identidad git de todos los commits del historial. |
| Codex | Agente de IA de programación | `src/silice/`, `tests/`, `scripts/` e informes en `resultados/codex/`. |
| Claude | Agente de IA (Anthropic) | `experimentos/*_claude` y `experimentos/glass_min1/`, respuestas en `coordinacion/respuestas/` y las auditorías de revisión asignadas. |

## Cómo se registra la atribución

- **Historial anterior.** Los commits existentes conservan su autoría original. No se reescribe el historial.
- **Commits nuevos.** Desde el commit `3c0c69d` (2026-10-09), los commits preparados con asistencia de Claude llevan la línea `Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>`. Quien revise un commit puede identificar así qué parte corresponde al agente.
- **Documentos.** Cada contrato, informe y respuesta indica su autor en el propio texto, según la convención de [AGENTS.md](AGENTS.md).

## Uso de IA

Parte del código, la documentación y la ejecución de ensayos se produjo con agentes de IA. El titular revisa las decisiones y la publicación. Los resultados deben reproducirse con el código del repositorio, sin depender de ninguna herramienta externa.

## Responsabilidad

Un agente de IA no es sujeto de derechos ni de responsabilidad. La titularidad, la licencia y las obligaciones frente a terceros corresponden al titular. Ver también [Docs/LICENCIA-PROPUESTA.md](Docs/LICENCIA-PROPUESTA.md).
