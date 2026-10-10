# Corrección de estados del plan (2026-10-11)

El plan de la sesión anterior (`coordinacion/tareas/PLAN-22-TAREAS-20261010.md`) marcó como «cerrada en modelo» tres tareas cuyo criterio principal no se cumple. Según el principio del plan final (`Docs/PLAN-FINAL-20261011.md`), «hecho» exige que el criterio preregistrado se cumpla. Esta corrección no reescribe el plan anterior: lo sustituye para los estados que aparecen abajo.

| Tarea | Estado anterior | Estado corregido | Motivo |
|---|---|---|---|
| T10 Estabilidad y control de fase | cerrada en modelo | **parcial** | H10a y H10c cumplen; H10b no cumple (cociente 1,68). |
| T11 Compilador | cerrada en modelo | **parcial** | C1 cumple; C2 no cumple (1,3e-2 a 1,7e-2 frente a 5e-3); C3 cumple en la realización preregistrada y en 28 de 36 realizaciones (78 %). |
| T16 Tarea con datos reales | cerrada en modelo | **parcial** | H-D1 y H-D3 cumplen; H-D2 no cumple (B = 0,4074 frente a 0,90). |
| T12 Red funcional | parcial | **fallido** (resultado negativo preregistrado) | H-F1 y H-F2 no cumplen; H-F3 sí. Documento de cierre: `Docs/T12-CIERRE-Y-BLOQUEADOS-20261011.md`. |
| T2 Barrido modal | cerrada | **cerrada con enmienda declarada** | P-B4 se evaluó con un criterio relativo declarado antes de juzgar; el criterio absoluto original no cumple por unidades. |

## Qué no cambia

- Los resultados de T10, T11 y T16 siguen publicados tal cual. Solo cambia su estado.
- T3, T4, T5, T6, T8, T19 y T20 siguen parciales o abiertas, como en el plan anterior.
- Los bloqueados (T1, T7, T9, T13, T14, T15, T17, T18, T21, T22, SK1310 y fabricación) siguen bloqueados, con criterios de aceptación en `Docs/PLAN-FINAL-20261011.md`.

## Regla

Un estado solo es «cerrado» si el criterio preregistrado se evaluó y se cumplió. Un criterio que no se cumple se publica como fallido o parcial, nunca como cerrado.
