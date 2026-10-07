# Ejecución condicionada de la prueba nueva K626

Fuente preparada durante H2, sin crear entradas N626 ni propagar. Sólo
ejecutar tras H2 completo/auditado, K640PASS en ambos métodos, y H2 sin
cierre propio. El contrato K y las predicciones e611a23 permanecen intactos.

Geometría: reutilizar función prepare640 de G sin modificar su fuente;
adaptar AST sólo nombre de función, N640→626 y dos nombres de archivos.
Exigir cuatro cambios exactos, mismos 48 controles y cierres de área/entrada.
Guardar AST adaptado antes de su ejecución. Ningún parámetro físico cambia.
Primer preflight del adaptador falló al visitar una función anidada; fuente
y error retenidos. Corrección anterior a cualquier geometría/propagación:
renombrar sólo la función exterior y exigir cuatro cambios exactos. Run2PASS.

Fuente/inputs/reportes/predicciones se congelan en manifiesto antes de
primer hijo. Worker H original inmutable, particiones11/17, CPUunhilo,
RAM>1.5GiB/disco>2GiB,7200s totales,360s por hijo/hardtimeout370.
Conservar todos los fallos/checkpoints; no recuperación automática.

Auditar28checkpoints completos, hashes, shapes/dtypes/finite, potencia
bruta y no incremento de norma por el operador disipativo, encadenado
y cronología posterior a las predicciones congeladas. Campo relativo
R11/R17<=1e-9; diferencia de potencia en ambos detectores<=1e-10;
cuadratura16/32<=1e-10. No alineación ni normalización de salida.

Predicciones campo0.3327881552636028/intensidad0.3328526391824184,
calculadas sólo desdeN320/400/500. Residual<=0.1|P626-P500| en ambos,
sin refit usandoN640. Presupuesto K640 yaPASS sigue obligatorio.
Todos los criterios y controles son necesarios para cierre local del
observable fijado T96/2mm/128um. No cierre de campo/fase/frontera/Maxwell
ni fabricación; no sustituir FAIL E/G/H por una nueva etiqueta retroactiva.
