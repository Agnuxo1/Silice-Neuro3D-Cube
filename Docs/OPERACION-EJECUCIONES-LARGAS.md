# Operación de ejecuciones largas en Colab: estado de F1 y procedimiento

## Estado verificado (2026-10-09, 13:12–13:16 UTC)

Lectura de solo lectura del cuaderno de recursos de M2 (`Silice_M2_recursos_20261009.ipynb`), que la bitácora enlaza como sesión de M2-R1 y de F1:

- La celda 9 contiene el código de ejecución de F1: lanza `scripts/run_point03_d16_fine_time.py`, audita el resultado y exporta ZIP en partes.
- La celda 9 no muestra salida guardada en la página.
- El panel Archivos de `/content` no mostró ninguna entrada en el árbol de la página.
- La pestaña dejó de responder a las capturas (tiempo agotado en dos intentos).
- No se ejecutó ninguna celda, no se inició sesión, no se montó Drive, no se descargó ningún fichero y no se cambió ningún permiso.

## Qué sigue sin saberse

- Si el proceso de F1 terminó, falló o sigue activo.
- Si existen partes ZIP exportadas.
- Si el entorno de ejecución se reinició.

## Hipótesis (no verificada)

El manifiesto de F1 se creó a las 03:22:29 UTC con un presupuesto global de 32 000 s, por lo que el corte previsto era hacia las **12:15:49 UTC**. Si la celda llegó a exportar, deberían existir ZIP en `/content`. Su ausencia en el panel es compatible con un reinicio del entorno o con una celda que no completó la exportación. Esto solo puede confirmarlo la sesión del titular.

## Causas probables (riesgo de diseño)

1. **Almacenamiento efímero.** Los resultados viven en `/content`, que pertenece a la máquina virtual y se pierde si el entorno se reinicia. El protocolo prohíbe montar Drive, lo que aumenta el riesgo.
2. **Exportación solo al final.** Si la celda se interrumpe antes, no hay partes intermedias que recuperar.
3. **Dependencia del navegador.** El seguimiento depende de sesiones de navegador con traspasos manuales y de un renderizado que se congela.

## Procedimiento propuesto para ejecuciones futuras

1. **Antes de lanzar.** Contrato con presupuesto total, margen de exportación (al menos el 15 % del presupuesto) y hash de todas las fuentes.
2. **Persistencia.** Exportar cada tarea terminada, con su SHA-256, en cuanto termina; no esperar al final. Montar Drive solo con autorización explícita del titular.
3. **Registro.** Un `progress.json` actualizado por tarea, con marca temporal UTC.
4. **Recuperación.** Si la sesión se pierde, documentar los prefijos disponibles y auditarlos antes de cualquier reanudación. Una tarea ya registrada no se vuelve a ejecutar sin un contrato nuevo.
5. **Fuente primaria.** El estado se registra por el propio proceso en el repositorio, no mediante lecturas del navegador.

## Decisiones pendientes del titular

- Autorizar o no el montaje de Drive para persistir las partes.
- Revisar la sesión de Colab y confirmar si existe alguna parte de F1. Una descarga requiere aprobación explícita.

La bitácora de coordinación (`coordinacion/CHECKPOINT.md`) no se modifica con este documento.
