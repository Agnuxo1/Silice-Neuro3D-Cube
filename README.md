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
python -B scripts/audit_glass004.py --out resultados/codex/glass004_replicacion.json
```

Un resultado fallido sigue guardándose y produce salida no exitosa.
Los nombres nuevos evitan sobrescribir evidencia previa. CPU un hilo,
presupuesto por script40s. No iniciar Blender/GPU por reproducir este README.

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
