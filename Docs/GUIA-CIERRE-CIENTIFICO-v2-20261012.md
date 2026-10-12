# Guía completa de cierre científico y presentación de Silice-Neuro3D-Cube

**Destinatario:** agente encargado de ejecutar, verificar y documentar el trabajo pendiente.  
**Titular:** Francisco Angulo de Lafuente.  
**Fecha de la revisión:** 12 de octubre de 2026.  
**Idioma de las instrucciones:** español. **Código, comentarios y mensajes nuevos:** inglés.

> **Versión 2 — revisión ampliada del 12 de octubre de 2026.** Este documento conserva íntegro el texto de la versión 1 (secciones 0–36) y todo su código byte a byte. Añade notas **«Adición v2»** dentro de las secciones afectadas y una **Parte II (secciones 37–51)** con verificaciones, erratas, nuevas tareas T23–T30, nuevas herramientas y un kit v2 probado. Cuando una nota v2 corrige o precisa el texto v1, prevalece la nota v2; el texto v1 se mantiene por trazabilidad. Ninguna adición convierte un modelo en medida ni declara resultados físicos.
>
> Resumen verificable de la revisión (detalle en §37 y §47):
> - Los tres commits de §1 coinciden con `git ls-remote` del 12-10-2026. Existe además la rama `codex/scientific-closure-20261006`, ya contenida en `main`.
> - El kit v1 se extrajo con su propio extractor y sus 32 pruebas pasan en Python 3.13.16 (Linux) con dos conjuntos de dependencias, incluido el fijado en `agentkit/requirements.txt`.
> - De 23 rutas del repositorio citadas, 21 existen tal como se citan (6 sólo en la rama de auditoría) y 2 aparecen abreviadas; §47 da las rutas completas.
> - Se encontró y demostró un fallo de integridad en `agentkit.evidence.evaluate_receipt` y un conflicto con la propiedad de `tests/` definida en `AGENTS.md`. Ambos se resuelven sin modificar el código v1.
> - El ejemplo de entrenamiento de §16 (`unitary_mzm`) no satisface su propio criterio de convergencia en ninguno de los ocho arranques; el modelo de campo con signo de §44 converge en los ocho.
> - Se comprobaron 27 referencias bibliográficas contra Crossref, arXiv o Europe PMC; §46 lista los metadatos verificados y §47 las correcciones.
> - Un revisor adversarial independiente auditó todo el material v2 antes de esta entrega y encontró 23 problemas en el borrador v2, ninguno en el texto v1 conservado. Todos se corrigieron y se volvieron a comprobar con sus propios scripts de ataque (§47, E17–E30).

## 0. Objetivo y significado del cierre

Llevar el proyecto hasta el máximo nivel de validación que permitan la evidencia, los recursos y la fabricación disponibles. Cada afirmación debe tener un modelo definido, una prueba pertinente, datos conservados y un alcance explícito. El resultado puede ser positivo, negativo o inconcluso. Una hipótesis refutada se conserva y explica; no se convierte en éxito cambiando su umbral.

Esta guía incluye un kit ejecutable completo, con herramientas de evidencia, checkpoints, referencias numéricas, entrenamiento, síntesis de transformaciones pasivas, metrología y pruebas. El kit complementa los solvers existentes. Las funciones incluidas están implementadas; los trabajos de investigación que el agente debe desarrollar se especifican por tareas. **El kit no es una implementación completa del dispositivo, del solver electromagnético vectorial 3D ni del proceso de fabricación.** Esos resultados requieren el trabajo indicado y, cuando corresponda, muestras e instrumentos. Ningún código puede sustituir medidas que no existen.

La calidad «Premio Nobel» no es un criterio de aceptación verificable de software. El objetivo operativo es una contribución científica original, falsable, reproducible y presentada con rigor. El premio, la recepción por la comunidad y el impacto futuro no se pueden garantizar.

> **Adición v2.** §38 traduce esa aspiración a propiedades observables de las contribuciones que la comunidad ha reconocido al máximo nivel y propone una ruta para perseguirlas sin autoengaño. La conclusión de v1 se mantiene: el premio no se puede planificar ni garantizar; sí se pueden maximizar la importancia de la pregunta, la solidez de la evidencia y la facilidad de replicación.

### Tres productos finales posibles

1. **Publicación numérica:** modelos y resultados validados en su dominio de validez, con limitaciones y negativos. Puede terminarse aunque la fabricación siga abierta.
2. **Demostrador físico:** componentes y una red pequeña fabricados, caracterizados e integrados, con una tarea reservada.
3. **Validación e impacto externos:** reproducción por otro equipo, revisión científica y resultados posteriores de terceros. Requieren participación y tiempo externos.

No anunciar el producto 2 cuando sólo se ha completado el 1. Mantener estados separados para software, modelo, componente físico, sistema completo y reproducción externa.

## 1. Versiones revisadas y fuentes que gobiernan el trabajo

| Fuente | Revisión consultada |
|---|---|
| `Agnuxo1/Silice-Neuro3D-Cube`, `main` | `309d705e873448e4e05f2efbbc0dcc98613e9e68` |
| Rama `auditoria-20261009` | `c9b76d43c4f707d0b0754b77b0de5363426075e9` |
| `openai/math`, `main` | `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` |

> **Adición v2 (verificado con `git ls-remote` el 12-10-2026).** Los tres hashes coinciden. La rama remota `codex/scientific-closure-20261006` (`b344dcf`) no figura en la tabla, pero es antecesora de `main`; la PR #1 (`03b5f55`) también está fusionada en `main`. Hay que revisarlas sólo como historia, no como trabajo pendiente.
>
> `AGENTS.md` de `main` fija propiedad de rutas: Codex es propietario de `src/silice/`, `tests/` y `scripts/`; Claude, de `experimentos/glass_min1/`. Prohíbe sobrescribir o preparar para commit archivos de otro contribuidor sin revisarlos, e instalar, publicar o fusionar como pasos incidentales. Exige `provenance=jev` para el consejo remoto de JEV. Estas reglas prevalecen sobre cualquier comando de esta guía.

Releer las instrucciones y el estado de la copia real antes de ejecutar. Si los commits actuales han avanzado, revisar el diff y actualizar un informe de procedencia; no tratar esta fotografía como el estado de una versión futura.

Leer en este orden:

1. `AGENTS.md`.
2. `coordinacion/CHECKPOINT.md`: entradas actuales y la entrada específica de cada ensayo; no usar como orden una anotación histórica.
3. `Docs/RESEARCH-CONTRACT.md` y `Docs/CPU-REPRODUCTION.md`.
4. `Docs/ESTADO-ACTUAL.md` y `Docs/PROJECT-STATUS.md`, conservando sus fechas.
5. En la rama de auditoría: `Docs/CORRECCION-ESTADOS-20261011.md`, `Docs/RESULTADOS-BPM-B5-20261011.md`, `Docs/T12-CIERRE-Y-BLOQUEADOS-20261011.md` y `Docs/NOVEDAD-ESTADO-20261011.md`.
6. El contrato, los datos y el auditor de la tarea que se vaya a ejecutar.

> **Adición v2.** Varios documentos citados en esta guía (§11, §24) o en las adiciones v2 sólo existen en `origin/auditoria-20261009`: `Docs/CONTRIBUCION-CENTRAL-T20.md`, `experimentos/acoplador_claude/g3_bpm_p2.py`, `experimentos/compilador_claude/RESULTADOS-COMPILADOR.md`, `Docs/PLAN-FINAL-20261011.md` y `Docs/PROTOCOLOS-BLOQUEADOS-22-TAREAS.md`. Leerlos sin cambiar de rama con `git show origin/auditoria-20261009:<ruta>`.

Los informes de estado no sustituyen sus datos crudos. Una frase «hecho» tampoco prevalece sobre una corrección posterior que declara un fallo. Integrar los avances de la rama de auditoría sólo después de revisar el diff, las pruebas y los archivos de otros contribuidores. No fusionar automáticamente toda la rama.

## 2. Reglas de trabajo para el agente

- Trabajar en una copia o worktree aislado, manteniendo el repositorio principal y los otros proyectos intactos.
- Priorizar `D:\PROJECTS` y `E:\Proyecto-concursos`. No descargar paquetes, repositorios voluminosos ni resultados en C:.
- Empezar con CPU y un hilo. GPU o Blender requieren una autorización vigente y la reserva exclusiva que exija el entorno real. Las ventanas de octubre anteriores están vencidas; no reutilizar sus permisos ni prolongar sus presupuestos.
- Preservar contratos, fuentes, matrices, checkpoints, negativos y hashes históricos. Escribir nuevas ejecuciones y nuevas auditorías en rutas nuevas.
- No normalizar salidas para hacer pasar balances; no alinear la fase global para aprobar una comparación que exige fase absoluta.
- Declarar unidades SI. Las fracciones de potencia de un modelo no son vatios medidos. Un tiempo CUDA no es la latencia de un procesador óptico.
- Separar semántica física y representación gráfica. La rasterización R3 validó representación y suma de campos manufacturados; no validó propagación guiada ni una red completa.
- Conservar la distinción entre índice ideal, dato bibliográfico, ficha de fabricante y perfil medido de la muestra concreta.
- El bloqueo de JEV documentado no debe eludirse. Usar un fallback local explícito; no atribuir consejo a JEV sin procedencia verificable.
- Utilizar herramientas y agentes disponibles dentro de las instrucciones reales de la sesión. La independencia física requiere otro equipo; una segunda respuesta de IA no la acredita.
- Si aparece un bloqueo material, documentar exactamente el recurso o dato ausente y preparar su protocolo. Continuar los trabajos independientes. No inventar el dato ni marcar la tarea como aprobada.
- Una publicación, una licencia, una comunicación externa o una compra deben respetar la autorización de la sesión donde se ejecuten. Esta guía entrega instrucciones; no publica cambios ni contacta a terceros.

> **Adición v2 (§47 E4).** La extracción v1 crea `tests/test_agentkit.py` dentro de `tests/`, directorio propiedad de Codex. Además, `scripts/check.py` descubre todos los `test*.py` de `tests/`; ese archivo cambiaría el recuento de la suite CPU (51 pruebas en el último registro) y la CI, que sólo instala NumPy, SciPy y psutil desde `requirements/cpu-*-py313.lock`. Un worktree del repositorio también contiene `tests/`, así que extraer allí no evita el problema. Regla v2: extraer el kit **fuera del repositorio**, en un directorio hermano (por ejemplo `D:\SiliceAgentkit`), y ejecutar allí sus pruebas. En el repositorio sólo se incorporan los módulos `agentkit/` tras coordinarlo; `tests/test_agentkit.py` sólo entra con revisión de Codex. Las pruebas nuevas de v2 viven en `agentkit/test_v2.py` y no alteran `scripts/check.py`. Crear un entorno auxiliar (§3.2) es una instalación explícita que requiere autorización vigente; no es un paso incidental.

### Estados obligatorios

| Estado | Uso |
|---|---|
| OPEN | Falta evidencia o un protocolo ejecutable. |
| RUNNING | Hay una ejecución identificada y verificable. |
| PARTIAL | Hay resultados útiles pero no todos los criterios se han evaluado o cumplido. |
| FAIL | Un criterio registrado no se cumple; conservar el resultado. |
| BLOCKED | Falta un dato, instrumento, permiso vigente o participante externo. |
| PASS | Todos los criterios obligatorios de esa afirmación y ese alcance están aprobados. |

PASS se refiere a una afirmación concreta. No se propaga automáticamente desde una prueba de software al experimento, ni desde un componente al sistema.

## 3. Preparación e instalación reproducible

### 3.1. Inspección y aislamiento en Windows

Estos comandos son para el agente, no para que Fran tenga que adaptar el programa. Resolver las rutas reales y comprobar espacio antes de crear la copia.

```powershell
Set-Location 'D:\PROJECTS\Silice-Neuro3D-Cube'
git status --short
git worktree list
git fetch origin
git rev-parse origin/main
git rev-parse origin/auditoria-20261009
git log --oneline origin/main..origin/auditoria-20261009
git diff --stat origin/main...origin/auditoria-20261009
git worktree add -b agent/scientific-closure-20261012 'D:\PROJECTS\Silice-Neuro3D-Cube-closure-20261012' origin/main
Set-Location 'D:\PROJECTS\Silice-Neuro3D-Cube-closure-20261012'
```

Si el nombre ya existe, inspeccionar esa copia y elegir un nombre nuevo; no borrar trabajo. Revisar la rama de auditoría por grupos: correcciones documentales, solvers, experimentos, datos y soporte. Reutilizar sólo evidencias cuyos hashes y alcance se hayan comprobado.

### 3.2. Entorno del proyecto y entorno auxiliar

Reproducir primero el entorno documentado en `Docs/CPU-REPRODUCTION.md` y ejecutar `scripts/check.py`. La CI revisada tenía 51 pruebas CPU y 8 vectoriales aprobadas en Windows y Ubuntu, pero eso no certifica todos los experimentos.

El kit puede usar el entorno compatible del proyecto. Si se necesita un entorno separado, crearlo en D:. Ejecutar la instalación después de extraer el código según 3.3. Las versiones de `agentkit/requirements.txt` son propuestas fijadas para una reproducción con Python 3.13; **esta entrega se probó en Linux con Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 y scikit-learn 1.8.0**. El agente debe verificar también el conjunto fijado, sin cambiar el entorno histórico.

```powershell
py -3.13 -m venv .venv-closure
& '.\.venv-closure\Scripts\python.exe' -m pip install -r agentkit/requirements.txt
$env:OMP_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:NUMEXPR_NUM_THREADS = '1'
& '.\.venv-closure\Scripts\python.exe' -B -m unittest discover -s tests -p 'test_agentkit.py' -v
```

Registrar versión de Python, SO, CPU, paquetes, bibliotecas BLAS y los hashes de ruedas descargadas. Convertir la propuesta en un lock con hashes para la plataforma real. No afirmar reproducción bit a bit sólo por fijar versiones. No instalar PyTorch ni Blender para ejecutar las herramientas CPU de esta guía.

> **Adición v2 (verificado).** El conjunto fijado de `agentkit/requirements.txt` (NumPy 2.2.6, SciPy 1.15.1, scikit-learn 1.6.1, Matplotlib 3.10.0) se instaló en un entorno nuevo de Python 3.13.16 en Linux, y las 32 pruebas v1 y las 25 v2 pasaron. También pasaron con NumPy 2.5.3, SciPy 1.18.1, scikit-learn 1.9.1 y Matplotlib 3.11.2. El repositorio ya mantiene locks con hashes para NumPy, SciPy y psutil (`requirements/cpu-linux-py313.lock`, `requirements/cpu-win-py313.lock`). La CI los usa. `AGENTS.md` no les asigna propietario, así que conviene coordinar con Codex antes de editarlos. Para scikit-learn y Matplotlib, crear un lock separado del kit con hashes. Falta verificar Windows.

### 3.3. Extracción automática del código

La sección de código contiene archivos completos identificados por `file=`. El agente debe materializar el primer archivo, `extract_agentkit.py`, exactamente como aparece y copiar esta guía al worktree. Después:

```powershell
& '.\.venv-closure\Scripts\python.exe' -B extract_agentkit.py --guide Guia_completa_Silice_Neuro3D_Cube_2026-10-12.md --destination .
```

Si todavía no existe el entorno auxiliar, usar el intérprete de Python disponible para esta extracción: sólo emplea la biblioteca estándar. Luego instalar las dependencias. El extractor rechaza rutas inseguras y archivos existentes diferentes. No sobrescribe los solvers históricos.

> **Adición v2.** Para esta versión, el argumento `--guide` debe nombrar el archivo v2 (`Guia_completa_Silice_Neuro3D_Cube_v2_2026-10-12.md`); con el nombre v1 no se extraen los archivos nuevos. El destino debe estar fuera del repositorio (nota de §2). Los archivos nuevos están todos bajo `agentkit/` y los bloques v1 no cambian, así que el mismo `extract_agentkit.py` sirve. En un directorio donde ya se extrajo v1, omite los archivos idénticos y crea sólo los nuevos. Pruebas v2: `python -B -m unittest agentkit.test_v2 -v` (29 pruebas).

## 4. Inventario de tareas y orden de ejecución

El orden de la tabla corresponde al plan de 22 tareas. Preparar métodos y protocolos independientes mientras se resuelve un bloqueo es válido; un cierre dependiente debe esperar su evidencia.

| ID | Pendiente y alcance | Estado de partida |
|---|---|---|
| T01 | T96/Q4, recuperación F1, convergencia y dominio | Abierto; F1 final no recuperada. |
| T02 | Barrido modal y casos sin selección | Barrido ampliado con enmienda; revisar sus límites y afirmaciones. |
| T03 | Frontera, dominio, campo complejo y fase | Parcial; nuevos controles de vacío no cierran la validación guiada. |
| T04 | Descomposición modal e interferencias | Biortogonalidad demostrada en casos sintéticos; aplicación física pendiente. |
| T05 | Material, índices y geometrías medidos | Presupuesto ideal; mediciones pendientes. |
| T06 | Contraste vectorial y polarización | Solvers de capas y pilotos; contraste independiente completo pendiente. |
| T07 | Acoplador coherente GLASS-006b | Fallos históricos y contraste BPM/modal pendientes. |
| T08 | Curvas, cruces y conexiones 3D | Pilotos y negativos; envolvente completa pendiente. |
| T09 | Escritura profunda y registro entre caras | Protocolo; fabricación/metrología pendientes. |
| T10 | Estabilidad y control de fase | Parcial: H10b falló; parámetros no medidos. |
| T11 | Compilador de red a geometría | Parcial: C2 falló y C3 aprobó 28/36 realizaciones. |
| T12 | Neurona y red funcional | F3-b negativo bajo su contrato; nueva validación necesaria. |
| T13 | Muestras y red pequeña fabricadas | Bloqueado por fabricación. |
| T14 | Medidas ópticas calibradas | Bloqueado por muestras e instrumentos. |
| T15 | Integración óptica, electrónica y control | Pendiente de hardware. |
| T16 | Tarea independiente y comparación | Parcial; dataset y referencias históricas requieren tratamiento correcto. |
| T17 | Rendimiento y consumo completos | Sin medidas del sistema. |
| T18 | Escalabilidad y variación entre dispositivos | CI parcial; repetibilidad física pendiente. |
| T19 | Novedad frente a antecedentes | Ninguna aportación original establecida. |
| T20 | Contribución central y prueba decisiva | Hipótesis y protocolo; datos decisivos pendientes. |
| T21 | Reproducción y revisión externas | Requiere otro equipo y revisión científica. |
| T22 | Impacto sostenido | Se observará posteriormente; no puede fabricarse en una sesión. |

> **Adición v2.** §48 añade T23–T30 (infraestructura de integridad, pruebas de descarte por límites fundamentales y por escalado 3D, revisión del estado del arte, entrenamiento con hardware en el lazo, acceso a fabricación, decisión de propiedad intelectual y revisión adversarial) y propone un orden que adelanta las pruebas de descarte.

### Entregable mínimo por tarea

Un contrato anterior a nuevos datos; fuentes y parámetros identificados; entradas y salidas por hash; resultados de todos los casos; auditor independiente del evaluador; tabla de criterios; límites y negativos; comandos de reproducción; recibo de recursos; estado y próxima acción concreta.

Las herramientas `agentkit.evidence` registran bytes y comprueban criterios. **No prueban por sí solas que el protocolo precediera a los datos:** conservar también el commit publicado antes del cálculo, las dependencias y el registro de ejecución. No importar un resultado retrospectivo como prospectivo.

> **Adición v2 (§41.1).** `agentkit.prereg` reduce esta brecha: exige que protocolo y fuentes estén versionados y sin cambios y que el protocolo declare sus artefactos; audita contra el protocolo leído del objeto git, no contra la copia del recibo; detecta en el historial otras versiones del protocolo con el mismo `experiment_id`; y puede volver a comprobar en el servidor que el commit está publicado. No puede detectar un protocolo que se committea por primera vez después de producir los datos. Para eso hacen falta una marca de tiempo externa y la custodia de datos (§41).

## 5. T01 — cerrar T96/Q4 sin mezclar formulaciones

### 5.1. Recuperar la evidencia ya existente

El ensayo E fue recuperado con ocho trayectorias y controles; conservó un resultado científico negativo. No relanzarlo como si siguiera perdido. Inspeccionar `Docs/POINT-03-Q4-REFINEMENT-RESULTS.md` y las auditorías posteriores.

F1 es diferente: a la revisión, no había copia final recuperada. Buscar primero los archivos y paquetes ya producidos en las rutas documentadas y copias autorizadas. No asumir que una sesión de Colab aún conserva el entorno. No usar contraseñas ni evadir restricciones de acceso.

Si aparecen paquetes completos, utilizar las herramientas originales después de revisar sus argumentos:

```powershell
& '.\.venv\Scripts\python.exe' scripts/import_point03_d16_fine.py --export-manifest resultados/agent/f1_export_manifest.json --archives resultados/agent/f1_archives --out resultados/agent/f1_transport_new
& '.\.venv\Scripts\python.exe' scripts/audit_point03_d16_fine_local.py --out resultados/codex/point03_d16_fine_time_20261009
```

Las rutas del manifiesto y archivos deben resolverse a archivos recuperados reales antes de ejecutar. No generar un manifiesto ficticio. El segundo comando es la interfaz histórica: verificar que su carpeta sea la adoptada por el importador y conservar auditorías previas sin sobrescribir. Si sólo hay un prefijo válido, aplicar `audit_point03_d16_fine_partial.py` con sus recuentos reales. Un prefijo aprobado acredita integridad, no F1 completa.

> **Adición v2 (§47 E1).** Ruta completa: `scripts/audit_point03_d16_fine_partial.py`. Existe también `scripts/check_point03_d16_fine_partial.py`; leer los argumentos de ambos antes de elegir.

Si F1 no es recuperable, registrar la pérdida operacional, los últimos recuentos verificables y las búsquedas realizadas. Un ensayo sustitutivo necesita **nuevo identificador, protocolo y presupuesto vigente**. No reinicia ni continúa retroactivamente la ventana terminada el 9 de octubre.

### 5.2. Mantener el contrato D16

No confundir D16/K16 con el ADI 2D de GLASS-009d, ni usar campos K8 como K16. F1 fijó:

- h = 0,35 µm; longitud 2 mm; dominio ±64 µm; λ = 1550 nm; n₀ = 1,444; contraste deprimido 0,003.
- Padé[3/3], 32768 pasos, como primaria; Radau[2/3], 65536 pasos, como contraste.
- Tramos de 512 pasos: 64 Padé y 128 Radau, 192 campos.
- Error relativo de campo en norma de masa ≤ 10⁻⁴.
- Diferencias de ambos observables de potencia ≤ 10⁻⁶.
- Indicadores de discrepancia de ambos operadores PSD ≤ 10⁻⁵.
- Matriz K16 identificada en el contrato por SHA-256, sin regeneración silenciosa.

Auditar cadenas, dimensiones, complex128, unidades, fuentes, matriz, detector, tiempos, recursos y los cinco criterios. No adoptar sólo un detector favorable. Preservar la procedencia de cada caso.

### 5.3. Serie espacial S16 y predicción reservada

Reutilizar los evaluadores registrados si siguen íntegros:

- `scripts/forecast_point03_s16.py`.
- `scripts/audit_point03_s16_forecast.py`.
- `Docs/POINT-03-D16-SPATIAL-CONTRACT.md`.
- `Docs/POINT-03-S16-EXECUTION-CONTRACT.md`.

La serie es h = 0,546875 / 0,4375 / 0,35 / 0,28 µm, razón r = 1,25. Las tres primarias necesitan sus auditorías temporales locales aprobadas. Para cada observable, con incrementos Δ₀₁ y Δ₁₂:

$$
p=\frac{\log(\Delta_{01}/\Delta_{12})}{\log r},\qquad
P_{3,\mathrm{pred}}=P_2+\Delta_{12}/r^p.
$$

Los incrementos deben ser finitos, no nulos, del mismo signo, con 0,5 ≤ p ≤ 6 y cada uno mayor que 20 veces su discrepancia temporal máxima. Registrar la predicción antes de generar la malla reservada. Si falla cualquier observable, conservar el negativo y detener esa predicción; no sustituir la terna.

En la reserva, exigir los criterios originales: signo, orden, consistencia de orden ≤ 20 %, residual de predicción ≤ 10 % del incremento, separación temporal y presupuesto combinado ≤ 10⁻³ y ≤ 1 % de la potencia fina. Conservar todos los términos. Ese presupuesto es un **indicador numérico**, no una cota rigurosa continua ni un IC95.

El kit incluye `spatial_forecast` y `spatial_holdout` como controles independientes escalares. Se probaron con leyes conocidas y casos negativos. No sustituyen la auditoría de campos D16.

### 5.4. Dominio y cierre

Prerregistrar un estudio que conserve h físico, perfil, entrada y región de observación, y aumente el dominio. Comparar campo complejo, fase y ambos detectores; separar efecto de discretización, retorno y truncamiento. Cambiar dominio y h simultáneamente no aísla una causa.

La auditoría ADI de `RESULTADOS-T96-Q4-AUDITORIA.md` aprobó su nuevo Q5 y su comparación de dominio, pero retuvo el Q4 histórico y no cerró D16. Reutilizarla como evidencia acotada.

> **Adición v2 (§47 E2).** Ruta completa: `experimentos/glass009d_claude/RESULTADOS-T96-Q4-AUDITORIA.md` (presente en `main` y en la rama de auditoría).

**Cierre T01:** recuperación o declaración operacional completa; integridad; criterios temporales y espaciales; reserva prospectiva; dominio; error y alcance publicados. El éxito de un solo par fino de BPM no cierra este punto.

## 6. T02 — barrido modal completo y selección justificada

Revisar `experimentos/glass006a_claude/RESULTADOS-BARRIDO-MODAL.md` y todos los casos conservados. El barrido ampliado da 18 casos seleccionados y dos sin selección; una búsqueda que no devuelve modo no demuestra ausencia física.

1. Enumerar las 20 geometrías, mallas, ventana, condición de contorno y todos los candidatos retenidos.
2. Recalcular residuales relativos adimensionales y contrastarlos con el residuo absoluto original, manteniendo la enmienda visible.
3. Seguir modos entre mallas usando solape en norma física, n_eff complejo, localización y continuidad de ramas. No elegir sólo el autovalor favorable.
4. Con fuga o no normalidad, calcular modos adjuntos, condición de autovalor y sensibilidad al contorno. Cerca de degeneración, seguir subespacios mediante Schur o valores singulares.
5. Comprobar las pérdidas imaginarias y sus signos con un caso analítico. Evitar el valor absoluto como corrección de un signo incorrecto.
6. Para los dos casos sin selección, ampliar búsqueda y comprobar que el criterio de confinamiento no excluya arbitrariamente una resonancia útil. Si no se establece ausencia, publicar «ningún candidato pasó esta regla».
7. Reconciliar contradicciones entre tablas y comentarios de confinamiento: conservar los números crudos y corregir sólo su interpretación.

`generalized_modes` ofrece un control denso reducido con residuales y biortogonalidad. No usarlo para matrices FEM de decenas de miles de grados de libertad.

**Cierre:** inventario completo, ramas seguidas, incertidumbres, residuales, clasificación de modos/resonancias y revisión de la enmienda. No presentar como «modo ligado» un modo de fuga.

## 7. T03 — frontera, dominio, campo y fase

Separar tres instrumentos: esponja FFT/BPM, contorno ADI/FEM y PML de un problema de onda completa. Una ley de reflexión de la PML 1D no acredita la esponja exponencial del BPM.

El estudio reciente de vacío tampoco representa propagación guiada. En su análisis, la cola del haz inicial dominaba ciertos observables de retorno; algunas corridas no terminaron. No cambiar después K1 para que las realizadas aprueben.

1. Definir una región y ventana longitudinal de observación común antes de medir.
2. Registrar haz, cintura, cola espectral, inclinación, polarización cuando aplique, posiciones de detectores y retorno.
3. Usar vacío y guía analítica como controles separados.
4. Medir amplitud y fase del coeficiente reflejado, flujo saliente y entrante y campo complejo en la región útil.
5. Barrer dominio, contorno, h y Δz con controles factoriales suficientes para distinguir sus efectos.
6. Comparar contra una referencia de dominio mayor o frontera transparente validada, con error de referencia cuantificado.
7. Mantener fase absoluta sin ajuste. En píxeles o puertos oscuros, la fase no está definida: excluirlos con un piso prerregistrado y reportar error absoluto.
8. Conservar campos crudos y componentes real/imaginaria; una curva de potencia sola no basta.

Propuesta para un **nuevo** estudio, que debe congelarse antes de producir datos: campo relativo ≤ 1 %, fase ≤ 0,01 rad en muestras por encima del piso registrado y retorno de potencia ≤ 10⁻⁴ en la región/ventana definida. Estos valores son metas de ingeniería propuestas, no una aprobación del protocolo histórico ni una garantía universal. Si el régimen no las permite, publicar el dominio de validez medido.

`phase_metrics` evita ajuste de fase. `agentkit.paraxial` proporciona una referencia CPU con fronteras periódicas y esponja opcional; **no es un solver vectorial ni certifica una frontera abierta**.

**Cierre:** dominio de validez conjunto de campo, fase, detector y frontera para las geometrías de guías/acopladores que usará la red.

## 8. T04 — descomposición modal correcta

Para u = u_m + u_r y una matriz de masa M:

$$
P(u)=u^\dagger Mu
=P(u_m)+P(u_r)+2\operatorname{Re}(u_m^\dagger Mu_r).
$$

Omitir el término cruzado falsea la asignación de potencia. En modos no ortogonales, tampoco se suman sin más las potencias individuales. Un coeficiente mayor que uno no es una eficiencia de conversión.

1. Definir el producto físico usado para potencia; no confundirlo con un producto bilineal algebraico del ECS.
2. Reproducir el caso ortonormal analítico y el caso sintético no normal.
3. Resolver K r = β M r y los adjuntos. Fijar L† M R = I.
4. Separar proyección ortogonal de proyección biortogonal: responden a preguntas distintas.
5. Aplicar la descomposición a los modos originales con fuga de GLASS-010 y conservar el término cruzado.
6. Comprobar que cambiar la normalización no cambia campo reconstruido ni balance.
7. Cuantificar truncamiento modal; un «resto» de una base finita no demuestra por sí mismo radiación.

`coherent_decomposition` implementa las dos proyecciones y el balance completo. Su prueba negativa muestra que descartar interferencias puede cambiar una suma de potencias en una cantidad material.

**Cierre:** aplicación a datos reales del solver, balance, residuales, condicionamiento y una clasificación de resto/radiación sustentada.

## 9. T05 — material y geometría con metrología

El índice de una ficha no es el perfil inducido por escritura fs. El artículo SK1310 identificado es `10.1016/j.optmat.2025.116651`. Su título/metadatos no acreditan todos los parámetros o pérdidas a 1550 nm; obtener el texto por una vía autorizada.

1. Extraer del texto material exacto, receta de escritura, λ, perfiles, incertidumbres, modos y método de pérdida.
2. Distinguir SK-1310 comercial de sílice fundida de referencia. No transferir automáticamente una receta entre materiales.
3. Medir geometría de trazos, profundidad, solapes, grietas, tensiones y birrefringencia.
4. Medir índice base y contraste inducido, con resolución y calibración suficientes; conservar mapas y máscaras crudos.
5. Registrar correlaciones espaciales y entre piezas. Un ruido IID no representa cualquier fabricación.
6. Propagar incertidumbres por sensibilidad de campo, fase y detector, con unidades y covarianzas.
7. Comparar predicción prospectiva con la muestra identificada, sin ajustar sus parámetros usando la misma medida que se reserva para validar.

Esquema mínimo de metadatos: identificador de lote/chip/guía, instrumento y calibración, fecha UTC, material, λ, polarización, unidades, geometría, resolución, incertidumbre, mapa de índice y protocolo. No rellenar parámetros no medidos con valores bibliográficos sin etiqueta.

**Cierre:** perfiles de las muestras utilizados en la simulación, trazabilidad y presupuesto de incertidumbre; mientras falten, estado BLOCKED_MEASUREMENT.

## 10. T06 — contraste electromagnético vectorial

El solver de capas proporciona referencias para geometrías circulares; no es un solver vectorial general 3D. La separación TE/TM del orden de 3·10⁻⁶ exige un error numérico sustancialmente menor para poder interpretarla.

1. Validar un segundo método contra fibra de salto con solución vectorial conocida.
2. Preferir elementos de Nédélec para el problema de Maxwell en H(curl), o un esquema vectorial probado con tratamiento explícito de interfaces. No usar un stencil escalar como solver vectorial por cambiar su nombre.
3. Resolver modos eléctricos y magnéticos con continuidad tangencial, materiales, condiciones de contorno y normalización de flujo coherentes.
4. Detectar modos espurios, residuales, divergencia y sensibilidad a malla/contorno.
5. Comparar HE11, TE01, TM01 y HE21 donde cada formulación sea válida; conservar los casos fuera de validez.
6. Controlar por separado error de n_eff real, pérdida imaginaria, perfil, polarización y fase acumulada a la longitud operativa.
7. Ejecutar la geometría efectiva de trinchera y después perfiles medidos. Registrar el error entre escalar y vectorial como error de modelo.

Usar una biblioteca electromagnética mantenida si el entorno ya la ofrece. La selección y su instalación forman parte de una tarea explícita, con documentación primaria y caso analítico previo. El kit no contiene una sustitución no verificada de Maxwell.

**Cierre:** contraste independiente con precisión suficiente para resolver la diferencia física que se afirma. Un error relativo total de 10⁻⁶ no distingue automáticamente una separación de índice de esa misma escala.

> **Adición v2.** Para el contraste de pérdidas, declarar siempre el modo. En la geometría de referencia, el modelo vectorial del proyecto da 0,044 dB/cm para HE11 y 2,75–2,79 dB/cm para HE21, TE01 y TM01 (`Docs/NOVEDAD-ESTADO-20261011.md`, rama de auditoría). Una medida que excite modos superiores no contrasta HE11.

## 11. T07 — acoplador coherente y transferencia

El piloto GLASS-006b usó puertos gaussianos; no eran eigenmodos. Sus fallos de dx y de reducción gaussiana deben permanecer.

1. Validar la base par/impar y su normalización de flujo. Para una pareja simétrica ideal:

$$
\kappa=(\beta_\mathrm{even}-\beta_\mathrm{odd})/2,\qquad
L_\mathrm{transfer}=\pi/(2|\kappa|).
$$

2. Reconstruir la matriz de transferencia compleja excitando cada puerto y varias superposiciones con fases 0, π/2 y π.
3. Comparar el modelo modal con BPM y un método independiente sobre los mismos perfiles/entradas, sin fit de fase.
4. Comprobar linealidad, reciprocidad cuando aplique, pasividad y coherencia entre potencia y campo.
5. Ejecutar G3/G4 sólo cuando el propagador satisfaga su criterio registrado. La mejora B5 en un caso no habilita todas las geometrías.
6. Probar d = 14 y 16 µm y longitudes que cubran la transferencia; incorporar pérdidas, desacoplo y tolerancias.
7. Reemplazar puertos gaussianos por puertos modales cuando se compare CMT. No ajustar κ a la salida BPM que se usa como validación.

Consultar `experimentos/acoplador_claude/g3_bpm_p2.py` y revisar que no sobrescriba resultados. Publicar curvas, matriz compleja, constantes inferidas independientemente y coste completo.

> **Adición v2 (§47 E3).** Ese archivo sólo existe en `origin/auditoria-20261009`.

**Cierre:** transferencia coherente validada con referencia independiente y presupuesto de error para la biblioteca de componentes.

## 12. T08 — curvas, cruces y rutas 3D

1. Mantener primero un control recto y después barrer radio, ángulo, separación, profundidad y longitud.
2. Seguir la rama modal; una pérdida de selección del eigensolver no es una pérdida física de toda la luz.
3. Distinguir cambio de n_eff, pérdida de confinamiento y pérdida radiativa. Un índice equivalente real no mide radiación.
4. Medir o simular, con frontera validada, la matriz compleja de cada cruce y curva.
5. Incluir cruces no coplanares y rutas 3D fabricables; comprobar acoplamiento no deseado entre segmentos cercanos.
6. Validar predicciones reservadas, por ejemplo un radio y una separación no usados para ajustar la biblioteca.
7. Publicar una envolvente de diseño: R mínimo, separación mínima, ángulos permitidos, pérdida, diafonía y error de fase.

No extrapolar 3D desde una sola sección 2D. La referencia de curva de Lee et al. utiliza otra geometría y no constituye una calibración de ésta.

**Cierre:** componentes aptos para las rutas del demostrador, con incertidumbre y límites documentados; completar medidas en T14.

## 13. T09 — profundidad y registro entre caras

Preparar un cupón con referencias geométricas comunes y una conexión escrita desde dos orientaciones. Medir profundidad, error lateral/axial/angular, aberración, tamaño de trazo y repetibilidad.

1. Calibrar el sistema de coordenadas de máquina y la refracción en cada cara.
2. Usar fiduciales y transformaciones rígidas primero; introducir distorsión sólo si la metrología la justifica.
3. Comparar registro previsto con muestras reservadas; no estimar precisión a partir de la resolución nominal del motor.
4. Medir pérdida/retorno de la unión, no sólo alineación visual.
5. Incorporar errores correlacionados y cambios de lote.
6. Establecer el error permitido a partir del presupuesto de fase/acoplo de T07/T10.

El resultado de un Monte Carlo de registro con σ supuesto no cierra T09. Sin máquina y muestras, entregar planos, lista de mediciones y protocolo al laboratorio, con estado BLOCKED.

## 14. T10 — fase, deriva y control

El resultado H10b negativo muestra que correlacionar errores cambió de forma material el percentil 95. La media no sustituye una especificación de rendimiento del 95 % de piezas.

1. Modelar fase estática, deriva temporal, temperatura, ruido de fuente, DAC y error de control; medir sus parámetros.
2. Utilizar covarianzas o modelos correlacionados; registrar el dominio de esas hipótesis.
3. Usar `transfer_sensitivity` para derivadas de la transferencia compleja y contrastarlas con diferencias finitas.
4. Derivar la tolerancia de longitud e índice a partir de la fase, incluyendo λ:

$$
\phi=2\pi nL/\lambda,\qquad
|\delta(nL)|\le n|\delta L|+L|\delta n|+|\delta n|\,|\delta L|.
$$

5. Simular el lazo real de calibración, rango de actuadores, cuantización, saturación, latencia y fallos de sensor.
6. Registrar antes de medir las condiciones de operación y criterios de media, cola y estabilidad.
7. Medir el consumo del control en T17.

`optical_error_budget` cubre una trayectoria escalar de índice uniforme y sus incertidumbres acotadas. No es la cota de error de una red guiada completa.

**Cierre:** tolerancias y lazo realizable demostrado bajo condiciones medidas; ensayos de deriva y percentiles aprobados.

> **Adición v2 (§42).** Una afirmación sobre el percentil 95 de piezas necesita un número mínimo de realizaciones independientes: con el método sin distribución de Wilks, 59 para 95 % de cobertura con 95 % de confianza, 90 para 95/99 y 299 para 99/95 (`agentkit.stats.wilks_sample_size`). Con menos realizaciones, el percentil empírico no es una cota. Dos cosas distintas: la correlación de errores **dentro** de una pieza (por ejemplo un sesgo común de escritura) ensancha la cola de cada realización (§43); la dependencia **entre** realizaciones aparece cuando comparten un componente (mismo lote u oblea) y reduce el número efectivo de realizaciones independientes. Modelar ambas de forma explícita.

## 15. T11 — compilador con geometría fabricable

Separar cuatro transformaciones:

1. Función entrenada → matrices/capas y detección/activación definidas.
2. Matriz objetivo → componentes ideales coherentes.
3. Componentes ideales → biblioteca calibrada de guías, fases y acopladores.
4. Biblioteca → geometría, rutas y archivo de máquina.

La parte pasiva realiza contracciones, no ganancia arbitraria. Para T = UΣV†, Σ contiene amplitudes entre cero y uno. Si se necesitan valores mayores, declarar y medir ganancia externa o escala de entrada. Una proyección a la unitaria más cercana cambia la función y debe evaluarse.

`agentkit.mesh` implementa SVD pasiva y una síntesis triangular mediante rotaciones complejas, con todas las fases y reconstrucción coherente. Rechaza amplificación. Conserva `geometry_validated=false` hasta validar la geometría real.

```powershell
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.mesh --input resultados/agent/manufactured/target.npz --out resultados/agent/compiled_transfer.json --kappa-per-m 471.64
```

El valor κ del ejemplo es un dato ideal de modelo, no una calibración física. La fórmula L = θ/κ sólo asigna la magnitud de mezcla; faltan fases, pérdidas y diseño espacial.

> **Adición v2 (§43).** `agentkit.mzi` añade síntesis rectangular de MZI en el orden de Clements, con una convención de dispositivo explícita, profundidad N (medida para N = 3 a 16) frente a 2N − 3 de la síntesis triangular de v1, compilación pasiva por SVD con dos mallas y estudio de errores de divisor con componente compartida. Un argumento de conteo de dimensiones muestra que ninguna malla de elementos de dos modos, plana o 3D, baja de N − 1 capas para unitarias universales; la ventaja de una red 3D hay que buscarla en otra parte (§39, H-B).

El agente debe implementar la exportación geométrica completa usando una biblioteca validada: unidades, radio mínimo, separación, trayectoria, profundidad, orden de escritura, coordenadas de caras, fiduciales y límites de máquina. Volver a simular la geometría exportada, incluyendo perturbaciones registradas. Conservar negativos C2 y las 28/36 realizaciones C3; no presentar 78 % como garantía universal.

**Cierre:** round trip de la función a geometría y respuesta física/modelada validada, más archivo fabricable revisado; sólo álgebra no cierra T11.

## 16. T12 — cerrar la función de la red y su aprendizaje

Los resultados históricos son: A = 64,25 %, B = 84,55 %; H-F1 y H-F2 fallaron. La ablación posterior obtuvo 86,2 % sin MZM y 59,05 % sin detección intermedia. La mejora de la segunda capa no puede atribuirse automáticamente a la activación; la referencia electrónica tuvo reinicios sin converger.

1. Reproducir primero las predicciones guardadas y verificar etiquetas, particiones, parámetros y pérdidas.
2. Corregir la presentación de diferencias: informar diferencia puntual y media bootstrap por separado.
3. Registrar un experimento nuevo con train/validation/test separados y criterio de convergencia común.
4. Entrenar varias inicializaciones completas; conservar fallos, gradientes, iteraciones y función objetivo. No afirmar óptimo global por una pérdida parecida entre reinicios.
5. Ajustar Vπ, sesgo y escala usando sólo train/validation; reentrenar en cada configuración según un protocolo anterior a nuevos resultados.
6. Comparar malla unitaria, pesos reales, detección/remeisión y MZM con recursos pertinentes. Igual número de parámetros nominales no equivale a igual clase funcional: U₂U₁ sigue siendo una sola unitaria.
7. Validar las convenciones de campo del MZM. La raíz positiva de una transmisión de intensidad pierde la posible fase π de una amplitud de campo con signo; el modelo debe corresponder al hardware.
8. Incluir las restricciones fabricables, ruido medido y resolución de actuadores en la validación de la red.
9. Congelar un candidato antes del test. Conservar también resultados negativos si no alcanza el umbral.

El kit implementa seis modelos y gradientes de Fréchet comprobados por diferencias finitas. Usa reemisión de amplitud positiva para los modelos de dos capas; su realizabilidad exige electrónica y una referencia de fase.

Ejemplo **de desarrollo**, que no renombra el dataset histórico como nuevo test independiente:

```powershell
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.learning prepare --directory resultados/agent/development_digits
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.learning fit --train resultados/agent/development_digits/train.npz --validation resultados/agent/development_digits/validation.npz --model unitary_mzm --seeds 1 2 3 4 5 6 7 8 --maxiter 1000 --v-pi 1 --bias 0 --out resultados/agent/candidate_unitary_mzm.json
```

Crear previamente un directorio `resultados/agent` nuevo o verificar que las rutas finales no existan. Supervisar cada entrenamiento con un presupuesto registrado; no bajar iteraciones después para declarar convergencia. Si se interrumpe, conservar el estado operacional y programar un nuevo trabajo registrado.

> **Adición v2 (reproducido; control de desarrollo, no confirmatorio).** El comando de ejemplo anterior (`unitary_mzm`, semillas 1–8, 1000 iteraciones) no produjo ningún arranque convergido: L-BFGS-B terminó por reducción relativa de la pérdida con max |gradiente| entre 4,8·10⁻³ y 6,1·10⁻², muy por encima de 10⁻⁵, así que `learning evaluate` rechazaría el candidato. El modelo `unitary` sin MZM sí convergió en 8/8 arranques. El arranque 1 reproduce la cifra de §33 (6,57·10⁻⁸). En esta ejecución el seleccionado fue el 7 (1,60·10⁻⁸), porque las ocho pérdidas coinciden hasta unos 10⁻¹⁴: qué arranque se elige es numéricamente frágil, aunque todos convergen. La hipótesis más simple es la no diferenciabilidad de |cos(·)| en cos = 0. El modelo de campo con signo de §44 (`unitary_mzm_signed`), que además corresponde a un MZM push-pull con portadora de fase referenciada, convergió en 8/8 arranques (max |gradiente| ≤ 2,0·10⁻⁶). Ver §44 para las cifras y para el problema de ganancia de las referencias de pesos reales.

Para datos externos preparados por el agente, `learning prepare --input` acepta un NPZ con X numérico bidimensional e y de clases. Registrar procedencia y aislamiento del test. El parser acepta de 2 a 8 clases; esta limitación es del control incluido, no del proyecto físico.

**Cierre:** modelo y hardware definidos, convergencia verificada, evaluación reservada y función realizada. Una red numérica que funciona no acredita automáticamente una red óptica construida.

## 17. T13 — fabricación de muestras y demostrador

Preparar un dossier fabricable antes de solicitar trabajo al laboratorio:

- Material y lote, receta autorizada de fs y dominios permitidos.
- Cupones rectos, de acoplador, fase, curva, cruce y unión entre caras.
- Al menos tres chips independientes para estimar variación.
- Identificación de cada muestra y archivo de máquina por hash.
- Medidas previstas, incertidumbres objetivo y predicciones congeladas.
- Control sin escritura y control de geometría de referencia.
- Red pequeña con las mismas componentes calibradas, no una geometría nueva sin validación.

No fijar una receta de láser para un material desconocido. El operador y el laboratorio deben validar parámetros e instrumentos. El agente entrega documentación completa y prepara análisis, pero no inventa fabricación ni permisos de una máquina que no controla.

**Cierre:** piezas físicamente existentes, identificadas, inspeccionadas y aceptadas para T14.

## 18. T14 — caracterización óptica y comparación prospectiva

### 18.1. Protocolo de pérdidas

Usar verdadero cutback sobre la misma guía cuando sea viable, con varios truncamientos y recoupling controlado. Si se comparan guías distintas de varias longitudes, denominarlo regresión de inserción frente a longitud y declarar el supuesto de pérdidas de acoplo comparables; no confundirlo con cutback.

Registrar Pin/Pout calibrados, longitud, λ, polarización, guía, chip, alineación, modo excitado, temperatura y repetición. Medir varios largos y al menos tres chips. La excitación modal debe quedar definida: un cambio de contenido modal puede falsear una pendiente.

El CSV para `agentkit.metrology cutback` tiene estas columnas exactas:

```text
chip_id,guide_id,length_m,wavelength_m,polarization,input_power_w,output_power_w,sigma_loss_db
```

Cada guía necesita cuatro longitudes distintas, y cada invocación analiza una λ/polarización. `sigma_loss_db` es la incertidumbre de la pérdida de esa lectura, no un número para mejorar el ajuste. No reutilizar el CSV manufacturado como medida.

```powershell
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.metrology cutback --input resultados/agent/measurements/cutback_x_1550.csv --out resultados/agent/analysis/cutback_x_1550.json
```

El análisis produce pendientes por guía, medias por chip e incertidumbre de chips independientes. Sus intervalos dependen de normalidad aproximada, calibración y linealidad. Añadir incertidumbres sistemáticas y verificar residuales; tres chips dan poca información de cola.

### 18.2. Campo, fase y modo

Medir matriz compleja de transferencia, interferencia, contenido modal, polarización, birrefringencia, pérdida, retorno y estabilidad. Emplear referencias y calibraciones externas al ajuste.

Comparar las medidas reservadas con las predicciones hechas a partir de perfiles y parámetros calibrados en otras muestras. Una pérdida ideal de 0,044 dB/cm para una camisa continua no es una cota universal de toda guía real: si la geometría y el perfil reales difieren, la comparación debe rehacerse. No exigir como ley física que toda medición quede por encima de ese número.

**Cierre:** datos crudos, incertidumbres, análisis reproducible y contraste de hipótesis. Distinguir confirmación, falsación e inconclusión cuando el intervalo cruza el umbral.

> **Adición v2 (§41.2 y §42).** Analizar las pérdidas a ciegas: un custodio oculta un desplazamiento secreto de la pendiente (`agentkit.blind`) hasta que se committea el registro de congelación del análisis. Decidir con la regla de tres zonas de `agentkit.stats.three_zone_decision`, registrada antes de medir. Planificar el número de chips con `agentkit.stats.sample_size_one_sided` (α unilateral 0,025, coherente con un IC bilateral del 95 %) y una σ entre chips declarada como valor de planificación.

## 19. T15 — integración del sistema completo

Definir entrada de datos, codificación de amplitud/fase, fuente, moduladores, chip, detectores, ADC/DAC, alimentación, control, activación y salida. Documentar qué está dentro y fuera del cubo.

1. Verificar unidades y sincronización de cada interfaz.
2. Calibrar fase/canales y respuesta detector/actuador en condiciones reales.
3. Ejecutar tareas completas con el candidato congelado; conservar latencia y fallos.
4. Verificar la activación y reemisión con el modelo usado para entrenar.
5. Probar reinicio, recalibración, deriva, pérdida de canal y recuperación.
6. Conservar firmware, configuración y versiones, sin incluir credenciales.

**Cierre:** inferencia extremo a extremo repetible, con especificación del sistema y límites de operación.

## 20. T16 — test independiente, estadísticas y alternativas

Los dígitos públicos 0–3 ya se usaron en el proyecto. Un nuevo split de ese mismo conjunto es un control de desarrollo; no borra la exposición anterior.

1. Registrar un dataset final nuevo, o un conjunto que haya estado realmente reservado, con procedencia y acceso controlado.
2. Mantener test separado físicamente del entrenamiento si es posible. Fijar clases, preprocesado, métricas, semillas, número de candidatos y reglas de selección.
3. Ajustar escalas y PCA sólo con entrenamiento. Seleccionar modelos usando validación.
4. Congelar pesos, arquitectura, configuración y código antes de revelar el test.
5. Evaluar una vez bajo el contrato; después, cualquier rediseño usa otro test prospectivo.
6. Comparar contra referencias electrónicas convergidas, con tarea, preprocesado, exactitud y recursos comparables.
7. Informar exactitud, matriz de confusión, pérdidas, IC, diferencias pareadas y sensibilidad a semillas.
8. Si hay varias hipótesis confirmatorias, registrar control de multiplicidad. Bootstrap de muestras de un test no estima automáticamente incertidumbre entre dispositivos o entrenamientos.
9. Separar estudios exploratorios y confirmatorios.

`paired_accuracy` devuelve la diferencia observada exacta y el intervalo bootstrap como cantidades distintas. `learning evaluate` rechaza el candidato si el entrenamiento seleccionado no convergió; el historial de acceso al test sigue siendo responsabilidad del protocolo.

**Cierre:** test íntegro y reservado, referencias pertinentes y conclusiones limitadas al tamaño/tarea estudiados.

> **Adición v2 (§41.2).** El conjunto de test final debe custodiarlo alguien que no entrena ni selecciona modelos; el analista recibe sólo las predicciones evaluadas una vez. Una referencia electrónica con pesos reales sin restricción usa ganancia que una red pasiva no tiene (σ_max de la segunda capa entre 2,6 y 5,7 en los arranques convergidos del control de §44, y hasta 974 en los no convergidos). Comparar con presupuestos de ganancia iguales o contar la ganancia como recurso.

## 21. T17 — rendimiento y consumo de todo el sistema

Medir el mismo problema a una precisión/fiabilidad comparable y registrar:

- Preparación y codificación de entradas.
- Calibración, arranque, fuente, moduladores y detección.
- Lectura, electrónica, activación, control y refrigeración.
- Latencia por inferencia, throughput sostenido, p50/p95/p99 y errores.
- Potencia idle/activa, tiempo, energía y tasa de inferencias correctas.

Un TOPS teórico o el tránsito de luz por una guía no equivale a throughput extremo a extremo. Los 6554 TOPS del antecedente LAMP se describen como pico teórico limitado por una tasa ideal de detector; no usarlos como medida del montaje.

Para `agentkit.metrology energy`, proporcionar lecturas sincronizadas:

```text
time_s,completed_inferences,source_w,modulation_w,detection_w,control_w,cooling_w
```

Usar contadores enteros de inferencias completadas y publicar las cinco componentes. Un cero debe estar justificado por instrumentación, no por omisión.

```powershell
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.metrology energy --input resultados/agent/measurements/system_power.csv --out resultados/agent/analysis/system_energy.json
```

La integración trapezoidal necesita frecuencia de muestreo suficiente e incertidumbre temporal/eléctrica cuantificada. Medir referencias en las mismas condiciones y presentar tradeoffs de exactitud, energía y latencia.

**Cierre:** comparación completa, reproducible y estadísticamente sustentada. Sin montaje e instrumentos, publicar sólo hipótesis o presupuestos paramétricos.

> **Adición v2 (§40).** Antes de construir el montaje, ejecutar la prueba de descarte energética T24 con parámetros con fuente. Si incluso el caso optimista no mejora una referencia digital citada, no se debe presentar la eficiencia energética como contribución central.

## 22. T18 — escalabilidad y repetibilidad

1. Separar complejidad de simulación, componentes físicos y tamaño de red.
2. Analizar acumulación de pérdida, errores de fase, cruces, detectores, actuadores y calibración.
3. Publicar memoria, tiempo y límites para los tamaños realmente ejecutados.
4. Validar diseños reservados más grandes antes de extrapolar.
5. Medir múltiples dispositivos y lotes; informar rendimiento y variación entre piezas.
6. Considerar yield, mantenibilidad, sustitución y coste energético de control.

No traducir triángulos de una escena a neuronas. No certificar 80/500 millones de unidades a partir de metadatos de una extensión gráfica.

**Cierre:** ley de escalado sustentada y replicación entre dispositivos; todo tamaño no medido queda como extrapolación con hipótesis.

> **Adición v2 (§39 y §43).** Separar profundidad lógica (cota inferior N − 1 para mallas universales de elementos de dos modos), pérdida acumulada por trayectoria, cruces y diafonía. La ventaja 3D, si existe, debe medirse en cruces eliminados, densidad o longitud de ruta, no en profundidad de una unitaria universal.

## 23. T19 — novedad y antecedentes

Revisar fuentes originales, no sólo resúmenes, y construir una tabla de reivindicaciones:

| Antecedente | Relación con el proyecto |
|---|---|
| Kondratyev et al., arXiv:2308.13452 | Interferómetro programable de ocho puertos escrito con fs, 920–980 nm. |
| Skryabin et al., arXiv:2408.06688 | Guías multiscan de baja pérdida; no equivale al perfil de camisa deprimida de esta muestra. |
| Cao et al., DOI 10.1038/s41467-026-72316-9 | Red fotónica 3D programable fabricada en borosilicato, publicada el 21-04-2026. |
| SK1310, DOI 10.1016/j.optmat.2025.116651 | Antecedente de guías de camisa deprimida en banda telecom; texto completo y detalles aún necesarios. |
| Shen et al., arXiv:1610.02365 | Redes fotónicas y procesamiento con matrices/interferómetros anteriores. |

En LAMP, separar cifras de entrenamiento, test y rendimiento teórico: el cuerpo del artículo informa un test de 48 imágenes con 91,7 %; no comparar ese número directamente con el dataset reducido de este proyecto. El material, λ operativa y geometría tampoco son iguales.

Una red 3D escrita con fs en vidrio **no puede reivindicarse aquí como idea nueva por sí sola**. Evaluar aportaciones específicas: sílice y perfil concretos, registro desde varias caras, biblioteca calibrada, cota de error válida, relación predicción/medida, tolerancias y arquitectura útil. Cada reivindicación necesita alcance, diferencia frente al antecedente y evidencia propia.

La falta de un artículo encontrado no prueba prioridad mundial. Registrar estrategia de búsqueda, fecha, términos, candidatos y textos no accesibles.

> **Adición v2 (§46).** Metadatos verificados de estos antecedentes y otros nuevos: Kondratyev et al. se publicó en *Photonics Research* 12(3), A28 (2024). Skryabin et al. se publicó en *Physical Review Applied* 22, 064079 (2024) y declara 0,07 dB/cm en sílice fundida con guías multiscan **caracterizadas a 920 nm**. El mismo artículo atribuye el récord a 1550 nm, también 0,07 dB/cm, a Tan, Sun, Li y Qiu, *Opt. Lett.* 47, 4766 (2022). Cao et al. es *Nature Communications* 17, 5476 (2026) y denomina LAMP a su sistema. Añadir Pentangelo et al. (2024), procesadores universales escritos con fs que operan a 785 y 1550 nm (relevante para la afirmación (b), operación a 1550 nm), y Moughames et al. (2020), interconexiones 3D impresas por polimerización de dos fotones.

**Cierre:** reivindicación precisa sustentada por comparación documental y resultados propios, o retirada explícita de la reivindicación.

> **Adición v2.** Registrar cada reivindicación en el registro de afirmaciones (`agentkit.claims`, §41.3). Una reivindicación de novedad sólo puede ser PASS con un registro de búsqueda bibliográfica como evidencia; la retirada de una reivindicación se conserva con su motivo.

## 24. T20 — contribución central y prueba decisiva

Revisar `Docs/CONTRIBUCION-CENTRAL-T20.md` y las correcciones de novedad/cota. La hipótesis de pérdida total ≤ 0,3 dB/cm sigue siendo comprobable si material, geometría, modo y λ se fijan; no demuestra automáticamente un descubrimiento fundamental.

Elegir una contribución principal antes de medir. Opciones que el agente puede desarrollar con la evidencia adecuada:

1. Diseño de una familia de guías en un material concreto, con predicción validada de pérdidas y tolerancias.
2. Modelo y control del error de campo/fase para una red coherente manufacturada, con contraste experimental.
3. Arquitectura optoelectrónica fabricable que resuelva una tarea relevante con ventaja medida bajo recursos comparables.
4. Resultado negativo sólido que delimite una arquitectura o método, sin afirmar más generalidad que la demostrada.

Registrar qué observación confirmaría, falsaría o dejaría inconclusa la hipótesis. Reservar casos que no se usaron para ajustar el diseño. Publicar todos los resultados bajo el mismo criterio.

**Cierre:** afirmación central, prueba decisiva y evidencia que la sostiene o refuta. Una lista larga de scripts no reemplaza este argumento.

> **Adición v2 (§39, §42 y §47 E3, E11).** `Docs/CONTRIBUCION-CENTRAL-T20.md` sólo existe en la rama de auditoría. Origen del umbral de 0,3 dB/cm: Bukharin, Khudyakov y Vartapetov, *Applied Physics A* 119, 397–403 (2015), DOI 10.1007/s00339-015-8990-x. El título trata del régimen de acumulación térmica. El resumen de la página de la editorial, consultado el 12-10-2026, dice: «We demonstrated low-loss (0.3 dB/cm) tubular waveguide inside fused silica». El resumen no da la longitud de onda de esa cifra. Frente a 0,07 dB/cm a 1550 nm en sílice (Tan et al., 2022), cumplir ≤ 0,3 dB/cm no sería competitivo con el estado del arte. Antes de medir, enmendar H1 con fecha en los cinco puntos que señala `Docs/NOVEDAD-ESTADO-20261011.md` §5: (i) modo y excitación; (ii) una única regla de decisión; (iii) origen del umbral; (iv) definición de «pérdida total de propagación» (fuga, dispersión y absorción, excluido el acoplo); (v) una sola fuente para la fuga de referencia (0,0443 escalar frente a 0,044044 vectorial). La regla de tres zonas de §42 resuelve las zonas que quedaban sin decidir.

## 25. T21 — reproducción y revisión externas

Preparar un paquete para otro equipo: entorno, licencias, fuentes, contratos, datasets, hashes, raw outputs, resultados esperados, negativos, comandos y tiempo/recursos reales.

El equipo externo debe reproducir desde las entradas, no sólo validar una tabla exportada. Comparar discrepancias y publicar su procedencia. La CI del mismo repositorio en Linux es útil para portabilidad, pero no es reproducción física externa.

Preparar manuscrito y material suplementario para revisión científica. Contactar, enviar o someter sólo con autorización de la sesión real. Registrar el resultado externo; no llamar «revisión por pares» a una revisión interna de código.

**Cierre:** reproducción externa documentada y revisión recibida, con respuestas y correcciones trazables.

> **Adición v2 (§41.4).** La concordancia entre agentes de IA (Claude, Codex, JEV u otros) no es reproducción externa ni revisión por pares: comparten datos, instrucciones y sesgos de entrenamiento correlacionados. El registro de afirmaciones rechaza una reproducción externa sin equipo independiente identificado.

## 26. T22 — impacto posterior

Definir indicadores observables: uso del código por terceros, reproducciones, dispositivos derivados, tareas resueltas, comparaciones independientes y publicaciones que utilicen el resultado.

Mantener un registro fechado y verificable. No contar promesas, descargas de una imagen o proyecciones teóricas como impacto científico consolidado. Entregar el plan de seguimiento y dejar el estado como OPEN_OBSERVATION mientras no exista evidencia posterior.

## 27. Matemáticas: revisión de openai/math y decisiones de adopción

### 27.1. Fiabilidad y alcance de la colección

Se revisaron README, catálogo, historial, notas de alcance Lean, enunciados de Comparator y fuentes TeX seleccionadas del commit fijado. La colección contiene manuscritos generados por un modelo y resultados con distintos estados de verificación. El historial del 7-10-2026 documenta retiradas y reparaciones; leer revisiones antes de apoyar una garantía.

La formalización declarada debe verificarse para el teorema y sus dependencias concretos. Los archivos de desafíos Comparator pueden contener `sorry` intencionalmente: son enunciados de comparación, no la prueba entregada. No certificar un teorema porque ese enunciado compile. Revisar configuración, declaración real, axiomas y resultado del Comparator. En esta entrega **no se compiló Lean ni se ejecutó Comparator**.

### 27.2. Resultado 374: estabilidad de mapas de Brenier

El manuscrito estudiado declara, para fuente uniforme ρ en un cuerpo compacto convexo K con interior y dimensión d ≥ 2, y objetivos soportados en un compacto fijo Y:

$$
\|T_\mu-T_\nu\|_{L^2(\rho)}
\le C(K,Y)\,W_2(\mu,\nu)^{1/3}.
$$

El exponente se declara óptimo en esa clase uniforme. Se leyeron el enunciado y la derivación de interpolación de gradientes; no se realizó una verificación independiente completa de toda la prueba.

**Utilidad posible:** estudiar estabilidad de una representación por transporte óptimo para calibración geométrica y registro de mapas medidos de intensidad, con iluminación y soportes que cumplan las hipótesis. Puede aportar una cota conservadora a esa etapa auxiliar.

**Límites decisivos:** intensidad no contiene fase; el teorema no controla Maxwell, la potencia de una guía ni la fase de una red. Una fuente discreta gaussiana no es la fuente uniforme continua del enunciado. Una proyección baricéntrica de un LP finito tampoco es el mapa de Brenier continuo.

**Experimento propuesto OT-CAL-001:**

1. Calibrar coordenadas con iluminación uniforme sobre una región convexa; fijar soporte y unidades.
2. Generar casos manufacturados con transformación y ruido conocidos, antes de leer muestras reservadas.
3. Comparar registro rígido/afín con un registro por transporte, utilizando sólo datos de calibración.
4. Medir error de coordenadas, estabilidad al ruido y coste. Para usar la cota, probar las hipótesis y documentar C(K,Y).
5. Reservar mapas y muestras para evaluación. Congelar la calibración antes de comparar solvers.
6. Rechazar el método si deforma la señal física o introduce un ajuste posterior que oculte error.

`exact_discrete_transport` implementa un LP cuadrático acotado, con auditoría de marginales. Sirve para ese piloto; no implementa ni verifica el teorema nuevo. Adopción: **exploratoria y opcional**, después de T01.

### 27.3. Resultado 107: exponente de multiplicación matricial ≤ 9/4

La fuente consultada formula Oε(n^(9/4+ε)) operaciones aritméticas complejas asintóticas. El manuscrito y la nota Lean distinguen ese resultado de precisión en coma flotante, bit complexity, constantes y tamaño de cruce práctico.

**Relación con el proyecto:** composición de transferencias y algunos cálculos de matrices podrían beneficiarse de futuros algoritmos concretos. Esto no modifica la propagación física ni demuestra una mejora de una malla 4×4.

**Decisión actual:** mantener NumPy/SciPy/BLAS como referencias prácticas. No implementar un supuesto kernel de exponente 9/4 ni anunciar un speedup que el repositorio no proporciona. Sólo evaluar una implementación concreta si aparece, bajo matrices de los tamaños reales, exactitud compleja y coste completo. No desplazar el núcleo gráfico del proyecto por una promesa asintótica.

> **Adición v2 (§47 E12).** Según `lean/docs/107.md` del commit fijado, el alcance formalizado es ω(ℂ) ≤ 9/4 en el modelo aritmético de programas sin divisiones sobre los complejos; para todo cuerpo, la cota formalizada es ω(F) < 2,371054886006746. Ese documento enlaza dos manuscritos fechados el 24-09-2026 («Complex Matrix Multiplication Below 2.258 and Rectangular Bounds» y «Staggered extraction for exact matrix multiplication over every field»), no el manuscrito del 2-10-2026 citado en §34. El alcance Lean corresponde, por tanto, a manuscritos distintos. La decisión de no adoptar no cambia.

### 27.4. Resultados descartados como solución directa

| Familia | Motivo |
|---|---|
| 080: convergencia puntual de Schrödinger libre | t → 0 y datos Sobolev no dan convergencia de malla/Δz de guías con interfaces, absorción y potencial discontinuo. |
| 079: suavizado local de onda libre 3D | No es una cota directa del modelo guiado/material de este proyecto. |
| 365: recuperación de métrica y conexión desde una región de frontera | Problema de datos de frontera a frecuencia cero; no equivale a invertir una imagen de intensidad óptica a 1550 nm. |
| 283: síntesis unitaria con oráculo booleano | Requiere un oráculo objetivo cuya construcción eficiente no se afirma; no es un compilador clásico a guías fs. |
| 362: Vlasov–Maxwell relativista | Plasma/cinética de partículas, diferente del problema dieléctrico guiado. |
| 371: blowup de Schrödinger defocusing en dimensión 12 | Régimen supercrítico ajeno a las guías escalares lineales aquí estudiadas. |

No adoptar un resultado sólo porque contiene «Maxwell», «unitario» o «Schrödinger».

## 28. Métodos matemáticos con utilidad inmediata

### 28.1. Regularidad e interfaces: no asumir orden dos

Bao, Ma y Wang estudian errores de splitting con potenciales de baja regularidad. Sus resultados de segundo orden para Strang requieren regularidad específica —por ejemplo H² del potencial en el resultado L² indicado—. Un perfil de índice con saltos no satisface automáticamente esas hipótesis. La transferencia al modelo óptico requiere identificar la ecuación y su dominio.

> **Adición v2 (§47 E9).** Referencia verificada: W. Bao, Y. Ma y C. Wang, *Mathematical Models and Methods in Applied Sciences* 34(5), 803–844 (2024), DOI 10.1142/S0218202524500155. El artículo trata la ecuación de Schrödinger **no lineal** con potencial y no linealidad de baja regularidad (cotas óptimas L² y H¹ para Lie–Trotter y Strang). Su traslado al BPM lineal con interfaces es una hipótesis que hay que comprobar, no una consecuencia.

Acciones: controlar las interfaces, la proyección de geometría y el observable; medir conjuntamente h y Δz; comparar Strang con la exponencial del **mismo** operador discreto; medir conmutadores y residuales. El control de matrices suaves de `splitting_control` acredita su caso reducido, no convergencia uniforme cuando h tiende a cero.

### 28.2. Estimación orientada al observable y adjuntos

Aplicar un adjunto al detector que importa, no sólo una norma global. Para un sistema semidiscreto M u' = A u + f y una aproximación v:

$$
r=Mv'-Av-f,\qquad
\mu_M=\lambda_{\max}\!\left((A+A^\dagger)/2,\ M\right).
$$

Si μ_M es una cota de crecimiento válida y b_i acota ||M^(-1/2)r|| en cada intervalo completo:

$$
\|e(z)\|_M \le e^{\mu_M(z-z_0)}\|e(z_0)\|_M
+\int_{z_0}^{z}e^{\mu_M(z-s)}b(s)\,ds.
$$

La condición sobre todo el intervalo es esencial. Muestras puntuales de residual no proporcionan esa envolvente. `logarithmic_norm` y `residual_error_bound` implementan el cálculo reducido; el agente debe construir cotas de residual y consistencia para el problema continuo si desea una garantía continua.

Para un detector PSD D y η que acota el error de campo en norma de masa:

$$
|J(u)-J(v)|\le
\|M^{-1/2}DM^{-1/2}\|_2\,
\bigl(2\|v\|_M\,\eta+\eta^2\bigr).
$$

`detector_error_bound` propaga ese error bajo sus hipótesis. Adaptar la malla por residual ponderado por el adjunto; validar efectividad y no llamar «cota» a un estimador sin prueba de fiabilidad.

### 28.3. Operadores no normales

Usar residuales, modos adjuntos, números de condición, pseudospectros o subespacios. Un autovalor pequeño con vector mal condicionado puede ser muy sensible a perturbaciones. No deducir robustez de fuga sólo por un residual pequeño.

`generalized_modes` rechaza bases casi defectivas o no biortogonales; no fuerza una normalización para hacerlas aprobar. Para sistemas grandes, usar métodos sparse y subespacios revisados.

### 28.4. Optimización compleja y restricciones pasivas

Usar gradientes de Fréchet de exp(iH), que el kit contrasta con diferencias finitas para las seis variantes. Los resultados de convergencia deben incluir gradiente, terminación, iteraciones y reinicios. Considerar optimización sobre U(N) o parametrización de malla física como siguiente paso, con el mismo protocolo de validación.

SVD separa la limitación pasiva de ganancia externa. La síntesis triangular incluida tiene reconstrucción algebraica probada. Una malla rectangular tipo Clements puede reducir profundidad y exposición a pérdidas, pero debe implementarse y contrastarse con la biblioteca física; no cambiar de arquitectura sin revalidar su función.

### 28.5. Cadena completa de errores

Publicar por separado:

| Componente | Evidencia necesaria |
|---|---|
| Geometría e índice | Metrología y su incertidumbre/correlación. |
| Modelo físico | Contraste escalar/vectorial y límites de aproximación. |
| Discretización espacial | Serie, reserva, geometría e interfaces. |
| Integración longitudinal | Referencia temporal y controles independientes. |
| Frontera y dominio | Campo/reflexión y dependencia de dominio. |
| Cuadratura y detector | Indicador/cota de operador, potencia y error de campo. |
| Reducción modal | Truncamiento, condicionamiento e interferencias. |
| Aritmética GPU | Campo complejo y fase frente a referencia, sin ajuste. |
| Fabricación y control | Datos de tolerancia y lazo real. |

No sumar errores relativos definidos con denominadores distintos. Las cotas deterministas compatibles se suman mediante desigualdades justificadas; las incertidumbres estadísticas se propagan con su modelo de dependencia. No confundir ambas.

## 29. GPU y motor 3D: validación adicional necesaria

Conservar R1/R2/P1 negativos y R3 positivo. R3 tuvo 168 campos manufacturados aprobados; su alcance era representación/superposición P2 en framebuffer FP32. La precisión del gráfico no prueba propagación guiada.

Para un futuro backend GPU:

1. Identificar la ecuación y operación que ejecuta, con código de shader/kernel y tipos reales.
2. Trasladar el operador validado, no una animación de puntos.
3. Comparar campos de las mismas entradas/mallas; incluir pérdida, fase, detectores y adversarios oscuros.
4. Evaluar complex64 y complex128 por separado; conservar fallos de precisión.
5. Medir preparación, transferencia, compilación, arranque, cómputo y readback.
6. Reservar casos y revisar CPU/GPU con auditores que no reutilicen el evaluador.
7. Añadir rendimiento sólo después de cumplir precisión. Los núcleos RT aceleran geometría; no resuelven por sí solos campo coherente.

La ventana y reserva deben ser actuales. Si no están disponibles, terminar contratos y controles CPU y dejar el ensayo GPU pendiente, sin inicializarlo incidentalmente.

## 30. Presentación, archivo y entrega profesional

### 30.1. README y estado consolidado

Mantener una entrada con: contribución central, alcance actual, resultados cuantificados, tabla de pendientes, comandos reproducibles y límites. Conservar fechas de informes históricos, pero enlazar correcciones actuales. No mezclar «calculado», «validado» y «medido».

Los GIF sirven para explicación. Para el manuscrito, exportar figuras estáticas de alta calidad con ejes, unidades, escalas fijas, umbrales, incertidumbres, n y procedencia. Conservar una fuente de cada figura y datos subyacentes. No elegir la repetición más favorable. El módulo agentkit.report exporta PNG a 300 dpi y PDF desde CSV con mesh_um, power_fraction y error_indicator; conserva todos los puntos y declara si las barras son indicadores numéricos. Su CLI exige --scope numerical_model o manufactured_control, y no acepta presentar esos datos como medidas físicas.

### 30.2. Manuscrito principal en inglés

Preparar un manuscrito completo con:

1. Title and abstract: contribución precisa y resultados realmente obtenidos.
2. Introduction and related work: antecedentes cercanos y diferencia sustentada.
3. Physical and mathematical model: ecuaciones, supuestos, SI y dominio de validez.
4. Numerical methods: discretización, interfaces, contorno, propagación y observables.
5. Verification: casos analíticos, refinamientos, reservas, negativos y controles.
6. Experimental methods: sólo medidas realizadas; protocolos futuros separados.
7. Results: todos los criterios, diferencias, incertidumbres y fallos.
8. Discussion: qué se sostiene, qué se refuta y qué no se puede concluir.
9. Reproducibility, data/code availability, authorship and AI assistance.

No escribir un abstract de demostración física si sólo hay simulación. No presentar una explicación causal no contrastada como mecanismo demostrado.

### 30.3. Archivo, licencia y release

Preparar una licencia acorde con la decisión del titular y la procedencia de dependencias/datos; no imponer una licencia pendiente. Actualizar CITATION.cff, CONTRIBUTORS y versiones después de revisar cambios.

> **Adición v2 (verificado).** `main` no contiene archivo de licencia; existe la propuesta `Docs/LICENCIA-PROPUESTA.md`, y el README indica que la licencia sigue pendiente. Sin licencia, terceros no tienen permiso explícito para reutilizar el código, lo que dificulta T21. La decisión sigue siendo del titular y conviene tomarla junto con T29 (§45).

No reescribir el historial ni borrar arrays pesados para reducir tamaño. Preparar un archivo científico externo con manifiesto y DOI cuando exista autorización; verificar que cada campo necesario para la reproducción esté disponible. Los hashes no sustituyen arrays ausentes.

Crear una release coherente después de aprobar el alcance anunciado. Si sólo se cierra el software/modelo, etiquetarla así y mantener visibles los bloques físicos.

## 31. Comandos de control y organización de evidencias

Después de extraer el kit, ejecutar sus controles antes de aplicarlo a datos del proyecto:

```powershell
& '.\.venv-closure\Scripts\python.exe' -B -m unittest discover -s tests -p 'test_agentkit.py' -v
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.demo --directory resultados/agent/manufactured
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.analyze forecast --input resultados/agent/manufactured/S16_manufactured.json --out resultados/agent/manufactured_forecast_control.json
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.paraxial run --input resultados/agent/manufactured/paraxial_input.npz --config resultados/agent/manufactured/paraxial_config.json --directory resultados/agent/paraxial_control --chunk-steps 8 --max-seconds 30 --receipt resultados/agent/paraxial_invocation_001.json
```

Son datos manufacturados y un control de desarrollo. No adjuntar estos resultados como cierre de T96, pérdidas medidas ni red física.

Para supervisar CPU con límite duro:

```powershell
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.supervisor --cwd . --log resultados/agent/check_log.txt --report resultados/agent/check_supervisor.json --seconds 40 --ram-floor-gib 4 --disk-floor-gib 2 -- .\.venv-closure\Scripts\python.exe -B -m unittest discover -s tests -p test_agentkit.py
```

El supervisor limita esa invocación. No otorga acceso GPU, no sustituye reservas y no valida un experimento. Los checkpoints del kit tienen identidad de entradas/configuración/fuentes, versión de NumPy/Python/plataforma y una cadena verificable de dimensiones constantes; no modifican los checkpoints originales D16.

### Esquema de un protocolo nuevo

El fichero `agentkit/example_protocol.json` es un protocolo completo para un control manufacturado. Usarlo sólo como demostración de esquema. Para investigación, escribir un protocolo nuevo con tarea, modelo, unidades, todos los criterios, política de reserva y presupuesto propios, usando las reglas anteriores.

Ejemplo de conservación de entradas del kit:

```powershell
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.evidence --root . snapshot --paths agentkit/numerics.py agentkit/learning.py agentkit/mesh.py --out resultados/agent/source_snapshot.json
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.evidence --root . freeze --protocol agentkit/example_protocol.json --sources agentkit/numerics.py --out resultados/agent/manufactured_protocol_freeze.json
```

`evaluate_receipt` exige identidad de protocolo, ejecución completa, raw artifacts y todos los criterios. Sus recibos son auditorías mecánicas propias: una auditoría independiente debe recalcular métricas sin importar el evaluador original y revisar el alcance.

## 32. Lista final de aceptación y bloqueos

Antes de cerrar la entrega, el agente debe producir:

- Estado actualizado de T01–T22, con enlaces a evidencia y dependencias.
- Resolución o informe operacional de F1, sin reaprovechar una ventana vencida.
- Cierre o negativo preservado de convergencia, fase, modos, acopladores y reducción.
- Material medido o bloqueo explícito por muestra/metrología.
- Función de red definida y evaluación reservada con referencias convergidas.
- Compilador con transferencia reconstruida y geometría validada, o estado parcial.
- Medidas de fabricación, integración y energía cuando existan; protocolos y bloqueos cuando no.
- Tabla de novedad con fuentes originales y reivindicación central corregida.
- Código completo, instrucciones reproducibles y pruebas pertinentes.
- Manuscrito en inglés, figuras verificadas y datos accesibles.
- Autores, licencia y release consistentes con la autorización.
- Reproducción externa y seguimiento de impacto como estados externos, no autoaprobados.

Cada negativo debe tener una conclusión útil y próxima acción. Si un requisito físico no está disponible, la entrega final puede ser un estudio numérico terminado con protocolos de fabricación completos; mantener el proyecto físico abierto.

## 33. Validación de esta entrega

Se ejecutaron 32 pruebas del kit: balances coherentes, norma de masa, operador disipativo, residual integrado, error de detector, sensibilidad de Fréchet, fase absoluta, Strang reducido, predicción/reserva S16, transporte, síntesis pasiva, rechazo de ganancia, checkpoints y corrupción, preprocesado sin fuga, gradientes de seis modelos, estadísticas pareadas, pérdidas y energía, y timeout del supervisor.

También se ejecutaron recorridos CLI de demostración, propagación resumible, pronóstico manufacturado, compilación, regresión de cutback, preparación de datos y entrenamiento/evaluación de un control de desarrollo. El candidato unitario de ese control convergió con gradiente máximo ≈ 6,6·10⁻⁸. **Ese resultado no es un nuevo experimento confirmatorio del proyecto**: usa dígitos de desarrollo y una partición/preprocesado nuevos.

Las pruebas se hicieron en CPU/Linux y el entorno declarado en 3.2. No se ejecutaron aquí los ensayos largos D16, GPU, Maxwell 3D, Lean, fabricación ni medidas físicas. El agente debe validar el kit en el entorno fijado y cumplir las tareas científicas; aprobar estos controles no equivale a completar el proyecto.

> **Adición v2 (revalidación del 12-10-2026).** Se repitieron todas las comprobaciones v1 en Python 3.13.16 sobre Linux: 32/32 pruebas, los recorridos CLI de §31 y la cifra de gradiente de este párrafo (reproducida en el arranque 1; ver la nota de §16 sobre qué arranque se selecciona). Detalle y resultados v2 en §37 y §49.

## 34. Fuentes primarias y enlaces de lectura

### Repositorio del proyecto

- [Repositorio](https://github.com/Agnuxo1/Silice-Neuro3D-Cube).
- [Contrato S16 revisado](https://github.com/Agnuxo1/Silice-Neuro3D-Cube/blob/309d705e873448e4e05f2efbbc0dcc98613e9e68/Docs/POINT-03-D16-SPATIAL-CONTRACT.md).
- [Corrección de estados](https://github.com/Agnuxo1/Silice-Neuro3D-Cube/blob/c9b76d43c4f707d0b0754b77b0de5363426075e9/Docs/CORRECCION-ESTADOS-20261011.md).
- [Red y bloqueados](https://github.com/Agnuxo1/Silice-Neuro3D-Cube/blob/c9b76d43c4f707d0b0754b77b0de5363426075e9/Docs/T12-CIERRE-Y-BLOQUEADOS-20261011.md).
- [Novedad actual](https://github.com/Agnuxo1/Silice-Neuro3D-Cube/blob/c9b76d43c4f707d0b0754b77b0de5363426075e9/Docs/NOVEDAD-ESTADO-20261011.md).

### OpenAI math, commit consultado

- [README y estados de verificación](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/README.md).
- [Catálogo](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/CONTENTS.md).
- [Historial de correcciones](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/history.md).
- [Brenier: manuscrito](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Sharp-One-Third-Stability-of-Brenier-Maps-September-25-2026/article.pdf).
- [Brenier: enunciado e hipótesis](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Sharp-One-Third-Stability-of-Brenier-Maps-September-25-2026/build/source/sections/introduction.tex).
- [Brenier: paso de potenciales a mapas](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Sharp-One-Third-Stability-of-Brenier-Maps-September-25-2026/build/source/sections/gradient.tex).
- [Alcance Lean de Brenier](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/374.md).
- [Multiplicación matricial: fuente TeX](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Matrix-Multiplication-Nine-Fourths-October-2-2026/build/paper.tex).
- [Alcance Lean de multiplicación](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/107.md).
- [Instrucciones Comparator](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/ComparatorChallenges/README.md).

### Métodos y antecedentes

- Bao, Ma y Wang: [errores de splitting con baja regularidad](https://arxiv.org/abs/2308.15089), versión revisada 2024; texto/resumen consultados para hipótesis y alcance.
- [Control de convergencia espacial, NASA](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html); guía metodológica, no garantía automática para T96.
- [Estimación orientada al observable para Helmholtz](https://doi.org/10.1007/s00466-010-0557-2); consultar formulación y supuestos antes de trasladarlos.
- Trefethen: [pseudospectros de operadores lineales](https://people.maths.ox.ac.uk/trefethen/publication/PDF/1997_72.pdf).
- [SciPy 1.15.1: expm_frechet](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.linalg.expm_frechet.html).
- [SciPy 1.15.1: eig](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.linalg.eig.html).
- [SciPy 1.15.1: expm_multiply](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.sparse.linalg.expm_multiply.html).
- Clements et al.: [síntesis de interferómetros universales](https://arxiv.org/abs/1603.08788).
- Kondratyev et al.: [interferómetro fs programable](https://arxiv.org/abs/2308.13452).
- Cao et al.: [red fotónica 3D programable](https://www.nature.com/articles/s41467-026-72316-9); artículo original consultado, con separación de métricas teóricas y medidas.
- [SK1310: identificación del artículo](https://doi.org/10.1016/j.optmat.2025.116651); texto completo pendiente en la evidencia del proyecto.

> **Adición v2 (§47 E8).** La referencia de Helmholtz anterior es L. M. Steffens, N. Parés y P. Díez, «Goal-oriented h-adaptivity for the Helmholtz equation: error estimates, local indicators and refinement strategies», *Computational Mechanics* 47(6), 681–699 (2011); el DOI citado es correcto aunque contiene «2010». La lista completa de referencias verificadas está en §46.

Las propuestas de adopción, protocolos nuevos y código del kit son trabajo de esta guía. No atribuirlos como implementaciones oficiales de OpenAI math ni como resultados experimentales de los autores citados.

## 35. Código completo del kit

Los bloques siguientes contienen los archivos enteros. No hay funciones vacías ni implementaciones omitidas. El código hace explícitas sus limitaciones de tamaño/modelo y rechaza entradas incompatibles. Todos los archivos se extraen con el procedimiento de 3.3.


### Archivo: extract_agentkit.py

```python file=extract_agentkit.py
"""Extract the complete agent kit embedded in the companion Markdown guide.

Only labeled files are extracted. Existing different files, traversal,
symlinks and unexpected file types are rejected before anything is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


def extract(guide: Path, destination: Path) -> dict:
    """Create the labeled source files after validating the whole batch."""
    text = guide.read_text(encoding="utf-8")
    fence = chr(96) * 3
    pattern = re.compile(
        r"^" + fence + r"(python|json|text) file=([A-Za-z0-9_./-]+)\r?\n"
        r"(.*?)^" + fence + r"\s*$", re.MULTILINE | re.DOTALL)
    root = destination.resolve()
    entries = []
    seen = set()
    for match in pattern.finditer(text):
        language, name, source = match.groups()
        rel = Path(name)
        if name in seen or rel.is_absolute() or ".." in rel.parts:
            raise ValueError("Duplicate or unsafe source path")
        seen.add(name)
        if not (name == "extract_agentkit.py" or name.startswith("agentkit/")
                or name == "tests/test_agentkit.py"):
            raise ValueError("Path is outside the declared kit")
        expected = {"python": ".py", "json": ".json", "text": ".txt"}[language]
        if rel.suffix != expected:
            raise ValueError("Source language and extension disagree")
        path = root / rel
        current = root
        for part in rel.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError("Source destination must not be a symlink")
        data = source.encode("utf-8")
        if path.exists() and (not path.is_file() or path.read_bytes() != data):
            raise FileExistsError("Refusing to overwrite different file: " + name)
        entries.append((name, path, data))
    if len(entries) < 10:
        raise ValueError("Guide is incomplete or its labeled code blocks are missing")
    for name, path, data in entries:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with path.open("xb") as output:
                output.write(data)
    manifest = {"guide_sha256": hashlib.sha256(guide.read_bytes()).hexdigest(),
                "files": {name: hashlib.sha256(data).hexdigest()
                          for name, _, data in entries}}
    print(json.dumps(manifest, indent=2))
    return manifest


def main() -> None:
    """Extract into the already reviewed isolated checkout."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--guide", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    extract(args.guide, args.destination)


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/__init__.py

```python file=agentkit/__init__.py
"""Scientific closure support for Silice-Neuro3D-Cube."""

__version__ = "1.0.0"
```

### Archivo: agentkit/requirements.txt

```text file=agentkit/requirements.txt
numpy==2.2.6
scipy==1.15.1
scikit-learn==1.6.1
matplotlib==3.10.0
```

### Archivo: agentkit/tasks.json

```json file=agentkit/tasks.json
{
  "schema": 1,
  "review_date": "2026-10-12",
  "note": "Baseline planning registry. It does not itself close tasks or replace their protocols. Development may proceed independently; PASS respects its declared scope and prerequisites.",
  "tasks": [
    {
      "id": "T01",
      "title": "Track convergence and F1 recovery",
      "scope": "numerical_wave_model",
      "requires": [],
      "status": "OPEN",
      "baseline_only": true
    },
    {
      "id": "T02",
      "title": "Complete modal sweep",
      "scope": "numerical_wave_model",
      "requires": [
        "T01"
      ],
      "status": "PARTIAL",
      "baseline_only": true
    },
    {
      "id": "T03",
      "title": "Boundary domain complex field and phase",
      "scope": "numerical_wave_model",
      "requires": [
        "T01"
      ],
      "status": "PARTIAL",
      "baseline_only": true
    },
    {
      "id": "T04",
      "title": "Coherent modal decomposition",
      "scope": "numerical_wave_model",
      "requires": [
        "T02",
        "T03"
      ],
      "status": "PARTIAL",
      "baseline_only": true
    },
    {
      "id": "T05",
      "title": "Measured material and geometry",
      "scope": "measured_material",
      "requires": [],
      "status": "BLOCKED",
      "baseline_only": true
    },
    {
      "id": "T06",
      "title": "Independent vectorial comparison",
      "scope": "numerical_wave_model",
      "requires": [
        "T02",
        "T03"
      ],
      "status": "PARTIAL",
      "baseline_only": true
    },
    {
      "id": "T07",
      "title": "Coherent two-guide coupler",
      "scope": "numerical_wave_model",
      "requires": [
        "T01",
        "T03",
        "T04",
        "T06"
      ],
      "status": "PARTIAL",
      "baseline_only": true
    },
    {
      "id": "T08",
      "title": "Bends crossings and 3D routing",
      "scope": "numerical_wave_model",
      "requires": [
        "T03",
        "T06",
        "T07"
      ],
      "status": "PARTIAL",
      "baseline_only": true
    },
    {
      "id": "T09",
      "title": "Deep writing and face registration",
      "scope": "physical_component",
      "requires": [
        "T05"
      ],
      "status": "BLOCKED",
      "baseline_only": true
    },
    {
      "id": "T10",
      "title": "Phase stability and control",
      "scope": "physical_component",
      "requires": [
        "T05",
        "T07"
      ],
      "status": "PARTIAL",
      "baseline_only": true
    },
    {
      "id": "T11",
      "title": "Fabricable network compiler",
      "scope": "fabricable_design",
      "requires": [
        "T05",
        "T07",
        "T08",
        "T09",
        "T10"
      ],
      "status": "PARTIAL",
      "baseline_only": true
    },
    {
      "id": "T12",
      "title": "Complete neural function",
      "scope": "numerical_neural_model",
      "requires": [
        "T07",
        "T10"
      ],
      "status": "FAIL",
      "baseline_only": true
    },
    {
      "id": "T13",
      "title": "Manufactured calibration samples and network",
      "scope": "physical_device",
      "requires": [
        "T05",
        "T09",
        "T11"
      ],
      "status": "BLOCKED",
      "baseline_only": true
    },
    {
      "id": "T14",
      "title": "Calibrated optical measurements",
      "scope": "physical_component",
      "requires": [
        "T13"
      ],
      "status": "BLOCKED",
      "baseline_only": true
    },
    {
      "id": "T15",
      "title": "Integrated optical electronic and control system",
      "scope": "physical_system",
      "requires": [
        "T12",
        "T13",
        "T14"
      ],
      "status": "BLOCKED",
      "baseline_only": true
    },
    {
      "id": "T16",
      "title": "Independent reserved task and baselines",
      "scope": "independent_evaluation",
      "requires": [
        "T12"
      ],
      "status": "PARTIAL",
      "baseline_only": true
    },
    {
      "id": "T17",
      "title": "Whole-system performance and energy",
      "scope": "physical_system_measurement",
      "requires": [
        "T15",
        "T16"
      ],
      "status": "BLOCKED",
      "baseline_only": true
    },
    {
      "id": "T18",
      "title": "Scaling and between-device reproducibility",
      "scope": "physical_system_measurement",
      "requires": [
        "T14",
        "T15",
        "T17"
      ],
      "status": "PARTIAL",
      "baseline_only": true
    },
    {
      "id": "T19",
      "title": "Verified original contribution versus literature",
      "scope": "scientific_claim",
      "requires": [],
      "status": "OPEN",
      "baseline_only": true
    },
    {
      "id": "T20",
      "title": "Central contribution and decisive evidence",
      "scope": "scientific_claim",
      "requires": [
        "T19"
      ],
      "status": "OPEN",
      "baseline_only": true
    },
    {
      "id": "T21",
      "title": "External reproduction and review",
      "scope": "external_replication",
      "requires": [
        "T20"
      ],
      "status": "BLOCKED",
      "baseline_only": true
    },
    {
      "id": "T22",
      "title": "Sustained observed impact",
      "scope": "observed_impact",
      "requires": [
        "T21"
      ],
      "status": "OPEN",
      "baseline_only": true
    }
  ]
}
```

### Archivo: agentkit/example_protocol.json

```json file=agentkit/example_protocol.json
{
  "experiment_id": "manufactured_controls_v1",
  "task_id": "T01",
  "scope": "manufactured_control",
  "model": "analytic_fixture",
  "units": {
    "length": "m",
    "power": "relative_to_input"
  },
  "criteria": [
    {
      "id": "holdout_passed",
      "operator": "eq",
      "threshold": true
    }
  ],
  "resource_limits": {
    "cpu_threads": 1,
    "seconds": 40,
    "gpu": false
  },
  "heldout_policy": "Known analytic law; never used as a T96 result"
}
```

### Archivo: agentkit/analyze.py

```python file=agentkit/analyze.py
"""Command-line access to independent scalar S16 and coherent-field controls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from agentkit.evidence import sha256_file, write_new_json
from agentkit.numerics import (coherent_decomposition, spatial_forecast,
                               spatial_holdout, transfer_sensitivity)
from agentkit.mesh import complex_pairs


def main() -> None:
    """Analyze explicit JSON or reduced NPZ inputs and preserve new output."""
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("forecast", "holdout", "decomposition", "sensitivity"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.kind in ("forecast", "holdout"):
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if set(payload["observables"]) != {"quadratic_field", "linear_intensity"}:
            raise ValueError("Both prescribed S16 observables are required")
        if args.kind == "forecast":
            result = {name: spatial_forecast(item["powers"], item["temporal_errors"])
                      for name, item in payload["observables"].items()}
            result = {"observables": result,
                      "eligible": len(result) == 2 and all(v["eligible"] for v in result.values())}
        else:
            result = {name: spatial_holdout(**item)
                      for name, item in payload["observables"].items()}
            result = {"observables": result,
                      "passed": len(result) == 2 and all(v["passed"] for v in result.values())}
    else:
        with np.load(args.input, allow_pickle=False) as data:
            if args.kind == "decomposition":
                values = coherent_decomposition(data["field"], data["basis"], data["mass"],
                                                data["dual"] if "dual" in data else None)
                result = {key: complex_pairs(value) if isinstance(value, np.ndarray) else value
                          for key, value in values.items()}
            else:
                values = transfer_sensitivity(data["generator"], data["perturbation"],
                                              float(data["length_m"].item()))
                result = {key: complex_pairs(value) if isinstance(value, np.ndarray) else value
                          for key, value in values.items()}
    result["input_sha256"] = sha256_file(args.input)
    result["scope"] = "reduced_model_diagnostic"
    write_new_json(args.out, result)
    print(json.dumps({key: value for key, value in result.items()
                      if key in ("eligible", "passed", "scope", "input_sha256")}))


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/checkpoint.py

```python file=agentkit/checkpoint.py
"""Atomic numerical checkpoints with input hashes and an explicit hash chain."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import uuid

import numpy as np

from agentkit.evidence import canonical, sha256_file, utc_now


def save_checkpoint(directory: Path, state, step: int, total_steps: int,
                    experiment_hash: str, previous_metadata_hash: str | None) -> Path:
    """Commit a new state; metadata is the final commit marker."""
    if type(step) is not int or type(total_steps) is not int or not 0 <= step <= total_steps:
        raise ValueError("Checkpoint step must lie inside the planned trajectory")
    array = np.asarray(state)
    if array.dtype != np.complex128 or not np.all(np.isfinite(array)):
        raise ValueError("Checkpoint state must be finite complex128")
    if not isinstance(experiment_hash, str) or len(experiment_hash) != 64:
        raise ValueError("Experiment must have a SHA-256 identity")
    directory.mkdir(parents=True, exist_ok=True)
    final = directory / f"step_{step:08d}.json"
    if final.exists():
        raise FileExistsError("A committed checkpoint already exists")
    token = uuid.uuid4().hex
    array_path = directory / f"state_{step:08d}_{token}.npz"
    with array_path.open("xb") as stream:
        np.savez_compressed(stream, state=array)
        stream.flush()
        os.fsync(stream.fileno())
    record = {"schema": 1, "step": step, "total_steps": total_steps,
              "experiment_hash": experiment_hash,
              "previous_metadata_hash": previous_metadata_hash,
              "array_file": array_path.name, "array_sha256": sha256_file(array_path),
              "dtype": str(array.dtype), "shape": list(array.shape),
              "created_utc": utc_now()}
    temp = directory / (final.name + "." + token + ".tmp")
    with temp.open("xb") as stream:
        stream.write(canonical(record) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    # Exclusive hard-link publication prevents overwriting a concurrent writer.
    try:
        os.link(temp, final)
    finally:
        temp.unlink(missing_ok=True)
    return final


def load_latest(directory: Path, experiment_hash: str, total_steps: int):
    """Validate the entire committed chain and return its last retained state."""
    paths = sorted(directory.glob("step_*.json"))
    if not paths:
        return None
    previous_hash = None
    previous_step = -1
    previous_shape = None
    last_state = None
    for path in paths:
        if path.is_symlink():
            raise ValueError("Checkpoint metadata must not be a symlink")
        record = json.loads(path.read_text(encoding="utf-8"))
        step = record["step"]
        if record["experiment_hash"] != experiment_hash or record["total_steps"] != total_steps:
            raise ValueError("Checkpoint configuration changed")
        if step <= previous_step or step > total_steps or (previous_step == -1 and step != 0):
            raise ValueError("Checkpoint chain has invalid step ordering")
        if path.name != f"step_{step:08d}.json":
            raise ValueError("Checkpoint filename and step disagree")
        if record["previous_metadata_hash"] != previous_hash:
            raise ValueError("Checkpoint metadata chain is broken")
        name = record["array_file"]
        if Path(name).name != name or Path(name).is_absolute():
            raise ValueError("Checkpoint array path escapes its directory")
        array_path = directory / name
        if array_path.is_symlink() or sha256_file(array_path) != record["array_sha256"]:
            raise ValueError("Checkpoint array changed")
        with np.load(array_path, allow_pickle=False) as data:
            last_state = data["state"].copy()
        if (last_state.dtype != np.complex128 or
                list(last_state.shape) != record["shape"] or
                record["dtype"] != "complex128" or
                not np.all(np.isfinite(last_state))):
            raise ValueError("Checkpoint state failed validation")
        if previous_shape is not None and tuple(last_state.shape) != previous_shape:
            raise ValueError("Checkpoint state shape changed inside the trajectory")
        previous_shape = tuple(last_state.shape)
        previous_step, previous_hash = step, sha256_file(path)
    return last_state, previous_step, previous_hash
```

### Archivo: agentkit/demo.py

```python file=agentkit/demo.py
"""Generate bounded manufactured controls; no data are physical measurements."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm

from agentkit.evidence import canonical, write_new_json
from agentkit.mesh import compile_passive
from agentkit.metrology import fit_cutback, system_energy
from agentkit.numerics import (coherent_decomposition, exact_discrete_transport,
                               generalized_modes, optical_error_budget,
                               splitting_control, spatial_forecast, spatial_holdout)
from agentkit.paraxial import grid, disk_area_weights


def run_demo(directory: Path) -> dict:
    """Create explicit control inputs and reports in a fresh directory."""
    if directory.exists():
        raise FileExistsError("Manufactured-control directory must be new")
    directory.mkdir(parents=True)
    (x, y), dx = grid(32, 64e-6)
    field = np.exp(-(x*x+y*y)/(6e-6)**2).astype(np.complex128)
    field /= np.sqrt(np.sum(abs(field)**2)*dx*dx)
    radius = np.hypot(x, y)
    profile = np.where((radius >= 6e-6) & (radius < 12e-6), -0.005, 0.0)
    with (directory/"paraxial_input.npz").open("xb") as output:
        np.savez_compressed(output, field=field, delta_n=profile)
    write_new_json(directory/"paraxial_config.json",
                   {"width_m": 64e-6, "wavelength_m": 1550e-9,
                    "n_reference": 1.444, "length_m": 100e-6, "steps": 32})
    a = 1j*np.array([[0.2, 0.5], [0.5, -0.3]])
    b = 1j*np.diag([0.7, -0.2])
    split = [splitting_control(a, b, np.array([1, 1j])/np.sqrt(2), 1.0, n)
             for n in (4, 8, 16)]
    operator = np.array([[1, 4], [0, 2]], dtype=complex)
    modes = generalized_modes(operator, np.ones(2))
    decomposition = coherent_decomposition(np.array([0.3, 0.7j]),
                                           modes["right"][:, :1], np.ones(2),
                                           modes["left"][:, :1])
    target = expm(1j*np.array([[0.2, 0.4], [0.4, -0.1]])) @ np.diag([0.8, 0.5])
    with (directory/"target.npz").open("xb") as output:
        np.savez_compressed(output, target=target)
    compiled = compile_passive(target)
    source = np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=float)
    transport = exact_discrete_transport(source, np.full(4, 0.25),
                                         source+np.array([0.1, 0.0]), np.full(4, 0.25))
    h = np.array([1, 0.8, 0.64, 0.512])
    powers = 0.333 + 0.002*h**2
    forecast = spatial_forecast(powers[:3], np.full(3, 1e-10))
    holdout = spatial_holdout(powers[:3], np.full(3, 1e-10), powers[3],
                             1e-10, 1e-10, 1e-10)
    rows = []
    for chip, slope in enumerate((0.09, 0.10, 0.11)):
        for length_cm in (1, 2, 3, 4):
            loss_db = 0.4 + slope*length_cm
            rows.append({"chip_id": str(chip), "guide_id": "manufactured",
                         "length_m": length_cm/100, "wavelength_m": 1550e-9,
                         "polarization": "x", "input_power_w": 1e-3,
                         "output_power_w": 1e-3*10**(-loss_db/10), "sigma_loss_db": 0.005})
    with (directory/"manufactured_cutback.csv").open("x", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    energy_rows = [{"time_s": i, "completed_inferences": i*1000,
                    "source_w": 1, "modulation_w": 0.2, "detection_w": 0.1,
                    "control_w": 0.3, "cooling_w": 0.4} for i in range(3)]
    summary = {"scope": "manufactured_controls_only",
               "splitting_errors": [s["relative_field_error"] for s in split],
               "coherent_balance_error": decomposition["balance_error"],
               "coherent_cross_power": decomposition["cross_power"],
               "compiler_error": compiled["reconstruction_error"],
               "transport_wasserstein2": transport["wasserstein2"],
               "forecast": forecast, "holdout": holdout,
               "optical_path_budget": optical_error_budget(1.444, 0.01, 1550e-9, 1e-6, 1e-9),
               "detector_area_m2": float(disk_area_weights(32, 64e-6, 6e-6, 16).sum()),
               "manufactured_cutback": fit_cutback(rows),
               "manufactured_energy": system_energy(energy_rows)}
    write_new_json(directory/"summary.json", summary)
    write_new_json(directory/"S16_manufactured.json",
                   {"observables": {"quadratic_field": {
                       "powers": powers[:3].tolist(), "temporal_errors": [1e-10]*3},
                       "linear_intensity": {"powers": powers[:3].tolist(),
                                            "temporal_errors": [1e-10]*3}}})
    protocol = {"experiment_id": "manufactured_controls_v1", "task_id": "T01",
                "scope": "manufactured_control", "model": "analytic_fixture",
                "units": {"length": "m", "power": "relative_to_input"},
                "criteria": [{"id": "holdout_passed", "operator": "eq", "threshold": True}],
                "resource_limits": {"cpu_threads": 1, "seconds": 40, "gpu": False},
                "heldout_policy": "Known analytic law; never used as a T96 result"}
    write_new_json(directory/"protocol.json", protocol)
    protocol_hash = hashlib.sha256(canonical(protocol)).hexdigest()
    result = {"experiment_id": protocol["experiment_id"], "scope": protocol["scope"],
              "protocol_sha256": protocol_hash, "status": "completed",
              "artifacts": ["summary.json"],
              "metrics": {"holdout_passed": bool(holdout["passed"])}}
    # This result is an explicit schema fixture, not a prospective research receipt.
    write_new_json(directory/"result_schema_fixture.json", result)
    return summary


def main() -> None:
    """Run the manufactured demonstration without importing any GPU library."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    summary = run_demo(args.directory)
    print(json.dumps({"scope": summary["scope"], "compiler_error": summary["compiler_error"],
                      "holdout_passed": summary["holdout"]["passed"]}))


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/evidence.py

```python file=agentkit/evidence.py
"""Immutable evidence receipts, protocols and task-status checks.

This module does not certify optical physics. It checks whether a recorded
claim has the declared prerequisites, criteria and retained evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    """Return an unambiguous UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    """Hash a file without loading large numerical arrays into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: Any) -> bytes:
    """Serialize JSON deterministically and reject non-finite values."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      allow_nan=False, separators=(",", ":")).encode("utf-8")


def write_new_json(path: Path, value: Any) -> None:
    """Write a new durable JSON record and refuse to overwrite evidence."""
    data = canonical(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def inside(root: Path, relative: str) -> Path:
    """Resolve a regular file beneath root, rejecting traversal and symlinks."""
    root = root.resolve()
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts:
        raise ValueError("Evidence paths must be relative and remain inside root")
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlinks are not accepted as evidence")
    current = current.resolve()
    if not current.is_relative_to(root) or not current.is_file():
        raise ValueError("Evidence must be an existing regular file inside root")
    return current


def snapshot(root: Path, relative_paths: list[str]) -> dict[str, Any]:
    """Record exact bytes of a reviewed, explicit list of inputs."""
    if not relative_paths or len(set(relative_paths)) != len(relative_paths):
        raise ValueError("Input paths must be nonempty and unique")
    return {"created_utc": utc_now(), "files": {
        name: {"sha256": sha256_file(inside(root, name)),
               "size": inside(root, name).stat().st_size}
        for name in sorted(relative_paths)}}


def verify_snapshot(root: Path, record: dict[str, Any]) -> None:
    """Reject missing files, changed bytes and malformed snapshots."""
    files = record.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("Snapshot has no input files")
    for name, info in files.items():
        path = inside(root, name)
        if path.stat().st_size != info["size"] or sha256_file(path) != info["sha256"]:
            raise ValueError("Input bytes changed: " + name)


def git_identity(root: Path) -> dict[str, str]:
    """Read the actual checkout identity without changing the repository."""
    def run(arguments: list[str]) -> str:
        result = subprocess.run(["git", "-C", str(root), *arguments],
                                capture_output=True, text=True, check=True)
        return result.stdout.rstrip()
    return {"head": run(["rev-parse", "HEAD"]),
            "branch": run(["branch", "--show-current"]),
            "status": run(["status", "--porcelain=v1", "-z"])}


def freeze(root: Path, protocol_path: str, sources: list[str],
           receipt_path: Path) -> dict[str, Any]:
    """Freeze a protocol and its sources before generating new data."""
    protocol_file = inside(root, protocol_path)
    protocol = json.loads(protocol_file.read_text(encoding="utf-8"))
    required = {"experiment_id", "task_id", "model", "units", "criteria",
                "resource_limits", "heldout_policy", "scope"}
    if not required.issubset(protocol):
        raise ValueError("Protocol is missing required fields")
    if not protocol["criteria"] or not isinstance(protocol["criteria"], list):
        raise ValueError("Protocol must declare explicit acceptance criteria")
    ids = [entry["id"] for entry in protocol["criteria"]]
    if len(set(ids)) != len(ids):
        raise ValueError("Criterion identifiers must be unique")
    for entry in protocol["criteria"]:
        if entry.get("operator") not in ("le", "ge", "eq"):
            raise ValueError("Unsupported criterion operator")
        threshold = entry["threshold"]
        if isinstance(threshold, bool):
            if entry["operator"] != "eq":
                raise ValueError("Boolean criteria must use equality")
        elif not isinstance(threshold, (int, float)) or not math.isfinite(threshold):
            raise ValueError("Criterion threshold must be finite or boolean")
    names = list(dict.fromkeys([protocol_path, *sources]))
    record = {"schema": 1, "kind": "prospective_protocol",
              "protocol_path": protocol_path, "protocol": protocol,
              "inputs": snapshot(root, names), "git": git_identity(root)}
    write_new_json(receipt_path, record)
    return record


def evaluate_receipt(root: Path, freeze_record: dict[str, Any],
                     result: dict[str, Any]) -> dict[str, Any]:
    """Evaluate every frozen criterion; missing and non-finite data fail."""
    if freeze_record.get("kind") != "prospective_protocol":
        raise ValueError("A frozen protocol receipt is required")
    verify_snapshot(root, freeze_record["inputs"])
    protocol = freeze_record["protocol"]
    if result.get("experiment_id") != protocol["experiment_id"]:
        raise ValueError("Result belongs to another experiment")
    if result.get("protocol_sha256") != hashlib.sha256(
            canonical(protocol)).hexdigest():
        raise ValueError("Result does not identify the frozen protocol")
    if result.get("scope") != protocol["scope"]:
        raise ValueError("Result scope differs from the protocol")
    if result.get("status") != "completed":
        raise ValueError("Partial or failed execution cannot pass")
    artifacts = result.get("artifacts", [])
    if not artifacts:
        raise ValueError("A result must retain raw artifacts")
    artifact_snapshot = snapshot(root, artifacts)
    metrics = result.get("metrics", {})
    checks = []
    for criterion in protocol["criteria"]:
        name = criterion["id"]
        value = metrics.get(name)
        threshold = criterion["threshold"]
        valid = (isinstance(value, bool) if isinstance(threshold, bool)
                 else isinstance(value, (int, float)) and
                 not isinstance(value, bool) and math.isfinite(value))
        passed = False
        if valid:
            op = criterion["operator"]
            passed = (value <= threshold if op == "le" else
                      value >= threshold if op == "ge" else value == threshold)
        checks.append({"id": name, "value": value, "threshold": threshold,
                       "operator": criterion["operator"],
                       "evaluated": valid, "passed": bool(passed)})
    return {"schema": 1, "created_utc": utc_now(),
            "experiment_id": protocol["experiment_id"],
            "task_id": protocol["task_id"], "scope": result["scope"],
            "checks": checks, "passed": all(c["passed"] for c in checks),
            "artifacts": artifact_snapshot,
            "note": "Mechanical receipt validation; not independent replication."}


def closure_status(task: dict[str, Any], audit: dict[str, Any],
                   dependency_status: dict[str, str]) -> str:
    """Keep passing numerical records separate from physical/external closure."""
    if task["scope"] != audit["scope"]:
        return "BLOCKED_SCOPE"
    if any(dependency_status.get(dep) != "PASS"
           for dep in task.get("requires", [])):
        return "BLOCKED_DEPENDENCY"
    return "PASS" if audit.get("passed") is True else "FAIL"


def main() -> None:
    """Expose snapshot, freeze and audit as explicit read/write operations."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    snap = commands.add_parser("snapshot")
    snap.add_argument("--paths", nargs="+", required=True)
    snap.add_argument("--out", type=Path, required=True)
    frozen = commands.add_parser("freeze")
    frozen.add_argument("--protocol", required=True)
    frozen.add_argument("--sources", nargs="+", required=True)
    frozen.add_argument("--out", type=Path, required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("--freeze", type=Path, required=True)
    audit.add_argument("--result", type=Path, required=True)
    audit.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "snapshot":
        write_new_json(args.out, snapshot(args.root, args.paths))
    elif args.command == "freeze":
        freeze(args.root, args.protocol, args.sources, args.out)
    else:
        read = lambda p: json.loads(p.read_text(encoding="utf-8"))
        value = evaluate_receipt(args.root, read(args.freeze), read(args.result))
        write_new_json(args.out, value)
        print(json.dumps({"passed": value["passed"]}))
        if not value["passed"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/learning.py

```python file=agentkit/learning.py
"""Prospective train/validation/test workflow with analytic complex gradients.

The built-in digit dataset is a development control, not pristine independent
evidence for this project. External final data need a provenance review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.linalg import expm, expm_frechet
from scipy.optimize import minimize
from scipy.special import logsumexp

from agentkit.evidence import sha256_file, write_new_json


MODELS = ("unitary", "real", "unitary_abs", "real_abs",
          "unitary_mzm", "real_mzm")


def hermitian_basis(n: int) -> np.ndarray:
    """Build n squared real directions spanning all Hermitian matrices."""
    if type(n) is not int or not 2 <= n <= 8:
        raise ValueError("Learning reference supports dimensions 2 through 8")
    basis = []
    for i in range(n):
        b = np.zeros((n, n), complex)
        b[i, i] = 1
        basis.append(b)
    for i in range(n):
        for j in range(i+1, n):
            b = np.zeros((n, n), complex)
            b[i, j] = b[j, i] = 1
            basis.append(b)
    for i in range(n):
        for j in range(i+1, n):
            b = np.zeros((n, n), complex)
            b[i, j], b[j, i] = 1j, -1j
            basis.append(b)
    return np.asarray(basis)


def transfer(parameters, n: int, unitary: bool, derivatives: bool):
    """Return a real matrix or an exact exponential unitary and its derivatives."""
    p = np.asarray(parameters, dtype=float)
    if p.shape != (n*n,) or not np.all(np.isfinite(p)):
        raise ValueError("Transfer parameter count is invalid")
    if not unitary:
        matrix = p.reshape(n, n)
        basis = np.eye(n*n).reshape(n*n, n, n) if derivatives else None
        return matrix, basis
    basis = hermitian_basis(n)
    h = np.einsum("k,kij->ij", p, basis)
    matrix = expm(1j * h)
    ds = (np.array([expm_frechet(1j*h, 1j*b, compute_expm=False) for b in basis])
          if derivatives else None)
    return matrix, ds


def model_size(model: str, n: int) -> int:
    """Return the full declared parameter count."""
    if model not in MODELS:
        raise ValueError("Unknown model")
    return n*n * (2 if "_" in model else 1)


def scores_and_directions(parameters, x, model: str, v_pi: float = 1.0,
                          bias: float = 0.0, derivatives: bool = False):
    """Evaluate intensity scores and optional analytic parameter directions.

    Two-layer models detect and re-emit a positive real amplitude with zero
    reference phase. This requires optoelectronic hardware; it is not passive.
    The positive MZM amplitude reproduces the legacy square-root intensity
    model, not every physical MZM field convention.
    """
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or not np.all(np.isfinite(x)):
        raise ValueError("Inputs must be finite feature rows")
    n = x.shape[1]
    if not 2 <= n <= 8 or not np.all(np.isfinite(parameters)):
        raise ValueError("Dimension or parameters are invalid")
    if np.asarray(parameters).shape != (model_size(model, n),):
        raise ValueError("Wrong parameter count")
    if not math.isfinite(v_pi) or v_pi <= 0 or not math.isfinite(bias):
        raise ValueError("Activation controls must be finite and V_pi positive")
    is_unitary = model.startswith("unitary")
    first, d_first = transfer(parameters[:n*n], n, is_unitary, derivatives)
    z1 = x @ first.T
    i1 = abs(z1)**2
    if "_" not in model:
        directions = (np.array([2*np.real(np.conj(z1)*(x @ d.T)) for d in d_first])
                      if derivatives else None)
        return i1, directions
    if model.endswith("_abs"):
        amplitude = np.sqrt(i1)
        slope = np.divide(0.5, amplitude, out=np.zeros_like(amplitude),
                          where=amplitude > 1e-14)
    else:
        angle = 0.5 * (math.pi * i1 / v_pi + bias)
        cosine = np.cos(angle)
        amplitude = abs(cosine)
        slope = -0.5 * math.pi / v_pi * np.sin(angle) * np.sign(cosine)
    second, d_second = transfer(parameters[n*n:], n, is_unitary, derivatives)
    z2 = amplitude @ second.T
    scores = abs(z2)**2
    if not derivatives:
        return scores, None
    directions = []
    for direction in d_first:
        di1 = 2 * np.real(np.conj(z1) * (x @ direction.T))
        dz2 = (slope * di1) @ second.T
        directions.append(2 * np.real(np.conj(z2) * dz2))
    for direction in d_second:
        dz2 = amplitude @ direction.T
        directions.append(2 * np.real(np.conj(z2) * dz2))
    return scores, np.asarray(directions)


def objective(parameters, x, y, model: str, v_pi: float = 1.0, bias: float = 0.0):
    """Return cross-entropy and its exact Fréchet-based gradient."""
    scores, directions = scores_and_directions(parameters, x, model, v_pi, bias, True)
    y = np.asarray(y)
    if y.shape != (len(x),) or y.dtype.kind not in "iu" or y.min() < 0 or y.max() >= scores.shape[1]:
        raise ValueError("Labels must index the declared output classes")
    log_normalizer = logsumexp(scores, axis=1)
    loss = float(np.mean(log_normalizer - scores[np.arange(len(y)), y]))
    derivative = np.exp(scores-log_normalizer[:, None])
    derivative[np.arange(len(y)), y] -= 1
    derivative /= len(y)
    gradient = np.einsum("nc,knc->k", derivative, directions)
    return loss, gradient


def accuracy(parameters, x, y, model: str, v_pi: float, bias: float) -> float:
    """Evaluate fixed parameters; no training or selection occurs here."""
    scores, _ = scores_and_directions(parameters, x, model, v_pi, bias)
    return float(np.mean(scores.argmax(axis=1) == y))


def prepare_data(directory: Path, raw_path: Path | None = None, seed: int = 20261012) -> dict:
    """Freeze stratified 60/20/20 partitions and fit preprocessing on train only."""
    if directory.exists():
        raise FileExistsError("Data output directory must be new")
    if raw_path is None:
        from sklearn.datasets import load_digits
        dataset = load_digits()
        mask = np.isin(dataset.target, [0, 1, 2, 3])
        x, labels = dataset.data[mask], dataset.target[mask]
        provenance = "development_public_digits_already_used_in_project"
    else:
        with np.load(raw_path, allow_pickle=False) as data:
            x, labels = data["X"].copy(), data["y"].copy()
        provenance = "external_data_independence_requires_provenance_review"
    if x.ndim != 2 or not np.all(np.isfinite(x)) or labels.shape != (len(x),):
        raise ValueError("Raw data must have finite X feature rows and matching y")
    classes = np.unique(labels)
    if not 2 <= len(classes) <= 8 or x.shape[1] < len(classes):
        raise ValueError("Use 2 through 8 classes and at least that many features")
    y = np.searchsorted(classes, labels)
    rng = np.random.default_rng(seed)
    indices = {"train": [], "validation": [], "test": []}
    for label in range(len(classes)):
        values = np.flatnonzero(y == label)
        if len(values) < 15:
            raise ValueError("Each class requires at least 15 samples")
        values = rng.permutation(values)
        n_train, n_val = int(0.6*len(values)), int(0.2*len(values))
        indices["train"].extend(values[:n_train])
        indices["validation"].extend(values[n_train:n_train+n_val])
        indices["test"].extend(values[n_train+n_val:])
    indices = {name: np.sort(value) for name, value in indices.items()}
    train = x[indices["train"]].astype(float)
    mean, std = train.mean(axis=0), train.std(axis=0)
    std[std < 1e-12] = 1
    standardized = (train-mean)/std
    _, singular, vh = np.linalg.svd(standardized, full_matrices=False)
    components = vh[:len(classes)].copy()
    for component in components:
        if component[np.argmax(abs(component))] < 0:
            component *= -1
    if singular[len(classes)-1] < 1e-12:
        raise ValueError("Training PCA has insufficient effective rank")
    train_features = standardized @ components.T
    feature_scale = train_features.std(axis=0)
    feature_scale[feature_scale < 1e-12] = 1
    directory.mkdir(parents=True)
    for name, values in indices.items():
        features = (((x[values]-mean)/std) @ components.T) / feature_scale
        with (directory/(name+".npz")).open("xb") as output:
            np.savez_compressed(output, X=features, y=y[values], raw_indices=values)
    raw_hash = hashlib.sha256(np.ascontiguousarray(x).tobytes() +
                              np.ascontiguousarray(labels).tobytes()).hexdigest()
    record = {"seed": seed, "provenance": provenance, "raw_array_sha256": raw_hash,
              "raw_file_sha256": None if raw_path is None else sha256_file(raw_path),
              "classes": classes.tolist(), "mean": mean.tolist(), "std": std.tolist(),
              "pca_components": components.tolist(), "feature_scale": feature_scale.tolist(),
              "partition_hashes": {name: sha256_file(directory/(name+".npz")) for name in indices},
              "counts": {name: len(values) for name, values in indices.items()}}
    write_new_json(directory/"manifest.json", record)
    return record


def fit_candidate(train_path: Path, validation_path: Path, model: str,
                  seeds: list[int], maxiter: int, v_pi: float, bias: float,
                  gradient_threshold: float = 1e-5) -> dict:
    """Fit all registered starts and retain convergence diagnostics for every start."""
    if not seeds or len(set(seeds)) != len(seeds) or maxiter < 1:
        raise ValueError("Training starts and iteration count must be positive")
    with np.load(train_path, allow_pickle=False) as data:
        x, y = data["X"].copy(), data["y"].copy()
    with np.load(validation_path, allow_pickle=False) as data:
        xv, yv = data["X"].copy(), data["y"].copy()
    if xv.shape[1] != x.shape[1]:
        raise ValueError("Training and validation feature dimensions differ")
    records = []
    for seed in seeds:
        initial = 0.5 * np.random.default_rng(seed).standard_normal(model_size(model, x.shape[1]))
        result = minimize(objective, initial, args=(x, y, model, v_pi, bias),
                          jac=True, method="L-BFGS-B",
                          options={"maxiter": maxiter, "gtol": 1e-8, "ftol": 1e-12})
        loss, gradient = objective(result.x, x, y, model, v_pi, bias)
        norm = float(np.max(abs(gradient)))
        records.append({"seed": seed, "parameters": result.x.tolist(),
                        "training_loss": loss, "gradient_infinity_norm": norm,
                        "optimizer_success": bool(result.success),
                        "optimizer_message": str(result.message), "iterations": int(result.nit),
                        "converged": bool(result.success and norm <= gradient_threshold)})
    best = min(records, key=lambda item: item["training_loss"])
    parameters = np.asarray(best["parameters"])
    return {"model": model, "dimension": x.shape[1], "v_pi": v_pi, "bias": bias,
            "maxiter": maxiter, "gradient_threshold": gradient_threshold,
            "train_sha256": sha256_file(train_path),
            "validation_sha256": sha256_file(validation_path),
            "selected_by": "minimum_training_loss_across_registered_starts",
            "selected": best, "all_starts": records,
            "train_accuracy": accuracy(parameters, x, y, model, v_pi, bias),
            "validation_accuracy": accuracy(parameters, xv, yv, model, v_pi, bias),
            "test_evaluated": False, "scope": "numerical_optoelectronic_model"}


def evaluate_locked(candidate_path: Path, test_path: Path) -> dict:
    """Evaluate one frozen candidate; no refit or hyperparameter search is allowed."""
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    if not candidate["selected"]["converged"]:
        raise ValueError("Final evaluation requires the selected training run to converge")
    with np.load(test_path, allow_pickle=False) as data:
        x, y = data["X"].copy(), data["y"].copy()
    if x.shape[1] != candidate["dimension"]:
        raise ValueError("Test feature dimension disagrees with the frozen candidate")
    scores, _ = scores_and_directions(candidate["selected"]["parameters"], x,
                                     candidate["model"], candidate["v_pi"], candidate["bias"])
    predictions = scores.argmax(axis=1)
    return {"candidate_sha256": sha256_file(candidate_path),
            "test_sha256": sha256_file(test_path), "n_test": len(y),
            "accuracy": float(np.mean(predictions == y)),
            "predictions": predictions.tolist(), "labels": y.tolist(),
            "scope": "numerical_optoelectronic_model",
            "note": "Independence, one-time test access and experimental hardware remain separate requirements."}


def paired_accuracy(first, second, labels, repeats: int = 2000, seed: int = 20261012) -> dict:
    """Report the observed paired difference separately from bootstrap uncertainty."""
    a, b, y = map(np.asarray, (first, second, labels))
    if a.ndim != 1 or a.shape != b.shape or a.shape != y.shape or len(y) < 2 or repeats < 100:
        raise ValueError("Paired predictions must refer to the same nonempty test samples")
    difference = (a == y).astype(float) - (b == y).astype(float)
    rng = np.random.default_rng(seed)
    draws = np.array([difference[rng.integers(0, len(y), len(y))].mean()
                      for _ in range(repeats)])
    return {"observed_difference": float(difference.mean()),
            "bootstrap_mean": float(draws.mean()),
            "percentile_ci95": np.percentile(draws, [2.5, 97.5]).tolist(),
            "repeats": repeats, "seed": seed}


def main() -> None:
    """Prepare data, train without test access, or evaluate a frozen candidate."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--directory", type=Path, required=True)
    prepare.add_argument("--input", type=Path)
    prepare.add_argument("--seed", type=int, default=20261012)
    fit = commands.add_parser("fit")
    fit.add_argument("--train", type=Path, required=True)
    fit.add_argument("--validation", type=Path, required=True)
    fit.add_argument("--model", choices=MODELS, required=True)
    fit.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 9)))
    fit.add_argument("--maxiter", type=int, default=1000)
    fit.add_argument("--v-pi", type=float, default=1)
    fit.add_argument("--bias", type=float, default=0)
    fit.add_argument("--gradient-threshold", type=float, default=1e-5)
    fit.add_argument("--out", type=Path, required=True)
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--candidate", type=Path, required=True)
    evaluate.add_argument("--test", type=Path, required=True)
    evaluate.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare_data(args.directory, args.input, args.seed)
    elif args.command == "fit":
        if args.out.exists():
            raise FileExistsError("Candidate path must be new")
        result = fit_candidate(args.train, args.validation, args.model, args.seeds,
                               args.maxiter, args.v_pi, args.bias, args.gradient_threshold)
        write_new_json(args.out, result)
    else:
        if args.out.exists():
            raise FileExistsError("Test receipt path must be new")
        result = evaluate_locked(args.candidate, args.test)
        write_new_json(args.out, result)
    summary_keys = ("model", "dimension", "provenance", "counts",
                    "train_accuracy", "validation_accuracy", "accuracy",
                    "test_evaluated", "n_test", "scope")
    print(json.dumps({key: result[key] for key in summary_keys if key in result}))


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/mesh.py

```python file=agentkit/mesh.py
"""Exact triangular unitary synthesis and passive SVD transfer compilation.

This produces mathematical optical components. Converting them to laser
paths requires an independently calibrated physical component library.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from agentkit.evidence import write_new_json
from agentkit.numerics import finite_array


def complex_pairs(matrix) -> list:
    """Encode complex matrices as portable real/imaginary pairs."""
    a = finite_array(matrix)
    return np.stack([a.real, a.imag], axis=-1).tolist()


def from_pairs(value) -> np.ndarray:
    """Decode the explicit last-axis real/imaginary representation."""
    a = finite_array(value)
    if a.shape[-1] != 2:
        raise ValueError("Complex representation must end in two coordinates")
    return a[..., 0] + 1j * a[..., 1]


def decompose_unitary(unitary, tolerance: float = 1e-10) -> dict:
    """Eliminate lower entries with complex Givens rotations and retain all phases."""
    u = finite_array(unitary, ndim=2).astype(complex)
    n = len(u)
    if u.shape != (n, n) or not 1 <= n <= 64:
        raise ValueError("Unitary compiler supports square matrices up to 64")
    if np.linalg.norm(u.conj().T @ u - np.eye(n), 2) > tolerance:
        raise ValueError("Target is not unitary")
    current = u.copy()
    eliminations = []
    for column in range(n - 1):
        for bottom in range(n - 1, column, -1):
            top = bottom - 1
            a, b = current[top, column], current[bottom, column]
            radius = np.hypot(abs(a), abs(b))
            if radius <= np.finfo(float).tiny:
                continue
            rotation = np.array([[np.conj(a)/radius, np.conj(b)/radius],
                                 [-b/radius, a/radius]], dtype=complex)
            current[[top, bottom], :] = rotation @ current[[top, bottom], :]
            eliminations.append((top, bottom, rotation))
    off_diagonal = current - np.diag(np.diag(current))
    if np.linalg.norm(off_diagonal, 2) > 20 * tolerance:
        raise RuntimeError("Triangular unitary reduction did not become diagonal")
    diagonal = np.diag(current)
    operations = [{"kind": "phase", "phases_rad": np.angle(diagonal).tolist()}]
    for top, bottom, rotation in reversed(eliminations):
        block = rotation.conj().T
        operations.append({"kind": "two_mode_unitary", "ports": [top, bottom],
                           "matrix_pairs": complex_pairs(block),
                           "mixing_angle_rad": float(np.arctan2(abs(block[0, 1]), abs(block[0, 0])))})
    compiled = {"dimension": n, "operations": operations,
                "geometry_validated": False, "scope": "ideal_transfer_algebra"}
    reconstructed = reconstruct(compiled)
    error = float(np.linalg.norm(reconstructed - u, 2))
    if error > 50 * tolerance:
        raise RuntimeError("Compiled coherent transfer failed reconstruction")
    compiled["reconstruction_error"] = error
    return compiled


def reconstruct(compiled: dict) -> np.ndarray:
    """Apply the recorded operations in propagation order."""
    n = compiled["dimension"]
    transfer = np.eye(n, dtype=complex)
    for operation in compiled["operations"]:
        kind = operation["kind"]
        if kind == "phase":
            transfer = np.exp(1j * np.asarray(operation["phases_rad"]))[:, None] * transfer
        elif kind == "attenuation":
            values = finite_array(operation["amplitudes"], ndim=1)
            if values.shape != (n,) or np.min(values) < 0 or np.max(values) > 1 + 1e-12:
                raise ValueError("Passive attenuation amplitudes must lie in [0,1]")
            transfer = values[:, None] * transfer
        elif kind == "two_mode_unitary":
            ports = operation["ports"]
            block = from_pairs(operation["matrix_pairs"])
            transfer[ports, :] = block @ transfer[ports, :]
        else:
            raise ValueError("Unknown optical operation")
    return transfer


def compile_passive(target) -> dict:
    """Compile a contraction as right unitary, amplitudes and left unitary."""
    t = finite_array(target, ndim=2).astype(complex)
    if t.shape[0] != t.shape[1] or len(t) > 64:
        raise ValueError("Passive compilation requires a square target up to 64")
    left, singular, right_h = np.linalg.svd(t)
    if singular.max() > 1 + 1e-12:
        raise ValueError("Target requires amplification; declare external gain or input scaling")
    # Clip only rounding at the passive threshold, never a substantive gain.
    singular = np.minimum(singular, 1.0)
    right = decompose_unitary(right_h)
    left_compiled = decompose_unitary(left)
    compiled = {"dimension": len(t), "scope": "ideal_passive_transfer_algebra",
                "geometry_validated": False,
                "operations": [*right["operations"],
                               {"kind": "attenuation", "amplitudes": singular.tolist()},
                               *left_compiled["operations"]]}
    compiled["reconstruction_error"] = float(np.linalg.norm(reconstruct(compiled) - t, 2))
    return compiled


def fixed_coupling_lengths(compiled: dict, kappa_per_m: float) -> list[dict]:
    """Map mixing magnitudes to lengths only; phase/layout calibration remains explicit."""
    if not math.isfinite(kappa_per_m) or kappa_per_m <= 0:
        raise ValueError("Calibrated coupling coefficient must be positive")
    return [{"ports": op["ports"], "mixing_angle_rad": op["mixing_angle_rad"],
             "length_m": op["mixing_angle_rad"] / kappa_per_m,
             "phase_mapping_validated": False}
            for op in compiled["operations"] if op["kind"] == "two_mode_unitary"]


def main() -> None:
    """Compile a supplied complex NPZ target and retain an exclusive report."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--kappa-per-m", type=float)
    args = parser.parse_args()
    with np.load(args.input, allow_pickle=False) as data:
        compiled = compile_passive(data["target"])
    if args.kappa_per_m is not None:
        compiled["mixing_lengths"] = fixed_coupling_lengths(compiled, args.kappa_per_m)
    write_new_json(args.out, compiled)
    print(json.dumps({"error": compiled["reconstruction_error"],
                      "geometry_validated": compiled["geometry_validated"]}))


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/metrology.py

```python file=agentkit/metrology.py
"""Cutback regression and whole-system energy calculations with explicit units."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import t

from agentkit.evidence import sha256_file, write_new_json


def fit_cutback(rows: list[dict]) -> dict:
    """Fit each cutback guide and use independent chip means for uncertainty.

    Fields: chip_id, guide_id, length_m, wavelength_m, polarization,
    input_power_w, output_power_w, sigma_loss_db. One invocation must
    represent one wavelength and one polarization.
    """
    if not rows:
        raise ValueError("No measurement rows")
    settings = {(float(r["wavelength_m"]), r["polarization"]) for r in rows}
    if len(settings) != 1:
        raise ValueError("Separate wavelengths and polarizations before fitting")
    wavelength, polarization = next(iter(settings))
    if not math.isfinite(wavelength) or wavelength <= 0 or not polarization:
        raise ValueError("Measurement settings are invalid")
    groups = {}
    for row in rows:
        key = (row["chip_id"], row["guide_id"])
        if not all(key):
            raise ValueError("Chip and guide identifiers are required")
        values = [float(row[k]) for k in ("length_m", "input_power_w",
                                          "output_power_w", "sigma_loss_db")]
        if not all(math.isfinite(v) and v > 0 for v in values):
            raise ValueError("Lengths, powers and loss uncertainties must be positive")
        groups.setdefault(key, []).append(values)
    guides, chip_slopes = [], {}
    for (chip, guide), data in sorted(groups.items()):
        values = np.asarray(data)
        lengths_cm = 100 * values[:, 0]
        if len(np.unique(lengths_cm)) < 4:
            raise ValueError("Each guide requires at least four distinct cutback lengths")
        loss = 10 * np.log10(values[:, 1] / values[:, 2])
        sigma = values[:, 3]
        design = np.column_stack([np.ones(len(data)), lengths_cm])
        weighted_design = design / sigma[:, None]
        weighted_loss = loss / sigma
        parameters, _, rank, _ = np.linalg.lstsq(weighted_design, weighted_loss, rcond=None)
        if rank != 2:
            raise ValueError("Cutback regression is rank deficient")
        residual = loss - design @ parameters
        dof = len(data) - 2
        reduced_chi2 = float(np.sum((residual / sigma)**2) / dof)
        covariance = np.linalg.inv(weighted_design.T @ weighted_design) * max(1.0, reduced_chi2)
        record = {"chip_id": chip, "guide_id": guide,
                  "loss_db_per_cm": float(parameters[1]),
                  "intercept_db": float(parameters[0]),
                  "slope_standard_error": float(np.sqrt(covariance[1, 1])),
                  "reduced_chi2": reduced_chi2,
                  "max_abs_residual_db": float(np.max(abs(residual))),
                  "lengths_cm": lengths_cm.tolist()}
        guides.append(record)
        chip_slopes.setdefault(chip, []).append(record)
    if len(chip_slopes) < 3:
        raise ValueError("At least three independent chips are required")
    chip_means = np.array([np.mean([r["loss_db_per_cm"] for r in records])
                           for records in chip_slopes.values()])
    between_chip_se = float(chip_means.std(ddof=1) / np.sqrt(len(chip_means)))
    measurement_se = float(np.sqrt(sum(
        sum(r["slope_standard_error"]**2 for r in records) / len(records)**2
        for records in chip_slopes.values())) / len(chip_slopes))
    # Conservative diagnostic: retain whichever uncertainty component is larger.
    standard_error = max(between_chip_se, measurement_se)
    mean = float(chip_means.mean())
    margin = float(t.ppf(0.975, len(chip_means)-1) * standard_error)
    return {"wavelength_m": wavelength, "polarization": polarization,
            "independent_chips": len(chip_means),
            "mean_loss_db_per_cm": mean, "ci95": [mean-margin, mean+margin],
            "between_chip_standard_error": between_chip_se,
            "measurement_standard_error": measurement_se,
            "guides": guides,
            "assumptions": "Independent chips, approximately normal chip means, linear cutback loss; systematic calibration uncertainty must be added separately."}


def system_energy(rows: list[dict]) -> dict:
    """Integrate synchronized electrical measurements and all accepted inferences."""
    if len(rows) < 2:
        raise ValueError("At least two synchronized electrical samples are required")
    time_s = np.array([float(r["time_s"]) for r in rows])
    count = np.array([float(r["completed_inferences"]) for r in rows])
    names = ("source_w", "modulation_w", "detection_w", "control_w", "cooling_w")
    powers = np.array([[float(r[name]) for name in names] for r in rows])
    if not all(np.all(np.isfinite(a)) for a in (time_s, count, powers)):
        raise ValueError("Measurements must be finite")
    if np.any(np.diff(time_s) <= 0) or np.any(np.diff(count) < 0) or powers.min() < 0:
        raise ValueError("Time/count ordering and nonnegative powers are required")
    if np.any(count != np.floor(count)):
        raise ValueError("Inference counters must be integers")
    completed = int(count[-1]-count[0])
    if completed <= 0:
        raise ValueError("No complete inferences were measured")
    energies = np.sum((powers[1:] + powers[:-1]) * np.diff(time_s)[:, None] / 2, axis=0)
    total = float(energies.sum())
    return {"duration_s": float(time_s[-1]-time_s[0]),
            "completed_inferences": completed,
            "component_energy_j": dict(zip(names, map(float, energies))),
            "total_energy_j": total, "joules_per_inference": total/completed,
            "inferences_per_second": completed/float(time_s[-1]-time_s[0]),
            "scope": "full_system_electrical_measurement",
            "note": "Include idle/active intervals and calibration uncertainty in the experimental report; zero power must be physically documented."}


def main() -> None:
    """Read calibrated CSV data and write a new analysis report."""
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("cutback", "energy"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result = fit_cutback(rows) if args.kind == "cutback" else system_energy(rows)
    result["input_sha256"] = sha256_file(args.input)
    write_new_json(args.out, result)
    print(json.dumps({key: value for key, value in result.items() if key != "guides"}))


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/numerics.py

```python file=agentkit/numerics.py
"""Small independent controls for coherent optics and numerical error.

Dense routines are restricted to reduced systems. Large FEM matrices must
use sparse solvers with a separately reviewed resource and accuracy protocol.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.linalg import eig, eigh, expm, expm_frechet
from scipy.optimize import linprog
from scipy.sparse import csr_matrix


def finite_array(value, *, ndim=None) -> np.ndarray:
    """Convert numerical input and reject NaNs and infinities."""
    array = np.asarray(value)
    if ndim is not None and array.ndim != ndim:
        raise ValueError("Unexpected array dimension")
    if not np.all(np.isfinite(array)):
        raise ValueError("Array must contain only finite values")
    return array


def mass_matrix(mass, n: int) -> np.ndarray:
    """Validate a positive Hermitian mass matrix or positive diagonal weights."""
    if not 1 <= n <= 512:
        raise ValueError("Dense reduced-system limit is 512 degrees of freedom")
    m = finite_array(mass)
    if m.ndim == 1:
        if m.shape != (n,) or np.iscomplexobj(m) or np.min(m) <= 0:
            raise ValueError("Mass weights must be positive and real")
        return np.diag(m)
    if m.shape != (n, n) or not np.allclose(m, m.conj().T, atol=1e-13, rtol=1e-13):
        raise ValueError("Mass matrix must be Hermitian")
    np.linalg.cholesky(m)
    return m


def mass_power(field, mass) -> float:
    """Compute the physical quadratic norm without normalizing the field."""
    u = finite_array(field, ndim=1).astype(complex)
    m = mass_matrix(mass, len(u))
    value = np.vdot(u, m @ u)
    if abs(value.imag) > 1e-11 * max(1.0, abs(value.real)):
        raise ValueError("Mass power has a material imaginary component")
    return float(value.real)


def logarithmic_norm(operator, mass) -> float:
    """Bound growth for M du/dz = A u in the validated mass norm."""
    a = finite_array(operator, ndim=2).astype(complex)
    if a.shape[0] != a.shape[1]:
        raise ValueError("Generator numerator must be square")
    m = mass_matrix(mass, len(a))
    return float(eigh((a+a.conj().T)/2, m, eigvals_only=True)[-1])


def residual_error_bound(times, residual_upper_bounds, initial_error: float,
                         growth_bound: float) -> float:
    """Integrate certified per-interval residual enclosures.

    Each supplied value must upper-bound the residual norm throughout its
    interval. Point samples alone do not satisfy this mathematical premise.
    """
    time = finite_array(times, ndim=1).astype(float)
    upper = finite_array(residual_upper_bounds, ndim=1).astype(float)
    if (len(time) < 2 or upper.shape != (len(time)-1,) or np.min(np.diff(time)) <= 0
            or np.min(upper) < 0 or not math.isfinite(initial_error)
            or initial_error < 0 or not math.isfinite(growth_bound)):
        raise ValueError("Residual enclosure inputs are invalid")
    end = time[-1]
    bound = math.exp(growth_bound*(end-time[0])) * initial_error
    for begin, finish, value in zip(time[:-1], time[1:], upper):
        duration = finish-begin
        weight = (duration if growth_bound == 0 else
                  math.exp(growth_bound*(end-finish)) *
                  math.expm1(growth_bound*duration) / growth_bound)
        bound += value*weight
    if not math.isfinite(bound):
        raise ValueError("Residual bound overflowed")
    return float(bound)


def detector_error_bound(reference_field, mass, detector, field_error: float) -> float:
    """Propagate a valid mass-norm field bound to a PSD detector functional."""
    u = finite_array(reference_field, ndim=1).astype(complex)
    m = mass_matrix(mass, len(u))
    d = finite_array(detector, ndim=2).astype(complex)
    if d.shape != m.shape or not np.allclose(d, d.conj().T, atol=1e-13):
        raise ValueError("Detector must be a matching Hermitian operator")
    spectrum = eigh(d, m, eigvals_only=True)
    if spectrum[0] < -1e-12 or not math.isfinite(field_error) or field_error < 0:
        raise ValueError("Detector must be PSD and field error nonnegative")
    norm = max(0.0, float(spectrum[-1]))
    return norm*(2*math.sqrt(mass_power(u, m))*field_error + field_error**2)


def coherent_decomposition(field, basis, mass, dual=None) -> dict:
    """Return mode, remainder and cross power with an exact coherent balance.

    With no dual, use the mass-orthogonal projection onto the basis span.
    With a dual, require dual.H @ M @ basis = I. Individual nonorthogonal
    modal powers are not additive and coefficients are not efficiencies.
    """
    u = finite_array(field, ndim=1).astype(complex)
    r = finite_array(basis, ndim=2).astype(complex)
    if r.shape[0] != len(u) or not 1 <= r.shape[1] <= len(u):
        raise ValueError("Basis shape is invalid")
    m = mass_matrix(mass, len(u))
    gram = r.conj().T @ m @ r
    if dual is None:
        if np.linalg.cond(gram) > 1e12:
            raise ValueError("Basis Gram matrix is too ill-conditioned")
        coefficients = np.linalg.solve(gram, r.conj().T @ m @ u)
    else:
        l = finite_array(dual, ndim=2).astype(complex)
        if l.shape != r.shape or np.linalg.norm(
                l.conj().T @ m @ r - np.eye(r.shape[1]), 2) > 1e-9:
            raise ValueError("Dual basis is not mass-biorthogonal")
        coefficients = l.conj().T @ m @ u
    mode = r @ coefficients
    remainder = u - mode
    total = mass_power(u, m)
    modal = mass_power(mode, m)
    residual = mass_power(remainder, m)
    cross = float(2 * np.real(np.vdot(mode, m @ remainder)))
    balance = total - modal - residual - cross
    return {"coefficients": coefficients, "mode": mode, "remainder": remainder,
            "total_power": total, "mode_power": modal,
            "remainder_power": residual, "cross_power": cross,
            "balance_error": float(abs(balance)),
            "basis_condition": float(np.linalg.cond(gram))}


def generalized_modes(operator, mass) -> dict:
    """Find left/right generalized modes and quantify nonnormal sensitivity."""
    k = finite_array(operator, ndim=2).astype(complex)
    if k.shape[0] != k.shape[1]:
        raise ValueError("Operator must be square")
    m = mass_matrix(mass, k.shape[0])
    values, left, right = eig(k, m, left=True, right=True)
    conditions, residuals = [], []
    scale = np.linalg.norm(k, 2) + np.linalg.norm(m, 2) * np.max(np.abs(values))
    for i, value in enumerate(values):
        rv = right[:, i]
        rv /= math.sqrt(mass_power(rv, m))
        overlap = np.vdot(left[:, i], m @ rv)
        if abs(overlap) <= 1e-13:
            raise ValueError("Near-defective eigenpair requires Schur/subspace analysis")
        left[:, i] /= np.conj(overlap)
        conditions.append(float(np.linalg.norm(left[:, i]) * np.linalg.norm(rv)))
        residuals.append(float(np.linalg.norm(k @ rv - value * (m @ rv)) /
                               max(np.finfo(float).tiny, scale * np.linalg.norm(rv))))
    gram = left.conj().T @ m @ right
    if np.linalg.norm(gram - np.eye(len(values)), 2) > 1e-8:
        raise ValueError("Eigenbasis is not biorthogonal; use invariant subspaces")
    return {"values": values, "right": right, "left": left,
            "relative_residuals": np.array(residuals),
            "eigenvalue_condition_indicators": np.array(conditions),
            "biorthogonality_error": float(np.linalg.norm(gram - np.eye(len(values)), 2))}


def splitting_control(a, b, initial, length: float, steps: int) -> dict:
    """Compare Strang with a dense exponential of the same discrete operator."""
    a, b = finite_array(a, ndim=2), finite_array(b, ndim=2)
    u = finite_array(initial, ndim=1).astype(complex)
    if a.shape != b.shape or a.shape != (len(u), len(u)) or len(u) > 128:
        raise ValueError("Dense splitting control requires matching matrices up to 128")
    if not math.isfinite(length) or length <= 0 or type(steps) is not int or steps < 1:
        raise ValueError("Length and step count must be positive")
    h = length / steps
    half, full = expm(h * a / 2), expm(h * b)
    approximation = u.copy()
    for _ in range(steps):
        approximation = half @ (full @ (half @ approximation))
    reference = expm(length * (a + b)) @ u
    commutator = a @ b - b @ a
    return {"field": approximation, "reference": reference,
            "relative_field_error": float(np.linalg.norm(approximation - reference) /
                                          max(np.linalg.norm(reference), 1e-300)),
            "commutator_norm": float(np.linalg.norm(commutator, 2)),
            "a_nested_norm": float(np.linalg.norm(a @ commutator - commutator @ a, 2)),
            "b_nested_norm": float(np.linalg.norm(b @ commutator - commutator @ b, 2))}


def transfer_sensitivity(generator, perturbation, length: float) -> dict:
    """Differentiate the complete complex transfer matrix, including phase."""
    h, dh = finite_array(generator, ndim=2), finite_array(perturbation, ndim=2)
    if h.shape != dh.shape or h.shape[0] != h.shape[1] or h.shape[0] > 128:
        raise ValueError("Reduced square matrices up to 128 are required")
    if not math.isfinite(length) or length <= 0:
        raise ValueError("Length must be positive")
    transfer, derivative = expm_frechet(1j * length * h, 1j * length * dh)
    return {"transfer": transfer, "derivative": derivative,
            "derivative_operator_norm": float(np.linalg.norm(derivative, 2))}


def optical_error_budget(index: float, length_m: float, wavelength_m: float,
                         delta_index: float, delta_length_m: float,
                         delta_wavelength_m: float = 0.0) -> dict:
    """Bound scalar optical-path phase perturbation, without claiming PDE closure."""
    inputs = (index, length_m, wavelength_m, delta_index,
              delta_length_m, delta_wavelength_m)
    if not all(math.isfinite(x) for x in inputs):
        raise ValueError("Budget values must be finite")
    if min(index, length_m, wavelength_m) <= 0 or min(inputs[3:]) < 0:
        raise ValueError("Nominal values must be positive and uncertainties nonnegative")
    if delta_wavelength_m >= wavelength_m:
        raise ValueError("Wavelength interval must exclude zero")
    opl_error = index * delta_length_m + length_m * delta_index + delta_index * delta_length_m
    phase_error = 2 * math.pi * (
        opl_error / (wavelength_m - delta_wavelength_m) +
        index * length_m * delta_wavelength_m /
        (wavelength_m * (wavelength_m - delta_wavelength_m)))
    return {"optical_path_error_m": opl_error, "phase_error_rad": phase_error,
            "unit_amplitude_field_error_bound": float(min(2.0, phase_error))}


def phase_metrics(reference, candidate, weights, amplitude_floor: float = 1e-12) -> dict:
    """Compare complex fields without global phase alignment."""
    ref, value, w = (finite_array(x, ndim=1) for x in (reference, candidate, weights))
    if (ref.shape != value.shape or w.shape != ref.shape or np.iscomplexobj(w)
            or np.min(w) < 0 or w.sum() <= 0):
        raise ValueError("Field and nonnegative weight shapes must agree")
    if not math.isfinite(amplitude_floor) or amplitude_floor <= 0:
        raise ValueError("Amplitude floor must be positive")
    error = np.sqrt(np.sum(w * abs(value - ref)**2))
    norm = np.sqrt(np.sum(w * abs(ref)**2))
    mask = (abs(ref) > amplitude_floor) & (abs(value) > amplitude_floor) & (w > 0)
    phase = np.angle(value[mask] * np.conj(ref[mask]))
    return {"absolute_field_error": float(error),
            "relative_field_error": None if norm == 0 else float(error / norm),
            "max_phase_error_rad": None if not mask.any() else float(np.max(abs(phase))),
            "phase_samples": int(mask.sum()),
            "power_difference": float(abs(np.sum(w * abs(value)**2) - np.sum(w * abs(ref)**2)))}


def spatial_forecast(powers, temporal_errors, ratio: float = 1.25) -> dict:
    """Implement the fixed S16 scalar forecast with strict eligibility gates."""
    p = finite_array(powers, ndim=1).astype(float)
    errors = finite_array(temporal_errors, ndim=1).astype(float)
    if p.shape != (3,) or errors.shape != (3,) or np.min(errors) < 0:
        raise ValueError("Three powers and three nonnegative temporal errors are required")
    if not math.isclose(ratio, 1.25, abs_tol=1e-14, rel_tol=0):
        raise ValueError("S16 fixes the refinement ratio to 1.25")
    d0, d1 = np.diff(p)
    same_sign = d0 != 0 and d1 != 0 and d0 * d1 > 0
    order = float(math.log(d0 / d1) / math.log(ratio)) if same_sign else None
    separation = min(abs(d0), abs(d1)) > 20 * max(errors)
    eligible = bool(same_sign and order is not None and 0.5 <= order <= 6 and separation)
    prediction = float(p[-1] + d1 / ratio**order) if eligible else None
    return {"eligible": eligible, "order": order, "prediction": prediction,
            "increments": [float(d0), float(d1)],
            "temporal_separation": bool(separation)}


def spatial_holdout(powers, temporal_errors, reserved_power: float,
                    temporal_psd_bound: float, reconstruction_difference: float,
                    quadrature_indicator: float) -> dict:
    """Evaluate S16's reserved sample; its uncertainty is a numerical indicator."""
    forecast = spatial_forecast(powers, temporal_errors)
    extras = (reserved_power, temporal_psd_bound, reconstruction_difference, quadrature_indicator)
    if not all(math.isfinite(x) for x in extras) or min(extras) < 0:
        raise ValueError("Reserved power and error indicators must be finite/nonnegative")
    if not forecast["eligible"]:
        return {"passed": False, "reason": "Forecast prerequisites failed", "forecast": forecast}
    increment = reserved_power - powers[-1]
    previous = forecast["increments"][-1]
    sign_ok = increment != 0 and increment * previous > 0
    order = math.log(previous / increment) / math.log(1.25) if sign_ok else None
    checks = {"same_sign": sign_ok,
              "order_range": order is not None and 0.5 <= order <= 6,
              "order_consistency": order is not None and
              abs(order - forecast["order"]) / max(order, forecast["order"]) <= 0.2,
              "prediction": abs(reserved_power - forecast["prediction"]) <= 0.1 * abs(increment),
              "temporal_separation": abs(increment) > 20 * max(temporal_errors)}
    uncertainty = None
    if checks["order_range"]:
        gci = 1.25 * abs(increment) / (1.25**min(order, 2.0) - 1.0)
        uncertainty = gci + temporal_psd_bound + reconstruction_difference + quadrature_indicator
    checks["budget"] = uncertainty is not None and uncertainty <= 1e-3 and uncertainty <= 0.01 * reserved_power
    checks = {key: bool(value) for key, value in checks.items()}
    return {"passed": all(checks.values()), "checks": checks,
            "new_order": order,
            "uncertainty_indicator": None if uncertainty is None else float(uncertainty),
            "forecast": forecast}


def exact_discrete_transport(source_points, source_mass, target_points, target_mass) -> dict:
    """Solve a bounded discrete quadratic OT problem with a checked LP.

    This is a calibration diagnostic. A finite barycentric plan is not the
    continuous Brenier map or a numerical implementation of the new theorem.
    """
    x, y = finite_array(source_points, ndim=2), finite_array(target_points, ndim=2)
    a, b = finite_array(source_mass, ndim=1), finite_array(target_mass, ndim=1)
    n, m = len(x), len(y)
    if x.shape[1] != y.shape[1] or a.shape != (n,) or b.shape != (m,):
        raise ValueError("Transport point and mass shapes disagree")
    if min(n, m) < 1 or n * m > 4096 or min(a.min(), b.min()) < 0:
        raise ValueError("Transport requires nonnegative masses and at most 4096 variables")
    if not np.isclose(a.sum(), 1.0) or not np.isclose(b.sum(), 1.0):
        raise ValueError("Transport masses must each sum to one")
    cost = np.sum((x[:, None, :] - y[None, :, :])**2, axis=2)
    rows = np.repeat(np.arange(n), m)
    cols = np.arange(n * m)
    source_constraints = csr_matrix((np.ones(n*m), (rows, cols)), shape=(n, n*m))
    rows = np.tile(np.arange(m), n)
    target_constraints = csr_matrix((np.ones(n*m), (rows, cols)), shape=(m, n*m))
    from scipy.sparse import vstack
    result = linprog(cost.ravel(), A_eq=vstack([source_constraints, target_constraints]),
                     b_eq=np.r_[a, b], bounds=(0, None), method="highs",
                     options={"time_limit": 20.0})
    if not result.success:
        raise RuntimeError("Transport LP failed: " + result.message)
    plan = result.x.reshape(n, m)
    marginal_error = max(np.max(abs(plan.sum(axis=1)-a)), np.max(abs(plan.sum(axis=0)-b)))
    if marginal_error > 1e-8 or plan.min() < -1e-10:
        raise RuntimeError("Transport solution failed the feasibility audit")
    positive = a > 0
    barycentres = np.full_like(x, np.nan, dtype=float)
    barycentres[positive] = (plan[positive] @ y) / a[positive, None]
    return {"plan": plan, "barycentres": barycentres,
            "wasserstein2": float(np.sqrt(max(0.0, result.fun))),
            "marginal_error": float(marginal_error)}
```

### Archivo: agentkit/paraxial.py

```python file=agentkit/paraxial.py
"""Independent bounded FFT split-step reference with resumable trajectories.

All distances are SI metres. The equation is a scalar, monochromatic,
weak-index paraxial model with periodic transverse boundaries. A sponge
is numerical absorption; it is not measured material loss or a PML proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import numpy as np

from agentkit.checkpoint import load_latest, save_checkpoint
from agentkit.evidence import canonical, sha256_file, write_new_json
from agentkit.numerics import phase_metrics


def grid(points: int, width_m: float):
    """Construct a centered periodic square grid with explicit spacing."""
    if type(points) is not int or not 16 <= points <= 512:
        raise ValueError("Bounded grid requires 16 through 512 points per axis")
    if not math.isfinite(width_m) or width_m <= 0:
        raise ValueError("Grid width must be positive")
    dx = width_m / points
    axis = (np.arange(points) - points // 2) * dx
    return np.meshgrid(axis, axis, indexing="xy"), dx


def disk_area_weights(points: int, width_m: float, radius_m: float,
                      subdivisions: int = 8) -> np.ndarray:
    """Compute a subpixel circle-area indicator; it is not an exact geometry bound."""
    if type(subdivisions) is not int or not 1 <= subdivisions <= 32:
        raise ValueError("Subpixel quadrature requires 1 through 32 subdivisions")
    (x, y), dx = grid(points, width_m)
    if not math.isfinite(radius_m) or not 0 < radius_m < width_m / 2:
        raise ValueError("Circle radius must fit inside the domain")
    weights = np.zeros_like(x)
    offsets = ((np.arange(subdivisions) + 0.5) / subdivisions - 0.5) * dx
    for ox in offsets:
        for oy in offsets:
            weights += ((x + ox)**2 + (y + oy)**2 <= radius_m**2)
    return weights * dx**2 / subdivisions**2


def split_step(field, profile, width_m: float, wavelength_m: float,
               n_reference: float, dz_m: float, sponge_rate=None) -> np.ndarray:
    """Execute one symmetric split step with nonnegative optional damping."""
    u, dn = np.asarray(field, dtype=np.complex128), np.asarray(profile)
    if u.ndim != 2 or u.shape[0] != u.shape[1] or dn.shape != u.shape:
        raise ValueError("Field and profile must be matching square arrays")
    (_, _), dx = grid(len(u), width_m)
    values = (wavelength_m, n_reference, dz_m)
    if not all(math.isfinite(v) and v > 0 for v in values):
        raise ValueError("Wavelength, reference index and step must be positive")
    if np.iscomplexobj(dn) or not np.all(np.isfinite(dn)) or not np.all(np.isfinite(u)):
        raise ValueError("Profile must be real and the field must be finite")
    if np.max(abs(dn)) > 0.01 or np.min(n_reference + dn) <= 0:
        raise ValueError("Profile is outside the declared weak-index regime")
    sigma = np.zeros_like(dn, dtype=float) if sponge_rate is None else np.asarray(sponge_rate)
    if sigma.shape != u.shape or np.iscomplexobj(sigma) or not np.all(np.isfinite(sigma)) or sigma.min() < 0:
        raise ValueError("Sponge rates must be finite, real and nonnegative")
    k0 = 2 * math.pi / wavelength_m
    freq = 2 * math.pi * np.fft.fftfreq(len(u), d=dx)
    kx, ky = np.meshgrid(freq, freq, indexing="xy")
    half = np.exp((1j * k0 * dn - sigma) * dz_m / 2)
    kernel = np.exp(-1j * (kx*kx + ky*ky) * dz_m / (2 * k0 * n_reference))
    return half * np.fft.ifft2(np.fft.fft2(half * u) * kernel)


def run_resumable(input_path: Path, config: dict, directory: Path,
                  chunk_steps: int = 100, max_seconds: float = 40.0) -> dict:
    """Resume only the exact frozen input/configuration/source identity.

    A partial return is an operational status. It does not pass any optical
    acceptance criterion and does not extend an external resource window.
    """
    if type(chunk_steps) is not int or chunk_steps < 1 or not math.isfinite(max_seconds) or max_seconds <= 0:
        raise ValueError("Chunk and invocation limits must be positive")
    required = ("width_m", "wavelength_m", "n_reference", "length_m", "steps")
    if any(key not in config for key in required):
        raise ValueError("Missing simulation parameter")
    steps = config["steps"]
    if type(steps) is not int or not 1 <= steps <= 10000000:
        raise ValueError("Step count must be a positive bounded integer")
    if not math.isfinite(config["length_m"]) or config["length_m"] <= 0:
        raise ValueError("Length must be positive")
    identity = {"config": config, "input_sha256": sha256_file(input_path),
                "numpy_version": np.__version__,
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "source_sha256": sha256_file(Path(__file__)),
                "checkpoint_source_sha256": sha256_file(Path(__file__).with_name("checkpoint.py")),
                "evidence_source_sha256": sha256_file(Path(__file__).with_name("evidence.py"))}
    experiment_hash = hashlib.sha256(canonical(identity)).hexdigest()
    with np.load(input_path, allow_pickle=False) as source:
        field = source["field"].astype(np.complex128, copy=True)
        profile = source["delta_n"].copy()
        sponge = source["sponge_rate"].copy() if "sponge_rate" in source else np.zeros_like(profile)
    # Validate all shapes and scalar parameters before publishing the first state.
    split_step(field, profile, config["width_m"], config["wavelength_m"],
               config["n_reference"], config["length_m"] / steps, sponge)
    retained = load_latest(directory, experiment_hash, steps)
    if retained is None:
        marker = save_checkpoint(directory, field, 0, steps, experiment_hash, None)
        step, previous_hash = 0, sha256_file(marker)
    else:
        restored, step, previous_hash = retained
        if restored.shape != field.shape:
            raise ValueError("Retained state shape differs from the frozen input")
        field = restored
    start = time.monotonic()
    completed_at_entry = step
    while step < steps and time.monotonic() - start < max_seconds:
        end = min(steps, step + chunk_steps)
        while step < end:
            field = split_step(field, profile, config["width_m"], config["wavelength_m"],
                               config["n_reference"], config["length_m"] / steps, sponge)
            step += 1
        marker = save_checkpoint(directory, field, step, steps, experiment_hash, previous_hash)
        previous_hash = sha256_file(marker)
    return {"status": "completed" if step == steps else "partial",
            "steps_completed": step, "steps_at_entry": completed_at_entry,
            "total_steps": steps, "experiment_hash": experiment_hash,
            "invocation_seconds": time.monotonic() - start,
            "note": "Chunk-level cooperative limit; use the supervisor for a hard deadline."}


def compare_fields(first: Path, second: Path, width_m: float) -> dict:
    """Compare matching final arrays without phase fitting or rescaling."""
    with np.load(first, allow_pickle=False) as f:
        u = f["state"] if "state" in f else f["field"]
    with np.load(second, allow_pickle=False) as f:
        v = f["state"] if "state" in f else f["field"]
    if u.shape != v.shape or u.ndim != 2 or u.shape[0] != u.shape[1]:
        raise ValueError("Comparison requires the same physical sampling grid")
    (_, _), dx = grid(len(u), width_m)
    return phase_metrics(u.ravel(), v.ravel(), np.full(u.size, dx*dx))


def main() -> None:
    """Run an explicit frozen NPZ/configuration pair or compare retained fields."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--input", type=Path, required=True)
    run.add_argument("--config", type=Path, required=True)
    run.add_argument("--directory", type=Path, required=True)
    run.add_argument("--chunk-steps", type=int, default=100)
    run.add_argument("--max-seconds", type=float, default=40)
    run.add_argument("--receipt", type=Path, required=True)
    compare = commands.add_parser("compare")
    compare.add_argument("--first", type=Path, required=True)
    compare.add_argument("--second", type=Path, required=True)
    compare.add_argument("--width-m", type=float, required=True)
    compare.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "run":
        if args.receipt.exists():
            raise FileExistsError("Invocation receipt must use a new path")
        config = json.loads(args.config.read_text(encoding="utf-8"))
        result = run_resumable(args.input, config, args.directory,
                               args.chunk_steps, args.max_seconds)
        write_new_json(args.receipt, result)
    else:
        result = compare_fields(args.first, args.second, args.width_m)
        write_new_json(args.out, result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/report.py

```python file=agentkit/report.py
"""Export publication figures from explicit CSV data with fixed scientific labels."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from agentkit.evidence import sha256_file, write_new_json


def plot_convergence(input_path: Path, output_prefix: Path, scope: str) -> dict:
    """Plot every retained mesh sample and numerical error indicator.

    Required CSV columns: mesh_um, power_fraction, error_indicator.
    Error bars are indicators, not statistical confidence intervals.
    """
    with input_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    values = np.array([[float(row[key]) for key in
                        ("mesh_um", "power_fraction", "error_indicator")] for row in rows])
    if values.ndim != 2 or values.shape[1] != 3 or len(values) < 3:
        raise ValueError("At least three complete convergence rows are required")
    if (not np.all(np.isfinite(values)) or np.any(values[:, 0] <= 0)
            or np.any(values[:, 1:] < 0)):
        raise ValueError("Convergence values must be finite and nonnegative")
    if len(np.unique(values[:, 0])) != len(values):
        raise ValueError("Duplicate meshes need a separately declared aggregation protocol")
    if scope not in ("numerical_model", "manufactured_control"):
        raise ValueError("This figure is for a numerical model or manufactured control")
    order = np.argsort(values[:, 0])
    values = values[order]
    outputs = [output_prefix.with_suffix(suffix) for suffix in (".png", ".pdf", ".json")]
    if any(path.exists() for path in outputs):
        raise FileExistsError("Figure output paths must be new")
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.facecolor": "white"}):
        fig, ax = plt.subplots(figsize=(6.8, 4.4), layout="constrained")
        ax.errorbar(values[:, 0], values[:, 1], yerr=values[:, 2],
                    marker="o", capsize=4, color="#146C94", label="All retained samples")
        ax.set_xlabel("Nominal mesh spacing (µm)")
        ax.set_ylabel("Core power / input power")
        ax.set_title("Spatial refinement")
        ax.grid(alpha=0.2)
        ax.legend()
        fig.supxlabel("Error bars: numerical indicators, not 95% confidence intervals. " +
                      scope.replace("_", " ") + "; no physical measurement.", fontsize=8)
        fig.savefig(outputs[0], dpi=300)
        fig.savefig(outputs[1])
        plt.close(fig)
    manifest = {"input_sha256": sha256_file(input_path), "scope": scope,
                "selection": "all retained CSV rows, sorted only by mesh spacing",
                "rows": len(values), "error_bar_type": "numerical_indicator",
                "outputs": {p.name: sha256_file(p) for p in outputs[:2]}}
    write_new_json(outputs[2], manifest)
    return manifest


def main() -> None:
    """Create static PNG/PDF figures and an input/output hash manifest."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    parser.add_argument("--scope", choices=("numerical_model", "manufactured_control"),
                        required=True)
    args = parser.parse_args()
    result = plot_convergence(args.input, args.output_prefix, args.scope)
    print("Exported", result["rows"], "rows with explicit numerical scope.")


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/supervisor.py

```python file=agentkit/supervisor.py
"""Bound an explicitly supplied CPU command and retain its log and exit status."""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from agentkit.evidence import utc_now, write_new_json


def available_ram_gib() -> float:
    """Read available system RAM on the supported Linux and Windows hosts."""
    if sys.platform.startswith("linux"):
        entries = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            name, value = line.split(":", 1)
            entries[name] = int(value.strip().split()[0]) * 1024
        return entries["MemAvailable"] / 1024**3
    if sys.platform == "win32":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                        ("total_phys", ctypes.c_ulonglong), ("available_phys", ctypes.c_ulonglong),
                        ("total_pagefile", ctypes.c_ulonglong), ("available_pagefile", ctypes.c_ulonglong),
                        ("total_virtual", ctypes.c_ulonglong), ("available_virtual", ctypes.c_ulonglong),
                        ("available_extended", ctypes.c_ulonglong)]
        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("Windows RAM telemetry failed")
        return status.available_phys / 1024**3
    raise RuntimeError("RAM telemetry supports Linux and Windows only")


def stop_tree(process: subprocess.Popen) -> None:
    """Terminate only the child and descendants belonging to this invocation."""
    if sys.platform == "win32":
        if process.poll() is None:
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                           capture_output=True, timeout=10, check=False)
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
        # Also kill any remaining descendants in this process group.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
    except ProcessLookupError:
        return


def supervise(command: list[str], cwd: Path, log_path: Path, report_path: Path,
              seconds: float, ram_floor_gib: float, disk_floor_gib: float,
              absolute_deadline: str | None = None) -> dict:
    """Enforce CPU runtime/free-resource limits without using a shell."""
    if (not command or not all(math.isfinite(v) for v in
            (seconds, ram_floor_gib, disk_floor_gib)) or
            seconds <= 0 or min(ram_floor_gib, disk_floor_gib) < 0):
        raise ValueError("Command and resource limits are invalid")
    deadline = None
    if absolute_deadline:
        stamp = datetime.fromisoformat(absolute_deadline.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("Absolute deadline must include its timezone")
        deadline = stamp.timestamp()
        if deadline <= time.time():
            raise ValueError("The authorized execution window has expired")
        seconds = min(seconds, deadline - time.time())
    cwd = cwd.resolve()
    cwd.mkdir(parents=True, exist_ok=True)
    if log_path.exists() or report_path.exists():
        raise FileExistsError("Supervisor output paths must be new")
    gib = 1024**3
    if available_ram_gib() < ram_floor_gib:
        raise RuntimeError("Insufficient free RAM")
    if shutil.disk_usage(cwd).free / gib < disk_floor_gib:
        raise RuntimeError("Insufficient free disk")
    environment = os.environ.copy()
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        environment[key] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    start = time.monotonic()
    minimum_ram = available_ram_gib()
    minimum_disk = shutil.disk_usage(cwd).free / gib
    reason = "completed"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("xb") as output:
        process = subprocess.Popen(command, cwd=cwd, env=environment,
                                   stdout=output, stderr=subprocess.STDOUT,
                                   shell=False, start_new_session=sys.platform != "win32",
                                   creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP
                                                  if sys.platform == "win32" else 0))
        try:
            while process.poll() is None:
                minimum_ram = min(minimum_ram, available_ram_gib())
                minimum_disk = min(minimum_disk, shutil.disk_usage(cwd).free / gib)
                if time.monotonic() - start >= seconds or (deadline and time.time() >= deadline):
                    reason = "timeout"
                elif minimum_ram < ram_floor_gib:
                    reason = "ram_floor"
                elif minimum_disk < disk_floor_gib:
                    reason = "disk_floor"
                if reason != "completed":
                    stop_tree(process)
                    break
                time.sleep(0.1)
            process.wait(timeout=10)
        finally:
            if process.poll() is None:
                stop_tree(process)
                process.wait(timeout=10)
    report = {"created_utc": utc_now(), "command": command, "cwd": str(cwd),
              "status": reason, "exit_code": process.returncode,
              "elapsed_seconds": time.monotonic() - start,
              "minimum_free_ram_gib": minimum_ram,
              "minimum_free_disk_gib": minimum_disk,
              "scope": "cpu_command_supervision",
              "note": "No GPU reservation, scientific acceptance or permission is granted."}
    write_new_json(report_path, report)
    return report


def main() -> None:
    """Supervise the exact reviewed argument vector supplied after the separator."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=40)
    parser.add_argument("--ram-floor-gib", type=float, default=4)
    parser.add_argument("--disk-floor-gib", type=float, default=2)
    parser.add_argument("--absolute-deadline")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    report = supervise(command, args.cwd, args.log, args.report, args.seconds,
                       args.ram_floor_gib, args.disk_floor_gib, args.absolute_deadline)
    if report["status"] != "completed" or report["exit_code"] != 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
```

### Archivo: tests/test_agentkit.py

```python file=tests/test_agentkit.py
"""Independent analytic controls and rejection tests for the delivered kit."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from scipy.linalg import expm

from agentkit.checkpoint import load_latest, save_checkpoint
from agentkit.demo import run_demo
from agentkit.evidence import (canonical, closure_status, evaluate_receipt,
                               freeze, inside, sha256_file, snapshot, verify_snapshot,
                               write_new_json)
from agentkit.learning import (MODELS, objective, paired_accuracy, prepare_data,
                               scores_and_directions)
from agentkit.mesh import compile_passive, decompose_unitary, reconstruct
from agentkit.metrology import fit_cutback, system_energy
from agentkit.numerics import (coherent_decomposition, exact_discrete_transport,
                               generalized_modes, mass_power, optical_error_budget,
                               phase_metrics, spatial_forecast, spatial_holdout,
                               splitting_control, transfer_sensitivity,
                               logarithmic_norm, residual_error_bound, detector_error_bound)
from agentkit.paraxial import grid, run_resumable, split_step
from agentkit.supervisor import supervise


class NumericalTests(unittest.TestCase):
    def test_dissipative_mass_generator_growth(self):
        m = np.diag([2.0, 3.0])
        a = -0.2*m + 1j*np.diag([1.0, 2.0])
        self.assertAlmostEqual(logarithmic_norm(a, m), -0.2)

    def test_residual_bound_recovers_exact_constant_forcing(self):
        result = residual_error_bound([0, 0.5, 1.0], [0.1, 0.1], 0.2, -0.3)
        expected = 0.2*np.exp(-0.3) + 0.1*(1-np.exp(-0.3))/0.3
        self.assertAlmostEqual(result, expected)

    def test_psd_detector_error_bound(self):
        u, e = np.array([1, 2j]), np.array([0.01j, 0.02])
        d, m = np.diag([0.4, 0.8]), np.diag([2, 3])
        measured = abs(np.vdot(u+e, d@(u+e))-np.vdot(u, d@u))
        bound = detector_error_bound(u, m, d, np.sqrt(mass_power(e, m)))
        self.assertLessEqual(measured, bound)

    def test_coherent_cross_term_cannot_be_discarded(self):
        u = np.array([1, 1j])
        r = np.array([[1], [1]], complex)
        dual = np.array([[1], [0]], complex)
        record = coherent_decomposition(u, r, np.ones(2), dual)
        self.assertAlmostEqual(record["total_power"], 2)
        self.assertAlmostEqual(record["cross_power"], -2)
        self.assertLess(record["balance_error"], 1e-12)

    def test_mass_orthogonal_projection(self):
        record = coherent_decomposition([1, 2j], [[1], [0]], [2, 3])
        self.assertAlmostEqual(record["total_power"], 14)
        self.assertAlmostEqual(record["cross_power"], 0)

    def test_nonpositive_mass_rejected(self):
        with self.assertRaises(ValueError):
            mass_power([1, 2], [1, -1])

    def test_nonnormal_eigenpair_condition(self):
        record = generalized_modes([[1, 4], [0, 2]], [1, 1])
        self.assertLess(record["relative_residuals"].max(), 1e-12)
        self.assertGreater(record["eigenvalue_condition_indicators"].max(), 4)

    def test_strang_second_order_on_fixed_smooth_matrices(self):
        a, b = 1j*np.array([[0, 1], [1, 0]]), 1j*np.diag([0.4, -0.4])
        errors = [splitting_control(a, b, [1, 0], 1, n)["relative_field_error"]
                  for n in (8, 16, 32)]
        self.assertTrue(3.8 < errors[0]/errors[1] < 4.2)
        self.assertTrue(3.8 < errors[1]/errors[2] < 4.2)

    def test_commuting_split_is_exact(self):
        result = splitting_control(1j*np.diag([1, 2]), 1j*np.diag([3, 4]), [1, 1j], 0.4, 3)
        self.assertLess(result["relative_field_error"], 1e-12)

    def test_frechet_derivative_matches_finite_difference(self):
        h, dh = np.array([[0, 0.5], [0.5, 0]]), np.diag([0.3, -0.2])
        result = transfer_sensitivity(h, dh, 0.8)
        epsilon = 1e-6
        reference = (expm(0.8j*(h+epsilon*dh))-expm(0.8j*(h-epsilon*dh)))/(2*epsilon)
        self.assertLess(np.linalg.norm(result["derivative"]-reference), 1e-8)

    def test_absolute_phase_error_is_retained(self):
        result = phase_metrics([1, 1], 1j*np.ones(2), np.ones(2))
        self.assertAlmostEqual(result["max_phase_error_rad"], np.pi/2)
        self.assertGreater(result["relative_field_error"], 1)

    def test_dark_field_does_not_divide_by_zero(self):
        result = phase_metrics([0, 0], [0, 0], [1, 1])
        self.assertIsNone(result["relative_field_error"])
        self.assertIsNone(result["max_phase_error_rad"])

    def test_s16_exact_law_and_heldout(self):
        h = np.array([1, 0.8, 0.64, 0.512])
        p = 0.333 + 0.002*h**2
        result = spatial_holdout(p[:3], [1e-10]*3, p[3], 1e-10, 1e-10, 1e-10)
        self.assertTrue(result["passed"])

    def test_s16_oscillation_and_temporal_noise_rejected(self):
        self.assertFalse(spatial_forecast([1, 2, 1.5], [0, 0, 0])["eligible"])
        self.assertFalse(spatial_forecast([1, 1.1, 1.15], [0.1]*3)["eligible"])

    def test_wavelength_interval_must_exclude_zero(self):
        with self.assertRaises(ValueError):
            optical_error_budget(1, 1, 1, 0, 0, 1)

    def test_transport_translation_and_mass_rejection(self):
        x = np.array([[0, 0], [1, 0]])
        result = exact_discrete_transport(x, [0.5, 0.5], x+[0, 0.2], [0.5, 0.5])
        self.assertAlmostEqual(result["wasserstein2"], 0.2, places=8)
        with self.assertRaises(ValueError):
            exact_discrete_transport(x, [1, 1], x, [0.5, 0.5])


class CompilerTests(unittest.TestCase):
    def test_complex_unitary_reconstruction(self):
        rng = np.random.default_rng(42)
        q, _ = np.linalg.qr(rng.standard_normal((6, 6))+1j*rng.standard_normal((6, 6)))
        compiled = decompose_unitary(q)
        self.assertLess(np.linalg.norm(reconstruct(compiled)-q), 1e-11)

    def test_passive_nondiagonal_target(self):
        q = expm(1j*np.array([[0.1, 0.7], [0.7, -0.3]]))
        target = q @ np.diag([0.9, 0.2]) @ q.T
        compiled = compile_passive(target)
        self.assertLess(np.linalg.norm(reconstruct(compiled)-target), 1e-12)
        self.assertFalse(compiled["geometry_validated"])

    def test_amplification_is_rejected(self):
        with self.assertRaises(ValueError):
            compile_passive(1.01*np.eye(2))


class PersistenceTests(unittest.TestCase):
    def test_atomic_checkpoint_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            marker = save_checkpoint(root, np.ones((2, 2), complex), 0, 10, "a"*64, None)
            next_marker = save_checkpoint(root, 2*np.ones((2, 2), complex), 5, 10,
                                          "a"*64, sha256_file(marker))
            state, step, _ = load_latest(root, "a"*64, 10)
            self.assertEqual(step, 5)
            self.assertTrue(np.all(state == 2))
            with self.assertRaises(FileExistsError):
                save_checkpoint(root, state, 5, 10, "a"*64, sha256_file(marker))
            record = json.loads(next_marker.read_text())
            (root/record["array_file"]).write_bytes(b"corrupt")
            with self.assertRaises(ValueError):
                load_latest(root, "a"*64, 10)

    def test_resume_matches_uninterrupted_trajectory(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (x, y), _ = grid(16, 64e-6)
            field = np.exp(-(x*x+y*y)/(8e-6)**2).astype(complex)
            profile = np.where(x < 0, -0.003, 0.0)
            source = root/"input.npz"
            np.savez(source, field=field, delta_n=profile)
            config = {"width_m": 64e-6, "wavelength_m": 1550e-9,
                      "n_reference": 1.444, "length_m": 20e-6, "steps": 7}
            result = run_resumable(source, config, root/"checkpoints", 2, 40)
            restored, step, _ = load_latest(root/"checkpoints", result["experiment_hash"], 7)
            expected = field
            for _ in range(7):
                expected = split_step(expected, profile, 64e-6, 1550e-9, 1.444, 20e-6/7)
            self.assertEqual(step, 7)
            np.testing.assert_array_equal(restored, expected)
            second = run_resumable(source, config, root/"checkpoints", 2, 40)
            self.assertEqual(second["steps_at_entry"], 7)

    def test_snapshot_rejects_mutation_and_traversal(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root/"input.txt").write_text("original")
            record = snapshot(root, ["input.txt"])
            (root/"input.txt").write_text("changed")
            with self.assertRaises(ValueError):
                verify_snapshot(root, record)
            with self.assertRaises(ValueError):
                inside(root, "../input.txt")

    def test_receipt_cannot_turn_partial_execution_into_pass(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.name=Kit Test",
                            "-c", "user.email=kit@example.invalid", "commit", "--allow-empty",
                            "-qm", "manufactured test"], check=True)
            protocol = {"experiment_id": "test", "task_id": "T01", "model": "fixture",
                        "units": {"length": "m"}, "scope": "manufactured_control",
                        "criteria": [{"id": "error", "operator": "le", "threshold": 0.1}],
                        "resource_limits": {"seconds": 1}, "heldout_policy": "fixture"}
            write_new_json(root/"protocol.json", protocol)
            (root/"source.py").write_text("x = 1\n")
            (root/"raw.csv").write_text("value\n0.05\n")
            frozen = freeze(root, "protocol.json", ["source.py"], root/"frozen.json")
            result = {"experiment_id": "test", "protocol_sha256": hashlib.sha256(canonical(protocol)).hexdigest(),
                      "scope": "manufactured_control", "status": "partial",
                      "artifacts": ["raw.csv"], "metrics": {"error": 0.05}}
            with self.assertRaises(ValueError):
                evaluate_receipt(root, frozen, result)
            result["status"] = "completed"
            result["metrics"] = {}
            self.assertFalse(evaluate_receipt(root, frozen, result)["passed"])
            result["metrics"] = {"error": 0.05}
            self.assertTrue(evaluate_receipt(root, frozen, result)["passed"])

    def test_numerical_audit_does_not_close_physical_task(self):
        task = {"scope": "physical_device", "requires": []}
        self.assertEqual(closure_status(task, {"scope": "numerical", "passed": True}, {}),
                         "BLOCKED_SCOPE")

    def test_supervisor_timeout(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            report = supervise([sys.executable, "-c", "import time; time.sleep(5)"],
                               root, root/"log.txt", root/"report.json", 0.2, 0, 0)
            self.assertEqual(report["status"], "timeout")
            self.assertNotEqual(report["exit_code"], 0)


class LearningAndMeasurementTests(unittest.TestCase):
    def test_analytic_gradients_for_all_models(self):
        rng = np.random.default_rng(9)
        x = rng.normal(size=(7, 3))
        y = np.arange(7) % 3
        for model in MODELS:
            with self.subTest(model=model):
                size = 18 if "_" in model else 9
                p = rng.normal(scale=0.2, size=size)
                loss, gradient = objective(p, x, y, model, 2.3, 0.1)
                numerical = np.zeros(size)
                for i in range(size):
                    delta = np.zeros(size)
                    delta[i] = 1e-6
                    high = objective(p+delta, x, y, model, 2.3, 0.1)[0]
                    low = objective(p-delta, x, y, model, 2.3, 0.1)[0]
                    numerical[i] = (high-low)/2e-6
                self.assertTrue(np.isfinite(loss))
                np.testing.assert_allclose(gradient, numerical, atol=3e-7, rtol=3e-5)

    def test_cascaded_unitaries_preserve_linear_function_class(self):
        rng = np.random.default_rng(3)
        u, v = expm(1j*np.diag([0.2, 0.4])), expm(1j*np.array([[0, 1], [1, 0]]))
        x = rng.normal(size=(10, 2))
        np.testing.assert_allclose((x @ u.T) @ v.T, x @ (v @ u).T, atol=1e-14)

    def test_bootstrap_reports_observed_difference_exactly(self):
        result = paired_accuracy([0, 1, 0, 0], [0, 0, 1, 0], [0, 1, 1, 0], 200)
        self.assertEqual(result["observed_difference"], 0.0)

    def test_data_preprocessing_uses_training_only(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            rng = np.random.default_rng(13)
            x = rng.normal(size=(90, 4))
            y = np.repeat(np.arange(3), 30)
            np.savez(root/"raw.npz", X=x, y=y)
            first = prepare_data(root/"first", root/"raw.npz", 42)
            with np.load(root/"first"/"test.npz") as data:
                test_indices = data["raw_indices"]
            x[test_indices] += 100000
            np.savez(root/"changed.npz", X=x, y=y)
            second = prepare_data(root/"second", root/"changed.npz", 42)
            np.testing.assert_allclose(first["mean"], second["mean"], atol=0)
            np.testing.assert_allclose(first["pca_components"], second["pca_components"], atol=0)

    def test_manufactured_cutback_recovers_known_slope(self):
        with tempfile.TemporaryDirectory() as name:
            report = run_demo(Path(name)/"demo")["manufactured_cutback"]
            self.assertAlmostEqual(report["mean_loss_db_per_cm"], 0.1, places=10)
            self.assertLess(report["ci95"][0], 0.1)
            self.assertGreater(report["ci95"][1], 0.1)

    def test_whole_system_energy_includes_all_components(self):
        rows = [{"time_s": i, "completed_inferences": i*10, "source_w": 1,
                 "modulation_w": 1, "detection_w": 1, "control_w": 1, "cooling_w": 1}
                for i in range(3)]
        result = system_energy(rows)
        self.assertAlmostEqual(result["total_energy_j"], 10)
        self.assertAlmostEqual(result["joules_per_inference"], 0.5)
        rows[1]["time_s"] = 0
        with self.assertRaises(ValueError):
            system_energy(rows)

    def test_split_step_does_not_renormalize_loss(self):
        (x, y), dx = grid(16, 64e-6)
        field = np.ones_like(x, dtype=complex)
        output = split_step(field, np.zeros_like(x), 64e-6, 1550e-9,
                            1.444, 1e-6, np.full_like(x, 1e5))
        ratio = np.sum(abs(output)**2) / np.sum(abs(field)**2)
        self.assertAlmostEqual(ratio, np.exp(-0.2), places=12)


if __name__ == "__main__":
    unittest.main()
```

## 36. Prompt de arranque para el agente ejecutor

Lee esta guía completa y las instrucciones actuales del repositorio. Trabaja sobre Silice-Neuro3D-Cube en un worktree aislado en D: o E:. Reconcilia main y auditoria-20261009, preserva datos y negativos, y ejecuta el orden de tareas con sus dependencias. Empieza por evidencia y T01; reutiliza los campos válidos por hash. Extrae y verifica el kit incluido antes de aplicarlo. Registra cada protocolo antes de nuevos datos, utiliza los auditores pertinentes y no rebajes umbrales después de ver resultados. Completa código y presentación en inglés profesional; las explicaciones para Fran, en español. Mantén estados separados de software, modelo y hardware. Prepara protocolos y entregables concretos para los bloqueos físicos y externos; continúa el trabajo independiente autorizado. No declares fabricación, medidas, novedad, independencia, impacto ni calidad Nobel sin evidencia. Entrega una release coherente con el alcance realmente validado, un manuscrito completo y una matriz T01–T22 con datos, criterios, limitaciones y próxima acción.

> **Adición v2.** Para ejecutar con esta versión, usar el prompt de §51, que incorpora las tareas T23–T30 y las reglas nuevas.

---

# Parte II — Ampliación v2 (12 de octubre de 2026)

Esta parte añade trabajo nuevo y no sustituye nada de la Parte I. Cada afirmación nueva indica cómo se comprobó. Lo que no se pudo comprobar se declara como tal.

## 37. Resultado de la revisión v2: qué se verificó y qué no

| Comprobación | Método | Resultado |
|---|---|---|
| Commits de §1 | `git ls-remote` de ambos repositorios | Coinciden los tres. Hay además `codex/scientific-closure-20261006` (`b344dcf`), antecesora de `main`, y la PR #1 (`03b5f55`), ya fusionada. |
| Rutas del proyecto citadas | Clon parcial (`--filter=blob:none`) y `git ls-tree` de `main`, de la rama de auditoría y de la rama de Codex | 23 rutas: 21 existen tal como se citan (6 sólo en la rama de auditoría, 4 de ellas ya señaladas en §1) y 2 están abreviadas (§47 E1, E2). |
| Rutas de `openai/math` | `git cat-file -e` en `fd4aeeb` | Las 10 rutas citadas existen. |
| Cifras del proyecto citadas | Lectura de los documentos de la rama de auditoría (`RESULTADOS-ABLACION.md`, `T12-CIERRE…`, `CORRECCION-ESTADOS…`, `NOVEDAD-ESTADO…`) | Coinciden: 64,25 %/84,55 %, 86,2 %/59,05 %, C3 28/36, H10b (cociente 1,68), 0,044 dB/cm en HE11, 91,7 % en 48 imágenes y 6554 TOPS teóricos. Hallazgo adicional: la tarea de F3 está muy desequilibrada (§44, punto 5). |
| Kit v1 | Extracción con su propio extractor y ejecución en Python 3.13.16 (Linux) con NumPy 2.5.3/SciPy 1.18.1 y con el conjunto fijado NumPy 2.2.6/SciPy 1.15.1 | 32/32 pruebas; CLI de §31, §16, §18 y §30.1 operativos. |
| Ejemplo de entrenamiento de §16 | Ejecución literal | `unitary_mzm`: 0/8 arranques convergidos. `unitary`: 8/8. El arranque 1 da 6,57·10⁻⁸, igual que §33; el seleccionado aquí es el 7 (1,60·10⁻⁸) por un empate numérico de pérdidas. |
| Integridad de recibos v1 | Prueba adversarial | Un recibo de congelación con el umbral relajado sólo en su copia del protocolo se acepta como PASS (§47 E5). |
| Gobernanza del repositorio | Lectura de `AGENTS.md`, `scripts/check.py` y la CI | La extracción v1 escribe en `tests/` (propiedad de Codex) y cambiaría la suite que ejecuta la CI (§47 E4). |
| Referencias bibliográficas | Crossref, páginas de arXiv y Europe PMC (las páginas de PMC exigían CAPTCHA) | 27 referencias comprobadas, más Tan et al. (2022) añadida tras la revisión; correcciones en §46 y §47. |
| Revisión adversarial del material v2 | Un agente separado, que no participó en la redacción, auditó todas las adiciones, recalculó cifras y atacó el código | 23 hallazgos (8 mayores) en el borrador v2. Todos corregidos; sus ataques se volvieron a ejecutar contra el código corregido y fallan (§47 E17–E30). |

**No se hizo:** compilar Lean ni ejecutar Comparator; ejecutar D16, GPU, Blender o Maxwell 3D; fabricar o medir; acceder a la máquina del titular; publicar, enviar o contactar a nadie. Las referencias se verificaron por sus metadatos y, cuando se indica, por su resumen o texto completo. No se leyeron completos todos los artículos.

## 38. Qué significa aquí «nivel Nobel» y cómo perseguirlo sin autoengaño

### 38.1. Lo que muestran los precedentes

Los premios del ámbito más cercano comparten un patrón. Charles Kao (Física, 2009) cuantificó que la atenuación de las fibras de vidrio se debía a impurezas y propuso un objetivo verificable por debajo de unos 20 dB/km en 1966; la industria lo alcanzó después y el premio llegó más de cuatro décadas más tarde. Akasaki, Amano y Nakamura (2014) resolvieron un problema de materiales y fabricación que llevaba décadas abierto: el LED azul eficiente. Ashkin, Mourou y Strickland (2018) crearon métodos que se reprodujeron y usaron de forma generalizada. Hopfield y Hinton (2024) recibieron el premio por descubrimientos fundacionales que permiten el aprendizaje automático con redes neuronales artificiales, con raíces explícitas en la física estadística.

El patrón operativo es este:

1. Una pregunta que la comunidad ya reconoce como importante, o un límite que se creía insuperable.
2. Una demostración decisiva y cuantitativa, con un número que otros pueden medir.
3. Reproducción y uso por terceros.
4. Impacto sostenido durante años o décadas.

Los puntos 1 y 2 dependen del proyecto. El 3 depende de facilitarlo y el 4 no se controla.

### 38.2. Lo que no cuenta

El número de scripts, de tareas cerradas o de documentos; las puntuaciones entre agentes de IA; los PASS internos de software; las cifras teóricas de rendimiento; y una afirmación de novedad sin búsqueda documentada. La competición entre agentes (Claude, Codex, JEV) es útil para encontrar fallos, pero crea un incentivo para sobreafirmar; las defensas de §41 existen también para eso.

### 38.3. Estado honesto de partida

Según T19 y `Docs/NOVEDAD-ESTADO-20261011.md`, ninguna aportación original está establecida. La red 3D multicapa escrita con fs en vidrio tiene un antecedente publicado (LAMP; Cao et al., 2026). El umbral H1 de 0,3 dB/cm queda lejos de 0,07 dB/cm a 1550 nm en sílice (Tan et al., 2022), cifra que Skryabin et al. (2024) citan como récord y que ellos mismos obtienen a 920 nm. Esta revisión no hizo una búsqueda exhaustiva de resultados posteriores (T26). F3-b no cumple sus hipótesis. El proyecto tiene, en cambio, un activo poco común: una disciplina de evidencia que conserva negativos, y una infraestructura numérica auditada.

### 38.4. Consecuencia para el plan

Antes de invertir en fabricación, hay que ejecutar pruebas de descarte baratas (T24, T25, T26) que digan si la afirmación central puede ganar en algún eje medible. Después se elige **una** afirmación central (T20), se diseña su experimento decisivo con datos reservados y análisis ciego, y se prepara la replicación externa. Un resultado negativo sólido, bien delimitado, es una contribución publicable; una afirmación grande sin evidencia no lo es.

## 39. Pregunta central y criba de hipótesis de alto impacto

Cada candidata tiene un criterio de descarte que se evalúa antes de gastar recursos de fabricación. Registrar la elección en el registro de afirmaciones (§41.3) y en T20 antes de generar datos nuevos.

| Id | Hipótesis candidata | Por qué importaría | Prueba decisiva | Criterio de descarte | Antecedente que superar |
|---|---|---|---|---|---|
| H-A | Una capa óptica pasiva en sílice, con su electrónica completa, necesita menos energía por MAC útil que una referencia digital citada, a igual precisión de salida. | Es el argumento habitual del cómputo óptico. | Energía medida del sistema completo (T17) frente a la referencia en la misma tarea. | El presupuesto T24 con parámetros con fuente da factor de ventaja ≤ 1 incluso en el caso optimista. | Hamerly et al. (2019); Wang et al. (2022); McMahon (2023). |
| H-B | Para transformaciones estructuradas no universales (tipo butterfly/FFT o convolución), el ruteo 3D elimina cruces que una disposición plana necesita, y reduce pérdida y diafonía medidas a igual N. | Sería una ventaja física específica de la escritura 3D. | Comparación medida de dos realizaciones (3D frente a plana con cruces) de la misma transformación. | La pérdida y diafonía medidas por cruce (T08/T14) hacen que la diferencia prevista para el N objetivo sea menor que la incertidumbre de medida. | Moughames et al. (2020); LAMP (2026); búsqueda T19 de redes butterfly fotónicas. |
| H-C | La calibración in situ de una red escrita con fs absorbe errores de fabricación correlacionados y medidos hasta un error de transferencia fijado. | Haría robusta una tecnología con tolerancias de escritura. | Error de transferencia tras calibrar, medido durante un tiempo fijado (T10/T15). | Con la correlación medida, el error tras recalibrar supera el umbral en el percentil registrado (§42). | Saygin et al. (2020); Kondratyev et al. (2024); Pentangelo et al. (2024). |
| H-D | Guías de trinchera en sílice a 1550 nm con pérdida cerca de su fuga vectorial ideal y curvas o cruces 3D de baja pérdida que permiten mayor densidad. | Caracterización útil si supera el estado del arte en un eje. | Cutback ciego con modo declarado y tres o más chips (T14). | Cota inferior del IC por encima de 0,07 dB/cm sin ventaja demostrada en curvatura o densidad. | Tan et al. (2022); Skryabin et al. (2024); Lee et al. (2021); Zhou et al. (2025, SK1310). |
| H-E | «Renderizar como computar»: existe una clase de operaciones del pipeline gráfico equivalente, con cotas de error, a operadores de propagación óptica lineal. | Contribución metodológica, no física. | Teorema más núcleo verificado con campos complejos y fases frente a la referencia CPU, y coste completo medido (§29). | El núcleo nunca supera al BPM FFT en CPU/GPU a igual precisión con coste completo (los negativos R1/R2/P1 piden prudencia). | Wright et al. (2022) sobre redes físicas; los negativos propios R1/R2/P1. |

**Resultado teórico que redirige H-B (conteo de dimensiones).** La dimensión real de U(N) es N². Una malla de elementos de dos modos con dos fases cada uno más N fases de salida necesita al menos N(N − 1)/2 elementos para cubrir un conjunto denso de unitarias. Una capa contiene como máximo ⌊N/2⌋ elementos disjuntos, de modo que la profundidad mínima es N − 1, **con cualquier conectividad, plana o 3D**. La malla de Clements alcanza N (§43). En general, si cada capa programable tiene p parámetros, la profundidad es al menos del orden de N²/p. La escritura 3D no puede mejorar la profundidad lógica de una unitaria universal con elementos de dos modos; su ventaja posible está en cruces, densidad, longitud de ruta o transformaciones estructuradas, que es lo que H-B mide.

**Regla.** Elegir una sola hipótesis como titular antes de nuevos datos. Las demás pasan a secundarias o se retiran con su motivo. Un cambio posterior de titular es una enmienda fechada que no reutiliza como confirmatorios los datos ya vistos.

## 40. T24 — Límites fundamentales y presupuesto energético (prueba de descarte)

### 40.1. Modelo

En cada detector, durante un periodo de muestra T y con N_e fotoelectrones a fondo de escala:

$$
\sigma^2 = N_e + \sigma_{th}^2,\qquad
\sigma_{th} = \frac{i_n\sqrt{B}\,T}{q},\qquad
k\,\sigma \le \frac{N_e}{2L},\quad L=2^{b}.
$$

La solución mínima es

$$
N_e = \frac{1+\sqrt{1+4a\sigma_{th}^2}}{2a},\qquad a=\frac{1}{4k^2L^2},
$$

que sin ruido térmico se reduce a N_e = 4k²L². La energía óptica por detección es N_e·hν/η. En una capa densa de N entradas y M salidas, la luz de cada detector sirve a N productos, de modo que la parte óptica por MAC cae como 1/N; es el argumento de multiplicación fotoeléctrica de Hamerly et al. (2019). El presupuesto completo suma láser (con eficiencia de enchufe y transmisión óptica total), moduladores, DAC, ADC y potencia estática de control y refrigeración.

### 40.2. Cifras del modelo (no son medidas)

Con λ = 1550 nm (hν = 1,2816·10⁻¹⁹ J), k = 1 y eficiencia cuántica 1, sin ruido térmico, `agentkit.limits` da:

| Bits | Fotoelectrones | Energía óptica por detección | Por MAC con N = 64 |
|---|---|---|---|
| 4 | 1024 | 1,31·10⁻¹⁶ J | 2,05·10⁻¹⁸ J |
| 6 | 16 384 | 2,10·10⁻¹⁵ J | 3,28·10⁻¹⁷ J |
| 8 | 262 144 | 3,36·10⁻¹⁴ J | 5,25·10⁻¹⁶ J |

Con 8 bits, eficiencia 0,8, i_n = 10 pA/√Hz y 1 GS/s (B = 0,5 GHz), el ruido térmico equivale a unos 1396 electrones y la energía por detección sube a 1,37·10⁻¹³ J. Estas cifras dependen del criterio k·σ ≤ ½ LSB elegido; otro criterio cambia los números y debe registrarse antes.

La energía óptica en el detector rara vez es el término dominante del sistema; suelen dominar la conversión electrónica y el control. Pero ese reparto depende de los parámetros reales y no se presupone. El ejemplo `agentkit/limits_example_params.json` usa valores **fabricados** sólo para ejercitar el código y declara la procedencia de cada parámetro, como exige la herramienta. En él, el término estático es el mayor, sólo un 4 % por encima del láser; ilustra el método y no describe ningún dispositivo.

### 40.3. Protocolo de la prueba de descarte

1. Rellenar cada parámetro con una fuente citada o una medida, con su intervalo plausible: eficiencia cuántica, ruido de entrada, ancho de banda, pérdida total, eficiencia del láser, energía de modulador, DAC y ADC, potencia estática y referencia digital. Las energías digitales deben citar nodo y año, por ejemplo la tabla de Horowitz (ISSCC 2014, 45 nm), y no copiarse sin esa etiqueta.
2. Registrar el protocolo con `agentkit.prereg` antes de calcular.
3. Calcular el caso nominal y el optimista con `python -B -m agentkit.limits --params <archivo> --out <nuevo>`.
4. Si el optimista da factor de ventaja ≤ 1, H-A queda descartada como titular y se conserva el negativo.
5. Calcular también la profundidad máxima permitida por la pérdida con `agentkit.limits.max_depth`, a partir de la potencia disponible, la pérdida fija y la pérdida por etapa medida (T08/T14). Si la profundidad que exige la arquitectura supera ese máximo, la arquitectura no escala con esa tecnología.

## 41. T23 — Defensas contra el autoengaño

### 41.1. Prerregistro anclado en git (`agentkit.prereg`)

El recibo v1 guardaba una copia del protocolo y `evaluate_receipt` la usaba sin compararla con el archivo. Con un umbral relajado sólo en esa copia, la evaluación aprobaba (demostrado; §47 E5). v2:

- exige que protocolo y fuentes estén versionados y sin cambios. Compara identificadores de blob con los filtros de git, de modo que un mismo commit se audita igual desde una copia con CRLF (Windows) o con LF (Linux). Normaliza los separadores `\` y decodifica la salida de git en UTF-8 en cualquier configuración regional;
- exige `planned_artifacts` no vacío y rechaza el compromiso si alguno ya existe;
- en la auditoría, relee el protocolo desde el objeto git y comprueba que las fuentes no cambiaron. Marca como fallo cualquier artefacto que ya estuviera en el commit del compromiso, que no estuviera planificado o que se añadiera en un commit que no desciende del compromiso;
- recorre el historial y marca como fallo cualquier otra versión del mismo archivo de protocolo con el mismo `experiment_id`. Así se detecta un protocolo relajado y committeado después de uno estricto;
- con `--query-server`, comprueba la publicación con `git ls-remote` en el servidor, tanto al comprometer como al auditar, en lugar de fiarse de una rama de seguimiento local que se puede mover sin publicar. `--require-published` hace que la auditoría falle si no se verifica.

```powershell
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.prereg commit --protocol <protocolo.json> --sources <fuentes...> --out resultados/agent/<id>_commitment.json --remote-ref origin/<rama> --query-server
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.prereg verify --commitment resultados/agent/<id>_commitment.json
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.prereg audit --commitment resultados/agent/<id>_commitment.json --result <resultado.json> --out resultados/agent/<id>_audit.json --query-server --require-published
```

Committear y publicar también el registro de compromiso antes de producir datos. **Límite que no se puede cerrar desde el repositorio:** un protocolo que se committea por primera vez después de producir los datos, sin una versión anterior en el historial, no es detectable. Para afirmaciones confirmatorias hace falta una marca externa (un depósito con DOI o un servicio de prerregistro) y la custodia de datos de §41.2. Publicar en una rama remota requiere autorización vigente.

### 41.2. Análisis ciego (`agentkit.blind`)

El analista desarrolla todo el análisis sin ver el valor real. Es práctica estándar en física de partículas (Klein y Roodman, 2005).

1. Un custodio, persona o agente que no analiza, crea el secreto y publica sólo su compromiso SHA-256, que se incluye en el protocolo prerregistrado.
2. El custodio genera el CSV ciego. Multiplicar cada potencia de salida por 10^(−δ·L_cm/10) suma exactamente δ dB/cm a cada pendiente y deja intactos residuos, intercepciones y anchuras de intervalo. Las potencias ciegas se redondean al número de cifras significativas del registro del instrumento (`--significant-digits`, obligatorio); sin ese redondeo, δ se recupera ajustando los valores a la rejilla del instrumento (ataque demostrado en la revisión, §47 E22).
3. El analista ajusta, revisa residuos y corrige errores sobre datos ciegos. Después crea un registro de congelación (`blind freeze`) con el hash del informe ciego y de las fuentes de análisis, y lo committea.
4. Sólo entonces se revela el secreto. `unblind` exige que el registro de congelación nombre ese informe, que esté committeado sin cambios y que el secreto coincida con el compromiso.
5. Tras desenmascarar no se cambia el análisis. Cualquier cambio posterior es exploratorio y se declara así.

```powershell
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.blind init --secret <ruta_custodio>/secret.json --scale-db-per-cm 2.0 --commitment-out resultados/agent/blind_commitment.json
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.blind blind --input <medidas.csv> --secret <ruta_custodio>/secret.json --commitment <sha256> --significant-digits <cifras_del_instrumento> --out resultados/agent/cutback_blinded.csv
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.metrology cutback --input resultados/agent/cutback_blinded.csv --out resultados/agent/cutback_blinded_report.json
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.blind freeze --report resultados/agent/cutback_blinded_report.json --sources agentkit/metrology.py --out resultados/agent/blind_analysis_freeze.json
git add resultados/agent/blind_analysis_freeze.json; git commit -m "Freeze blinded cutback analysis"
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.blind unblind --report resultados/agent/cutback_blinded_report.json --secret <ruta_custodio>/secret.json --commitment <sha256> --analysis-freeze resultados/agent/blind_analysis_freeze.json --out resultados/agent/cutback_unblinded_report.json
```

**Escala y fugas.** El desplazamiento es uniforme en [−s, s]. Cualquier desplazamiento acotado revela el veredicto en las colas, con probabilidad como máximo |μ − U|/(2s), donde μ es la pendiente real y U el umbral. Con s = 2 dB/cm y |μ − U| ≤ 0,26 dB/cm, esa probabilidad es ≤ 6,5 %. Las pendientes ciegas negativas (ganancia aparente) son esperables y no son anomalías; el análisis no debe usar el signo físico de la pendiente. El mismo principio se aplica al test de T16: el custodio guarda las etiquetas y entrega sólo la evaluación única.

### 41.3. Registro de afirmaciones (`agentkit.claims`)

Todas las frases públicas sobre el proyecto (README, manuscrito, mensajes) salen de un único registro JSON. Reglas que el validador aplica:

- Cada afirmación tiene alcance, estado, enunciado y **falsador**, es decir, qué observación la refutaría. Los alcances cubren todos los de `agentkit/tasks.json` y `tasks_v2.json`, de modo que T01–T30 se pueden volcar sin traducción.
- PASS exige evidencia cuyos bytes coinciden con el hash registrado y cuyo tipo corresponde al alcance: una simulación nunca cierra una afirmación física; la novedad exige un registro de búsqueda; una afirmación científica central exige medida o test reservado.
- Cada evidencia declara quién la produjo y cómo. Una medida declara instrumento y operador. Una reproducción externa o un registro de terceros declara el equipo independiente y un registro público (DOI o URL). El validador rechaza como reproducción externa cualquier evidencia que nombre a un agente del proyecto (`project_agents`: Claude, Codex, JEV). El tipo de evidencia sigue siendo una declaración; un auditor humano comprueba esas declaraciones.
- PASS exige que todas las dependencias sean PASS, y el validador rechaza los ciclos de dependencias.
- Una afirmación retirada conserva su motivo.
- La tabla sólo se escribe si el registro es consistente. Columnas: id, alcance, estado, enunciado, falsador, evidencia, limitaciones y próxima acción.

```powershell
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.claims --ledger <registro.json> --root . --table resultados/agent/claims_table.md
```

`agentkit/claims_example.json` contiene afirmaciones reales del proyecto con su estado actual y es consistente según el validador. Ninguna está en PASS: la afirmación del propio kit queda OPEN hasta adjuntar el registro de ejecución de sus pruebas, y H1 conserva su redacción registrada, sin enmiendas no fechadas. La tabla generada se pega en README y manuscrito; no se reescribe a mano.

### 41.4. Independencia y agentes de IA

- Los agentes de IA que trabajan sobre el mismo repositorio, con instrucciones parecidas, comparten fuentes de error. Su acuerdo es una comprobación débil y nunca una replicación.
- Usarlos como revisores adversariales: cada objeción se registra por escrito con su resolución, y un auditor reimplementa las métricas desde cero en lugar de importar el evaluador.
- Control de alucinaciones: toda referencia se verifica por DOI o identificador arXiv contra Crossref, arXiv o la editorial antes de citarla (como en §46); todo número de un manuscrito se rastrea hasta un archivo con hash; toda cita literal se comprueba en la fuente.
- La procedencia del consejo de JEV sigue la regla de `AGENTS.md` (`provenance=jev`).

### 41.5. Hipótesis rivales e inferencia fuerte

Para cada resultado positivo, listar las explicaciones alternativas y el control que excluye cada una, antes de medir. Ejemplos del proyecto: una pérdida baja medida puede deberse a filtrado modal, deriva del acoplo o longitudes mal medidas; una mejora de exactitud puede deberse a ganancia o escala de la referencia (§44) y no a la activación. Un resultado sólo se interpreta cuando cada rival tiene su control.

### 41.6. Pre-mortem y equipo rojo (T30)

Antes de enviar el manuscrito, suponer que fue refutado un año después y escribir las tres causas más probables. Pedir a revisores humanos externos que intenten romper la afirmación central con los datos y el código. Registrar las objeciones y sus respuestas.

## 42. Estadística de decisión

### 42.1. Regla de tres zonas para H1 (resuelve las zonas abiertas)

Para una magnitud de pérdida con IC 95 % [l, u], umbral U y suelo de modelo F < U:

- **CONFIRMED** si u ≤ U y l ≥ F;
- **FALSIFIED** si l > U;
- **MODEL_CONTROL_FAIL** si u < F: la medida bate una fuga ideal, lo que indica un error de modelo o de medida y nunca un éxito;
- **INCONCLUSIVE** en cualquier otro caso, incluido un IC que contiene U o F.

`agentkit.stats.three_zone_decision` implementa la regla y devuelve por separado la zona respecto del umbral (veredicto de H1) y la zona respecto del suelo (consistencia del modelo). Ejemplo: [0,25; 0,35] con U = 0,3 y F = 0,044 da INCONCLUSIVE. Una sola regla sustituye la mezcla de IC 95 % y «0,044 − 3σ» señalada en `NOVEDAD-ESTADO` §5(ii). Como advierte §18.2, 0,044 dB/cm no es un suelo universal: F debe ser la fuga recalculada para el perfil medido (T05), con su incertidumbre.

### 42.2. Número de chips (planificación)

Prueba unilateral H0: μ ≥ U frente a H1: μ < U con α = 0,025, que es lo que implica decidir con el límite superior de un IC bilateral del 95 % (§42.1); potencia 0,8, unidades independientes (chips) y σ entre chips como **valor de planificación**:

| Margen esperado U − μ | σ entre chips | Chips necesarios | Potencia alcanzada |
|---|---|---|---|
| 0,10 dB/cm | 0,05 dB/cm | 5 | 0,91 |
| 0,05 dB/cm | 0,05 dB/cm | 10 | 0,80 |
| 0,02 dB/cm | 0,05 dB/cm | 52 | 0,81 |

El cálculo usa la distribución t no central y se contrastó por Monte Carlo en las pruebas. Es un mínimo: `metrology.fit_cutback` usa el mayor de los errores estándar entre chips y de medida. Con tres chips sólo se detectan márgenes muy grandes. Fijar σ a partir de datos piloto declarados como tales, no de los datos confirmatorios.

### 42.3. Rendimientos y colas

- Proporciones: intervalo exacto de Clopper–Pearson. Para C3, 28/36 = 77,8 % con IC 95 % [60,8 %; 89,9 %] (comprobado contra la implementación exacta de SciPy). Presentar siempre el intervalo, no sólo el 78 %.
- Percentiles: para afirmar una cota del percentil 95 sin suponer distribución, hacen falta al menos 59 realizaciones independientes (95/95), 90 (95/99) o 299 (99/95); `upper_tolerance_bound` devuelve la cota o indica cuántas faltan.
- Equivalencia: para afirmar «A y B coinciden dentro de ±m» (por ejemplo CPU frente a GPU), usar TOST (Schuirmann, 1987); un test de diferencia no significativo no demuestra equivalencia.
- Multiplicidad: con varias hipótesis confirmatorias, aplicar Holm y registrarlo antes.
- Clasificación: declarar siempre la línea base de clase mayoritaria y una métrica equilibrada (exactitud equilibrada o F1 macro) junto con la exactitud; con clases desequilibradas, la exactitud sola exagera la mejora (§44, punto 5).

## 43. Compilador v2: malla rectangular de MZI (T11, T25)

`agentkit.mzi` implementa:

- **Convención explícita.** MZI(θ, φ) = B · diag(e^{iθ}, 1) · B · diag(e^{iφ}, 1), con B un acoplador simétrico 50:50 y ambos desfasadores en el brazo superior. Otras convenciones requieren su propia derivación; la prueba de aceptación es la reconstrucción, no las fórmulas.
- **Orden de Clements** (Optica, 2016): N(N − 1)/2 MZI más una pantalla de fases de salida. Profundidad medida N para N = 3 a 16, frente a 2N − 3 de la síntesis triangular de v1 (N = 4: 5; N = 8: 13; N = 16: 29). Error de reconstrucción espectral por debajo de 10⁻¹² en las pruebas.
- **Compilación pasiva** T = U·diag(s)·V† con dos mallas y amplitudes s ≤ 1; rechaza la ganancia, como `agentkit.mesh` v1. La profundidad informada es la de ambas mallas más la columna de atenuadores.
- **Errores de divisor** con componente compartida: con N = 6, σ = 0,02 rad y 1000 realizaciones (unitaria `random_unitary(6, 2)`, semilla 7), la fidelidad media es 0,99801, 0,99783 y 0,99773 con 0 %, 50 % y 80 % de varianza compartida, y el percentil 5 baja de 0,99684 a 0,99425 y 0,99251. La correlación casi no cambia la media pero ensancha la cola, lo mismo que mostró H10b. Son resultados de modelo sin calibrar; la recalibración in situ puede recuperar parte de esa pérdida.

Decisiones de diseño que T11 debe registrar antes de exportar geometría:

1. **Fases estáticas o programables.** Una red con fases fijadas por la longitud escrita no se puede entrenar ni recalibrar después; todos los errores deben precompensarse, lo que exige la precisión de T09 y T10. Con microcalentadores, como LAMP y los procesadores de Pentangelo et al., la red se calibra in situ a cambio de potencia estática (T24).
2. **Arquitectura robusta.** Comparar Clements con arquitecturas tolerantes a errores de divisor (Saygin et al., 2020) usando los errores medidos.
3. **Correspondencia física.** Traducir θ y φ a diferencias de camino óptico, Δ(nL) = θλ/(2π), y a acopladores con la κ medida; volver a simular la geometría exportada con la biblioteca calibrada.

## 44. Red neuronal v2: convergencia, ganancia y entrenamiento con hardware en el lazo (T12, T27)

Todos los resultados de esta sección son **controles de desarrollo** sobre los dígitos públicos 0–3, ya usados en el proyecto; no son confirmatorios. Datos: partición del ejemplo de §16 (430/142/148).

| Modelo | Arranques convergidos (max \|g\| ≤ 10⁻⁵) | Arranque seleccionado y su pérdida de entrenamiento | Exactitud entrenamiento / validación del seleccionado |
|---|---|---|---|
| `unitary_mzm` (v1, \|cos\|) | 0/8 (4,8·10⁻³ a 6,1·10⁻²) | 1 (no convergido), 1,1019 | 61,4 % / 56,3 % |
| `unitary_mzm_signed` (v2) | 8/8 (≤ 2,0·10⁻⁶) | 6, 0,7315 | 76,7 % / 73,2 % |
| `unitary` (v1, sin MZM) | 8/8 | 7, 0,7943 | 80,0 % / 73,9 % |
| `real_mzm_signed` (v2) | 3/8 | 2, 0,3440 | 85,8 % / 84,5 % |

v2 selecciona por pérdida de entrenamiento mínima **entre los arranques convergidos** (o entre todos, marcándolo, si ninguno converge). En `real_mzm_signed`, el arranque de menor pérdida (8; 0,2683) no convergió. La validación de ese modelo (pérdida 0,645 frente a 0,344 en entrenamiento) indica sobreajuste en esta partición pequeña.

Lecturas:

1. **No diferenciabilidad.** La reemisión v1 |cos(·)| tiene un pico en cos = 0. En el punto final v1, que no convergió, 15 de 1720 activaciones de entrenamiento (0,87 %) están a menos de 10⁻² del pico, repartidas en 15 de 430 muestras (3,5 %) (`learning_v2 kink`). La terminación por estancamiento de la pérdida con gradiente grande es consistente con esa causa, pero no la demuestra. El modelo de campo con signo es suave y converge en 8/8 arranques en este control.
2. **Correspondencia con el hardware.** Un MZM push-pull alimentado por una portadora con referencia de fase transmite la amplitud con signo cos(·); la versión positiva pierde la fase π (T12, punto 7). El modelo v2 sólo es válido si el montaje tiene esa referencia y un sesgo estable, lo que debe medirse.
3. **Ganancia en las referencias de pesos reales.** En los tres arranques convergidos de `real_mzm_signed`, el mayor valor singular de la segunda capa vale 2,6, 4,8 y 5,7. En los no convergidos llega a 172 (arranque 4) y a 974 (arranque 1, con la primera capa en 0,12). La ganancia de la segunda capa actúa como inversa de la temperatura del softmax sobre los logits de intensidad, un recurso que los modelos unitarios acotados no tienen. La historia del proyecto registra el síntoma asociado (M_real agotó 300 iteraciones en 7 de 8 reinicios). Para T12 y T16: limitar la ganancia a la de la red óptica (por ejemplo σ_max ≤ 1 más una ganancia externa declarada y medida, o una temperatura del softmax fijada para todos los modelos) y comparar sólo candidatos convergidos.
4. **Selección.** `learning_v2 select` elige entre configuraciones convergidas por pérdida de validación, sin tocar el test. En este control elegiría `real_mzm_signed`, precisamente el modelo con ganancia no igualada; por eso el punto 3 debe resolverse antes de cualquier comparación.
5. **Línea base trivial y desequilibrio.** En la tarea histórica de F3 (2000 imágenes de test, clases 701/242/1050/7), la clase mayoritaria ya da 52,5 %; M1 (59,05 %) la supera por 6,55 puntos y M_full (64,25 %) por 11,75 (`experimentos/verificacion_claude/VERIFICACION-V3.md`, rama de auditoría). Toda comparación nueva debe declarar la línea base de clase mayoritaria y la exactitud equilibrada o el F1 macro, y no estimar nada por clase con 7 muestras.

**Entrenamiento con hardware en el lazo (T27).** Los errores de fabricación de una red escrita con fs se absorben mejor entrenando con el dispositivo en el lazo que precompensando sobre un modelo ideal. Opciones con antecedentes verificados: entrenamiento consciente de la física (Wright et al., 2022), retropropagación in situ con medida de gradientes (Hughes et al., 2018; demostrada experimentalmente por Pai et al., 2023) y entrenamiento sin retropropagación (Momeni et al., 2023). T27 especifica cuál es compatible con fases estáticas o programables (§43) y simula su rendimiento con el modelo de errores medido antes de construir.

## 45. Fabricación, colaboración y propiedad intelectual (T13, T28, T29)

### 45.1. Acceso a fabricación

T13 está bloqueada por falta de fabricación. Rutas posibles, sin afirmar disponibilidad ni precios:

- **Colaboración académica** con grupos que escriben guías con fs en vidrio. Los autores de los antecedentes de §46 son candidatos naturales. En España hay grupos con publicaciones en el tema; por ejemplo, el Grupo de Investigación en Aplicaciones del Láser y Fotónica de la Universidad de Salamanca (afiliación comprobada en un editorial de *Frontiers in Physics*, 2022, DOI 10.3389/fphy.2022.875736) y los trabajos de J. Solis y colaboradores en Madrid sobre guías inscritas con fs en vidrios fosfato (afiliación actual no comprobada). Verificar líneas, equipos y materiales actuales antes de cualquier contacto.
- **Servicios comerciales** de micromecanizado fs de vidrio. Buscar proveedores y confirmar que ofrecen escritura de guías con perfil de índice controlado y metrología, no sólo grabado selectivo; esta revisión no verificó proveedores concretos.
- **Instalaciones compartidas** de universidades o centros públicos con acceso para usuarios externos.

El dossier de T13 debe incluir: objetivo científico y afirmación central registrada; material y lote; geometrías con tolerancias; cupones de calibración; número de chips calculado en §42.2; medidas pedidas (perfil de índice, pérdida por cutback con modo declarado, birrefringencia, registro entre caras); formato de datos crudos; política de datos y autoría (CRediT) acordada antes de fabricar. Cualquier contacto requiere autorización del titular.

### 45.2. Propiedad intelectual antes de publicar (T29)

En el sistema europeo de patentes (EPC) no hay un periodo de gracia general: una divulgación pública antes de presentar la solicitud destruye la novedad de lo divulgado. Estados Unidos concede un año de gracia para la divulgación del propio inventor, con condiciones. El repositorio es público, de modo que todo lo ya publicado es estado de la técnica también frente a solicitudes propias. Antes de publicar resultados nuevos (preprint, push o README), el titular decide si alguno se protege; esa decisión debe tomarse con un agente de la propiedad industrial y no es asesoramiento legal de esta guía. La decisión de licencia (§30.3) se toma a la vez.

### 45.3. Publicación y comunicación

- Preprint en arXiv (physics.optics o cs.ET) cuando la afirmación central tenga su evidencia y T29 esté decidida.
- Revistas: elegir por el tipo de resultado. Un resultado de dispositivo medido y uno numérico o negativo van a revistas distintas.
- Datos y código: depósito con DOI y manifiesto de hashes; CITATION.cff actualizado.
- Uso de IA: editoriales como Nature Portfolio no admiten modelos de lenguaje como autores y piden documentar su uso en los métodos. Consultar la política vigente de la revista elegida y describir con precisión qué hicieron los agentes.

## 46. Antecedentes y métodos verificados

Metadatos comprobados el 12-10-2026 contra Crossref, arXiv o Europe PMC. Los comentarios sólo resumen lo comprobado en metadatos, resumen o texto indicado.

| Referencia | Publicación | DOI / arXiv | Nota verificada |
|---|---|---|---|
| Kondratyev et al., «Large-scale error-tolerant programmable interferometer fabricated by femtosecond laser writing» | *Photonics Research* 12(3), A28 (2024) | 10.1364/PRJ.504588; arXiv:2308.13452 | 8 puertos; tolerancia a errores en 920–980 nm. |
| Skryabin et al., «Femtosecond-laser-written low-loss multiscan waveguides in fused silica» | *Physical Review Applied* 22, 064079 (2024) | 10.1103/PhysRevApplied.22.064079; arXiv:2408.06688 | 0,07 dB/cm de propagación caracterizada a 920 nm (texto de arXiv), 0,2 dB por cara, interferómetro de 25 canales. |
| Tan, Sun, Li y Qiu, «Effectively writing low propagation and bend loss waveguides in the silica glass by using a femtosecond laser» | *Optics Letters* 47, 4766 (2022) | 10.1364/OL.470670 | Récord de 0,07 dB/cm a 1550 nm según la ref. [60] de Skryabin et al. Título, revista y volumen tomados de esa bibliografía; DOI comprobado en Crossref por el revisor independiente; artículo no leído. |
| Cao et al., «Programmable Three-dimensional Photonic Neural Network Chip» (LAMP) | *Nature Communications* 17, 5476 (2026) | 10.1038/s41467-026-72316-9; PMC13284361 | Borosilicato (Corning EAGLE XG); 4 clases de MNIST (0–3), 200 imágenes de entrenamiento; 93 % en entrenamiento y 91,7 % en 48 de test; 6554 TOPS teóricos limitados por detector. |
| Zhou et al., «Femtosecond laser writing of telecom-band depressed-cladding waveguides and mode modulation in SK1310 glass» | *Optical Materials* 159, 116651 (2025) | 10.1016/j.optmat.2025.116651 | Metadatos; texto completo pendiente. |
| Bukharin, Khudyakov y Vartapetov, «Heat accumulation regime of femtosecond laser writing in fused silica and Nd:phosphate glass» | *Applied Physics A* 119, 397–403 (2015) | 10.1007/s00339-015-8990-x | Resumen de la editorial (consultado el 12-10-2026): guía tubular de 0,3 dB/cm en sílice fundida, sin longitud de onda. Origen del umbral H1. |
| Lee, Sun, Beresna y Brambilla, «Low bend loss femtosecond laser written waveguides exploiting integrated microcrack» | *Scientific Reports* 11, 23770 (2021) | 10.1038/s41598-021-03116-y | Sílice; 1 dB/cm con radio de 10 mm a 1550 nm. |
| Pentangelo et al., «High-fidelity and polarization-insensitive universal photonic processors fabricated by femtosecond laser writing» | *Nanophotonics* 13(12), 2259–2270 (2024) | 10.1515/nanoph-2023-0636; arXiv:2310.19718 | Procesadores programables escritos con fs para 785 y 1550 nm (resumen de arXiv). |
| Moughames et al., «Three-dimensional waveguide interconnects for scalable integration of photonic neural networks» | *Optica* 7(6), 640 (2020) | 10.1364/OPTICA.388205 | Interconexiones 3D por polimerización de dos fotones, no escritura fs en vidrio. |
| Saygin et al., «Robust architecture for programmable universal unitaries» | *Physical Review Letters* 124, 010501 (2020) | 10.1103/PhysRevLett.124.010501 | Arquitectura tolerante a errores. |
| Clements et al., «Optimal design for universal multiport interferometers» | *Optica* 3(12), 1460 (2016) | 10.1364/OPTICA.3.001460; arXiv:1603.08788 | Malla rectangular de profundidad N. |
| Shen et al., «Deep learning with coherent nanophotonic circuits» | *Nature Photonics* 11, 441–446 (2017) | 10.1038/nphoton.2017.93; arXiv:1610.02365 | — |
| Hughes, Minkov, Shi y Fan, «Training of photonic neural networks through in situ backpropagation and gradient measurement» | *Optica* 5(7), 864 (2018) | 10.1364/OPTICA.5.000864 | — |
| Pai et al., «Experimentally realized in situ backpropagation for deep learning in photonic neural networks» | *Science* 380, 398–404 (2023) | 10.1126/science.ade8450 | — |
| Lin et al., «All-optical machine learning using diffractive deep neural networks» | *Science* 361, 1004–1008 (2018) | 10.1126/science.aat8084 | — |
| Hamerly, Bernstein, Sludds, Soljačić y Englund, «Large-scale optical neural networks based on photoelectric multiplication» | *Physical Review X* 9, 021032 (2019) | 10.1103/PhysRevX.9.021032 | Base del argumento de amortización de §40. |
| Wang et al., «An optical neural network using less than 1 photon per multiplication» | *Nature Communications* 13, 123 (2022) | 10.1038/s41467-021-27774-8 | — |
| Wright et al., «Deep physical neural networks trained with backpropagation» | *Nature* 601, 549–555 (2022) | 10.1038/s41586-021-04223-6 | — |
| Momeni et al., «Backpropagation-free training of deep physical neural networks» | *Science* 382, 1297–1303 (2023) | 10.1126/science.adi8474 | — |
| McMahon, «The physics of optical computing» | *Nature Reviews Physics* 5, 717–734 (2023) | 10.1038/s42254-023-00645-5 | Revisión de referencia para T24. |
| Horowitz, «1.1 Computing's energy problem (and what we can do about it)» | ISSCC 2014, 10–14 | 10.1109/ISSCC.2014.6757323 | Energías digitales por operación a 45 nm; citar con nodo y año. |
| Bao, Ma y Wang, «Optimal error bounds on time-splitting methods for the nonlinear Schrödinger equation with low regularity potential and nonlinearity» | *M3AS* 34(5), 803–844 (2024) | 10.1142/S0218202524500155; arXiv:2308.15089 | Ecuación no lineal. |
| Steffens, Parés y Díez, «Goal-oriented h-adaptivity for the Helmholtz equation…» | *Computational Mechanics* 47(6), 681–699 (2011) | 10.1007/s00466-010-0557-2 | — |
| Roache, «Quantification of uncertainty in computational fluid dynamics» | *Annual Review of Fluid Mechanics* 29, 123–160 (1997) | 10.1146/annurev.fluid.29.1.123 | GCI; propuesto en Roache, *J. Fluids Eng.* 116, 405–413 (1994), DOI 10.1115/1.2910291. |
| Klein y Roodman, «Blind analysis in nuclear and particle physics» | *Annual Review of Nuclear and Particle Science* 55, 141–163 (2005) | 10.1146/annurev.nucl.55.090704.151521 | Base de §41.2. |
| Nosek, Ebersole, DeHaven y Mellor, «The preregistration revolution» | *PNAS* 115(11), 2600–2606 (2018) | 10.1073/pnas.1708274114 | Base de §41.1. |
| Schuirmann, «A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability» | *J. Pharmacokinetics and Biopharmaceutics* 15(6), 657–680 (1987) | 10.1007/BF01068419 | TOST. |
| Clopper y Pearson, «The use of confidence or fiducial limits illustrated in the case of the binomial» | *Biometrika* 26(4), 404–413 (1934) | 10.1093/biomet/26.4.404 | Intervalo exacto. |

## 47. Erratas y verificaciones

| Id | Sección | Hallazgo | Evidencia | Corrección |
|---|---|---|---|---|
| E1 | §5.1 | `audit_point03_d16_fine_partial.py` citado sin carpeta. | `git ls-tree` de `main`. | `scripts/audit_point03_d16_fine_partial.py`. |
| E2 | §5.4 | `RESULTADOS-T96-Q4-AUDITORIA.md` citado sin carpeta. | `git ls-tree`. | `experimentos/glass009d_claude/RESULTADOS-T96-Q4-AUDITORIA.md`. |
| E3 | §11, §24 | `Docs/CONTRIBUCION-CENTRAL-T20.md` y `experimentos/acoplador_claude/g3_bpm_p2.py` sólo existen en la rama de auditoría, sin indicarlo. | `git ls-tree` de ambas ramas. | Leer con `git show origin/auditoria-20261009:<ruta>`. |
| E4 | §2, §3.3 | La extracción escribe `tests/test_agentkit.py` en `tests/`, propiedad de Codex, y `scripts/check.py` lo ejecutaría en la CI. | `AGENTS.md`, `scripts/check.py`, `.github/workflows/cpu-tests.yml`. | Worktree propio o revisión de Codex; pruebas v2 en `agentkit/test_v2.py`. |
| E5 | §4, §35 | `evaluate_receipt` usa la copia del protocolo del recibo sin compararla con el archivo: un umbral relajado en el recibo aprueba. | Prueba adversarial ejecutada en la revisión. | `agentkit.prereg.audit_v2`. El código v1 no se modifica. |
| E6 | §16 | El ejemplo `unitary_mzm` no converge en ningún arranque. | Ejecución literal (§44). | Modelo con signo `unitary_mzm_signed`; nunca rebajar el criterio de gradiente. |
| E7 | §16, §20 | Las referencias de pesos reales sin restricción usan ganancia que una red pasiva no tiene. | σ_max de 2,6 a 5,7 en arranques convergidos y hasta 974 en no convergidos (§44). | Comparaciones con ganancia igualada o ganancia contada como recurso. |
| E8 | §34 | Referencia de Helmholtz sin autores ni año. | Crossref. | Steffens, Parés y Díez, *Comput. Mech.* 47, 681–699 (2011). |
| E9 | §28.1, §34 | Bao, Ma y Wang tratan la ecuación de Schrödinger no lineal. | Crossref y arXiv. | *M3AS* 34(5), 803–844 (2024), DOI 10.1142/S0218202524500155. |
| E10 | §23, §34 | Faltan las versiones publicadas de Kondratyev y Skryabin. Skryabin informa 0,07 dB/cm a 920 nm; el récord a 1550 nm es de Tan et al. (2022). | Crossref y texto de arXiv. | §46. |
| E11 | §24 | El origen del umbral de 0,3 dB/cm no estaba identificado en la guía. | Crossref y resumen en la página de la editorial. | Bukharin et al., *Appl. Phys. A* 119, 397–403 (2015). |
| E12 | §27.3 | La cota 9/4 se refiere sólo a ℂ, y el alcance Lean de 107 enlaza dos manuscritos del 24-09-2026, no el del 2-10-2026 citado en §34. | `lean/docs/107.md` en `fd4aeeb`. | Para todo cuerpo, ω(F) < 2,371054886006746. |
| E13 | §1 | Rama `codex/scientific-closure-20261006` y PR #1 no mencionadas. | `git ls-remote`, `merge-base`. | Ambas ya contenidas en `main`. |
| E14 | §35 | Imports sin usar en `checkpoint.py` (`hashlib`) y `supervisor.py` (`timezone`). | `pyflakes`. | Cosmético; se conserva el código v1 byte a byte. |
| E15 | §3.2 | El conjunto fijado no estaba verificado en Python 3.13. | Instalación y pruebas en 3.13.16 (Linux). | Verificado en Linux; falta Windows. |
| E16 | §23 | Detalles de LAMP. | Texto completo vía Europe PMC. | El 93 % es exactitud de entrenamiento; la tarea es de 4 clases de MNIST. |

**Hallazgos de la revisión adversarial sobre el borrador v2 (E17–E30).** Son errores del material nuevo de esta revisión, no del texto v1. Se conservan aquí por trazabilidad.

| Id | Dónde | Fallo del borrador v2 | Corrección y comprobación |
|---|---|---|---|
| E17 | §41.1, `prereg` | Integridad sobreafirmada: el registro se podía reapuntar a un commit posterior con un protocolo relajado; `planned_artifacts` era opcional; la marca de publicación se copiaba sin volver a comprobarla. | `planned_artifacts` obligatorio; recorrido del historial; comprobación en servidor con `ls-remote` al auditar; límite residual declarado. Los ataques A1, A1b y A2 del revisor fallan ahora. |
| E18 | `prereg` | Decodificaba la salida de git con la codificación regional (cp1252 en Windows): protocolos con «Á», «µ» fallaban o cambiaban de hash; las rutas con `\` no se resolvían. | UTF-8 explícito y normalización POSIX; comprobado con configuración regional ASCII. |
| E19 | `prereg` | La auditoría comparaba bytes crudos: un commit hecho con CRLF no se podía auditar desde una copia LF. | Comparación por blob de git; comprobado CRLF→LF. |
| E20 | §42.2 | Tabla con α = 0,05 cuando la regla decide con IC bilateral del 95 % (α = 0,025). | Recalculada: 5, 10 y 52 chips. |
| E21 | §23, §24, §38, §39, §46 | Se presentó 0,07 dB/cm de Skryabin como referencia a 1550 nm; se midió a 920 nm. | Tan et al. (2022) como referencia a 1550 nm. |
| E22 | §41.2, `blind` | El cegado se podía romper por cuantización; la escala de ejemplo (0,2) contradecía la regla del propio texto; el registro de congelación no se comprobaba. | Redondeo obligatorio a las cifras del instrumento, escala 2 dB/cm con cota de fuga, registro de congelación con hash del informe y committeado. El ataque de rejilla ya no recupera δ. |
| E23 | §41.3, §48, §51, `claims` | Los alcances del registro no coincidían con los de `tasks.json` (16 errores al volcar T01–T30); la tabla carecía de columnas pedidas; tipos de evidencia sin procedencia; aceptaba ciclos y agentes como reproducción externa; un PASS de ejemplo usaba el código fuente como evidencia y H1 añadía «HE11» sin enmienda. | Alcances alineados y comprobados por prueba; procedencia obligatoria; ciclos y agentes rechazados; tabla sólo si es consistente y con todas las columnas; ejemplo corregido. |
| E24 | §2, §3.3, §51 | «Extraer en un worktree propio» seguía escribiendo `tests/` del repositorio; el comando de §3.3 nombra el archivo v1. | Extraer fuera del repositorio; usar el nombre del archivo v2. |
| E25 | §27.3 | Atribución incorrecta de manuscritos en 107.md. | Corregida (ver E12). |
| E26 | §16, §33, §37 | Se comparaba la cifra de §33 con el arranque 1, no con el seleccionado. | Ambos indicados; selección frágil por empate. |
| E27 | §44 | «0,87 % de las muestras» era por activación, y el punto v1 no estaba convergido. | 15/1720 activaciones; 15/430 muestras; la herramienta informa de ambas. |
| E28 | §20, §44 | σ_max extremos procedían de arranques no convergidos; «degeneración de escala» no estaba demostrada. | Valores de los convergidos (2,6–5,7) y explicación por temperatura del softmax. |
| E29 | §42.1 | Suelo fijo de 0,044 dB/cm, contra la advertencia de §18.2. | F recalculado para el perfil medido; veredictos separados. |
| E30 | Varios | Menores: propiedad de los locks inferida; omisión de `Docs/LICENCIA-PROPUESTA.md`; independencia mal explicada en §14; prueba sintética débil; comprobaciones de dimensión y selección en `learning_v2`; profundidad pasiva sin atenuadores; procedencia global en `limits`; «domina» con un 4 % de margen; longitudes de onda de Pentangelo; secciones de E3; «citados en esta guía». | Todos corregidos en el texto o el código. |

**Nota de proceso de esta revisión.** En el primer borrador de `agentkit/test_v2.py`, la prueba de convergencia sintética exigía exactitud de validación > 0,6 y observó exactamente 0,6. Se sustituyó ese umbral arbitrario por el nivel de azar (1/3), que es el criterio con fundamento para una comprobación de sanidad de software. El cambio se hizo después de ver el resultado y se declara aquí; la prueba no es evidencia científica. El revisor independiente señaló que ese criterio ya no detectaría una regresión; se añadió una comprobación de que la pérdida final del arranque seleccionado es menor que el 80 % de la inicial.

## 48. Nuevas tareas T23–T30 y orden de ejecución v2

| ID | Tarea | Alcance | Depende de | Estado inicial |
|---|---|---|---|---|
| T23 | Infraestructura de integridad: prerregistro anclado, análisis ciego, registro de afirmaciones | software | — | OPEN |
| T24 | Prueba de descarte por límites fundamentales: presupuesto con fuentes por MAC | modelo numérico | — | OPEN |
| T25 | Escalado 3D frente a plano: profundidad, cruces, pérdida y acumulación de error | modelo numérico | — | OPEN |
| T26 | Revisión del estado del arte y del umbral de H1 | novedad | T19 | OPEN |
| T27 | Plan de entrenamiento con hardware en el lazo con modelos de error medidos | modelo numérico | T12 | OPEN |
| T28 | Dossier de acceso a fabricación y colaboración | diseño fabricable | T11 | OPEN |
| T29 | Decisión de propiedad intelectual y divulgación antes de nuevos resultados públicos | decisión del titular | — | OPEN |
| T30 | Revisión adversarial y pre-mortem de la afirmación central | revisión | T20 | OPEN |

El registro está en `agentkit/tasks_v2.json`, que extiende `agentkit/tasks.json` sin modificarlo.

**Orden v2.** El orden de §4 sigue siendo válido; v2 adelanta lo que es barato y decide el rumbo.

1. **Fase 0 (CPU, sin datos nuevos):** T23; volcar T01–T30 en el registro de afirmaciones con su estado real (los alcances de `tasks.json` y `tasks_v2.json` ya son válidos en el registro); prerregistrar T24, T25 y T26.
2. **Fase 1 (pruebas de descarte):** T24, T25 y T26; decisión registrada de la afirmación central (T20) y retirada explícita de las candidatas descartadas.
3. **Fase 2 (numérica):** T01–T08 como en v1, priorizando lo que la afirmación central necesita.
4. **Fase 3 (física):** T29 y T28, luego T13 y T14 con análisis ciego y el número de chips de §42.2.
5. **Fase 4 (sistema):** T12, T16 y T27; después T15, T17 y T18.
6. **Fase 5 (presentación):** T30, manuscrito, T21 y seguimiento T22.

## 49. Kit v2: módulos, comandos y validación

| Módulo | Función | Tareas |
|---|---|---|
| `agentkit.prereg` | Compromiso de protocolo anclado en git, comprobación de publicación en servidor, recorrido del historial y auditoría contra el objeto committeado. | T23, todas las confirmatorias |
| `agentkit.blind` | Análisis ciego de cutback: compromiso SHA-256, redondeo a la resolución del instrumento y congelación committeada antes de desenmascarar. | T14, T20 |
| `agentkit.claims` | Registro de afirmaciones con procedencia de la evidencia y tabla de estado. | T19–T22, presentación |
| `agentkit.stats` | Regla de tres zonas, TOST, potencia y tamaño muestral, Clopper–Pearson, Wilks, Holm. | T10, T14, T16, T20 |
| `agentkit.limits` | Presupuesto energético y de precisión con procedencia por parámetro; profundidad máxima por pérdidas. | T17, T24 |
| `agentkit.mzi` | Malla rectangular de MZI, compilación pasiva y estudio de errores de divisor. | T10, T11, T25 |
| `agentkit.learning_v2` | Modelos MZM de campo con signo, selección entre arranques convergidos y por validación, y diagnóstico de no diferenciabilidad. | T12, T16, T27 |
| `agentkit/test_v2.py` | 29 pruebas de control y rechazo. | — |

Validación ejecutada en esta revisión (Python 3.13.16, Linux, CPU, un hilo BLAS):

- 29/29 pruebas v2 y 32/32 v1, con NumPy 2.5.3/SciPy 1.18.1 y con el conjunto fijado.
- Extracción limpia de esta guía con su propio extractor (28 archivos), y extracción sobre un directorio v1 existente (crea sólo los 11 archivos nuevos).
- Flujo CLI completo contra un remoto git local:
  - `prereg commit --query-server`;
  - `blind init` con s = 2 dB/cm y `blind blind` con 6 cifras: la pendiente ciega salió negativa (−1,29 dB/cm), como se espera;
  - ajuste ciego, `blind freeze`;
  - `unblind`, que se rechazó antes del commit de la congelación;
  - commit y `unblind`: media 0,0999992 dB/cm frente a la verdad fabricada de 0,1 (diferencia debida al redondeo a 6 cifras);
  - `prereg audit --query-server --require-published`: PASS.
- `claims` (consistente, tabla escrita), `stats`, `limits`, `mzi --passive` (error 1,0·10⁻¹⁶; profundidad 3 con atenuadores) y `learning_v2 fit`, `select` y `kink`.
- Ataques del revisor independiente repetidos contra el código corregido: registro reapuntado (A1, A1b), protocolo sin plan (A2), configuración regional ASCII con caracteres no ASCII, auditoría CRLF→LF y recuperación de δ por la rejilla de cuantización. Ninguno tiene éxito ya.
- `pyflakes` sin avisos en los módulos v2.

Comandos, después de extraer fuera del repositorio:

```powershell
& '.\.venv-closure\Scripts\python.exe' -B -m unittest agentkit.test_v2 -v
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.claims --ledger agentkit/claims_example.json --root .
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.stats yield --k 28 --n 36 --out resultados/agent/yield_c3.json
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.stats decide --ci-low 0.25 --ci-high 0.35 --threshold 0.3 --model-floor 0.044 --out resultados/agent/decide_example.json
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.stats sample-size --effect 0.05 --sigma 0.05 --out resultados/agent/n_chips_plan.json
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.limits --params agentkit/limits_example_params.json --out resultados/agent/limits_manufactured.json
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.mzi --passive --input resultados/agent/manufactured/target.npz --out resultados/agent/clements_passive.json
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.learning_v2 fit --train resultados/agent/development_digits/train.npz --validation resultados/agent/development_digits/validation.npz --model unitary_mzm_signed --seeds 1 2 3 4 5 6 7 8 --maxiter 1000 --out resultados/agent/candidate_unitary_mzm_signed.json
& '.\.venv-closure\Scripts\python.exe' -B -m agentkit.learning_v2 kink --candidate resultados/agent/candidate_unitary_mzm.json --data resultados/agent/development_digits/train.npz --out resultados/agent/kink_unitary_mzm.json
```

Las rutas de `resultados/agent` de los últimos comandos son las del ejemplo de §16 y §31; deben existir y las de salida deben ser nuevas. Los resultados de `limits_example_params.json` y de los datos fabricados no son evidencia del proyecto.

## 50. Código v2 del kit

Archivos completos, extraíbles con el mismo `extract_agentkit.py` de §35. No modifican ningún archivo v1.

### Archivo: agentkit/prereg.py

```python file=agentkit/prereg.py
"""Git-anchored prospective commitments and a stricter receipt audit (kit v2).

Closes gaps of agentkit.evidence (v1):
1. evaluate_receipt trusts the protocol dictionary stored in the receipt, so
   editing that dictionary relaxes criteria without touching the protocol file.
   Here the protocol is always re-read from the committed git object.
2. freeze does not require the protocol or sources to be committed, clean or
   published. Here they must be tracked and unmodified, planned artifacts are
   mandatory, and publication can be re-verified at audit time, optionally
   against the server with `git ls-remote`.
3. The audit scans git history for other protocols with the same
   experiment_id at the same path, and for planned artifacts committed outside
   the descendants of the commitment commit.

Residual limits, stated rather than hidden: a commitment record is a local
file; a protocol committed after data were produced (and never committed
before in another form) cannot be detected from the repository alone. Only
an external timestamp (archive DOI, preregistration service) plus data
custody closes that gap. This module never pushes, publishes or contacts
anyone; `--query-server` only reads the remote's refs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

from agentkit.evidence import (canonical, evaluate_receipt, inside, snapshot,
                               utc_now, write_new_json)


REQUIRED = {"experiment_id", "task_id", "model", "units", "criteria",
            "resource_limits", "heldout_policy", "scope", "planned_artifacts"}


def _git(root: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run git without a shell; decode output as UTF-8 on every platform."""
    return subprocess.run(["git", "-C", str(root), *arguments], capture_output=True,
                          text=True, encoding="utf-8", errors="strict", check=check)


def _git_bytes(root: Path, *arguments: str) -> bytes:
    """Run git and return raw bytes (used for committed file content)."""
    return subprocess.run(["git", "-C", str(root), *arguments], capture_output=True,
                          check=True).stdout


def _norm(name: str) -> str:
    """Repository-relative POSIX path, so Windows separators resolve in git."""
    posix = str(name).replace("\\", "/")
    if not posix or posix.startswith("/") or ":" in posix.split("/")[0]:
        raise ValueError("Paths must be relative to the repository root: " + str(name))
    return posix


def _committed_blob(root: Path, commit: str, relative: str) -> str | None:
    """Return the blob id of a path in a commit, or None if absent."""
    result = _git(root, "rev-parse", "--verify", "--quiet", f"{commit}:{relative}", check=False)
    return result.stdout.strip() or None


def _working_blob(root: Path, relative: str) -> str:
    """Hash the working file with git's own filters (CRLF-normalization aware)."""
    return _git(root, "hash-object", "--", relative).stdout.strip()


def _load_committed_json(root: Path, commit: str, relative: str) -> dict:
    return json.loads(_git_bytes(root, "show", f"{commit}:{relative}").decode("utf-8"))


def _validate_protocol(protocol: dict) -> None:
    """Structural rules: the v1 rules plus mandatory planned artifacts."""
    if not REQUIRED.issubset(protocol):
        raise ValueError("Protocol is missing required fields: " +
                         ", ".join(sorted(REQUIRED - set(protocol))))
    criteria = protocol["criteria"]
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("Protocol must declare explicit acceptance criteria")
    ids = [entry["id"] for entry in criteria]
    if len(set(ids)) != len(ids):
        raise ValueError("Criterion identifiers must be unique")
    for entry in criteria:
        if entry.get("operator") not in ("le", "ge", "eq"):
            raise ValueError("Unsupported criterion operator")
        threshold = entry.get("threshold")
        if isinstance(threshold, bool):
            if entry["operator"] != "eq":
                raise ValueError("Boolean criteria must use equality")
        elif not isinstance(threshold, (int, float)) or not math.isfinite(threshold):
            raise ValueError("Criterion threshold must be finite or boolean")
    planned = protocol["planned_artifacts"]
    if (not isinstance(planned, list) or not planned
            or not all(isinstance(p, str) and p for p in planned)
            or len({_norm(p) for p in planned}) != len(planned)):
        raise ValueError("planned_artifacts must be a nonempty list of unique relative paths")


def remote_contains(root: Path, commit: str, remote_ref: str, query_server: bool) -> bool | None:
    """Whether `commit` is contained in `remote_ref` ("remote/branch").

    Without query_server the local remote-tracking ref is used, which a user
    can create without pushing. With query_server the branch head is read
    from the server; None means the head is not available locally (fetch).
    """
    if not query_server:
        return _git(root, "merge-base", "--is-ancestor", commit, remote_ref,
                    check=False).returncode == 0
    remote, _, branch = remote_ref.partition("/")
    if not branch:
        raise ValueError("remote_ref must look like remote/branch")
    listed = _git(root, "ls-remote", "--heads", remote, "refs/heads/" + branch, check=False)
    if listed.returncode or not listed.stdout.strip():
        return False
    head = listed.stdout.split()[0]
    if _git(root, "cat-file", "-e", head + "^{commit}", check=False).returncode:
        return None
    return _git(root, "merge-base", "--is-ancestor", commit, head, check=False).returncode == 0


def commit_protocol(root: Path, protocol_path: str, sources: list[str], out: Path,
                    remote_ref: str | None = None, allow_unpublished: bool = False,
                    query_server: bool = False) -> dict:
    """Record a protocol committed (and optionally published) before any new data."""
    root = root.resolve()
    protocol_path = _norm(protocol_path)
    names = list(dict.fromkeys([protocol_path, *[_norm(s) for s in sources]]))
    for name in names:
        inside(root, name)
        if _git(root, "ls-files", "--error-unmatch", "--", name, check=False).returncode:
            raise ValueError("Path is not tracked by git: " + name)
    head = _git(root, "rev-parse", "HEAD").stdout.strip()
    blobs = {}
    for name in names:
        committed = _committed_blob(root, head, name)
        if committed is None or committed != _working_blob(root, name):
            raise ValueError("Path has uncommitted changes: " + name)
        blobs[name] = committed
    protocol = _load_committed_json(root, head, protocol_path)
    _validate_protocol(protocol)
    for planned in protocol["planned_artifacts"]:
        planned = _norm(planned)
        if (root / planned).exists() or _committed_blob(root, head, planned) is not None:
            raise ValueError("A planned artifact already exists before the commitment: " + planned)
    published = None
    if remote_ref is not None:
        published = remote_contains(root, head, remote_ref, query_server)
        if not published and not allow_unpublished:
            raise ValueError("Commitment commit is not verifiably contained in " + remote_ref)
    record = {"schema": 2, "kind": "git_anchored_protocol",
              "created_utc": utc_now(), "protocol_path": protocol_path,
              "protocol_sha256": hashlib.sha256(canonical(protocol)).hexdigest(),
              "commit": head,
              "commit_time_iso": _git(root, "show", "-s", "--format=%cI", head).stdout.strip(),
              "git_blobs": blobs, "remote_ref": remote_ref,
              "published_at_commitment": published,
              "published_check": "server" if query_server else "local_tracking_ref",
              "inputs": snapshot(root, names),
              "note": ("Commit the record itself and publish it before producing data; "
                       "a commit date can be forged and only an external timestamp is strong.")}
    write_new_json(out, record)
    return record


def committed_protocol(root: Path, record: dict) -> dict:
    """Return the protocol exactly as committed, after verifying the anchor."""
    root = root.resolve()
    if record.get("kind") != "git_anchored_protocol":
        raise ValueError("A git-anchored commitment is required")
    commit = record["commit"]
    if _git(root, "cat-file", "-e", commit + "^{commit}", check=False).returncode:
        raise ValueError("Committed protocol commit is not present in this repository")
    for name, blob in record["git_blobs"].items():
        if _committed_blob(root, commit, name) != blob:
            raise ValueError("Committed object differs from the commitment: " + name)
    protocol = _load_committed_json(root, commit, record["protocol_path"])
    if hashlib.sha256(canonical(protocol)).hexdigest() != record["protocol_sha256"]:
        raise ValueError("Commitment protocol hash does not match the committed protocol")
    _validate_protocol(protocol)
    return protocol


def history_conflicts(root: Path, record: dict, protocol: dict) -> list[dict]:
    """Other committed versions of the protocol path with the same experiment_id."""
    path = record["protocol_path"]
    conflicts = []
    for commit in _git(root, "rev-list", "--all", "--", path).stdout.split():
        blob = _committed_blob(root, commit, path)
        if blob is None or blob == record["git_blobs"][path]:
            continue
        try:
            other = _load_committed_json(root, commit, path)
        except (ValueError, UnicodeDecodeError):
            continue
        if other.get("experiment_id") == protocol["experiment_id"]:
            conflicts.append({"commit": commit,
                              "protocol_sha256": hashlib.sha256(canonical(other)).hexdigest()})
    return conflicts


def _first_added(root: Path, path: str) -> str | None:
    commits = _git(root, "log", "--all", "--diff-filter=A", "--format=%H", "--", path).stdout.split()
    return commits[-1] if commits else None


def audit_v2(root: Path, record: dict, result: dict, query_server: bool = False,
             require_published: bool = False) -> dict:
    """Evaluate a result against the committed protocol, never the record's copy."""
    root = root.resolve()
    protocol = committed_protocol(root, record)
    names = list(record["git_blobs"])
    for name in names:
        if _working_blob(root, name) != record["git_blobs"][name]:
            raise ValueError("Committed input changed after the commitment: " + name)
    # Inputs were verified through git blob ids (portable across CRLF/LF
    # checkouts); evaluate against a fresh byte snapshot of the same files.
    receipt = evaluate_receipt(root, {"kind": "prospective_protocol", "protocol": protocol,
                                      "inputs": snapshot(root, names)}, result)
    commit = record["commit"]
    artifacts = [_norm(a) for a in result["artifacts"]]
    planned = [_norm(p) for p in protocol["planned_artifacts"]]
    preexisting = [a for a in artifacts if _committed_blob(root, commit, a) is not None]
    unplanned = [a for a in artifacts if a not in planned]
    outside = []
    for artifact in artifacts:
        first = _first_added(root, artifact)
        if first is not None and _git(root, "merge-base", "--is-ancestor", commit, first,
                                      check=False).returncode:
            outside.append({"artifact": artifact, "first_added_in": first})
    conflicts = history_conflicts(root, record, protocol)
    published = None
    if record.get("remote_ref"):
        published = remote_contains(root, commit, record["remote_ref"], query_server)
    failures = {"artifacts_present_at_commitment": preexisting,
                "unplanned_artifacts": unplanned,
                "artifacts_added_outside_commitment_descendants": outside,
                "other_protocol_versions_same_experiment": conflicts}
    published_ok = bool(published) if require_published else True
    receipt.update({"schema": 2, "commitment_commit": commit,
                    "published_verified_at_audit": published,
                    "published_check": "server" if query_server else "local_tracking_ref",
                    **failures,
                    "criteria_passed": receipt["passed"],
                    "passed": bool(receipt["passed"] and published_ok
                                   and not any(failures.values())),
                    "residual_limits": ("A protocol first committed after the data were "
                                        "produced is not detectable here; use an external "
                                        "timestamp and data custody for confirmatory claims."),
                    "note": "Mechanical audit; independent recomputation and review remain required."})
    return receipt


def main() -> None:
    """Commit-check, verify or audit with explicit paths; outputs are never overwritten."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    commit = commands.add_parser("commit")
    commit.add_argument("--protocol", required=True)
    commit.add_argument("--sources", nargs="+", required=True)
    commit.add_argument("--out", type=Path, required=True)
    commit.add_argument("--remote-ref")
    commit.add_argument("--allow-unpublished", action="store_true")
    commit.add_argument("--query-server", action="store_true")
    verify = commands.add_parser("verify")
    verify.add_argument("--commitment", type=Path, required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("--commitment", type=Path, required=True)
    audit.add_argument("--result", type=Path, required=True)
    audit.add_argument("--out", type=Path, required=True)
    audit.add_argument("--query-server", action="store_true")
    audit.add_argument("--require-published", action="store_true")
    args = parser.parse_args()
    read = lambda path: json.loads(path.read_text(encoding="utf-8"))
    if args.command == "commit":
        record = commit_protocol(args.root, args.protocol, args.sources, args.out,
                                 args.remote_ref, args.allow_unpublished, args.query_server)
        print(json.dumps({"commit": record["commit"],
                          "published_at_commitment": record["published_at_commitment"]}))
    elif args.command == "verify":
        record = read(args.commitment)
        protocol = committed_protocol(args.root, record)
        print(json.dumps({"verified": True,
                          "other_protocol_versions_same_experiment":
                              history_conflicts(args.root.resolve(), record, protocol)}))
    else:
        receipt = audit_v2(args.root, read(args.commitment), read(args.result),
                           args.query_server, args.require_published)
        write_new_json(args.out, receipt)
        print(json.dumps({"passed": receipt["passed"]}))
        if not receipt["passed"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/blind.py

```python file=agentkit/blind.py
"""Blind analysis of cutback measurements with a hidden slope offset (kit v2).

Roles: a custodian (a person, or an agent that does not analyse) creates a
secret offset and publishes only its SHA-256 commitment in the protocol.
The custodian blinds the raw CSV; analysts develop the whole analysis on
blinded data and record a freeze that names the blinded report hash; only
then is the secret revealed. Multiplying each output power by
10**(-offset*L_cm/10) adds exactly `offset` dB/cm to every fitted slope and
leaves residuals, intercepts and interval widths unchanged.

Two leaks are handled explicitly:
- Quantization: blinded powers are rounded to the declared number of
  significant digits of the instrument record, so the hidden factor cannot
  be recovered by snapping values back onto the original grid. The rounding
  perturbs unblinded results at that resolution only.
- Tails: any bounded offset uniform in [-s, s] reveals the verdict with
  probability at most |mu - U| / (2 s) (mu true slope, U threshold). Choose
  s much larger than the decision range; negative blinded slopes (apparent
  gain) are expected and are not anomalies.
See Klein and Roodman, Annu. Rev. Nucl. Part. Sci. 55, 141 (2005).
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import secrets
import subprocess

from agentkit.evidence import canonical, sha256_file, utc_now, write_new_json


def create_secret(path: Path, scale_db_per_cm: float) -> dict:
    """Draw an unpredictable offset in [-scale, scale] and return its commitment."""
    if not math.isfinite(scale_db_per_cm) or scale_db_per_cm <= 0:
        raise ValueError("Blinding scale must be positive")
    generator = secrets.SystemRandom()
    record = {"kind": "additive_slope_offset", "units": "dB/cm",
              "offset_db_per_cm": generator.uniform(-scale_db_per_cm, scale_db_per_cm),
              "salt": secrets.token_hex(16), "created_utc": utc_now()}
    data = canonical(record) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return {"commitment_sha256": hashlib.sha256(data).hexdigest(),
            "scale_db_per_cm": scale_db_per_cm, "kind": record["kind"],
            "tail_leak_bound": "P(verdict revealed) <= |mu - U| / (2 * scale)"}


def _load_secret(path: Path, commitment: str) -> float:
    if sha256_file(path) != commitment:
        raise ValueError("Secret does not match the published commitment")
    return float(json.loads(path.read_text(encoding="utf-8"))["offset_db_per_cm"])


def _round_significant(value: float, digits: int) -> float:
    return float(f"{value:.{digits - 1}e}")


def blind_rows(rows: list[dict], offset_db_per_cm: float, significant_digits: int) -> list[dict]:
    """Return blinded copies of cutback rows (custodian only)."""
    if type(significant_digits) is not int or not 2 <= significant_digits <= 17:
        raise ValueError("Declare the instrument resolution as 2 to 17 significant digits")
    out = []
    for row in rows:
        length_cm = 100 * float(row["length_m"])
        value = float(row["output_power_w"]) * 10 ** (-offset_db_per_cm * length_cm / 10)
        blinded = dict(row)
        blinded["output_power_w"] = repr(_round_significant(value, significant_digits))
        out.append(blinded)
    return out


def freeze_analysis(report_path: Path, sources: list[Path], out: Path) -> dict:
    """Record the blinded report and analysis sources before unblinding."""
    record = {"kind": "blind_analysis_freeze", "created_utc": utc_now(),
              "blinded_report_sha256": sha256_file(report_path),
              "analysis_sources": {str(p): sha256_file(p) for p in sources}}
    write_new_json(out, record)
    return record


def _is_committed(path: Path) -> bool:
    folder = path.resolve().parent
    run = lambda *a: subprocess.run(["git", "-C", str(folder), *a], capture_output=True,
                                    text=True, encoding="utf-8")
    tracked = run("ls-files", "--error-unmatch", "--", path.name).returncode == 0
    clean = run("diff", "--quiet", "HEAD", "--", path.name).returncode == 0
    return tracked and clean


def unblind_report(report: dict, offset_db_per_cm: float) -> dict:
    """Subtract the offset from every slope-valued field of a fit_cutback report."""
    result = copy.deepcopy(report)
    result["mean_loss_db_per_cm"] -= offset_db_per_cm
    result["ci95"] = [value - offset_db_per_cm for value in result["ci95"]]
    for guide in result["guides"]:
        guide["loss_db_per_cm"] -= offset_db_per_cm
    result["unblinded"] = True
    return result


def main() -> None:
    """init and blind (custodian), freeze (analyst), unblind (after a committed freeze)."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--secret", type=Path, required=True)
    init.add_argument("--scale-db-per-cm", type=float, required=True)
    init.add_argument("--commitment-out", type=Path, required=True)
    blind = commands.add_parser("blind")
    blind.add_argument("--input", type=Path, required=True)
    blind.add_argument("--secret", type=Path, required=True)
    blind.add_argument("--commitment", required=True)
    blind.add_argument("--significant-digits", type=int, required=True)
    blind.add_argument("--out", type=Path, required=True)
    freeze = commands.add_parser("freeze")
    freeze.add_argument("--report", type=Path, required=True)
    freeze.add_argument("--sources", type=Path, nargs="+", required=True)
    freeze.add_argument("--out", type=Path, required=True)
    reveal = commands.add_parser("unblind")
    reveal.add_argument("--report", type=Path, required=True)
    reveal.add_argument("--secret", type=Path, required=True)
    reveal.add_argument("--commitment", required=True)
    reveal.add_argument("--analysis-freeze", type=Path, required=True)
    reveal.add_argument("--allow-uncommitted-freeze", action="store_true")
    reveal.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "init":
        record = create_secret(args.secret, args.scale_db_per_cm)
        write_new_json(args.commitment_out, record)
        print(json.dumps({"commitment_sha256": record["commitment_sha256"]}))
    elif args.command == "blind":
        offset = _load_secret(args.secret, args.commitment)
        with args.input.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        blinded = blind_rows(rows, offset, args.significant_digits)
        with args.out.open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(blinded)
        print(json.dumps({"blinded_rows": len(blinded), "input_sha256": sha256_file(args.input),
                          "significant_digits": args.significant_digits}))
    elif args.command == "freeze":
        record = freeze_analysis(args.report, args.sources, args.out)
        print(json.dumps({"blinded_report_sha256": record["blinded_report_sha256"]}))
    else:
        freeze_record = json.loads(args.analysis_freeze.read_text(encoding="utf-8"))
        if (freeze_record.get("kind") != "blind_analysis_freeze"
                or freeze_record.get("blinded_report_sha256") != sha256_file(args.report)):
            raise ValueError("The freeze record does not name this blinded report")
        committed = _is_committed(args.analysis_freeze)
        if not committed and not args.allow_uncommitted_freeze:
            raise ValueError("Commit the freeze record before unblinding")
        offset = _load_secret(args.secret, args.commitment)
        report = json.loads(args.report.read_text(encoding="utf-8"))
        result = unblind_report(report, offset)
        result.update({"analysis_freeze_sha256": sha256_file(args.analysis_freeze),
                       "analysis_freeze_committed": committed,
                       "blinded_report_sha256": sha256_file(args.report)})
        write_new_json(args.out, result)
        print(json.dumps({"mean_loss_db_per_cm": result["mean_loss_db_per_cm"], "ci95": result["ci95"]}))


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/claims.py

```python file=agentkit/claims.py
"""Claims ledger: one place where every public statement meets its evidence (kit v2).

A claim cannot be PASS unless evidence of its own scope exists, its bytes
match the recorded hashes, its dependencies pass (without cycles), and the
evidence kind is the one that scope demands: a simulation never closes a
physical claim, and agreement between project AI agents never counts as
external replication. Evidence kinds are declarations; each item must state
who produced it and how, and a human auditor checks those declarations.
The scopes include every scope used in agentkit/tasks.json and tasks_v2.json.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentkit.evidence import inside, sha256_file

STATUSES = {"OPEN", "RUNNING", "PARTIAL", "FAIL", "BLOCKED", "PASS",
            "OPEN_OBSERVATION", "WITHDRAWN"}
# scope -> evidence kinds that can close it
REQUIRED_KIND = {
    "software": {"software_test"},
    "manufactured_control": {"software_test", "simulation"},
    "numerical_model": {"simulation"},
    "numerical_wave_model": {"simulation"},
    "numerical_neural_model": {"simulation"},
    "fabricable_design": {"simulation", "design_review"},
    "measured_material": {"measurement"},
    "physical_component": {"measurement"},
    "physical_device": {"measurement"},
    "physical_system": {"measurement"},
    "physical_system_measurement": {"measurement"},
    "independent_evaluation": {"reserved_test"},
    "scientific_claim": {"measurement", "reserved_test"},
    "novelty": {"literature_search"},
    "external_replication": {"external_replication"},
    "observed_impact": {"third_party_record"},
    "decision": {"decision_record"},
    "review": {"review_record"},
}
KINDS = set().union(*REQUIRED_KIND.values())
EXTRA_FIELDS = {"measurement": ("instrument", "operator"),
                "external_replication": ("independent_team", "public_record"),
                "third_party_record": ("public_record",)}


def _cycles(by_id: dict) -> list[str]:
    """Claim ids that lie on a dependency cycle."""
    state, on_cycle = {}, set()

    def visit(node, stack):
        state[node] = 1
        stack.append(node)
        for dep in by_id[node].get("depends_on", []):
            if dep not in by_id:
                continue
            if state.get(dep) == 1:
                on_cycle.update(stack[stack.index(dep):])
            elif dep not in state:
                visit(dep, stack)
        stack.pop()
        state[node] = 2

    for node in by_id:
        if node not in state:
            visit(node, [])
    return sorted(on_cycle)


def validate(ledger: dict, root: Path) -> list[str]:
    """Return every rule violation; an empty list means the ledger is consistent."""
    problems = []
    claims = ledger.get("claims")
    if ledger.get("schema") != 1 or not isinstance(claims, list) or not claims:
        return ["Ledger must have schema 1 and a nonempty claims list"]
    agents = [str(a).strip().lower() for a in ledger.get("project_agents", []) if str(a).strip()]
    by_id = {}
    for claim in claims:
        cid = claim.get("id")
        if not cid or cid in by_id:
            problems.append(f"Missing or duplicate claim id: {cid!r}")
            continue
        by_id[cid] = claim
    for cid in _cycles(by_id):
        problems.append(f"{cid}: dependency cycle")
    for cid, claim in by_id.items():
        status, scope = claim.get("status"), claim.get("scope")
        if status not in STATUSES:
            problems.append(f"{cid}: unknown status {status!r}")
        if scope not in REQUIRED_KIND:
            problems.append(f"{cid}: unknown scope {scope!r}")
            continue
        if not str(claim.get("statement", "")).strip():
            problems.append(f"{cid}: empty statement")
        if not str(claim.get("falsifier", "")).strip():
            problems.append(f"{cid}: a falsifier (what would refute it) is required")
        if status == "WITHDRAWN" and not str(claim.get("withdrawal_reason", "")).strip():
            problems.append(f"{cid}: withdrawn claims keep their reason")
        valid_matching = 0
        for item in claim.get("evidence", []):
            kind, path = item.get("kind"), item.get("path")
            if kind not in KINDS:
                problems.append(f"{cid}: unknown evidence kind {kind!r}")
                continue
            missing = [f for f in ("produced_by", "how", *EXTRA_FIELDS.get(kind, ()))
                       if not str(item.get(f, "")).strip()]
            if missing:
                problems.append(f"{cid}: evidence {path!r} lacks {', '.join(missing)}")
                continue
            if kind in ("external_replication", "third_party_record") and agents:
                named = (str(item.get("independent_team", "")) + " " +
                         str(item.get("produced_by", ""))).lower()
                if any(agent in named for agent in agents):
                    problems.append(f"{cid}: project agents cannot provide {kind}")
                    continue
            try:
                resolved = inside(root, path)
            except (ValueError, TypeError, OSError):
                problems.append(f"{cid}: evidence path missing or unsafe: {path!r}")
                continue
            if not resolved.is_file() or sha256_file(resolved) != item.get("sha256"):
                problems.append(f"{cid}: evidence bytes missing or changed: {path}")
                continue
            if kind in REQUIRED_KIND[scope]:
                valid_matching += 1
        for dep in claim.get("depends_on", []):
            if dep not in by_id:
                problems.append(f"{cid}: unknown dependency {dep}")
            elif status == "PASS" and by_id[dep].get("status") != "PASS":
                problems.append(f"{cid}: PASS requires dependency {dep} to PASS")
        if status == "PASS" and valid_matching == 0:
            needed = ", ".join(sorted(REQUIRED_KIND[scope]))
            problems.append(f"{cid}: PASS requires verified evidence of kind {needed}")
    return problems


def render_table(ledger: dict) -> str:
    """Markdown status table; statements are shown as written, never upgraded."""
    cell = lambda value: " ".join(str(value).split()).replace("|", "/")
    lines = ["| Id | Scope | Status | Statement | Falsifier | Evidence | Limitations | Next action |",
             "|---|---|---|---|---|---|---|---|"]
    for claim in ledger["claims"]:
        evidence = "; ".join(f"{e.get('kind')}: {e.get('path')}" for e in claim.get("evidence", []))
        lines.append("| " + " | ".join(cell(v) for v in (
            claim["id"], claim["scope"], claim["status"], claim.get("statement", ""),
            claim.get("falsifier", ""), evidence or "none", claim.get("limitations", ""),
            claim.get("next_action", ""))) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    """Validate a ledger; write the rendered table only if the ledger is consistent."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--table")
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    problems = validate(ledger, args.root.resolve())
    if args.table and not problems:
        with Path(args.table).open("x", encoding="utf-8") as stream:
            stream.write(render_table(ledger))
    print(json.dumps({"consistent": not problems, "problems": problems,
                      "table_written": bool(args.table and not problems)},
                     ensure_ascii=False, indent=1))
    if problems:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/stats.py

```python file=agentkit/stats.py
"""Decision statistics for preregistered claims (kit v2).

Implements a complete three-zone decision rule, equivalence (TOST) and
one-sided tests, sample-size planning for between-chip studies, exact
binomial intervals for yields, distribution-free tolerance bounds for tail
percentiles and Holm multiplicity control. Each function states its
assumptions; none of them turns a model result into a measurement.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import beta, binom, nct, t

from agentkit.evidence import write_new_json


def _finite(*values: float) -> None:
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in values):
        raise ValueError("Inputs must be finite numbers")


def three_zone_decision(ci_low: float, ci_high: float, threshold: float,
                        model_floor: float | None = None) -> dict:
    """Classify a confidence interval for a loss-like quantity (smaller is better).

    CONFIRMED: ci_high <= threshold and (no floor or ci_low >= floor).
    FALSIFIED: ci_low > threshold.
    MODEL_CONTROL_FAIL: ci_high < floor (the measurement beats an ideal limit,
    which signals a model or measurement error, never a success).
    INCONCLUSIVE: every other case, including an interval containing the
    threshold or the floor. Every zone is defined before any data are seen.
    """
    _finite(ci_low, ci_high, threshold)
    if ci_low > ci_high:
        raise ValueError("Interval bounds are reversed")
    if model_floor is not None:
        _finite(model_floor)
        if not model_floor < threshold:
            raise ValueError("The model floor must lie below the threshold")
    threshold_zone = ("below" if ci_high <= threshold else
                      "above" if ci_low > threshold else "straddles")
    floor_zone = None
    if model_floor is not None:
        floor_zone = ("above" if ci_low >= model_floor else
                      "below" if ci_high < model_floor else "straddles")
    if floor_zone == "below":
        verdict = "MODEL_CONTROL_FAIL"
    elif threshold_zone == "above":
        verdict = "FALSIFIED"
    elif threshold_zone == "below" and floor_zone in (None, "above"):
        verdict = "CONFIRMED"
    else:
        verdict = "INCONCLUSIVE"
    return {"verdict": verdict, "threshold_zone": threshold_zone,
            "floor_zone": floor_zone, "interval": [ci_low, ci_high],
            "threshold": threshold, "model_floor": model_floor}


def _mean_se(values) -> tuple[float, float, int]:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.all(np.isfinite(x)):
        raise ValueError("At least two finite independent values are required")
    return float(x.mean()), float(x.std(ddof=1) / math.sqrt(len(x))), len(x)


def one_sided_upper(values, threshold: float, alpha: float = 0.05) -> dict:
    """Test H0: mean >= threshold against H1: mean < threshold (t, independent units)."""
    _finite(threshold, alpha)
    if not 0 < alpha < 0.5:
        raise ValueError("alpha must lie in (0, 0.5)")
    mean, se, n = _mean_se(values)
    if se == 0:
        raise ValueError("Zero spread: the t model is not identifiable")
    statistic = (mean - threshold) / se
    return {"mean": mean, "standard_error": se, "n": n,
            "p_value": float(t.cdf(statistic, n - 1)),
            "upper_confidence_bound": mean + float(t.ppf(1 - alpha, n - 1)) * se,
            "reject_h0": bool(t.cdf(statistic, n - 1) < alpha), "alpha": alpha}


def tost(values, low: float, high: float, alpha: float = 0.05) -> dict:
    """Two one-sided tests (Schuirmann 1987) for equivalence within [low, high]."""
    _finite(low, high, alpha)
    if not low < high or not 0 < alpha < 0.5:
        raise ValueError("Require low < high and alpha in (0, 0.5)")
    mean, se, n = _mean_se(values)
    if se == 0:
        raise ValueError("Zero spread: the t model is not identifiable")
    p_low = float(t.sf((mean - low) / se, n - 1))
    p_high = float(t.cdf((mean - high) / se, n - 1))
    margin = float(t.ppf(1 - alpha, n - 1)) * se
    return {"mean": mean, "n": n, "p_low": p_low, "p_high": p_high,
            "equivalent": bool(max(p_low, p_high) < alpha),
            "ci_1_minus_2alpha": [mean - margin, mean + margin], "alpha": alpha}


def one_sided_power(n: int, effect: float, sigma: float, alpha: float = 0.05) -> float:
    """Power of the one-sided t test for a true margin `effect` below the threshold."""
    if type(n) is not int or n < 2:
        raise ValueError("n must be an integer of at least two")
    _finite(effect, sigma, alpha)
    if effect <= 0 or sigma <= 0:
        raise ValueError("effect and sigma must be positive")
    critical = t.ppf(1 - alpha, n - 1)
    return float(nct.sf(critical, n - 1, effect / sigma * math.sqrt(n)))


def sample_size_one_sided(effect: float, sigma: float, alpha: float = 0.025,
                          power: float = 0.8, max_n: int = 10000) -> int:
    """Smallest number of independent units (e.g. chips) reaching the target power.

    alpha = 0.025 matches a decision taken from one bound of a two-sided 95 %
    interval, as in three_zone_decision. The plan assumes the decision uses
    the between-unit standard error; metrology.fit_cutback uses the larger of
    the between-chip and measurement errors, so treat the result as a minimum.
    """
    _finite(power)
    if not 0 < power < 1:
        raise ValueError("power must lie in (0, 1)")
    for n in range(2, max_n + 1):
        if one_sided_power(n, effect, sigma, alpha) >= power:
            return n
    raise ValueError("Target power is not reachable within max_n")


def clopper_pearson(k: int, n: int, confidence: float = 0.95) -> list[float]:
    """Exact two-sided binomial interval (Clopper and Pearson 1934)."""
    if type(k) is not int or type(n) is not int or not 0 <= k <= n or n < 1:
        raise ValueError("Require integers 0 <= k <= n, n >= 1")
    alpha = 1 - confidence
    low = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    high = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [low, high]


def wilks_sample_size(coverage: float = 0.95, confidence: float = 0.95, order: int = 1) -> int:
    """Runs needed so the `order`-th largest value bounds the coverage quantile."""
    _finite(coverage, confidence)
    if not (0 < coverage < 1 and 0 < confidence < 1) or type(order) is not int or order < 1:
        raise ValueError("Invalid coverage, confidence or order")
    n = order
    while binom.sf(order - 1, n, 1 - coverage) < confidence:
        n += 1
        if n > 10_000_000:
            raise ValueError("Sample size beyond supported range")
    return n


def upper_tolerance_bound(values, coverage: float = 0.95, confidence: float = 0.95) -> dict:
    """Distribution-free one-sided upper bound for the coverage quantile.

    Valid for independent, identically distributed realizations. Correlated
    Monte Carlo draws or reused seeds violate this premise.
    """
    x = np.sort(np.asarray(values, dtype=float))
    if x.ndim != 1 or not np.all(np.isfinite(x)):
        raise ValueError("Values must be finite")
    n = len(x)
    best = None
    for r in range(1, n + 1):
        if binom.sf(r - 1, n, 1 - coverage) >= confidence:
            best = r
        else:
            break
    if best is None:
        return {"bound": None, "n": n, "required_n": wilks_sample_size(coverage, confidence),
                "coverage": coverage, "confidence": confidence}
    return {"bound": float(x[n - best]), "order_from_top": best, "n": n,
            "achieved_confidence": float(binom.sf(best - 1, n, 1 - coverage)),
            "coverage": coverage, "confidence": confidence}


def holm(p_values, alpha: float = 0.05) -> list[bool]:
    """Holm step-down rejection decisions in the original order."""
    p = np.asarray(p_values, dtype=float)
    if p.ndim != 1 or len(p) < 1 or np.any((p < 0) | (p > 1)):
        raise ValueError("p-values must lie in [0, 1]")
    order = np.argsort(p)
    reject = np.zeros(len(p), dtype=bool)
    for rank, index in enumerate(order):
        if p[index] <= alpha / (len(p) - rank):
            reject[index] = True
        else:
            break
    return reject.tolist()


def main() -> None:
    """Compute a preregistered decision from a JSON request and keep the result."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    zone = commands.add_parser("decide")
    zone.add_argument("--ci-low", type=float, required=True)
    zone.add_argument("--ci-high", type=float, required=True)
    zone.add_argument("--threshold", type=float, required=True)
    zone.add_argument("--model-floor", type=float)
    size = commands.add_parser("sample-size")
    size.add_argument("--effect", type=float, required=True)
    size.add_argument("--sigma", type=float, required=True)
    size.add_argument("--alpha", type=float, default=0.025)
    size.add_argument("--power", type=float, default=0.8)
    yields = commands.add_parser("yield")
    yields.add_argument("--k", type=int, required=True)
    yields.add_argument("--n", type=int, required=True)
    for sub in (zone, size, yields):
        sub.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "decide":
        result = three_zone_decision(args.ci_low, args.ci_high, args.threshold, args.model_floor)
    elif args.command == "sample-size":
        n = sample_size_one_sided(args.effect, args.sigma, args.alpha, args.power)
        result = {"n_independent_units": n, "effect": args.effect, "sigma": args.sigma,
                  "alpha": args.alpha, "power_target": args.power,
                  "achieved_power": one_sided_power(n, args.effect, args.sigma, args.alpha),
                  "assumption": "independent, approximately normal unit means; sigma is a planning value"}
    else:
        result = {"k": args.k, "n": args.n, "fraction": args.k / args.n,
                  "clopper_pearson_95": clopper_pearson(args.k, args.n)}
    write_new_json(args.out, result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/limits.py

```python file=agentkit/limits.py
"""Parametric energy and precision budget for an optoelectronic linear layer (kit v2).

This is a kill test, not a measurement. It asks whether, with stated
parameters, a passive optical layer could beat a digital reference energy
per multiply-accumulate (MAC) at a stated output precision. Every input is
explicit; nothing is looked up. Digital reference energies must come from a
cited source or a measurement, with technology node and year.

Noise model at each detector over one sample period T (electrons):
  variance = N_e (shot) + sigma_th**2, sigma_th = i_n * sqrt(B) * T / q.
Requirement: k * sqrt(variance) <= N_e / (2 L), L = 2**bits levels.
Optical amortization over fan-in follows the photoelectric multiplication
argument of Hamerly et al., Phys. Rev. X 9, 021032 (2019).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from agentkit.evidence import write_new_json

PLANCK_J_S = 6.62607015e-34
LIGHT_M_S = 299792458.0
ELEMENTARY_C = 1.602176634e-19


def _positive(**values: float) -> None:
    for name, value in values.items():
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(name + " must be finite and positive")


def photon_energy_j(wavelength_m: float) -> float:
    """Return h c / lambda in joules."""
    _positive(wavelength_m=wavelength_m)
    return PLANCK_J_S * LIGHT_M_S / wavelength_m


def required_electrons(bits: int, sigma_multiple: float = 1.0,
                       thermal_sigma_electrons: float = 0.0) -> float:
    """Full-scale photoelectrons resolving 2**bits levels at k sigma."""
    if type(bits) is not int or not 1 <= bits <= 24:
        raise ValueError("bits must be an integer from 1 to 24")
    _positive(sigma_multiple=sigma_multiple)
    if not math.isfinite(thermal_sigma_electrons) or thermal_sigma_electrons < 0:
        raise ValueError("thermal noise must be finite and nonnegative")
    a = 1.0 / (4.0 * sigma_multiple**2 * (2.0**bits)**2)
    return (1.0 + math.sqrt(1.0 + 4.0 * a * thermal_sigma_electrons**2)) / (2.0 * a)


def detection_energy_j(bits: int, wavelength_m: float, quantum_efficiency: float,
                       sample_rate_hz: float, current_noise_a_rthz: float = 0.0,
                       bandwidth_hz: float | None = None, sigma_multiple: float = 1.0) -> dict:
    """Optical energy that must reach one detector per sample."""
    _positive(wavelength_m=wavelength_m, sample_rate_hz=sample_rate_hz)
    if not 0 < quantum_efficiency <= 1:
        raise ValueError("quantum efficiency must lie in (0, 1]")
    if not math.isfinite(current_noise_a_rthz) or current_noise_a_rthz < 0:
        raise ValueError("current noise must be finite and nonnegative")
    bandwidth = sample_rate_hz / 2 if bandwidth_hz is None else bandwidth_hz
    _positive(bandwidth_hz=bandwidth)
    period = 1.0 / sample_rate_hz
    sigma_th = current_noise_a_rthz * math.sqrt(bandwidth) * period / ELEMENTARY_C
    electrons = required_electrons(bits, sigma_multiple, sigma_th)
    photons = electrons / quantum_efficiency
    return {"electrons": electrons, "photons": photons,
            "thermal_sigma_electrons": sigma_th,
            "optical_energy_j": photons * photon_energy_j(wavelength_m)}


def layer_budget(n_inputs: int, n_outputs: int, bits: int, wavelength_m: float,
                 quantum_efficiency: float, sample_rate_hz: float,
                 optical_transmission: float, laser_wall_plug_efficiency: float,
                 modulator_energy_j: float, dac_energy_j: float, adc_energy_j: float,
                 static_power_w: float = 0.0, current_noise_a_rthz: float = 0.0,
                 sigma_multiple: float = 1.0,
                 digital_reference_j_per_mac: float | None = None) -> dict:
    """Energy per frame and per MAC for a dense passive N-by-M layer.

    Assumes the laser energy is shared without excess loss beyond
    `optical_transmission` (all coupling, propagation, splitting excess and
    crossing loss, as a fraction). Electrical energies are per sample.
    """
    if type(n_inputs) is not int or type(n_outputs) is not int or min(n_inputs, n_outputs) < 1:
        raise ValueError("Layer dimensions must be positive integers")
    if not 0 < optical_transmission <= 1 or not 0 < laser_wall_plug_efficiency <= 1:
        raise ValueError("Transmission and wall-plug efficiency must lie in (0, 1]")
    for name, value in (("modulator", modulator_energy_j), ("dac", dac_energy_j),
                        ("adc", adc_energy_j), ("static", static_power_w)):
        if not math.isfinite(value) or value < 0:
            raise ValueError(name + " energy must be finite and nonnegative")
    detector = detection_energy_j(bits, wavelength_m, quantum_efficiency, sample_rate_hz,
                                  current_noise_a_rthz, None, sigma_multiple)
    laser_optical = n_outputs * detector["optical_energy_j"] / optical_transmission
    components = {"laser_electrical_j": laser_optical / laser_wall_plug_efficiency,
                  "modulators_j": n_inputs * modulator_energy_j,
                  "dacs_j": n_inputs * dac_energy_j,
                  "adcs_j": n_outputs * adc_energy_j,
                  "static_j": static_power_w / sample_rate_hz}
    total = sum(components.values())
    macs = n_inputs * n_outputs
    result = {"scope": "parametric_budget_not_measurement",
              "components_per_frame_j": components, "total_per_frame_j": total,
              "macs_per_frame": macs, "joules_per_mac": total / macs,
              "detector": detector, "dominant_component": max(components, key=components.get)}
    if digital_reference_j_per_mac is not None:
        _positive(digital_reference_j_per_mac=digital_reference_j_per_mac)
        result["advantage_factor"] = digital_reference_j_per_mac / result["joules_per_mac"]
    return result


def max_depth(available_laser_optical_w: float, sample_rate_hz: float, n_outputs: int,
              detector_energy_j: float, fixed_loss_db: float, loss_per_stage_db: float) -> int | None:
    """Deepest cascade whose loss still leaves enough photons at every detector."""
    _positive(available_laser_optical_w=available_laser_optical_w,
              sample_rate_hz=sample_rate_hz, detector_energy_j=detector_energy_j,
              loss_per_stage_db=loss_per_stage_db)
    if type(n_outputs) is not int or n_outputs < 1 or not math.isfinite(fixed_loss_db) or fixed_loss_db < 0:
        raise ValueError("Invalid outputs or fixed loss")
    headroom_db = 10 * math.log10(available_laser_optical_w /
                                  (sample_rate_hz * n_outputs * detector_energy_j)) - fixed_loss_db
    if headroom_db < 0:
        return None
    return int(math.floor(headroom_db / loss_per_stage_db + 1e-12))


def main() -> None:
    """Evaluate a JSON parameter file with layer_budget and keep the result."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    params = json.loads(args.params.read_text(encoding="utf-8"))
    provenance = params.pop("provenance", None)
    if not isinstance(provenance, dict):
        raise ValueError("provenance must map every parameter to its source")
    missing = [k for k in params if not str(provenance.get(k, "")).strip()]
    if missing:
        raise ValueError("Missing provenance for: " + ", ".join(sorted(missing)))
    result = layer_budget(**params)
    result["parameters"] = params
    result["provenance"] = provenance
    write_new_json(args.out, result)
    print(json.dumps({"joules_per_mac": result["joules_per_mac"],
                      "dominant_component": result["dominant_component"],
                      "advantage_factor": result.get("advantage_factor")}))


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/mzi.py

```python file=agentkit/mzi.py
"""Rectangular (Clements-ordered) MZI mesh synthesis with an explicit device convention.

Convention (stated, not universal): a symmetric directional coupler
B = [[cos a, i sin a], [i sin a, cos a]] with a = pi/4 + eps, and
MZI(theta, phi) = B(eps2) @ diag(exp(i theta), 1) @ B(eps1) @ diag(exp(i phi), 1),
both phase shifters on the upper arm of the pair (m, m+1). The ideal MZI is
i exp(i theta/2) [[exp(i phi) sin(theta/2), cos(theta/2)],
                  [exp(i phi) cos(theta/2), -sin(theta/2)]].
Ordering follows Clements et al., Optica 3, 1460 (2016): N(N-1)/2 MZIs in a
rectangular arrangement of depth N, then an output phase screen. Other device
conventions require their own derivation; the reconstruction check below is
the acceptance test, not the formulas.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from agentkit.evidence import write_new_json
from agentkit.numerics import finite_array


def coupler(eps: float = 0.0) -> np.ndarray:
    """Directional coupler with splitting angle pi/4 + eps."""
    a = math.pi / 4 + eps
    return np.array([[math.cos(a), 1j * math.sin(a)], [1j * math.sin(a), math.cos(a)]])


def mzi(theta: float, phi: float, eps1: float = 0.0, eps2: float = 0.0) -> np.ndarray:
    """Return the 2x2 transfer of one MZI in the stated convention."""
    return (coupler(eps2) @ np.diag([np.exp(1j * theta), 1.0]) @ coupler(eps1)
            @ np.diag([np.exp(1j * phi), 1.0]))


def _embed(block: np.ndarray, n: int, m: int) -> np.ndarray:
    full = np.eye(n, dtype=complex)
    full[m:m + 2, m:m + 2] = block
    return full


def _null_right(a: complex, b: complex) -> tuple[float, float]:
    """(theta, phi) with [a, b] @ MZI(theta, phi)^dagger having a zero first entry."""
    theta = 2 * math.atan2(abs(b), abs(a))
    phi = 0.0 if abs(a) == 0 or abs(b) == 0 else float(np.angle(-a / b))
    return theta, phi


def _null_left(a: complex, b: complex) -> tuple[float, float]:
    """(theta, phi) with MZI(theta, phi) @ [a, b]^T having a zero second entry."""
    theta = 2 * math.atan2(abs(a), abs(b))
    phi = 0.0 if abs(a) == 0 or abs(b) == 0 else float(np.angle(b / a))
    return theta, phi


def clements_decompose(unitary, tolerance: float = 1e-10) -> dict:
    """Decompose a unitary into MZIs (propagation order) and output phases."""
    u = finite_array(unitary, ndim=2).astype(complex)
    n = len(u)
    if u.shape != (n, n) or not 2 <= n <= 64:
        raise ValueError("Clements synthesis supports square matrices from 2 to 64")
    if np.linalg.norm(u.conj().T @ u - np.eye(n), 2) > tolerance:
        raise ValueError("Target is not unitary")
    work = u.copy()
    right, left = [], []
    for i in range(1, n):
        if i % 2 == 1:
            for j in range(i):
                row, col = n - 1 - j, i - 1 - j
                theta, phi = _null_right(work[row, col], work[row, col + 1])
                work = work @ _embed(mzi(theta, phi), n, col).conj().T
                right.append((col, theta, phi))
        else:
            for j in range(1, i + 1):
                row, col = n - 1 + j - i, j - 1
                theta, phi = _null_left(work[row - 1, col], work[row, col])
                work = _embed(mzi(theta, phi), n, row - 1) @ work
                left.append((row - 1, theta, phi))
    off = work - np.diag(np.diag(work))
    if np.linalg.norm(off, 2) > 50 * tolerance:
        raise RuntimeError("Nulling sequence did not produce a diagonal matrix")
    diagonal = np.diag(work).copy()
    # U = L_1^dag ... L_k^dag D R_p ... R_1 ; move each L^dag through D.
    moved = []
    for m, theta, phi in reversed(left):
        d1, d2 = diagonal[m], diagonal[m + 1]
        kappa = -np.exp(-1j * theta)
        diagonal[m], diagonal[m + 1] = kappa * np.exp(-1j * phi) * d2, kappa * d2
        moved.append((m, theta, float(np.angle(d1 / d2))))
    sequence = right + moved
    last = [0] * n
    mzis = []
    for m, theta, phi in sequence:
        layer = max(last[m], last[m + 1]) + 1
        last[m] = last[m + 1] = layer
        mzis.append({"modes": [m, m + 1], "theta_rad": float(theta % (2 * math.pi)),
                     "phi_rad": float(phi % (2 * math.pi)), "layer": layer})
    result = {"dimension": n, "convention": "MZI = B P(theta) B P(phi), B symmetric 50:50, upper-arm phases",
              "mzis": mzis, "output_phases_rad": np.angle(diagonal).tolist(),
              "n_mzis": len(mzis), "depth": max(last),
              "scope": "ideal_transfer_algebra", "geometry_validated": False}
    error = float(np.linalg.norm(clements_reconstruct(result) - u, 2))
    if error > 100 * tolerance:
        raise RuntimeError("Clements reconstruction failed")
    result["reconstruction_error"] = error
    return result


def clements_reconstruct(decomposition: dict, splitter_errors=None) -> np.ndarray:
    """Rebuild the transfer; optional per-MZI (eps1, eps2) splitter-angle errors."""
    n = decomposition["dimension"]
    count = len(decomposition["mzis"])
    errors = (np.zeros((count, 2)) if splitter_errors is None
              else finite_array(splitter_errors, ndim=2))
    if errors.shape != (count, 2):
        raise ValueError("splitter_errors must have shape (n_mzis, 2)")
    transfer = np.eye(n, dtype=complex)
    for op, (e1, e2) in zip(decomposition["mzis"], errors):
        block = mzi(op["theta_rad"], op["phi_rad"], float(e1), float(e2))
        transfer = _embed(block, n, op["modes"][0]) @ transfer
    return np.exp(1j * np.asarray(decomposition["output_phases_rad"]))[:, None] * transfer


def fidelity(target, realized) -> float:
    """Global-phase-insensitive fidelity |Tr(U^dagger V)| / N for unitaries."""
    a, b = finite_array(target, ndim=2), finite_array(realized, ndim=2)
    if a.shape != b.shape or a.shape[0] != a.shape[1]:
        raise ValueError("Matrices must be square and equal in shape")
    return float(abs(np.trace(a.conj().T @ b)) / a.shape[0])


def splitter_error_study(unitary, sigma: float, realizations: int, seed: int,
                         correlation: float = 0.0) -> dict:
    """Fidelity distribution under Gaussian splitter errors with a shared component.

    correlation in [0, 1) is the fraction of variance shared by all splitters
    (for example one wafer-level writing bias). Use measured values in T10.
    """
    if not 0 <= correlation < 1 or sigma < 0 or realizations < 1:
        raise ValueError("Invalid error-study parameters")
    decomposition = clements_decompose(unitary)
    rng = np.random.default_rng(seed)
    count = decomposition["n_mzis"]
    values = []
    for _ in range(realizations):
        shared = rng.normal(0, sigma * math.sqrt(correlation))
        local = rng.normal(0, sigma * math.sqrt(1 - correlation), size=(count, 2))
        values.append(fidelity(unitary, clements_reconstruct(decomposition, shared + local)))
    values = np.asarray(values)
    return {"sigma_rad": sigma, "correlation": correlation, "realizations": realizations,
            "seed": seed, "mean_fidelity": float(values.mean()),
            "p05_fidelity": float(np.percentile(values, 5)), "fidelities": values.tolist(),
            "note": "Uncalibrated mesh; in-situ recalibration can recover part of this loss."}


def compile_passive_clements(target) -> dict:
    """T = U diag(s) V^dagger with two rectangular meshes and amplitudes s <= 1."""
    t = finite_array(target, ndim=2).astype(complex)
    if t.shape[0] != t.shape[1]:
        raise ValueError("Passive compilation requires a square target")
    left, singular, right_h = np.linalg.svd(t)
    if singular.max() > 1 + 1e-12:
        raise ValueError("Target requires amplification; declare external gain or input scaling")
    singular = np.minimum(singular, 1.0)
    first, second = clements_decompose(right_h), clements_decompose(left)
    realized = clements_reconstruct(second) @ np.diag(singular) @ clements_reconstruct(first)
    return {"dimension": len(t), "input_mesh": first, "attenuation_amplitudes": singular.tolist(),
            "output_mesh": second, "mesh_depths": [first["depth"], second["depth"]],
            "depth": first["depth"] + second["depth"] + 1,
            "depth_note": "MZI layers of both meshes plus one attenuator column",
            "reconstruction_error": float(np.linalg.norm(realized - t, 2)),
            "scope": "ideal_passive_transfer_algebra", "geometry_validated": False}


def main() -> None:
    """Decompose a complex NPZ `target` (unitary, or contraction with --passive)."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--passive", action="store_true")
    args = parser.parse_args()
    with np.load(args.input, allow_pickle=False) as data:
        target = data["target"]
    result = compile_passive_clements(target) if args.passive else clements_decompose(target)
    write_new_json(args.out, result)
    print(json.dumps({"depth": result["depth"],
                      "reconstruction_error": result["reconstruction_error"]}))


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/learning_v2.py

```python file=agentkit/learning_v2.py
"""Smooth signed-field MZM activation and validation-based selection (kit v2).

Finding recorded in guide v2: with the v1 example (unitary_mzm, 8 starts,
1000 iterations, development digits), no start satisfied the v1 gradient
gate; L-BFGS-B stopped on relative loss reduction with max |gradient| of
about 5e-3 to 6e-2. The v1 re-emission uses |cos(.)|, which is not
differentiable where cos = 0, and a positive amplitude discards the sign of
the field. A push-pull MZM fed by a phase-referenced carrier transmits the
signed field amplitude cos(.), which is smooth. These models implement that
convention; their physical validity still requires the hardware check of
T12 point 7 (reference phase, bias stability, measured V_pi).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

from agentkit.evidence import sha256_file, write_new_json
from agentkit.learning import transfer

MODELS_V2 = ("unitary_mzm_signed", "real_mzm_signed")


def model_size_v2(model: str, n: int) -> int:
    """Two full n-by-n transfers."""
    if model not in MODELS_V2:
        raise ValueError("Unknown v2 model")
    return 2 * n * n


def scores_and_directions_v2(parameters, x, model: str, v_pi: float = 1.0,
                             bias: float = 0.0, derivatives: bool = False):
    """Intensity scores and exact parameter directions for signed re-emission."""
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or not np.all(np.isfinite(x)) or not 2 <= x.shape[1] <= 8:
        raise ValueError("Inputs must be finite rows with 2 to 8 features")
    n = x.shape[1]
    p = np.asarray(parameters, dtype=float)
    if p.shape != (model_size_v2(model, n),) or not np.all(np.isfinite(p)):
        raise ValueError("Wrong or non-finite parameters")
    if not math.isfinite(v_pi) or v_pi <= 0 or not math.isfinite(bias):
        raise ValueError("V_pi must be positive and bias finite")
    unitary = model.startswith("unitary")
    first, d_first = transfer(p[:n * n], n, unitary, derivatives)
    second, d_second = transfer(p[n * n:], n, unitary, derivatives)
    z1 = x @ first.T
    i1 = abs(z1) ** 2
    angle = 0.5 * (math.pi * i1 / v_pi + bias)
    amplitude = np.cos(angle)
    slope = -0.5 * math.pi / v_pi * np.sin(angle)
    z2 = amplitude @ second.T
    scores = abs(z2) ** 2
    if not derivatives:
        return scores, None
    directions = []
    for direction in d_first:
        di1 = 2 * np.real(np.conj(z1) * (x @ direction.T))
        directions.append(2 * np.real(np.conj(z2) * ((slope * di1) @ second.T)))
    for direction in d_second:
        directions.append(2 * np.real(np.conj(z2) * (amplitude @ direction.T)))
    return scores, np.asarray(directions)


def objective_v2(parameters, x, y, model: str, v_pi: float = 1.0, bias: float = 0.0):
    """Cross-entropy on intensity logits and its exact gradient."""
    scores, directions = scores_and_directions_v2(parameters, x, model, v_pi, bias, True)
    y = np.asarray(y)
    if y.shape != (len(x),) or y.dtype.kind not in "iu" or y.min() < 0 or y.max() >= scores.shape[1]:
        raise ValueError("Labels must index the output classes")
    normalizer = logsumexp(scores, axis=1)
    loss = float(np.mean(normalizer - scores[np.arange(len(y)), y]))
    weights = np.exp(scores - normalizer[:, None])
    weights[np.arange(len(y)), y] -= 1
    weights /= len(y)
    return loss, np.einsum("nc,knc->k", weights, directions)


def _load_split(path: Path):
    """Load X (finite, 2 to 8 features) and integer labels y of equal length."""
    with np.load(path, allow_pickle=False) as data:
        x, y = data["X"].copy(), data["y"].copy()
    if (x.ndim != 2 or not 2 <= x.shape[1] <= 8 or not np.all(np.isfinite(x))
            or y.shape != (len(x),) or y.dtype.kind not in "iu" or len(x) < 1 or y.min() < 0):
        raise ValueError("Invalid split: " + str(path))
    return x, y


def fit_candidate_v2(train_path: Path, validation_path: Path, model: str, seeds: list[int],
                     maxiter: int, v_pi: float, bias: float,
                     gradient_threshold: float = 1e-5) -> dict:
    """Fit every registered start and keep all diagnostics (same record shape as v1)."""
    if not seeds or len(set(seeds)) != len(seeds) or maxiter < 1:
        raise ValueError("Starts must be unique and iterations positive")
    x, y = _load_split(train_path)
    xv, yv = _load_split(validation_path)
    if xv.shape[1] != x.shape[1]:
        raise ValueError("Training and validation feature dimensions differ")
    records = []
    for seed in seeds:
        start = 0.5 * np.random.default_rng(seed).standard_normal(model_size_v2(model, x.shape[1]))
        result = minimize(objective_v2, start, args=(x, y, model, v_pi, bias), jac=True,
                          method="L-BFGS-B",
                          options={"maxiter": maxiter, "gtol": 1e-8, "ftol": 1e-12})
        loss, gradient = objective_v2(result.x, x, y, model, v_pi, bias)
        norm = float(np.max(abs(gradient)))
        records.append({"seed": seed, "parameters": result.x.tolist(), "training_loss": loss,
                        "gradient_infinity_norm": norm, "optimizer_success": bool(result.success),
                        "optimizer_message": str(result.message), "iterations": int(result.nit),
                        "converged": bool(result.success and norm <= gradient_threshold)})
    converged = [r for r in records if r["converged"]]
    best = min(converged or records, key=lambda item: item["training_loss"])
    parameters = np.asarray(best["parameters"])
    accuracy = lambda a, b: float(np.mean(
        scores_and_directions_v2(parameters, a, model, v_pi, bias)[0].argmax(axis=1) == b))
    validation_scores = scores_and_directions_v2(parameters, xv, model, v_pi, bias)[0]
    validation_loss = float(np.mean(logsumexp(validation_scores, axis=1) -
                                    validation_scores[np.arange(len(yv)), yv]))
    return {"model": model, "dimension": x.shape[1], "v_pi": v_pi, "bias": bias,
            "maxiter": maxiter, "gradient_threshold": gradient_threshold,
            "train_sha256": sha256_file(train_path), "validation_sha256": sha256_file(validation_path),
            "selected_by": ("minimum_training_loss_among_converged_starts" if converged
                            else "minimum_training_loss_no_start_converged"),
            "selected": best, "all_starts": records,
            "converged_starts": sum(r["converged"] for r in records),
            "train_accuracy": accuracy(x, y), "validation_accuracy": accuracy(xv, yv),
            "validation_loss": validation_loss, "test_evaluated": False,
            "scope": "numerical_optoelectronic_model"}


def select_by_validation(candidate_paths: list[Path]) -> dict:
    """Choose among converged configurations by validation loss (test untouched)."""
    entries = []
    for path in candidate_paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        entries.append({"path": str(path), "sha256": sha256_file(path), "model": record["model"],
                        "v_pi": record["v_pi"], "bias": record["bias"],
                        "converged": bool(record["selected"]["converged"]),
                        "validation_loss": record.get("validation_loss"),
                        "validation_accuracy": record["validation_accuracy"]})
    eligible = [e for e in entries if e["converged"] and e["validation_loss"] is not None]
    if not eligible:
        raise ValueError("No converged candidate with a validation loss is available")
    chosen = min(eligible, key=lambda e: (e["validation_loss"], -e["validation_accuracy"]))
    return {"chosen": chosen, "considered": entries,
            "rule": "minimum validation loss among converged candidates; ties by accuracy"}


def evaluate_locked_v2(candidate_path: Path, test_path: Path) -> dict:
    """Evaluate one frozen converged v2 candidate exactly once."""
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    if candidate["model"] not in MODELS_V2 or not candidate["selected"]["converged"]:
        raise ValueError("Requires a converged v2 candidate")
    x, y = _load_split(test_path)
    if x.shape[1] != candidate["dimension"]:
        raise ValueError("Test feature dimension differs from the candidate")
    scores, _ = scores_and_directions_v2(candidate["selected"]["parameters"], x,
                                         candidate["model"], candidate["v_pi"], candidate["bias"])
    predictions = scores.argmax(axis=1)
    return {"candidate_sha256": sha256_file(candidate_path), "test_sha256": sha256_file(test_path),
            "n_test": len(y), "accuracy": float(np.mean(predictions == y)),
            "predictions": predictions.tolist(), "labels": y.tolist(),
            "scope": "numerical_optoelectronic_model"}


def kink_fraction(candidate_path: Path, data_path: Path, epsilon: float = 1e-2) -> dict:
    """For a v1 *_mzm or *_abs candidate, fraction of samples near the nonsmooth point."""
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    model = candidate["model"]
    if not (model.endswith("_mzm") or model.endswith("_abs")):
        raise ValueError("Only v1 models with |.| re-emission have a kink")
    with np.load(data_path, allow_pickle=False) as data:
        x = data["X"].copy()
    n = x.shape[1]
    first, _ = transfer(np.asarray(candidate["selected"]["parameters"])[:n * n], n,
                        model.startswith("unitary"), False)
    i1 = abs(x @ first.T) ** 2
    value = (np.cos(0.5 * (math.pi * i1 / candidate["v_pi"] + candidate["bias"]))
             if model.endswith("_mzm") else np.sqrt(i1))
    near = abs(value) < epsilon
    return {"model": model, "epsilon": epsilon,
            "selected_converged": bool(candidate["selected"]["converged"]),
            "activations_near_kink": int(near.sum()), "activations": int(near.size),
            "fraction_near_kink": float(near.mean()),
            "samples_with_any_near_kink": int(near.any(axis=1).sum()), "samples": len(near),
            "fraction_samples_near_kink": float(near.any(axis=1).mean()),
            "candidate_sha256": sha256_file(candidate_path)}


def main() -> None:
    """fit, select, evaluate or kink diagnostics with new output paths only."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    fit = commands.add_parser("fit")
    fit.add_argument("--train", type=Path, required=True)
    fit.add_argument("--validation", type=Path, required=True)
    fit.add_argument("--model", choices=MODELS_V2, required=True)
    fit.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 9)))
    fit.add_argument("--maxiter", type=int, default=1000)
    fit.add_argument("--v-pi", type=float, default=1.0)
    fit.add_argument("--bias", type=float, default=0.0)
    fit.add_argument("--gradient-threshold", type=float, default=1e-5)
    select = commands.add_parser("select")
    select.add_argument("--candidates", type=Path, nargs="+", required=True)
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--candidate", type=Path, required=True)
    evaluate.add_argument("--test", type=Path, required=True)
    kink = commands.add_parser("kink")
    kink.add_argument("--candidate", type=Path, required=True)
    kink.add_argument("--data", type=Path, required=True)
    kink.add_argument("--epsilon", type=float, default=1e-2)
    for sub in (fit, select, evaluate, kink):
        sub.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Output path must be new")
    if args.command == "fit":
        result = fit_candidate_v2(args.train, args.validation, args.model, args.seeds,
                                  args.maxiter, args.v_pi, args.bias, args.gradient_threshold)
    elif args.command == "select":
        result = select_by_validation(args.candidates)
    elif args.command == "evaluate":
        result = evaluate_locked_v2(args.candidate, args.test)
    else:
        result = kink_fraction(args.candidate, args.data, args.epsilon)
    write_new_json(args.out, result)
    keys = ("model", "converged_starts", "train_accuracy", "validation_accuracy",
            "validation_loss", "accuracy", "fraction_near_kink", "chosen")
    print(json.dumps({k: result[k] for k in keys if k in result}))


if __name__ == "__main__":
    main()
```

### Archivo: agentkit/test_v2.py

```python file=agentkit/test_v2.py
"""Controls and rejection tests for the v2 modules. Run: python -B -m unittest agentkit.test_v2 -v

Kept inside agentkit/ so scripts/check.py (which discovers tests/) and the
Codex-owned tests/ directory are not changed.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import numpy as np
from scipy.stats import binomtest

from agentkit.blind import blind_rows, create_secret, unblind_report
from agentkit.claims import REQUIRED_KIND, render_table, validate
from agentkit.evidence import canonical, sha256_file, write_new_json
from agentkit.learning_v2 import fit_candidate_v2, objective_v2
from agentkit.limits import (detection_energy_j, layer_budget, max_depth,
                             photon_energy_j, required_electrons)
from agentkit.mesh import decompose_unitary, reconstruct
from agentkit.metrology import fit_cutback
from agentkit.mzi import (clements_decompose, clements_reconstruct, compile_passive_clements,
                          fidelity, splitter_error_study)
from agentkit.prereg import audit_v2, commit_protocol, committed_protocol, history_conflicts
from agentkit.stats import (clopper_pearson, holm, one_sided_power, one_sided_upper,
                            sample_size_one_sided, three_zone_decision, tost,
                            upper_tolerance_bound, wilks_sample_size)


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=Kit Test",
                           "-c", "user.email=kit@example.invalid", *args],
                          check=True, capture_output=True, text=True)


def random_unitary(n, seed):
    rng = np.random.default_rng(seed)
    q, r = np.linalg.qr(rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n)))
    return q * (np.diag(r) / abs(np.diag(r)))


class PreregTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        git(self.root, "init", "-q")
        self.protocol = {"experiment_id": "e1", "task_id": "T01", "model": "fixture",
                         "units": {"length": "m", "note": "Á í µm dB/cm"}, "scope": "manufactured_control",
                         "criteria": [{"id": "err", "operator": "le", "threshold": 0.01}],
                         "resource_limits": {"seconds": 1}, "heldout_policy": "fixture",
                         "planned_artifacts": ["raw.csv"]}
        write_new_json(self.root / "protocol.json", self.protocol)
        (self.root / "source.py").write_text("x = 1\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "protocol")

    def tearDown(self):
        self.tmp.cleanup()

    def result(self, value):
        return {"experiment_id": "e1", "scope": "manufactured_control", "status": "completed",
                "protocol_sha256": hashlib.sha256(canonical(self.protocol)).hexdigest(),
                "artifacts": ["raw.csv"], "metrics": {"err": value}}

    def test_honest_flow_passes_and_failure_is_kept(self):
        record = commit_protocol(self.root, "protocol.json", ["source.py"], self.root / "c.json")
        (self.root / "raw.csv").write_text("v\n0.005\n")
        self.assertTrue(audit_v2(self.root, record, self.result(0.005))["passed"])
        self.assertFalse(audit_v2(self.root, record, self.result(0.5))["passed"])

    def test_uncommitted_protocol_is_rejected(self):
        (self.root / "protocol.json").write_text(json.dumps({**self.protocol, "x": 1}))
        with self.assertRaises(ValueError):
            commit_protocol(self.root, "protocol.json", ["source.py"], self.root / "c.json")

    def test_relaxed_threshold_in_record_is_detected(self):
        record = commit_protocol(self.root, "protocol.json", ["source.py"], self.root / "c.json")
        relaxed = json.loads(json.dumps(self.protocol))
        relaxed["criteria"][0]["threshold"] = 1.0
        record["protocol_sha256"] = hashlib.sha256(canonical(relaxed)).hexdigest()
        with self.assertRaises(ValueError):
            committed_protocol(self.root, record)

    def test_source_changed_after_commitment_is_rejected(self):
        record = commit_protocol(self.root, "protocol.json", ["source.py"], self.root / "c.json")
        (self.root / "source.py").write_text("x = 2\n")
        (self.root / "raw.csv").write_text("v\n0.005\n")
        with self.assertRaises(ValueError):
            audit_v2(self.root, record, self.result(0.005))

    def test_planned_artifact_existing_before_commitment_is_rejected(self):
        (self.root / "raw.csv").write_text("v\n0.005\n")
        with self.assertRaises(ValueError):
            commit_protocol(self.root, "protocol.json", ["source.py"], self.root / "c.json")

    def test_publication_on_remote_ref(self):
        remote = Path(self.tmp.name) / "remote.git"
        subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
        git(self.root, "remote", "add", "origin", str(remote))
        git(self.root, "push", "-q", "origin", "HEAD:refs/heads/main")
        git(self.root, "fetch", "-q", "origin")
        record = commit_protocol(self.root, "protocol.json", ["source.py"],
                                 self.root / "c1.json", remote_ref="origin/main",
                                 query_server=True)
        self.assertTrue(record["published_at_commitment"])
        (self.root / "raw.csv").write_text("v\n0.005\n")
        receipt = audit_v2(self.root, record, self.result(0.005), query_server=True,
                           require_published=True)
        self.assertTrue(receipt["published_verified_at_audit"] and receipt["passed"])
        (self.root / "other.txt").write_text("later\n")
        git(self.root, "add", "other.txt")
        git(self.root, "commit", "-qm", "unpushed")
        # A local tracking ref moved without pushing is caught by the server check.
        git(self.root, "update-ref", "refs/remotes/origin/main", "HEAD")
        (self.root / "raw.csv").unlink()
        with self.assertRaises(ValueError):
            commit_protocol(self.root, "protocol.json", ["source.py"], self.root / "c2.json",
                            remote_ref="origin/main", query_server=True)
        local = commit_protocol(self.root, "protocol.json", ["source.py"], self.root / "c3.json",
                                remote_ref="origin/main", query_server=False)
        self.assertTrue(local["published_at_commitment"])


    def test_planned_artifacts_are_mandatory(self):
        protocol = {k: v for k, v in self.protocol.items() if k != "planned_artifacts"}
        (self.root / "protocol.json").unlink()
        write_new_json(self.root / "protocol.json", protocol)
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "no plan")
        with self.assertRaises(ValueError):
            commit_protocol(self.root, "protocol.json", ["source.py"], self.root / "c.json")

    def test_later_relaxed_protocol_is_flagged_by_history(self):
        commit_protocol(self.root, "protocol.json", ["source.py"], self.root / "strict.json")
        relaxed = json.loads(json.dumps(self.protocol))
        relaxed["criteria"][0]["threshold"] = 1.0
        (self.root / "protocol.json").unlink()
        write_new_json(self.root / "protocol.json", relaxed)
        git(self.root, "add", "protocol.json")
        git(self.root, "commit", "-qm", "relaxed")
        record = commit_protocol(self.root, "protocol.json", ["source.py"], self.root / "late.json")
        self.assertEqual(len(history_conflicts(self.root, record, relaxed)), 1)
        (self.root / "raw.csv").write_text("v\n0.5\n")
        result = self.result(0.5)
        result["protocol_sha256"] = hashlib.sha256(canonical(relaxed)).hexdigest()
        receipt = audit_v2(self.root, record, result)
        self.assertTrue(receipt["criteria_passed"])
        self.assertFalse(receipt["passed"])

    def test_windows_separators_are_normalized(self):
        (self.root / "sub").mkdir()
        (self.root / "sub" / "s.py").write_text("y = 1\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "sub")
        record = commit_protocol(self.root, "protocol.json", ["sub\\s.py"], self.root / "c.json")
        self.assertIn("sub/s.py", record["git_blobs"])


class StatsTests(unittest.TestCase):
    def test_three_zone_rule_covers_every_case(self):
        cases = {(0.10, 0.25): "CONFIRMED", (0.31, 0.40): "FALSIFIED",
                 (0.25, 0.35): "INCONCLUSIVE", (0.03, 0.20): "INCONCLUSIVE",
                 (0.01, 0.03): "MODEL_CONTROL_FAIL"}
        for (low, high), verdict in cases.items():
            self.assertEqual(three_zone_decision(low, high, 0.3, 0.044)["verdict"], verdict)
        with self.assertRaises(ValueError):
            three_zone_decision(0.1, 0.2, 0.3, 0.4)

    def test_clopper_pearson_matches_scipy_exact(self):
        ours = clopper_pearson(28, 36)
        ref = binomtest(28, 36).proportion_ci(confidence_level=0.95, method="exact")
        np.testing.assert_allclose(ours, [ref.low, ref.high], rtol=1e-10)

    def test_wilks_classic_59(self):
        self.assertEqual(wilks_sample_size(0.95, 0.95), 59)
        self.assertIsNone(upper_tolerance_bound(np.arange(58.0))["bound"])
        self.assertEqual(upper_tolerance_bound(np.arange(59.0))["bound"], 58.0)

    def test_sample_size_matches_monte_carlo_power(self):
        n = sample_size_one_sided(effect=0.05, sigma=0.05, alpha=0.05, power=0.8)
        self.assertEqual(sample_size_one_sided(0.05, 0.05), 10)  # default alpha 0.025
        rng = np.random.default_rng(3)
        hits = 0
        for _ in range(4000):
            sample = rng.normal(0.25, 0.05, size=n)
            hits += one_sided_upper(sample, 0.30, 0.05)["reject_h0"]
        self.assertGreater(hits / 4000, 0.77)
        self.assertLess(one_sided_power(n - 1, 0.05, 0.05, 0.05), 0.8)

    def test_tost_and_holm(self):
        rng = np.random.default_rng(5)
        self.assertTrue(tost(rng.normal(0, 0.01, 40), -0.05, 0.05)["equivalent"])
        self.assertFalse(tost(rng.normal(0.2, 0.01, 40), -0.05, 0.05)["equivalent"])
        self.assertEqual(holm([0.01, 0.04, 0.03], 0.05), [True, False, False])
        self.assertEqual(holm([0.001, 0.02, 0.04], 0.05), [True, True, True])


class LimitsTests(unittest.TestCase):
    def test_photon_energy_and_shot_limit(self):
        self.assertAlmostEqual(photon_energy_j(1550e-9) / 1.2815e-19, 1, places=3)
        self.assertAlmostEqual(required_electrons(4), 4 * 16**2)
        self.assertGreater(required_electrons(4, 1, 100.0), required_electrons(4))

    def test_optical_energy_per_mac_amortizes_with_fan_in(self):
        common = dict(n_outputs=8, bits=4, wavelength_m=1550e-9, quantum_efficiency=0.8,
                      sample_rate_hz=1e9, optical_transmission=0.5, laser_wall_plug_efficiency=0.2,
                      modulator_energy_j=0, dac_energy_j=0, adc_energy_j=0)
        a = layer_budget(n_inputs=16, **common)["joules_per_mac"]
        b = layer_budget(n_inputs=64, **common)["joules_per_mac"]
        self.assertAlmostEqual(a / b, 4.0, places=10)

    def test_max_depth_boundary(self):
        e = detection_energy_j(4, 1550e-9, 1.0, 1e9)["optical_energy_j"]
        power = 1e9 * 8 * e * 10 ** ((3 + 10 * 0.5) / 10)
        self.assertEqual(max_depth(power, 1e9, 8, e, 3.0, 0.5), 10)
        self.assertIsNone(max_depth(power / 1e6, 1e9, 8, e, 3.0, 0.5))


class MeshTests(unittest.TestCase):
    def test_clements_reconstruction_and_depth(self):
        for n in range(2, 10):
            u = random_unitary(n, n)
            d = clements_decompose(u)
            self.assertLess(d["reconstruction_error"], 1e-12)
            self.assertEqual(d["n_mzis"], n * (n - 1) // 2)
            self.assertLessEqual(d["depth"], n)

    def test_triangular_v1_is_deeper_than_rectangular(self):
        n = 8
        u = random_unitary(n, 11)
        tri = decompose_unitary(u)
        last = [0] * n
        for op in tri["operations"]:
            if op["kind"] == "two_mode_unitary":
                a, b = op["ports"]
                last[a] = last[b] = max(last[a], last[b]) + 1
        self.assertGreater(max(last), clements_decompose(u)["depth"])
        self.assertLess(np.linalg.norm(reconstruct(tri) - u), 1e-11)

    def test_passive_contraction_and_gain_rejection(self):
        target = random_unitary(4, 5) @ np.diag([0.9, 0.6, 0.3, 0.0]) @ random_unitary(4, 6)
        self.assertLess(compile_passive_clements(target)["reconstruction_error"], 1e-12)
        with self.assertRaises(ValueError):
            compile_passive_clements(1.01 * np.eye(3))

    def test_permutation_and_identity(self):
        for m in (np.eye(5), np.eye(5)[[4, 3, 2, 1, 0]]):
            self.assertLess(clements_decompose(m.astype(complex))["reconstruction_error"], 1e-12)

    def test_splitter_errors_reduce_fidelity_and_correlation_widens_tail(self):
        u = random_unitary(6, 2)
        self.assertAlmostEqual(fidelity(u, clements_reconstruct(clements_decompose(u))), 1, places=12)
        independent = splitter_error_study(u, 0.03, 300, 1, 0.0)
        shared = splitter_error_study(u, 0.03, 300, 1, 0.8)
        self.assertLess(independent["mean_fidelity"], 1)
        self.assertLess(shared["p05_fidelity"], independent["p05_fidelity"])


def evidence(root, kind, path, **extra):
    item = {"kind": kind, "path": path, "sha256": sha256_file(root / path),
            "produced_by": "fixture", "how": "unit test"}
    item.update(extra)
    return item


class LedgerAndBlindTests(unittest.TestCase):
    def test_ledger_rejects_simulation_for_physical_claim(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "sim.json").write_text("{}")
            (root / "meas.csv").write_text("a\n1\n")
            claim = {"id": "C1", "statement": "Loss <= 0.3 dB/cm", "scope": "physical_component",
                     "status": "PASS", "falsifier": "CI lower bound above 0.3",
                     "evidence": [evidence(root, "simulation", "sim.json")]}
            ledger = {"schema": 1, "claims": [claim]}
            self.assertTrue(validate(ledger, root))
            claim["evidence"].append(evidence(root, "measurement", "meas.csv"))
            self.assertTrue(validate(ledger, root))  # instrument and operator missing
            claim["evidence"][1].update({"instrument": "OSA", "operator": "lab"})
            self.assertEqual(validate(ledger, root), [])
            (root / "meas.csv").write_text("a\n2\n")
            self.assertTrue(validate(ledger, root))
            self.assertIn("C1", render_table(ledger))

    def test_project_agents_cannot_replicate(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "r.json").write_text("{}")
            item = evidence(root, "external_replication", "r.json",
                            independent_team="Codex agent", public_record="https://example.invalid/r")
            claim = {"id": "C2", "statement": "Replicated", "scope": "external_replication",
                     "status": "PASS", "falsifier": "Independent rerun disagrees", "evidence": [item]}
            ledger = {"schema": 1, "project_agents": ["Claude", "Codex", "JEV"], "claims": [claim]}
            self.assertTrue(validate(ledger, root))
            item["independent_team"] = "University lab X"
            self.assertEqual(validate(ledger, root), [])

    def test_dependencies_must_pass_and_cycles_fail(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "t.txt").write_text("ok\n")
            ev = [evidence(root, "software_test", "t.txt")]
            ledger = {"schema": 1, "claims": [
                {"id": "A", "statement": "s", "scope": "software", "status": "OPEN",
                 "falsifier": "f", "evidence": ev},
                {"id": "B", "statement": "s", "scope": "software", "status": "PASS",
                 "falsifier": "f", "evidence": ev, "depends_on": ["A"]}]}
            self.assertTrue(any("dependency" in p for p in validate(ledger, root)))
            ledger["claims"][0].update({"status": "PASS", "depends_on": ["B"]})
            self.assertTrue(any("cycle" in p for p in validate(ledger, root)))

    def test_every_task_scope_is_known_to_the_ledger(self):
        folder = Path(__file__).resolve().parent
        for name in ("tasks.json", "tasks_v2.json"):
            for task in json.loads((folder / name).read_text(encoding="utf-8"))["tasks"]:
                self.assertIn(task["scope"], REQUIRED_KIND, task["id"])

    def test_blinding_is_reversible_and_rounded(self):
        rows = []
        for chip, slope in enumerate((0.11, 0.12, 0.10)):
            for cm in (1, 2, 3, 4):
                rows.append({"chip_id": str(chip), "guide_id": "g", "length_m": cm / 100,
                             "wavelength_m": 1550e-9, "polarization": "x", "input_power_w": 1e-3,
                             "output_power_w": 1e-3 * 10 ** (-(0.5 + slope * cm + 0.003 * (-1) ** cm) / 10),
                             "sigma_loss_db": 0.01})
        truth = fit_cutback(rows)
        with tempfile.TemporaryDirectory() as name:
            commitment = create_secret(Path(name) / "secret.json", 2.0)
            secret = json.loads((Path(name) / "secret.json").read_text())
            self.assertEqual(sha256_file(Path(name) / "secret.json"), commitment["commitment_sha256"])
        offset = secret["offset_db_per_cm"]
        blinded_rows = blind_rows(rows, offset, 6)
        for row in blinded_rows:
            mantissa = format(float(row["output_power_w"]), ".5e")
            self.assertEqual(float(mantissa), float(row["output_power_w"]))
        blinded = fit_cutback(blinded_rows)
        self.assertNotAlmostEqual(blinded["mean_loss_db_per_cm"], truth["mean_loss_db_per_cm"], places=6)
        restored = unblind_report(blinded, offset)
        # Six significant digits perturb each power by at most 5e-6 relative (2.2e-5 dB).
        self.assertAlmostEqual(restored["mean_loss_db_per_cm"], truth["mean_loss_db_per_cm"], delta=1e-4)
        np.testing.assert_allclose(restored["ci95"], truth["ci95"], atol=1e-4)
        with self.assertRaises(ValueError):
            blind_rows(rows, offset, 1)


class LearningV2Tests(unittest.TestCase):
    def test_signed_models_gradient(self):
        rng = np.random.default_rng(4)
        x, y = rng.normal(size=(9, 3)), np.arange(9) % 3
        for model in ("unitary_mzm_signed", "real_mzm_signed"):
            p = rng.normal(scale=0.3, size=18)
            _, g = objective_v2(p, x, y, model, 1.7, 0.2)
            num = np.array([(objective_v2(p + 1e-6 * e, x, y, model, 1.7, 0.2)[0] -
                             objective_v2(p - 1e-6 * e, x, y, model, 1.7, 0.2)[0]) / 2e-6
                            for e in np.eye(18)])
            np.testing.assert_allclose(g, num, atol=3e-7, rtol=3e-5)

    def test_signed_model_converges_on_synthetic_task(self):
        rng = np.random.default_rng(8)
        centers = rng.normal(scale=1.5, size=(3, 3))
        y = np.repeat(np.arange(3), 40)
        x = centers[y] + 0.4 * rng.normal(size=(120, 3))
        with tempfile.TemporaryDirectory() as name:
            np.savez(Path(name) / "tr.npz", X=x[::2], y=y[::2])
            np.savez(Path(name) / "va.npz", X=x[1::2], y=y[1::2])
            record = fit_candidate_v2(Path(name) / "tr.npz", Path(name) / "va.npz",
                                      "unitary_mzm_signed", [1, 2, 3], 1000, 1.0, 0.0)
        self.assertTrue(record["selected"]["converged"])
        start = 0.5 * np.random.default_rng(record["selected"]["seed"]).standard_normal(18)
        initial, _ = objective_v2(start, x[::2], y[::2], "unitary_mzm_signed")
        self.assertLess(record["selected"]["training_loss"], 0.8 * initial)
        # Sanity check against chance (1/3). A first draft used 0.6 and observed
        # exactly 0.6; the chance criterion replaced it and is recorded in the guide.
        self.assertGreater(record["validation_accuracy"], 1 / 3)


if __name__ == "__main__":
    unittest.main()
```

### Archivo: agentkit/tasks_v2.json

```json file=agentkit/tasks_v2.json
{
  "schema": 1,
  "review_date": "2026-10-12",
  "extends": "agentkit/tasks.json",
  "note": "Guide v2 additions. Planning registry only; it closes nothing. T01-T22 keep their v1 entries unchanged.",
  "tasks": [
    {
      "id": "T23",
      "title": "Integrity infrastructure: git-anchored preregistration, blind analysis, claims ledger",
      "scope": "software",
      "requires": [],
      "status": "OPEN",
      "baseline_only": true
    },
    {
      "id": "T24",
      "title": "Fundamental-limit kill test: sourced energy and precision budget per MAC",
      "scope": "numerical_model",
      "requires": [],
      "status": "OPEN",
      "baseline_only": true
    },
    {
      "id": "T25",
      "title": "3D versus planar mesh scaling: depth, crossings, loss and error accumulation",
      "scope": "numerical_model",
      "requires": [],
      "status": "OPEN",
      "baseline_only": true
    },
    {
      "id": "T26",
      "title": "State-of-the-art benchmark and threshold revision for H1",
      "scope": "novelty",
      "requires": [
        "T19"
      ],
      "status": "OPEN",
      "baseline_only": true
    },
    {
      "id": "T27",
      "title": "Hardware-in-the-loop and physics-aware training plan with measured error models",
      "scope": "numerical_model",
      "requires": [
        "T12"
      ],
      "status": "OPEN",
      "baseline_only": true
    },
    {
      "id": "T28",
      "title": "Fabrication access and collaboration dossier",
      "scope": "fabricable_design",
      "requires": [
        "T11"
      ],
      "status": "OPEN",
      "baseline_only": true
    },
    {
      "id": "T29",
      "title": "Intellectual property and disclosure decision before new public results",
      "scope": "decision",
      "requires": [],
      "status": "OPEN",
      "baseline_only": true
    },
    {
      "id": "T30",
      "title": "Adversarial red-team review and pre-mortem of the central claim",
      "scope": "review",
      "requires": [
        "T20"
      ],
      "status": "OPEN",
      "baseline_only": true
    }
  ]
}
```

### Archivo: agentkit/claims_example.json

```json file=agentkit/claims_example.json
{
  "schema": 1,
  "project_agents": [
    "Claude",
    "Codex",
    "JEV"
  ],
  "claims": [
    {
      "id": "C-KIT-MZI",
      "scope": "software",
      "status": "OPEN",
      "statement": "Kit v2 rectangular MZI synthesis reconstructs random unitaries for N = 2 to 9 with spectral error below 1e-12.",
      "falsifier": "Any N from 2 to 9 with reconstruction error of at least 1e-12 in agentkit.test_v2.MeshTests.",
      "evidence": [],
      "limitations": "Ideal transfer algebra only; no geometry, loss or fabrication error.",
      "next_action": "Run agentkit.test_v2 in the project environment, keep the run log and attach it as software_test evidence."
    },
    {
      "id": "C-T19-a",
      "scope": "novelty",
      "status": "WITHDRAWN",
      "statement": "A multilayer 3D network written by fs laser in glass is new.",
      "falsifier": "A published prior fs-written multilayer 3D photonic network in glass.",
      "withdrawal_reason": "Cao et al., Nat. Commun. 17, 5476 (2026), DOI 10.1038/s41467-026-72316-9: 8-layer fs-written network in borosilicate glass.",
      "evidence": [],
      "references": [
        "Docs/NOVEDAD-ESTADO-20261011.md (audit branch)"
      ],
      "next_action": "Evaluate the narrower variant: silica, multi-face writing with measured registration (T09, T19)."
    },
    {
      "id": "C-T20-H1",
      "scope": "physical_component",
      "status": "OPEN",
      "statement": "A trench waveguide (core n = 1.444, trench delta n = -0.005, t = 12 um, a = 6 um), written by fs laser in silica, has a total propagation loss <= 0.3 dB/cm at 1550 nm.",
      "falsifier": "Lower bound of the 95% CI above 0.3 dB/cm (registered F1). Separately, an upper bound below the leakage recomputed for the measured profile signals a model or measurement error.",
      "evidence": [],
      "references": [
        "Docs/CONTRIBUCION-CENTRAL-T20.md (audit branch)"
      ],
      "limitations": "Mode, excitation and the single decision rule are not yet declared; the 0.3 dB/cm threshold is far above the 0.07 dB/cm reported at 1550 nm in fused silica (Tan et al., Opt. Lett. 47, 4766, 2022).",
      "next_action": "Dated amendment before measuring (NOVEDAD-ESTADO section 5, points i to v), then T26 threshold review."
    },
    {
      "id": "C-T11-C3",
      "scope": "numerical_model",
      "status": "PARTIAL",
      "statement": "8-bit recalibration meets C3 in the preregistered realization and in 28 of 36 realizations (78 %, exact 95% CI 0.61 to 0.90).",
      "falsifier": "Recomputation from the retained realizations disagrees, or C2 remains failed.",
      "evidence": [],
      "references": [
        "experimentos/compilador_claude/RESULTADOS-COMPILADOR.md (audit branch)",
        "Docs/CORRECCION-ESTADOS-20261011.md (audit branch)"
      ],
      "limitations": "C2 fails (1.3e-2 to 1.7e-2 against 5e-3); delta is a model value, not measured (T14).",
      "next_action": "Keep the C2 failure visible; measure delta (T14) before any yield claim."
    },
    {
      "id": "C-T12-F3b",
      "scope": "numerical_neural_model",
      "status": "FAIL",
      "statement": "Network F3-b meets H-F1 and H-F2.",
      "falsifier": "Registered criteria H-F1 or H-F2 not met.",
      "evidence": [],
      "references": [
        "Docs/T12-CIERRE-Y-BLOQUEADOS-20261011.md (audit branch)"
      ],
      "limitations": "Majority-class baseline is 52.5 % on the imbalanced test set; the electronic reference did not converge.",
      "next_action": "New registered experiment with converged, gain-matched baselines and balanced metrics (T12, T16)."
    },
    {
      "id": "C-T24-energy",
      "scope": "numerical_model",
      "status": "OPEN",
      "statement": "With sourced parameters, the full optoelectronic layer needs less energy per MAC than a cited digital reference at equal output precision.",
      "falsifier": "agentkit.limits budget with sourced inputs gives an advantage factor <= 1 for every plausible parameter set.",
      "evidence": [],
      "next_action": "Collect cited values for every parameter, then run the kill test before any energy claim."
    },
    {
      "id": "C-T21-repro",
      "scope": "external_replication",
      "status": "OPEN",
      "statement": "An independent team reproduces the central numerical result from the archived inputs.",
      "falsifier": "The independent rerun disagrees beyond the declared uncertainty.",
      "evidence": [],
      "next_action": "Prepare the reproduction package; agreement among AI agents does not count."
    }
  ]
}
```

### Archivo: agentkit/limits_example_params.json

```json file=agentkit/limits_example_params.json
{
  "provenance": {
    "n_inputs": "Design choice for the example; replace with the registered architecture.",
    "n_outputs": "Design choice for the example; replace with the registered architecture.",
    "bits": "Design choice for the example; replace with the registered architecture.",
    "wavelength_m": "Project operating wavelength assumption (1550 nm); not a measurement.",
    "quantum_efficiency": "MANUFACTURED placeholder to exercise the code; not a measurement, literature value or project estimate. Replace with a cited source.",
    "sample_rate_hz": "MANUFACTURED placeholder to exercise the code; not a measurement, literature value or project estimate. Replace with a cited source.",
    "optical_transmission": "MANUFACTURED placeholder to exercise the code; not a measurement, literature value or project estimate. Replace with a cited source.",
    "laser_wall_plug_efficiency": "MANUFACTURED placeholder to exercise the code; not a measurement, literature value or project estimate. Replace with a cited source.",
    "modulator_energy_j": "MANUFACTURED placeholder to exercise the code; not a measurement, literature value or project estimate. Replace with a cited source.",
    "dac_energy_j": "MANUFACTURED placeholder to exercise the code; not a measurement, literature value or project estimate. Replace with a cited source.",
    "adc_energy_j": "MANUFACTURED placeholder to exercise the code; not a measurement, literature value or project estimate. Replace with a cited source.",
    "static_power_w": "MANUFACTURED placeholder to exercise the code; not a measurement, literature value or project estimate. Replace with a cited source.",
    "current_noise_a_rthz": "MANUFACTURED placeholder to exercise the code; not a measurement, literature value or project estimate. Replace with a cited source."
  },
  "n_inputs": 64,
  "n_outputs": 64,
  "bits": 6,
  "wavelength_m": 1.55e-06,
  "quantum_efficiency": 0.8,
  "sample_rate_hz": 1000000000.0,
  "optical_transmission": 0.1,
  "laser_wall_plug_efficiency": 0.2,
  "modulator_energy_j": 1e-12,
  "dac_energy_j": 1e-12,
  "adc_energy_j": 1e-12,
  "static_power_w": 0.1,
  "current_noise_a_rthz": 1e-11
}
```

## 51. Prompt de arranque v2 para el agente ejecutor

Lee esta guía completa, incluidas las notas «Adición v2» y la Parte II, y las instrucciones actuales del repositorio, en especial `AGENTS.md`. Respeta la propiedad de rutas: no escribas en `tests/`, `scripts/` ni `src/silice/` sin revisión de Codex. Extrae el kit **fuera del repositorio**, con el nombre del archivo v2 en `--guide`, y verifica sus 32 pruebas v1 y 29 v2. Trabaja el repositorio en un worktree aislado en D: o E: y reconcilia `main` con la rama de auditoría preservando datos, negativos y archivos ajenos. Empieza por la Fase 0 de §48: registro de afirmaciones con el estado real de T01–T30, y prerregistro anclado en git de T24, T25 y T26, con el registro de compromiso también committeado. Ejecuta esas pruebas de descarte y registra la decisión de la afirmación central antes de nuevos datos confirmatorios. Después sigue T01–T22 según sus dependencias, con estas reglas: análisis ciego para toda medida, con custodio y resolución declarada; comparaciones con ganancia igualada y métricas equilibradas para toda red; y planificación de muestras con α coherente con la regla de decisión. No rebajes umbrales después de ver resultados, no cuentes el acuerdo entre agentes de IA como replicación y verifica cada referencia por DOI y, cuando una cifra dependa de la longitud de onda, en el texto. Código y manuscrito en inglés profesional; las explicaciones para Fran, en español. Prepara dossiers concretos para los bloqueos físicos y externos, y no contactes, publiques ni instales nada sin autorización vigente. Entrega la matriz T01–T30 generada desde el registro de afirmaciones, con enunciado, falsador, evidencia, limitaciones y próxima acción. No declares fabricación, medidas, novedad, independencia, impacto ni calidad Nobel sin evidencia.
