# Conservación de campos parciales F1

El auditor nuevo `audit_point03_d16_fine_partial.py` permite comprobar un
prefijo explícito de campos completos si F1 termina con un fallo operativo.
Se ha preparado mientras F1 sigue activa, sin modificar sus fuentes,
matrices, manifiesto, criterios, campos ni presupuesto. No se ha ejecutado
sobre resultados T96. JEV: fallback local por el bloqueo remoto conservado.

Tras transportar todos los grupos y comprobar SHA/CRC, conservar el fallo
y auditar directamente la carpeta extraída, sin adoptarla como ejecución
completa. Contar los reportes consecutivos con estado completed; no incluir
un reporte fallido, un campo sin reporte o un salto en la cadena. Radau sólo
es válido después de los64campos Padé. Indicar ambos recuentos explícitos:

    python scripts/audit_point03_d16_fine_partial.py --out EXTRACTED_F1_FOLDER --pade-count N --radau-count M --output NEW_PARTIAL_AUDIT_JSON

Comprueba hashes de fuentes congeladas y K16,74049grados libres, cadenas,
tipo complex128, dimensión, finitud, potencia física en norma de masa,
pasos512, incrementos temporales originales y recursos del trabajador.
Registra el hash y estado de execution.json si existe, sin reescribirlo.
Cada dictamen se escribe de forma exclusiva en un archivo nuevo.

El resultado afirma sólo integridad del prefijo. No aprueba precisión
temporal, las reservas del controlador, el tiempo global ni el final antes
del límite absoluto. Los trabajadores no guardan una hora final en sus
reportes: se comprueban su hora inicial y duración declarada, sin inventar
una hora final. Las comprobaciones completas corresponden al auditor F1
original y a su repetición local, que siguen siendo obligatorios para un
resultado completo. Un aprobado parcial no autoriza S16 ni h=0,28.

Los controles manufacturados utilizan vectores de3componentes, masa
identidad y una amplitud decreciente conocida. Las65muestras permiten
verificar cadenas de ambas familias; no son campos ópticos propagados.
Se aprobaron18grupos de controles: una cadena válida y17grupos de rechazo
de hash/cadena/ruta, pasos, potencia, duración, RAM/disco, tiempo de inicio,
estado, recuentos, dimensión/tipo y valores no finitos. No se leyeron datos
T96. Recibo: point03_d16_fine_partial_controls_20261009.json.

Antes de una eventual recuperación, conservar y auditar los campos válidos
y registrar el nuevo controlador. No repetir campos, cambiar el trabajador
o reiniciar los32000s originales o la espera acumulada900s. El límite
absoluto13:45UTC prevalece. Este documento prepara conservación; no
autoriza ni ejecuta una recuperación y no cambia el contrato vigente.
