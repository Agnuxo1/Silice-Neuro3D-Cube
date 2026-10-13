# FEMTO-1 — ejecución autorizada, 13/10/2026

Guía original: D:/PROJECTS/.cognition/silice-femtoprint/GUIA-PROTOTIPO-FEMTOPRINT.md v1.1. La instrucción del titular autoriza los trabajos y el primer contacto para formatos/viabilidad. El envío final, pedido, pago y acuerdos siguen sujetos a la revisión F8 y aprobación expresa. Repositorio en rama codex/femto1-20261013; trabajos ajenos preservados.

F0: correo Gmail enviado a info@femtoprint.ch; hilo 1a134b2ae1501c9f. Nota conceptual y recibo en D:/PROJECTS/.cognition/silice-femtoprint. Se comunica estudio inicial/piloto con intención de proponer después colaboración de I+D para Cubos 3D Silice. Reglas reales pendientes.

JEV: consulta nueva de la tarea en 13/10/2026, exit_code=0, status=connected, provenance=jev, modelo jev-1.13.0. Recomienda prepare_and_validate (1.0). No es evidencia física. La conectividad actual sustituye solo para esta tarea el estado histórico del conector; no se reintentó una credencial inválida ni se eludió un bloqueo.

## Prerregistro y custodia

El kit se inspeccionó: --query-server sin --remote-ref deja published_at_commitment=null. Se requiere origin/codex/femto1-20261013 explícito, commit y lectura del servidor antes de entrenar. Los registros se publican en esa rama; main y las entregas ajenas no se modifican.

MNIST tiene uso exploratorio previo. Se usa una nueva división estratificada del train oficial, 60/20/20; un 20% del train se reserva para calibración. No se usa el test oficial, ya explorado. Los datos grandes y etiquetas selladas se guardan fuera de git en D:/PROJECTS/.cognition/femto1. Se publica el manifiesto/hash, no la sal de la custodia. Es una reserva procedural en el mismo equipo; no un custodio independiente ni datos históricamente inéditos.

## Aclaraciones prospectivas

- N3: las medias normalizadas originales se conservan. Para mantener tres hojas útiles y descarte se resta el mínimo común de cada columna y se aplica una escala global. La decisión no cambia. No se normaliza cada columna por separado.
- N4: árbol de cuatro hojas útiles, sin descarte; mapeo distinto del clasificador con cero estructural.
- La prueba sellada final de Blender se hace una vez, después de fijar la física y geometría. Antes solo controles sintéticos/train/validation. Esto evita repetir test sellado cuando F5 obliga a rehacer F3/F4.
- F5/F6 requieren perfil, polarización, banda y tolerancias reales. Una simulación escalar provisional no demuestra dos polarizaciones ni sustituye esas respuestas.
- N2 se presenta como variante de precompensación supuesta hasta medir K1.

## Dependencias y salidas

F1/F2: scripts/femto1/custodian.py, common.py y train.py; protocolo y resultados prospectivos. F3/F4: compilar rutas y controles en SI, Blender por cola y reserva; no abrir el test hasta pasar dependencias. F5: perfil confirmado, eigenmodos/LP11, solver independiente con refinamientos, acceso en S, lateral/vertical/profundidad, banda y dos polarizaciones. F6: 200 realizaciones, pérdidas/fuga/desalineación/codificación y potencia/ruido. F7: exportar/reimportar formatos confirmados y manifiesto. F8: revisión independiente y aprobación del titular. F9: cupones, caracterización de W, calibración y prueba de banco después de fabricar.

No se firma, etiqueta ni declara listo para fabricar un paquete que aún dependa de F0/F5. La licencia actual del repositorio es Apache-2.0 por decisión del titular; autoría, datos e IP de la futura colaboración siguen pendientes de acuerdo.
