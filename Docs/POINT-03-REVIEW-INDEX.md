# Evidencias revisables del punto 3

**T96/Q4 permanece abierto.** M1 terminó y su auditor confirma FAIL de
predicción/orden con integridad y precisión longitudinal aprobadas. N1
es un contraste analítico distinto, no un cierre ni una causa demostrada.

- Estado: [actualización del 7 de octubre](PROJECT-STATUS-20261007.md).
- Dictamen: [M1](POINT-03-M1-RESULTS.md).
- Diagnóstico conocido: [N1](POINT-03-N1-RESULTS.md).
- Historial: E/G2/H2/K626/L1 conservan sus FAIL; L2 precisión práctica PASS.

## Paquete de informes

`resultados/codex/point03_export_M1_20261007/` contiene informe,74filas de
potencias,455fuentes/informes archivados, hashes y verificación CRC/SHA.
Los arrays no están incluidos en ese ZIP. N1 está registrado por separado
en `point03_n1_analytic_contrast_20261007.json`, junto a su contrato/fuente.

## Verificación de los observables finales desde otra copia

`resultados/codex/point03_terminal_20261007/` contiene siete arrays finales:
cuatro primarias320/400/500/640 y las tres trayectorias M1 N767. El índice
usa rutas relativas y conserva el hash del archivo original, sin alterar
su contenido. Permite volver a medir las potencias de las tablas:

```powershell
& '.\.venv\Scripts\python.exe' scripts/package_point03_terminal.py --output resultados/codex/terminal_review_new.json
```

La verificación realizada pasó7arrays y14observables, con discrepancias
<=1e-12. El comando requiere las dependencias fijadas; no instala nada.
No añadir `--build`: el paquete ya existe. Usar una salida nueva para
conservar registros anteriores.

También se conservan las entradas y geometría M1 y los90reportes de
tramo. Los campos intermedios adicionales permanecen localmente en D:.
Por ello, esta subida permite verificar los observables finales, pero
**no contiene todos los arrays necesarios para repetir la auditoría
completa de las90cadenas**. Los hashes no sustituyen esos datos crudos.

La auditoría completa se ejecutó localmente desde los90campos y verificó
los4primarios adicionales y20fuentes. Su independencia es del evaluador
original; comparte librerías y detector. No es replicación física externa.

## Próximo trabajo científico

Rediseñar el estudio espacial con posición de dominio, generación de malla
y muestreo controlados; mantener todos los casos negativos, congelar una
nueva predicción antes de datos nuevos y reservar controles de precisión.
No repetir la misma serie hasta conseguir una aprobación ni relajar M1.
El barrido modal y los hitos posteriores siguen pendientes. Los perfiles
medidos, fabricación y caracterización requieren datos externos reales.
