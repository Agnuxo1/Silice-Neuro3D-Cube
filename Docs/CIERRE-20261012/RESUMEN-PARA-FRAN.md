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
6. **Registro de afirmaciones** con 41 afirmaciones de T01 a T30, cada una con su evidencia y su falsador. Tabla: `CLAIMS-TABLE-20261013-final.md`.
7. **Manuscrito en inglés**, de 7 páginas: `paper/manuscript.pdf`.
8. **Registros:**
   - pérdida operacional de F1 (T01);
   - dossier de fabricación (T28);
   - tu decisión de publicar (T29).

## Qué se sostiene y qué no

| Se sostiene | Ha caído |
|---|---|
| El 3D ahorra como mucho una capa | La ventaja energética de una capa óptica pasiva en vidrio |
| El suelo electrónico pierde frente al digital moderno | «Primera red 3D multicapa escrita con fs en vidrio» (existe LAMP, 2026) |
| La calibración absorbe errores pequeños (modelo, N ≤ 8) | «Primera guía de trinchera a 1550 nm» (existe SK1310, 2025) |
| Las cifras de estado del arte y su verificación | La ventaja de los cruces 3D como titular |

## Lo que solo puedes decidir tú

1. **Licencia.** Sigue sin licencia; la propuesta es Apache-2.0 para el código y CC-BY-4.0 para documentos y datos (`Docs/LICENCIA-PROPUESTA.md`). Sin licencia nadie puede reutilizarlo legalmente, lo que impide una reproducción externa (T21).
2. **Laboratorio.** Sin un socio con escritura fs y medida a 1550 nm, el proyecto no pasa de simulación. El dossier está listo, pero no he contactado a nadie.
3. **Archivo con DOI** (Zenodo u otro). Daría una marca de tiempo externa y guardaría las evidencias grandes.
4. **F1.** Si en tu Colab o Drive siguen los resultados finos del 9 de octubre, descárgalos a `D:\PROJECTS` y se auditan con las herramientas que ya existen.
5. **Lecturas pendientes:** el artículo de SK1310 (Zhou, 2025), que no pudimos leer, y una **revisión humana externa** del manuscrito antes de enviarlo a una revista o a arXiv.

## Dónde mirar primero

- `README.md`, sección «Scientific closure · 13 October 2026».
- `Docs/CIERRE-20261012/T20-DECISION.md`: la afirmación central y su revisión.
- `Docs/CIERRE-20261012/T30-REDTEAM-RESPONSE.md`: qué se corrigió y por qué.
