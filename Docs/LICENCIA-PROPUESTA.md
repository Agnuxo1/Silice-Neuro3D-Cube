# Licenciamiento: propuesta pendiente de aprobación

**Estado: pendiente de decisión del titular.** El repositorio no tenía licencia y esta nota **no concede ningún permiso de uso**. Hasta que se publique un fichero `LICENSE` aprobado, se aplican los derechos de autor por defecto.

Este documento es una propuesta técnica y no constituye asesoramiento jurídico.

## Propuesta

| Contenido | Licencia propuesta | Texto oficial (SHA-256 del texto obtenido de la API de GitHub) |
|---|---|---|
| Código: `src/`, `scripts/`, `tests/`, `tools/`, `experimentos/**/*.py` | Apache-2.0 | `c95bae1d1ce0235ecccd3560b772ec1efb97f348a79f0fbe0a634f0c2ccefe2c` |
| Documentación, figuras y GIF: `Docs/`, `README.md`, `assets/` | CC-BY-4.0 | `5eebefd3682e32d661f307a28539b304e5e52fb1eb33ba214e61d7a57663e4f0` |
| Datos de evidencia: `resultados/` (JSON, NPZ, logs) | CC-BY-4.0 (alternativa: CC0-1.0, SHA-256 `7179683e8000e6bdc9bbc60d85edf0a4ac8e76f951857f54fcb775d5886f1309`) | — |

## Motivos

- **Código, Apache-2.0.** Incluye una concesión expresa de patentes por parte de los contribuidores y una cláusula de represalia. Con MIT, la cobertura de patentes es implícita y su alcance es ambiguo ([FOSSA](https://fossa.com/resources/license-compliance-tools/license-compatibility-checker/apache-2-0-vs-mit/)); la elección entre ambas es una decisión de equilibrio, que [Producing OSS](https://producingoss.com/en/license-choosing.html) describe ([Auckland, guía de licencias para software de investigación](https://www.auckland.ac.nz/en/research/research-resources/intellectual-property-commercialisation/commercialisation-licensing-open-sourcing-research-software.html)). Harvard Library recomienda Apache-2.0 en sus proyectos por la misma razón ([Harvard Library wiki](https://harvardwiki.atlassian.net/wiki/x/0qWUAg)); Leiden lo cita como ejemplo de licencia abierta con atribución ([Leiden](https://www.digitalscholarshipleiden.nl/articles/tip-4-share-your-research-software-with-an-open-license)).
- **Compatibilidad.** Las dependencias declaradas son `numpy` (BSD-3 y componentes BSD), `scipy` (BSD-3-Clause) y `psutil` (BSD-3-Clause). Todas son compatibles con Apache-2.0.
- **Documentación y figuras, CC-BY-4.0.** Exige atribución, que es lo habitual para artículos y figuras ([Figshare](https://info.figshare.com/?p=2627)).
- **Datos, CC-BY-4.0 o CC0.** Las guías divergen. Varias recomiendan CC0 para datos factuales por facilitar la agregación ([CASRAI](https://casrai.org/wp/?p=1201); [Canadensys](https://www.canadensys.net/post/2023/whycc0/)). Otras recomiendan CC-BY por defecto para datos de investigación ([Cranfield](https://library.cranfield.ac.uk/research-data-management/selecting-data-licence)). Se propone CC-BY-4.0 para conservar la atribución; CC0 es una alternativa válida.
- **No usar licencias CC para software.** Una guía universitaria lo desaconseja explícitamente ([Humboldt-Universität zu Berlin](https://www.cms.hu-berlin.de/en/dl-en/dataman-en/share/legal-aspects/license)), por eso el código va con Apache-2.0.

## Decisiones que requieren al titular

1. Aprobar la propuesta o indicar cambios.
2. Nombre del titular para la línea de copyright (propuesta: *Francisco Angulo de Lafuente*).
3. Datos: CC-BY-4.0 (propuesta) o CC0-1.0.
4. **Contenido generado con herramientas de IA.** El estatus jurídico de la autoría de ese contenido no está resuelto en todas las jurisdicciones. Conviene revisarlo antes de conceder licencias sobre él.
5. **Política de propiedad intelectual de una institución**, si la hubiera. Debe revisarse antes de publicar.
6. Las patentes: Apache-2.0 no garantiza libertad de operar. Si el diseño es patentable, la decisión sobre patentar debe tomarse antes de publicar el código.

## Aplicación tras la aprobación

Con la propuesta aprobada, el titular puede aplicarla con estos comandos desde la raíz del repositorio. Después conviene verificar los hashes anteriores.

```bash
gh api licenses/apache-2.0 --jq .body > LICENSE
```

```bash
mkdir -p LICENSES && gh api licenses/cc-by-4.0 --jq .body > LICENSES/CC-BY-4.0.txt
```

Además, añadir un fichero `NOTICE` con la línea de copyright y una sección de licencias en el `README.md` que apunte a este documento.
