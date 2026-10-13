# Neuro-cube environment (2026-10-13)

- Blender 4.5.14 LTS, portable, at `D:/TOOLS/Blender/blender-4.5.14-windows-x64/` (already present; see `Docs/BLENDER-PLATFORMS-ASSESSMENT-20261008.md`). Bundled Python 3.11.15 and NumPy 1.26.4.
- SciPy was missing from Blender's Python. Installed **only on D:**, for this task, on 2026-10-13:
  `blender's python -m pip install --no-deps --only-binary=:all: --target D:/TOOLS/blender_pylibs_neurocubo scipy==1.13.1`
  (pip cache in `D:/TOOLS/pip_cache`). `nc_blender.py` adds that folder to `sys.path`. Nothing was installed on C:.
- Outside Blender: venv `D:/SiliceAgentkit/.venv-closure` (Python 3.13.7, NumPy 2.2.6, SciPy 1.15.1, scikit-learn 1.6.1, Matplotlib 3.10.0).
- CPU work runs on one thread: `blender -b ... -t 1` with `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1` (set by `run_pipeline.sh`).
- Rendering (presentation only) goes through the shared GPU queue `D:/PROJECTS/.cognition/gpu_queue/gpuq.py`.
- Large files stay outside the repository: Blender files, the per-iteration trajectories of every start and the sealed test labels live in `D:/PROJECTS/.cognition/neurocubo/`.

## Files

| File | Role |
|---|---|
| `neurocubo_core.py` | Physics and model without bpy: kappa(g), geometry -> transfer, meshes (agentkit.mzi), network, exact gradients, training start, errors, DAC |
| `nc_blender.py` | bpy: build objects with SI custom properties, export geometry from objects, write phases and keyframes |
| `build_cube.py` | Build nominal geometries; Blender round-trip reconstruction check |
| `custodian.py` | Partitions, preprocessing fitted on train, sealed test labels, one-time reveal |
| `train_in_blender.py` | Training loop inside Blender (phases in objects, keyframe each iteration) |
| `references.py` | Majority, logistic regression, MLP, gain-matched real network |
| `blender_eval.py` | Frozen-model outputs inside Blender (phases read from objects) |
| `benchmark.py` | One-shot benchmark, equivalence, robustness, reveal, metrics, criteria |
| `make_figures.py`, `render_scene.py` | 300-dpi figures; EEVEE stills and video (presentation) |
| `run_pipeline.sh` | Orchestration (`real` or synthetic `dry`) |
| `PROTOCOL-NEUROCUBO.json` | Preregistration |
