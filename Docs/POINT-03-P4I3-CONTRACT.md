# P4I3: refinar la referencia Radau conservando Padé

Registrar controlador, auditor y contrato antes de los nuevos campos.
P4I2 terminó en 7910,727 s, con sus 128 campos nuevos y los 224 retenidos
auditados: integridad aprobada. La cota de discrepancia del observable
de intensidad fue 1,169059e-5, superior al límite 1e-5. Su dictamen
temporal negativo permanece; no se modifica ni se vuelve a ejecutar.

Nuevo contraste motivado por ese fallo: conservar la trayectoria Padé6
de 32768 pasos de P4I2 y añadir sólo Radau5 de 65536 pasos, en la misma
malla P4C y con las mismas matrices, entrada, geometría, detector,
amortiguación, longitud de onda y propagación de 2 mm. Es un refinamiento
de referencia, no evidencia previa de que Padé o Radau sean el causante.
Si el nuevo contraste vuelve a fallar, guardar el rechazo sin relajarlo.

Radau emplea el trabajador P4I sin editarlo: 256 tramos de 256 pasos,
paso longitudinal 0,002/65536 m. Reutilizar todos los artefactos por hash.
Padé sigue siendo la primaria para un eventual estudio espacial;
Radau es contraste independiente de precisión. No renormalizar salidas
ni alinear fase. No repetir ningún tramo anterior válido.

Los mismos tres criterios simultáneos de P4I y P4I2:

- Diferencia relativa del campo en norma de masa ≤1e-4.
- Ambas diferencias de potencia ≤1e-6.
- Ambas cotas PSD locales de discrepancia observable ≤1e-5:
  (sqrt(a*Qa)+sqrt(b*Qb))*sqrt((a-b)*Q(a-b)).

Q es la matriz del campo cuadrático o los pesos de intensidad lineal.
Las cotas comparan soluciones calculadas y no demuestran un error
absoluto respecto de la solución continua. Guardar también la diferencia
Radau32768–Radau65536 como diagnóstico, sin convertirla en criterio
de orden retrospectivo ni seleccionar la comparación más favorable.

Un hilo, RAM disponible >3 GiB y disco libre >2 GiB. Cada hijo ≤360 s,
corte externo 370 s; presupuesto global 22000 s, fijado antes de campos
para el doble de pasos y factorizaciones de P4I2. Sin ampliarlo durante
el ensayo, reinicios automáticos ni simulaciones externas atribuidas.
Auditar los 256 campos nuevos y reauditar las cadenas retenidas antes
de aprobar precisión temporal en esta única malla.

P5C permanece sin empezar: su prerrequisito P4I2 es negativo. Un eventual
aprobado P4I3 requerirá registrar explícitamente la nueva dependencia de
P5C antes de sus campos; no se falseará la bandera de P4I2. Las mallas
gruesas preparadas y la reserva fina 0,28 se conservan sin propagación.
La tarea 1 actual (punto 3 histórico) continúa abierta. JEV fallback local.
