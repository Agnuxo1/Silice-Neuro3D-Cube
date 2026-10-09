# Estado actual del repositorio · 2026-10-09

Documento de entrada. Resume el estado a fecha de hoy. El detalle científico sigue en [PROJECT-STATUS](PROJECT-STATUS.md), reconciliado el 2026-10-06.

## Repositorio

- **Rama principal:** `main`. Los cambios de hoy llegan por fast-forward; el historial anterior no se reescribe.
- **Licencia:** no publicada. La propuesta está en [LICENCIA-PROPUESTA](LICENCIA-PROPUESTA.md) y espera la decisión del titular.
- **Visibilidad:** pública. El registro de eventos de GitHub indica que lo fue desde su creación el 2026-09-30 (un `PublicEvent` con la misma marca temporal que `created_at`). Falta la confirmación del titular.
- **Integración continua:** [`cpu-tests.yml`](../.github/workflows/cpu-tests.yml) ejecuta las 51 pruebas CPU en Windows 2022 y Ubuntu 24.04, y el guardián de tamaño. Ejecuciones verificadas en GitHub Actions.
- **Tamaño:** 947,5 MB únicos en el historial (paquete de 776,7 MiB). Política en [ARCHIVO-Y-TAMANO](ARCHIVO-Y-TAMANO.md).
- **Autoría y citación:** [CONTRIBUTORS](../CONTRIBUTORS.md) y [CITATION.cff](../CITATION.cff).
- **Bitácora de coordinación:** la instantánea íntegra está en [`coordinacion/archivo/`](../coordinacion/archivo/LEEME.md). La bitácora viva sigue activa.

## Operación

- **Ejecuciones largas en Colab:** el estado de F1 no está verificado. Procedimiento en [OPERACION-EJECUCIONES-LARGAS](OPERACION-EJECUCIONES-LARGAS.md).

## Ciencia (resumen sin nuevos resultados)

- Pruebas CPU: 51 de 51 aprobadas en Windows y en Linux (CI).
- Hitos y criterios: ver [PROJECT-STATUS](PROJECT-STATUS.md).
- Hoja de ruta de 25 puntos: 2 cerrados, 3 parciales y el resto abierto o sin demostrar.

## Decisiones pendientes del titular

1. Licencia (propuesta lista, sin publicar).
2. Confirmar que la visibilidad pública es intencionada.
3. Autorizar la subida de evidencias pesadas a Zenodo (acción externa con DOI).
4. Revisar desde su navegador la sesión de Colab de F1 y decidir si descarga alguna parte.
5. Decidir si se monta Drive para persistir partes en ejecuciones futuras.
