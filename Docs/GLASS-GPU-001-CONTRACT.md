# GLASS-GPU-001 — contraste prospectivo CUDA, 2026-10-05

Pregunta: ¿el mismo SSFM paraxial puede trasladarse a CUDA sin alterar
los campos complejos conservados de GLASS-006b?
Registro local GLASS-GPU-001-v1, contrato y código congelados antes de
ejecutar. No registro externo/IPFS ni artículo/publicación automática.
Es validación de backend sobre un modelo existente, no nueva física.

Casos inmutables: near_left, near_right, near_coherent de pilot_v1 y
near_left de refinement_v2. Leer los NPZ y comprobar SHA con sus JSON.
N=256/320, 400 pasos, z=1mm, lambda=1550nm, n0=1.444; sin generar una
nueva geometría, sin ajustar fase ni renormalizar resultados.
Dos precisiones CUDA: complex128 (referencia) y complex64 (aproximación
explícita). Operadores construidos NumPy CPU; transferencia explícita;
FFT/fase/amortiguador y acumulación de potencia removida en CUDA.
Comparación final CPU contra campo completo, puertos gaussianos, áreas
de detector y presupuesto numérico, con artefacto NPZ de salida nuevo.

Gate primario ||GPU-CPU||2/||CPU||2 <=1e-10 (128), <=1e-4 (64).
Puertos y potencias: error absoluto <=1e-10/1e-4 respectivamente.
Balance numérico <=1e-10/1e-4. Linealidad L+iR: <=1e-10/1e-4.
Fracaso de cualquier gate queda retenido, no se ajustan umbrales.
La equivalencia no repara los gates previos dx/CMT fallidos.

Costes descriptivos: una pasada fría por caso/dtype y 3 repeticiones
calientes del near_left nominal por dtype. Misma configuración CPU:
un calentamiento y 3 repeticiones, un hilo. Publicar todas las muestras,
preparación/H2D, propagación sincronizada (incluye budget), D2H y disco
separados; no afirmar ventaja general, RT o energía desde este piloto.
Semilla 7; determinista, 3 repeticiones son de tiempo, no evidencia
estadística independiente de exactitud física.

Ventana autorizada: 2026-10-05 01:13:06 a 13:13:06 UTC (12h).
gpuq exclusivo por job. Supervisor fail-closed: RAM>=4GiB durante hijo
y >=4GiB DESPUÉS de reservar 1GiB antes; total VRAM<=18GiB; T<=80C;
120s máximo por hijo y deadline absoluto. Telemetría no disponible:
abortar, no fallback inseguro. Solo matar hijo propio. Sin instalaciones.
RTX3090; torch instalado2.6.0+cu124, verificar entorno en informe.
Guardar fallos/hashes y liberar turno. JEV bloqueado, fallback local.
Claude: contraste ADI independiente pendiente; no atribuir aval.

Limitaciones: paraxial escalar, malla pequeña, amortiguador no certificado
para toda radiación, puertos Gaussianos no modos, sin polarización/reflejos,
sin fabricar cristal, sin validación Maxwell ni red neuronal completa.
