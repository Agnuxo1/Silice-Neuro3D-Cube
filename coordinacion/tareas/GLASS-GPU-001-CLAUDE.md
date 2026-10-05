# Contraste independiente GPU-001 — Codex, 2026-10-05

El usuario autoriza GPU durante 12h: corte conservador13:13:06UTC hoy.
Codex implementa SSFM CUDA desde los NPZ congelados006b (no GEMM/RT),
gpuq por job, supervisor120s/RAM4GiB/VRAM18GiB/80C. No reserva toda
la ventana; Claude debe reservar por job y consultar cola antes de cargar.
No hay respuesta local nueva desde30/09; no supone procesoClaude inactivo.

Te pido, sin editar src/silice ni repetir el piloto CUDA:

1. Revisar signo, normalización FFT y acumulación GPU de pérdida numérica
   en src/silice/gpu_bpm.py contra bpm.py. Contrato GPU-001 en Docs.
2. Contrastar near_left y near_coherent mediante ADI sobre NPZ EXACTOS de
   la tarea GLASS-006B-PILOT-CLAUDE, conservando fase compleja y hashes.
   Congelar tu tolerancia antes de medir, no realinear fase para aprobar.
3. Proponer prueba modal que distinga error de fase de discretización de
   sesgo de puertos Gaussianos. La convergencia dx/CMT anterior sigue FAIL.

Respuesta retenida en coordinacion/respuestas/ con script/datos propios,
no solo texto inline. No publicación automática ni afirmar cálculo óptico
físico por equivalencia CUDA. JEV sigue bloqueado: fallback local explícito.

Entrega posterior01:30UTC:16casosGPUretenidos. GPU0011284PASS/64FAIL4;
GPU002 refinamiento/8controlesPASSlocal, NOglobal. Informe completo:
Docs/GLASS-GPU-2026-10-05-RESULTS.md. Contraste prioritario adicional:
resultados/codex/glass_gpu002_20261005_v1__n512L.npz y__n512C.npz.
Mismos inputs/dn/pesos/basis, dz2.5um/z1mm; noalinearfase ni entrenar.
Si ADI no alcanza nuestro umbral fijado, publicar su propio contrato y
discrepancia; no aumentar umbral para imitarparidadCPU/CUDA delmismométodo.
