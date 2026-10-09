# Ejecución del pronóstico S16

Se implementa antes de las potencias finales F1 y de los campos reservados,
sin alterar el contrato S16 ni la función P5D ya registrada. El evaluador
`point03_fem_spatial.py` se reutiliza sólo si su hash coincide con los
once controles históricos aprobados. No se ejecutan éstos otra vez.

La ejecución requiere auditorías locales aprobadas de C2-R1, M2-R1 y F1.
Si F1 no terminó o no aprueba, el pronóstico no se ejecuta. Se comprueban
K16 en las tres mallas, hashes de los campos/reportes primarios y el método
Padé32768, sin sustituirlos por Radau. No se calcula ninguna nueva onda.

Para cada observable se utiliza su propia máxima diferencia temporal de
potencia entre las tres mallas, exactamente como recibe la función escalar
forecast(powers, temporal_differences). No se mezclan las diferencias de
los dos observables. Se mantienen el factor20, el rango de orden0,5–6,
la razón1,25 y todos los criterios del contrato S16.

El resultado global exige ambos observables elegibles. Si uno falla,
guardar estado negativo y no permitir generación de h=0,28. Los resultados
individuales se conservan; un pronóstico individual no autoriza la malla.
No cambiar terna, umbrales, modelos ni fases por esos resultados.

El auditor independiente recalcula incrementos, órdenes y predicciones
sin importar el evaluador. Comprueba las fuentes y auditorías de entrada.
Los controles nuevos usan dos leyes escalares conocidas de órdenes2y3,
predicción exacta, oscilación de un solo observable, ruido temporal en
un solo observable, incrementos nulos y prerrequisito temporal falso.
Son controles manufacturados sin leer resultados T96 ni generar campos.
También se rechaza una razón o un orden de auditorías de malla alterados.
La segunda versión de controles conserva la primera y enlaza los hashes
de los cuatro módulos actuales en point03_s16_controls_run2_20261009.json.

El pronóstico y su auditoría se guardarán en carpeta nueva de resultados.
Publicar y verificar los hashes antes de generar la malla reservada; el
protocolo de ejecución reservada y los recursos deben aprobarse aparte.
Un pronóstico elegible no equivale a aprobación espacial o de dominio.
Tarea1 abierta; JEV fallback local por bloqueo remoto retenido.

Comandos posteriores a F1 local aprobada:

    python scripts/forecast_point03_s16.py --out resultados/codex/point03_s16_forecast_20261009
    python scripts/audit_point03_s16_forecast.py --out resultados/codex/point03_s16_forecast_20261009

## Transporte F1 preparado

`import_point03_d16_fine.py` comprueba todos los ZIPs del manifiesto
exportado por SHA/CRC, rutas, duplicados, ausencia de enlaces simbólicos,
fuentes congeladas, cadenas de reportes y192campos. Sólo adopta archivos
ausentes después de un aprobado remoto de integridad; acepta y conserva
un criterio temporal negativo. El dictamen final exige después el auditor
local, preservando el remoto. Un fallo operativo se conserva en la carpeta
de transporte y no se adopta como resultado completo.

    python scripts/import_point03_d16_fine.py --export-manifest MANIFEST_JSON --archives ZIP_FOLDER --out NEW_TRANSPORT_FOLDER
    python scripts/audit_point03_d16_fine_local.py --out resultados/codex/point03_d16_fine_time_20261009

El control de transporte aprobó cuatro nombres válidos y rechazó siete
rutas/nombres inválidos. La segunda comprobación añadió tres rutas de
fuentes fuera del proyecto y también las rechazó; conserva el control
precedente. No leyó ni generó un campo óptico F1.
