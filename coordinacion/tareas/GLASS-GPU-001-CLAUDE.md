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
