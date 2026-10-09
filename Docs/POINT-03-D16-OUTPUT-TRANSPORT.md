# Recuperación de evidencia sin modificarla

D16-C1 terminó7621,698s,64tramos válidos; auditoría remota de integridad
aprobada y precisión temporal negativa por cotaPSD de intensidad1,349108e-5.
La malla intermedia queda bloqueada por su requisito temporal previo.

La exportación produjo el ZIP científico con SHA256
154c97d008acb69c766cd4e802e932e42317f4b7a42e1b6cf985b0374e83064e.
La descarga automática y desde el panel de archivos no han entregado
todavía una ruta local verificable. Una petición de visitar la página
interna chrome://downloads fue rechazada por política del navegador.
No se utilizan otras superficies para acceder a esa página ni a su historial.

Alternativa limitada a los datos de este ensayo: leer ese ZIP inmutable
mediante una celda del cuaderno HTTPS autorizado, imprimir bloques64KiB
en base64, recuperar únicamente esa salida visible, reconstruir el archivo
local y comprobar SHA256/CRC antes de extraer y auditar. No accede al
estado interno del navegador, no cambia permisos ni crea un servicio remoto.
La función sólo permite leer ese archivo, con índices acotados y tamaño fijo.
No modifica los campos, informes, resultados negativos ni fuentes numéricas.
La recuperación no convierte la evaluación negativa en un aprobado.

Resultado: transporte verificado inicialmente con7bloques64KiB; después
rangos dehasta512KiB comprobados por índice/tamaño antes de guardarlos.
Se reconstruyeron30429527bytes; SHA256 exacto y CRC aprobados. Se
recuperaron198archivos y se auditó localmente el mismo resultado negativo.
La adaptación del tamaño sólo cambia el transporte, no los datos ni
ninguna decisión numérica del ensayo.
