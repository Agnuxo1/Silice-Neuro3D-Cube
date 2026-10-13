# Resumen del cierre científico para Fran (13 de octubre de 2026)

Has pedido completar todos los pasos de la guía v2, llevar el proyecto al nivel más alto que permita la evidencia y publicarlo todo sin borrar nada. Esto es lo que se ha hecho y lo que significa.

## En una frase

El proyecto tiene ahora un resultado numérico sólido, prerregistrado y revisado adversarialmente, pero es una **delimitación** (qué no puede dar una red 3D escrita con láser en vidrio) y no una novedad. Lo que podría ser original está en una medida que necesita laboratorio: la pérdida de las guías de trinchera.

## Qué se ha hecho

1. **Kit de la guía** en `agentkit/`, idéntico byte a byte a la guía, con 61 pruebas que pasan en Windows y Linux (CI nueva). No he tocado `tests/` ni nada de Codex.
2. **Cuatro pruebas de descarte**, todas con el protocolo publicado en GitHub antes de calcular, comprobado en el servidor:
   - **T25, profundidad y cruces.** Una malla 3D puede ahorrar como mucho una capa frente a una plana. Una mariposa plana necesita del orden de N² cruces.
   - **T27, calibración in situ (modelo).** Con errores de acoplador de 0,02 rad, la calibración deja la infidelidad por debajo de 1,3·10⁻⁴ (sin calibrar, 1,5·10⁻²). Con 0,05 rad ya no llega.
   - **T24, energía.** **La ventaja energética cae.** A 64×64 y 8 bits, los conversores y moduladores ya gastan 1,4–4,5 veces lo que una MAC digital de 3 nm, aunque la parte óptica no perdiera nada.
   - **T26, estado del arte.** 31 referencias verificadas una a una. La mejor pérdida que encontramos a 1550 nm en sílice es 0,06 dB/cm (Ackermann, 2025). Ya existen circuitos 3D de Fourier escritos con láser (2016) y una red neuronal 3D en vidrio (2026).
3. **Diseño de la guía de trinchera (T20D).** Con 16 µm de trinchera, la fuga ideal baja a 0,002 dB/cm. Así la prueba de laboratorio medirá la calidad de la escritura, no la geometría.
4. **Enmienda de H1**, fechada antes de medir:
   - H1-A: umbral de 0,3 dB/cm, que es de viabilidad.
   - H1-SOTA: umbral de 0,06 dB/cm, que es de estado del arte.
5. **Revisión adversarial (T30).** Un agente independiente intentó romper la afirmación central y encontró exageraciones reales en mis primeras cifras. Las he corregido todas y el registro conserva la versión anterior.
6. **Registro de afirmaciones** con 41 afirmaciones de T01 a T30, cada una con su evidencia y su falsador. Tabla vigente: `CLAIMS-TABLE-20261013b.md` (16 parciales, 7 aprobadas, 2 fallidas, 4 retiradas). La versión anterior, `CLAIMS-TABLE-20261013-final.md`, se conserva.
7. **Manuscrito en inglés**, de 7 páginas: `paper/manuscript.pdf`.
8. **Registros:**
   - pérdida operacional de F1 (T01) y su recuperación con F1R2 (punto 9);
   - dossier de fabricación (T28);
   - tu decisión de publicar (T29).

9. **F1 recuperada (F1R2, 13 de octubre).** Repetí en este PC, con el protocolo publicado antes de calcular, la prueba fina de convergencia temporal que se perdió en Colab. **Cumple los cinco criterios del contrato**: diferencia de campo 1,35·10⁻⁵, con umbral 10⁻⁴. Pasa la auditoría de integridad y la auditoría anclada al servidor. Tardó 23 273 s de 32 000 y hubo 8 reintentos por falta de memoria puntual, todos conservados. El primer intento (F1R), que falló por memoria, también se conserva. T01 sigue parcial: falta la convergencia espacial (S16, malla de 0,28 µm y dominio). Informe: `T01-F1R2-RESULTS.md`.
10. **Otros cambios en el registro.** T23 incluye ya la CI en Windows y Linux, y T28 la lista de 23 laboratorios candidatos (no he contactado a ninguno).

## Qué se sostiene y qué no

| Se sostiene | Ha caído |
|---|---|
| El 3D ahorra como mucho una capa | La ventaja energética de una capa óptica pasiva en vidrio |
| El suelo electrónico pierde frente al digital moderno | «Primera red 3D multicapa escrita con fs en vidrio» (existe LAMP, 2026) |
| La calibración absorbe errores pequeños (modelo, N ≤ 8) | «Primera guía de trinchera a 1550 nm» (existe SK1310, 2025) |
| Las cifras de estado del arte y su verificación | La ventaja de los cruces 3D como titular |

## Lo que solo puedes decidir tú

1. **Licencia: ya decidida.** Elegiste Apache-2.0 para todo el repositorio y está aplicada en `main` (`LICENSE`, `NOTICE`, `LICENSE-DECISION-20261013.md`). En el registro, C-LICENSE pasa a PASS.
2. **Laboratorio.** Sin un socio con escritura fs y medida a 1550 nm, el proyecto no pasa de simulación. El dossier está listo, pero no he contactado a nadie.
3. **Archivo con DOI** (Zenodo u otro). Daría una marca de tiempo externa y guardaría las evidencias grandes.
4. **F1: resuelto sin Colab.** La repetición registrada F1R2 sustituye a los resultados perdidos (punto 9). Si aun así aparecen los del 9 de octubre, servirían como comparación independiente.
5. **Lecturas pendientes:** el artículo de SK1310 (Zhou, 2025), que no pudimos leer, y una **revisión humana externa** del manuscrito antes de enviarlo a una revista o a arXiv.

## Dónde mirar primero

- `README.md`, sección «Scientific closure · 13 October 2026».
- `Docs/CIERRE-20261012/T20-DECISION.md`: la afirmación central y su revisión.
- `Docs/CIERRE-20261012/T30-REDTEAM-RESPONSE.md`: qué se corrigió y por qué.
