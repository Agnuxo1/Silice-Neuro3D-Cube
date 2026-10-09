# Ventana de investigación del 9 de octubre

El usuario autoriza hasta doce horas de trabajo autónomo y actualización de
la rama y PR existentes. Se adopta como límite conservador el 9 de octubre
a las 13:45 UTC (15:45, Europe/Madrid). El tiempo disponible no permite
declarar completos trabajos que necesitan fabricación, instrumentos,
datos medidos, revisión independiente o impacto posterior.

## Pregunta activa y orden

¿El caso escalar ideal T96/Q4 supera, con parámetros y criterios previamente
registrados, los controles temporales, la convergencia espacial, una
predicción de malla reservada y la sensibilidad al dominio?

Esta es la tarea 1 de las 22 indicadas por el usuario. Las tareas 2–22
permanecen pendientes hasta cerrar y documentar la primera. No se cambia
el perfil supuesto para buscar un aprobado ni se sustituye un detector.
Una consistencia entre soluciones discretas no establece validación física.

## Reanudación verificada

- Rama aislada: `codex/scientific-closure-20261006`; HEAD local y remoto
  `c9cf004ba33475989acb1580149883654f01fd84` al reanudar. PR 1 abierta,
  sin fusionar; metadatos consultados mediante el conector GitHub.
- M2 original comenzó a las 22:55:32,699189 UTC del 8 de octubre.
  Su límite de 22000 s y espera acumulada de 900 s siguen vigentes.
  La ventana de doce horas no reinicia ninguno de ellos.
- Últimos campos observados: Padé 32/32 y Radau 51/64, total 83/96.
  El proceso permanece activo esperando memoria; no se ha lanzado otro.
- Auditor independiente parcial: integridad de los 83 campos aprobada,
  25 fuentes congeladas comprobadas y residuo máximo de potencia 0.
  No hay dictamen temporal final ni auditoría de las reservas del
  controlador hasta obtener su registro de ejecución final.
- Preservación actual aprobada: 333 archivos versionados principales,
  estado Git principal y 603 productos originales de E. El alcance no
  incluye certificar todos los archivos no versionados del principal.
- JEV: `v2-doctor` ejecutado, exit 0, estado ready, provenance local.
  Sigue el bloqueo remoto heredado. No se ejecutan probe ni query para
  eludirlo; las decisiones son fallback local explícito.

## Secuencia siguiente

1. Conservar el límite y esperar el dictamen del controlador M2; no editar
   sus fuentes, matrices, manifiesto, umbrales ni campos.
2. Si completa, ejecutar `audit_point03_d16_mid_refined_time.py` antes de
   adoptar cualquier resultado. Si falla, conservar execution.json y
   auditar todos los campos válidos; una recuperación exige registro previo,
   mismos datos y presupuesto original, sin repetir campos calculados.
3. Sólo si M2 aprueba, registrar la propagación h=0,35 con K Duffy16.
   Los campos históricos K8 no sirven como campos K16. Después registrar
   el estudio espacial actualizado y la predicción antes de h=0,28.
4. Controlar el dominio con un protocolo anterior a sus campos. Cerrar
   la tarea 1 sólo si todos sus controles y auditorías necesarios aprueban.

Los fallos científicos siguen siendo resultados. No se amplían presupuestos
o criterios para forzar un aprobado. Al vencer un límite, documentar el
estado factual y la siguiente acción, sin declarar cerrado el proyecto.

## Herramientas y fuentes verificadas

Se reutiliza el entorno científico de D:, con NumPy 2.2.6, SciPy 1.15.1 y
psutil 6.1.1. Auditorías y cálculos se ejecutan directamente, sin subagentes.
No se inicia carga GPU ni Blender sin una reserva vigente y comprobada.

La consulta pública actual de [P2PCLAW](https://www.p2pclaw.com/lab)
redirige el lanzador al hub. No acredita un ejecutor óptico compatible ni
un trabajo completado. No se envió simulación a esa plataforma ni se
reintentaron credenciales bloqueadas. Un listado de herramientas no es
evidencia de su ejecución.

[NASA](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html)
explica el régimen asintótico y la necesidad de mantener la generación
de malla consistente. Se usa como referencia metodológica; no proporciona
una cota certificada para T96 ni valida estas mallas no anidadas.
[SciPy 1.15.1](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.sparse.linalg.expm_multiply.html)
documenta la acción de la exponencial matricial. Su disponibilidad no
certifica el coste ni el error del problema generalizado con masa FEM.

Estos controles son deterministas: no se inventan intervalos estadísticos,
réplicas independientes o medidas materiales a partir de repetir un cálculo.
La aspiración Nobel exige novedad, contribución importante, revisión e
impacto demostrados; ninguno de esos resultados queda garantizado por
la duración de esta ventana.

## Evidencia

- `resultados/codex/point03_preservation_resume_20261009.json`.
- `resultados/codex/point03_d16_mid_refined_time_20261008/partial83_integrity_audit_20261009.json`.
- `scripts/audit_point03_d16_mid_partial.py`.

Documento de reanudación; las actualizaciones posteriores se añaden al
checkpoint y a informes nuevos, sin sustituir registros históricos.

## Actualización de publicación solicitada por el usuario

El9deoctubre el usuario pidió publicar todoslos resultados en GitHubmain y añadirGIFprofesionales enREADME. Se autoriza esa integración revisada después de preparar y verificar artefactos/datos/QA, preservando el checkoutprincipal local. Sustituye la restricción de nofusionar para esta publicación; no modifica el límite13:45UTC, los presupuestos, las fuentes de ensayos activos ni el orden de tareas. La red completa/fabricación/validaciónfísica siguen pendientes.
