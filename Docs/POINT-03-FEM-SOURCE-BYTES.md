# Fuentes generadas y finales de línea

Las fuentes P4B/P4H generadas en Windows mantienen CRLF y los informes
registran hashes de esos bytes ejecutados. Git normalizó inicialmente a
LF; se comprobó identidad de texto tras convertir sólo CRLF→LF.
Se conserva el historial y se añade -text para publicar los bytes
efectivamente usados, sin editar archivos de trabajo ni repetir pruebas.

- P4B fuente ejecutada:831e35d874a42053cf62539004f4a042f9dad6f765253199636fab54bb343efc.
- P4H fuente ejecutada:558b39864234c4e00d732b2c7ee6310df68b4e78eb8ed41e3dd7ac35da2412c0.

El compromiso previo registra texto prospectivo equivalente, no identidad
de bytes con el blob normalizado. Las fuentes/hashes ejecutados y sus
resultados se conservan; no se reescribe el registro anterior. Archivos
generados dentro resultados/codex/point03_* ya retienen bytes por atributos.
