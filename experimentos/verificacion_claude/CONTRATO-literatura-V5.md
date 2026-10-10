# CONTRATO: verificación bibliográfica V5 (literatura)

- Autor: agente Claude (carpeta `experimentos/verificacion_claude/`).
- Fecha de redacción: 2026-10-10, antes de cualquier búsqueda (`date -u` a las 04:11 UTC).
- Hora límite de entrega: 06:20 UTC.
- Plan JEV de esta fase: `router.py plan`, id `1791605554-research`, ejecutor `main_agent`, esfuerzo bajo, sin segunda opinión. No consta `provenance=jev` en esa salida; la decisión se registra como local.
- Proyecto: Silice-Neuro3D-Cube. Esto es literatura y verificación documental. No hay cálculo numérico de la red. Modelo, predicción y medida no se mezclan.

## 1. Hipótesis

- **P1.** «Programmable Three-dimensional Photonic Neural Network Chip» (HUST y SJTU, *Nature Communications*, 2026) existe, tiene DOI, describe una red en vidrio escrita con láser fs, reporta una longitud de onda, y sus cifras de 93 % en MNIST y 6554 TOPS aparecen en el propio artículo.
- **P2.** Lee et al., *Scientific Reports* (2021), trata la pérdida de curvatura en sílice escrita con fs mediante la técnica de microgrietas, y da unos 1 dB/cm con radio de 10 mm a 1550 nm.
- **P3.** El artículo «Camisa deprimida SK1310» (*Optical Materials*, `S0925346725000102`) tiene o no PDF de acceso abierto. La ficha OHARA enlazada en `Docs/SK1310-FUENTES.md` funciona y da índices a 25 °C coherentes con los de esa tabla.

## 2. Criterios numéricos (umbrales fijados ahora)

Veredicto por punto, con la terminología del esquema de salida:
- **confirmed** (equivale a «verified»): fuente primaria leída en el texto que devolvió la herramienta, y el dato coincide con el criterio numérico de abajo.
- **refuted**: fuente primaria accesible que contradice el dato, o no existe la referencia tras búsqueda en editorial, Crossref y autores.
- **unverified**: sin acceso a fuente primaria, o solo prensa o fragmentos.

Umbrales:
- **P1a** (existencia y DOI): confirmed si el DOI resuelve a una página de la editorial con ese título. Refuted si no hay ningún registro con ese título en Crossref ni en la editorial.
- **P1b** (longitud de onda, vidrio, fs): confirmed si la fuente primaria lo dice explícitamente.
- **P1c** (93 % MNIST y 6554 TOPS): confirmed solo si ambas cifras aparecen en la fuente primaria (resumen o texto). Si el artículo existe pero una cifra no aparece, esa cifra queda unverified, no confirmed.
- **P2a** (pérdida): confirmed si el valor primario está en [0,5; 2] dB/cm, con radio = 10 mm y λ = 1550 nm exactos. Refuted si la fuente primaria da un valor fuera de [0,5; 2] dB/cm o un radio o una λ distintos. Unverified si solo hay fragmentos.
- **P2b** (DOI y técnica de microgrietas): confirmed si el DOI resuelve al artículo y el texto menciona microgrietas (microcracks) como técnica.
- **P3a** (acceso abierto): confirmed si la página del artículo o su DOI indica de forma explícita el estado de acceso. Unverified si la página devuelve error y no hay otra fuente.
- **P3b** (enlace OHARA): confirmed si el enlace devuelve contenido de la ficha (no error ni página vacía).
- **P3c** (índices a 25 °C): confirmed si, en las longitudes de onda comparables, cada índice de la ficha coincide con el de `Docs/SK1310-FUENTES.md` dentro de 1·10⁻⁴ (aire, sin factor de vacío). Refuted si alguna diferencia es mayor que 1·10⁻⁴. Unverified si la ficha no es legible.

## 3. Métodos

- `WebSearch` para localizar las fuentes y `WebFetch` para leer páginas, DOI, resultados de Crossref y la ficha OHARA.
- Ninguna descarga de archivos al disco. No se guarda ningún PDF con copyright en el repositorio ni en el disco.
- Para P3c, comparación en Python (`python -B`, biblioteca estándar) con los valores que devuelva la ficha. La salida se guarda en esta carpeta.
- Cada veredicto lleva el enlace concreto que se usó.

## 4. Lo que NO afirmo

- No afirmo que los resultados del artículo HUST/SJTU sean correctos, reproducibles ni que tengan buena metodología. Solo afirmo lo que aparece en la fuente primaria consultada.
- No afirmo la pérdida de curvatura a 1550 nm más allá del texto que se pueda leer. Si solo hay un fragmento, la cifra queda unverified.
- No afirmo el índice de SK-1310 a 1550 nm. La extrapolación desde la ficha no está verificada.
- No afirmo que el PDF de SK1310 sea accesible sin acceso institucional si no lo verifico.
- No leo ni imprimo claves. No abro `Desktop/UTILIDADES_HERRAMIENTAS_APIs.txt`.
- No toco `src/silice/`, `tests/`, `scripts/`, `coordinacion/` ni `Docs/`. No hago git add, commit ni push.
