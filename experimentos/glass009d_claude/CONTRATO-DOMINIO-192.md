# T96/Q4 · estudio de dominio · contrato prospectivo (2026-10-10)

Publicado antes de calcular. Mismo solver (`adi2d.py`), geometría de 96 trazos, dz = 2,5 µm, 800 pasos, σmax y paso de píxel. Se varía solo el dominio lateral.

- **Referencia:** dominio 128 µm, dx = 0,5 µm (ya calculada): P = 0,332236756.
- **Prueba:** dominio 192 µm, dx = 0,5 µm (N = 384).
- **Criterio D1 (fijado ahora):** |P(192) − P(128)| / P(128) < 0,2 %.
- **Predicción P-D1:** el dominio de 128 µm ya es suficiente. El cambio es menor que 0,2 %, porque el haz guiado (w = 6 µm) queda lejos de la frontera y la difracción no alcanza el borde en 2 mm con la esponja activa.
- **Q1** de integral de δn en el nuevo dominio: < 10⁻³.
- Ejecución en 4 trozos de 200 pasos (límite de 30 s por proceso; la reanudación es exacta, comprobada en `resultados_q4_reserva_028.json`).
- Lo que no hace: no mide el efecto de la esponja por separado ni estudia dominios mayores de 256 µm.
