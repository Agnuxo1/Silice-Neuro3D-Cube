# Protocolos y estados de las tareas bloqueadas o externas (2026-10-10)

Ninguna de estas tareas está cerrada. Cada bloque dice qué falta, el protocolo preregistrado que se ejecutará cuando haya medios, qué se puede hacer ya en modelo, y la decisión que necesita Fran. Las cifras de criterio son propuestas y se fijan antes de medir.

## T9 · escritura profunda y registro entre caras con muestras reales
- **Estado:** bloqueado (equipo de escritura fs y muestras).
- **Falta:** un láser fs y una plataforma de escritura con acceso a varias caras, o un socio que escriba.
- **Protocolo:** escribir 3 muestras con la misma receta en 2 profundidades (p. ej., 100 µm y 500 µm). Medir el registro entre caras por microscopía con marcas de referencia. Criterio: desplazamiento lateral < 1 µm (1σ) entre caras. Falsable: si la dispersión entre muestras supera 3 µm, la escritura desde varias caras no es viable con esa receta.
- **En modelo ahora:** los límites de tolerancia de T5 (`Docs/TAREA-5-INCERTIDUMBRES.md`) dan el presupuesto de geometría de partida.
- **Decisión de Fran:** socio o equipo para escribir muestras.

## T13 · fabricar muestras de calibración y red pequeña
- **Estado:** bloqueado (fabricación; depende de T9 y T14).
- **Protocolo:** fabricar un juego de guías de calibración (cutback a 1550 nm) y una red 4×4 de 6 MZI, con la misma receta. Criterio de aceptación: al menos 3 de 4 guías de calibración dentro de la incertidumbre preregistrada.
- **En modelo ahora:** el compilador (T11) da la netlist de DFT₄ con códigos de 8 bits (`experimentos/compilador_claude/compilador_resultados.json`). Su fabricación no está comprobada: no hay layout.
- **Decisión de Fran:** fabricante o taller con escritura fs.

## T14 · medidas ópticas calibradas
- **Estado:** bloqueado (requiere muestras de T13 y equipo de medida).
- **Protocolo:** cutback a 1550 nm según `Docs/F2-PROTOCOLO-MEDIDA.md` (≥ 4 longitudes, ≥ 3 muestras, dos polarizaciones). Medir δ, la razón de división de los acopladores, y la fase de cada MZI con un barrido de voltaje. Criterio: pérdida con IC 95 % (H1 de `Docs/CONTRIBUCION-CENTRAL-T20.md`) y δ medido con dispersión menor que 0,02 (σ supuesta en T11).
- **En modelo ahora:** `Docs/PRESUPUESTO-INCERTIDUMBRE-GEOMETRIA.json` (T5) fija el presupuesto que hay que contrastar.
- **Decisión de Fran:** equipo de medida y calibración del láser de medida a 1550 nm.

## T15 · integración óptica–electrónica–control
- **Estado:** bloqueado (requiere un prototipo de control y la red de T13).
- **Protocolo:** lazo cerrado de control de fase con la red de T13 y un controlador de DAC de 8 bits. Criterio: el lazo mantiene el error de transferencia por debajo de 10⁻² durante 1 h, con deriva medida.
- **En modelo ahora:** la fase con deriva y errores correlacionados ya está modelada (T10, `experimentos/fase_claude/RESULTADOS-FASE.md`), incluido el fallo de H10b (ℓ = 3 frente a 0, cociente 1,68), que obliga a medir la correlación antes de diseñar el control.
- **Decisión de Fran:** hardware de control y una planta de medida.

## T17 · rendimiento y consumo del sistema completo
- **Estado:** bloqueado (depende de T13 y T15).
- **Protocolo:** medir latencia, energía por operación y rendimiento del sistema completo, con potencia de entrada y de control, frente a un baseline electrónico con los mismos datos (T16). Criterio: energía por operación del sistema completo menor que la del baseline, con IC 95 %.
- **En modelo ahora:** el balance paramétrico de `experimentos/f3_red_pequena/CONTRATO-F3.md` no incluye energía medida; no hay cifras que comparar.
- **Decisión de Fran:** equipo de medida eléctrica y tiempo de laboratorio.

## T18 · escalabilidad y reproducibilidad
- **Estado:** parcial en lo que es software; bloqueado en lo experimental.
- **Software ya hecho:** CI en `.github/workflows/cpu-tests.yml` con instalación por hashes (`requirements/cpu-linux-py313.lock`) en Linux y Windows; guardia de tamaño de repositorio (`tools/repo_size_guard.py`).
- **Protocolo experimental:** reproducir dos muestras de T13 en un segundo laboratorio. Criterio: diferencia de pérdida entre laboratorios menor que la incertidumbre combinada.
- **Decisión de Fran:** un segundo laboratorio o socio.

## T21 · reproducción independiente y revisión externa
- **Estado:** externo (no se puede cerrar desde el repositorio).
- **Protocolo:** publicar el código y los datos con licencia y DOI de archivo (ver `Docs/LICENCIA-PROPUESTA.md` y `Docs/ARCHIVO-Y-TAMANO.md`), y pedir a un tercero que reproduzca al menos T2 (barrido modal) y T11 (compilador). Criterio: el tercero obtiene las mismas cifras con el mismo código, con tolerancia de 10⁻⁶ relativo en el modelo.
- **Bloqueo:** la publicación exige decisión de Fran (licencia, visibilidad, archivo externo).
- **Decisión de Fran:** licencia, visibilidad del repositorio y depósito en Zenodo.

## T22 · impacto sostenido
- **Estado:** temporal (no se puede medir en una sesión).
- **Protocolo:** indicadores de seguimiento a 12 meses: citas, descargas del archivo, reproducciones independientes y decisiones de socios. Se fijan ahora y se revisan en la fecha acordada.
- **Decisión de Fran:** fecha de revisión y responsable del seguimiento.
