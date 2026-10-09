# M2-R1: malla intermedia completa y auditada localmente

M2-R1 completó los trece tramos pendientes y terminó dentro del presupuesto
original:13847,597305s<=22000s desde2026-10-08T22:55:32,662346UTC.
La auditoría remota y la recalculada en Windows aprueban la integridad de
los96campos y los cinco criterios temporales. No se repitieron los83
campos conservados ni se añadió espera por recursos.

| Criterio | Resultado local | Umbral | Dictamen |
|---|---:|---:|---|
| Diferencia relativa del campo en norma de masa | 1,1961462696e-5 | 1e-4 | Aprobado |
| Diferencia de potencia, detector de campo | 3,4854330533e-10 | 1e-6 | Aprobado |
| Diferencia de potencia, detector de intensidad | 4,1612246537e-8 | 1e-6 | Aprobado |
| Cota PSD, detector de campo | 4,4457901576e-6 | 1e-5 | Aprobado |
| Cota PSD, detector de intensidad | 8,7846713761e-6 | 1e-5 | Aprobado |

Potencias fraccionales respecto a la entrada normalizada:

- Padé32768:campo0,332923454652748;intensidad0,3325896943239196.
- Radau65536:campo0,33292345430420467;intensidad0,33258965271167307.

Se comprobaron los96camposcomplex128, finitud, fuentes, hashes, cadena,
pasos, potencias y recursos. Residuo máximo de potencia recalculada:0.
Las diferencias entre auditorías remota/local cumplen1e-12. El informe
remoto permanece intacto; el local se escribe como local_integrity_audit.json.
Esto establece consistencia temporal de dos soluciones discretas en esta
malla, no una cota del error continuo ni una medición física del dispositivo.

## Fallos y transporte conservados

M2 original sigue fallida por agotar900s de espera de memoria, con83campos.
Su execution.json conserva SHA-256
b3e68b02488949a3851d363318092720a84541e274fc753a48403ba41e5fec5c.
La recuperación registrada en626310e usó exactamente el trabajador y
manifiesto originales, manteniendo reserva>6GiB, guardia>3GiB, un hilo,
tiempos por hijo y presupuesto original. Los trece nuevos tramos se
calcularon en CPU estándar Colab; no hay carga GPU ni validación Maxwell.

ZIP final:9499714bytes/44archivos, SHA-256
671b34d6fd5b3b7f96f37f4e11c8a6666801baaad5aa942268922ddc8ed6b9bc.
La espera de la descarga del navegador falló y la descarga oficial no
produjo un archivo local accesible. El acceso al gestor interno de Chrome
fue rechazado por políticaHTTP/HTTPS; no se eludió esa protección.
Se recuperó el mismo ZIP mediante49bloques base64 visibles de sólo lectura
en el cuaderno HTTPS propio. La reconstrucción local reproduce bytes,
SHA-256 y CRC; no se altera ni se inventa ningún campo.

El importador verificó fuentes y fallos retenidos, extrajo a carpeta nueva
y adoptó exclusivamente44archivos ausentes. La auditoría local se ejecutó
después. El primer control de arranque del wrapper falló por una invocación
runpy sin ruta scripts; se corrigió la invocación y aprobó con la misma
fuente. No ejecutó campos ópticos ni alteró las auditorías.

## Continuación autorizada

F1h=0,35/K16 tiene ahora su prerrequisito local aprobado. Protocolo y
controles se publicaron en4f46e04 antes de campos. Paquete28archivos
verificado por SHA/CRC:14011045bytes, SHA-256
d79a777e2d5d1d955205c039aef95faae9c54efd38ca40fc3815828ad616368f.
Esta preparación no equivale a su ejecución. Se debe verificar publicación
del paquete y recursos reales antes de propagar.

S16 se registró en a1fa85d antes de F1 y antes de la malla reservada;
mantiene los criterios históricos con dependencias K16 explícitas. Todavía
no hay predicción S16, campos h=0,28 ni contraste de dominio.

La conservación actual vuelve a aprobar:333archivos principales/estadoGit
y603productos de E sin cambios. Tarea1/T96-Q4 abierta, tareas2–22 sin
iniciar en este ciclo. JEV fallback local por bloqueo remoto heredado.

Evidencia principal:

- point03_d16_mid_recovery_20261009/local_integrity_audit.json.
- point03_d16_mid_recovery_20261009/integrity_audit.json, remoto preservado.
- point03_m2_ui_transfer_20261009/receipt.json y ZIP reconstruido.
- point03_d16_mid_recovery_transport_20261009/receipt.json.
- point03_preservation_m2_completed_20261009.json.
