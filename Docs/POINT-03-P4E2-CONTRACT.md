# P4E2: extensión temporal del control de coste, sin rehacer niveles previos

P4E controles parcialmente negativos:campo full/half1,77899e-5>1e-5,
pasividad aprobada y previsión8192pasos1538s viable. Conservar FAIL.

Registrar fuente antes de extender. Reutilizar matrices/entrada/campos
P4E por hashes; no repetir100/200pasos. Misma duración corta24,414µm,
inicialseno, sin GaussianT96 ni potencia núcleo. Nuevos400/800/1600pasos,
dt=2mm/32768,/65536,/131072. Padé6 sin editar. CPUunhilo,900s,
RAM>3GiB/disco>2GiB,sinGPU. Guardar todos los resultados/pasividades.

Hipótesis primaria:la última diferencia de campoM (1600vs800) <=1e-6;
las tres diferencias(400vs200,800vs400,1600vs800) decrecen. No exigir
orden6 antes de verificar régimen; informar todos los órdenes calculables
y coste extrapolado. Ningún cambio retrospectivo al límite P4E1e-5.
Normas físicas positivas<=1+1e-9. Si falla,conservar resultado.

Este controlcorto no prueba error exacto ni precisión a2mm ni valida
convergenciaespacial. El caso real exige controltemporal/detector propio
registrado antes de datos y auditoría. JEVlocal/bloqueo heredado.
