# Bytes de la fuente M1 y publicación Git

Revisión efectuada durante M1, sin editar el controlador ni relanzar óptica.
Los 20 archivos del manifiesto mantienen sus hashes de trabajo. De los
16 ya comprometidos, 15 coinciden byte por byte con Git. El controlador
M1 conserva CRLF en disco, mientras Git normalizó su blob a LF:

- Fuente de trabajo: `cba2162a6955ecea5dcbb05b8989301108e22f4f713df9d9168df0a5eac0c208`.
- Blob publicado inicialmente: `6c37c26ad2645f462266b0d257d56aaae0953fd13fb7b7e2944b81a65e8daf67`.
- Diferencia comprobada: únicamente 158 finales de línea CRLF frente a LF;
  al normalizar esos finales los contenidos son iguales.

Se añade una excepción `-text` para esa fuente en `.gitattributes` y se
comprometen sus bytes originales, sin cambiar el archivo de trabajo.
Así una futura descarga puede conservar el hash del manifiesto.
No se reescribe el historial: el compromiso anterior registra el texto
normalizado, y el preflight y manifiesto prospectivos registran el hash
exacto de los bytes efectivamente ejecutados. No afirmar identidad de
bytes entre aquel blob Git y la fuente original.

Las cuatro fuentes/evidencias geométricas generadas que todavía no estaban
en Git se conservarán al publicar el resultado final. Los arrays y todos
los tramos crudos requieren disponibilidad adicional para reproducir la
auditoría completa; un hash remoto no sustituye al archivo que identifica.
Los criterios científicos y el presupuesto de M1 permanecen congelados.
