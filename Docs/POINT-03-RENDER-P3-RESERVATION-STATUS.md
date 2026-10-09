# Actualización tras las reservas inmediatas: R3 completada

El 9 de octubre, a las 12:00–12:01 UTC, FIFO libre y RAM suficiente permitieron
las dos solicitudes inmediatas registradas. Cada backend ejecutó 84 campos,
con cierre normal y auditoría local de integridad y precisión aprobadas.
No se añadieron esperas de polling al presupuesto agotado; no repetir estos
campos. [Resultado y costes](POINT-03-RENDER-P3-ANALYTIC-RESULTS.md).

El registro previo siguiente conserva los dos bloqueos originales y la
política de adquisición anterior a los campos. No se borra su historia.

# Registro previo (11:09 UTC): reserva no obtenida; sin campos

Las dos solicitudes FIFO de un minuto finalizaron por timeout con otro
turno ocupado. No se crearon carpetas run01 ni se lanzó Blender en R3.
Perfiles y once fuentes permanecen por hash como en ce183e71. Los logs
completos y auditoría de ausencia de productos se conservan; no se atribuye
un fallo físico o de precisión a este bloqueo de reserva.

Para continuar, comprobar disponibilidad real y hacer sólo una solicitud
inmediata, sin añadir otra espera al minuto agotado por backend. La cola
compartida no se modifica. Su parámetro --max-wait 0 significa sin límite:
NO usarlo. Un valor positivo --max-wait 0.000001 (60 microsegundos) permite
la primera evaluación FIFO/recurso, que concede si está lista y termina
si está ocupada, antes de otra espera de polling. No rebaja ningún gate
RAM/VRAM/temperatura ni interrumpe turnos ajenos. Registrar cada respuesta
en un log nuevo, y nunca repetir un backend cuyos 84 campos ya existan.

Usar guard/profile/commit originales publicados, carpeta exclusiva sin
campos anteriores, mismo child120/timer115/worker110 y deadline13:45UTC.
Si el supervisor completa: audit_point03_render_p3_analytic.py --out carpeta.
Adoptar exclusivamente después de auditoría local; conservar todo negativo.
Publicar crudos, auditorías, costes y README factual. No T96/red/física.

F1 no aparece en el almacenamiento reasignado. Dos búsquedas acotadas en
el conector Drive devolvieron cero resultados accesibles; esto no acredita
ausencia en todos los Drive ni sustituye el dictamen final de F1. La consulta
al usuario sobre una copia descargada sigue pendiente. No reejecutar F1,
reiniciar presupuesto ni iniciar S16 sin su auditoría local aprobada.
