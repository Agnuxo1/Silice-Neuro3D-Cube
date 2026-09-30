# GLASS-007 — trazos discretos y huecos, contrato prospectivo

2026-09-30 10:02UTC. Decisión local, JEVsecurityblocked sin reintentar.
Claude trabaja solver radial005: este ensayo no lo duplica ni edita.
Pregunta: ¿la camisa ideal continua oculta pérdidas al escribir trazos
separados? No se asegura una mejora ni una receta real de fabricación.

SolverBPM003 inmutable. lambda1550nm/n0=1.444/a6um/camisa6um/cintura6um,
z2mm. Nominaldominio128um/256²/dx0.5um/dz2.5um/800pasos; máximo40s total.
Se incorpora crítica005 deClaude ANTES de medir: usar paso más fino y
comparar800→1000pasos (dz2.5→2um), solver003 permaneceintacto.
Profildn=-0.003 continuo frente unión de discos de radio1.25um con centros
radiales7.25/9/10.75um y16/32/64trazos por corona. Coronas alternadas
desfasadas pi/N. Cada disco es una sección hipotética de un trazo recto
paralelo a z; NO modelo de pulsos/daño/índice medido de la máquina.
Los discos tangentes no modifican el núcleo r<a ni exterior r>a+t.
Unión, no suma de dn cuando se solapan. Control16/32/64 igual dn pico;
otro control32 con integral de |dn| igual a la camisa continua. No confundir
misma fuerza material con misma área de modificación. Rechazar si ese
reescalado requiere |dn|>0.01; no subir límite para hacerlo pasar.
Igual integral de índice NO significa igual energía/dosis de fabricación.

Adversario32: omitir centros dentro de una cuña de30grados alrededor +x.
No exigir a priori que el hueco empeore: patrones de interferencia pueden
ser no monótonos. Se reportan todas las diferencias.

Observables potencia_nucleo/entrada y campos; frontera removida aparte;
integral|dn|, área modificada, pico, counttrazos, trackslist/sha.
Gates separados antesmedir: balance<1e-10; perfil núcleo/exteriorintactos;
control igualintegralerror<1e-12relativo; refinamiento de32discos
dx0.5→2/3um (256→192 puntos a128um) y dominio128→170.666um
(dx2/3um,192→256puntos); cada comparaciónabs<0.005 yrel<10%.
También comparar paso800→1000 para32trazos y continuo con mismosumbrales.
Comparar dominio a igualdx: no mezclar cambios sin etiquetar.
No convergencia combinada total/modeigen ni red neuronal completa.

Todosfallosretenidos. No renormalizar traspropagación ni interpretar balance
como guiado. Pendiente solver2D independiente para perfil no radial;
radial005 solo puede contrastar continuo. No GPU/Blender/instalar/publicar.
