# Silice-Neuro3D-Cube

Investigación de una red óptica tridimensional que pueda escribirse por láser
en vidrio de sílice. Buscamos conectar geometría y propiedades materiales con
cálculos verificables, primero en simulación y después en un diseño fabricable.

Estado: **investigación inicial CPU**, sin dispositivo fabricado, red completa,
GPU propio de esta línea ni ventaja de velocidad/eficiencia demostrada.
No es una representación artística ni una réplica de Project Silica:
el [proyecto de Microsoft](https://www.microsoft.com/en-us/research/project/project-silica/)
demuestra almacenamiento volumétrico, no nuestro procesador.

## Experimentos

- `src/silice/bpm.py`: propagación de campo por un perfil de índice, modelo
  escalar paraxial CPU con difracción y fase. Núcleo intacto/camisa finita.
- `experimentos/glass_min1/`: contribución Claude preservada, cuatro canales
  por modos acoplados y objetivo DFT4. Backend matemático, no geometría 3D.
- `scripts/audit_glass004.py`: auditoría Codex independiente del modelo Claude.
- `resultados/codex/`: informes JSON con parámetros/hashes/gates y fallos.

Primer hito: 13 tests CPU, auditoría del modelo CMT de Claude y 28 casos
BPM/refinamientos. [V1 y auditoría](Docs/GLASS-003-004-PRIMER-HITO.md),
[V2](Docs/GLASS-003-V2-RESULTS.md). V1 y gate general V2 fallan convergencia:
son resultados científicos retenidos, no una red ya validada.
Los refinamientos separados del perfil -0.003 pasan; falta segundo solver.

No confundir un anillo ideal de índice reducido con una receta medida de
escritura. El modelo actual omite polarización, reflexión, curvas y trazos
discretos. Una malla pasiva es lineal en campo: detectar intensidad y aplicar
activaciones/electrónica requiere un alcance adicional explícito.

## Reproducir

Python y NumPy ya disponibles en el equipo. Auditoría peer necesita además
SciPy existente; ningún script instala dependencias ni inicializa CUDA.

```powershell
cd D:\PROJECTS\Silice-Neuro3D-Cube
python -B scripts/check.py
python -B scripts/run_glass003.py --out resultados/codex/glass003_replicacion.json
python -B scripts/run_glass003_v2.py --out resultados/codex/glass003_v2_replicacion.json
python -B scripts/audit_glass004.py --out resultados/codex/glass004_replicacion.json
```

Un resultado fallido sigue guardándose y produce salida no exitosa.
Los nombres nuevos evitan sobrescribir evidencia previa. CPU un hilo,
presupuesto por script40s. No iniciar Blender/GPU por reproducir este README.
Los módulos y artefactos de Claude y los tableros compartidos siguen locales
sin versionar: la auditoría peer requiere esa carpeta, no basta clonar los
archivos propios. Su incorporación se revisará conjuntamente antes de publicar.

## Método y colaboración

Leer [contrato](Docs/RESEARCH-CONTRACT.md), [checkpoint](coordinacion/CHECKPOINT.md)
y [tablón](coordinacion/TABLON.md). Codex y Claude tienen tareas independientes
y revisan evidencia mutuamente; JEV no cuenta como consultado sin provenance=jev.
Su canal sigue bloqueado por seguridad: fallback local explícito.
El proyecto anterior `D:\PROJECTS\9_NEBULA_NEW` queda intacto.

Próximos pasos: convergencia/fronteras y segundo solver, camisa discreta,
acoplador físico vs modos acoplados, tolerancias correlacionadas/calibración,
red 3D pequeña y posterior fabricación. La publicación remota es un hito
separado; no hay todavía un repositorio GitHub conectado a esta línea.
