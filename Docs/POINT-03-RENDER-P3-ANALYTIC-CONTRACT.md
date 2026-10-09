# R3: campo P2 con coordenadas analíticas en el fragment shader

Prerregistro después de P1 publicada en ba16528. P1 completa permanece
negativa: nueve marcas smooth fallan por backend. Sus auditorías de
integridad aprueban y las 21 marcas de uniformes, atributos constantes,
suma y coordenadas analíticas pasan por backend. Este ensayo exige por
hash ambas auditorías, la totalidad de sus 30 marcas y todos los gates de
las siete familias correspondientes a la ruta utilizada. No se etiqueta
la calibración completa como aprobada ni se borra la ruta negativa.

Se registran ahora dos nuevos ensayos independientes OpenGL y Vulkan,
84 campos por backend. Conservan la referencia P2 original y sus doce
controles por hash, sin repetir controles; mismos nodos, perturbaciones,
casos, fases, tamaños64/128/256, geometría3D, máscaras y gates originales.
No se transforma ningún campo R1/R2/P1 para adoptarlo como resultado R3.

Cambio prospectivo: el fragment shader obtiene coordenadas baricéntricas
desde centros de píxel gl_FragCoord, con el triángulo fijo w=1:
l2=(y+0.7)/1.5, l1=(1-l2)/2+x/1.6, l0=1-l1-l2.
El polinomio P2 complejo, uniforms nodales, rotaciones y suma ADDITIVE no
cambian. El motor sigue rasterizando los triángulos3D; se prescinde del
atributo smooth para calcular estas coordenadas. No se generaliza la
fórmula a geometrías/perspectivas arbitrarias ni a propagación guiada.

Gates R1/R2 intactos: máximo complejo y L2 relativo<=5e-6, diferencia
absoluta de potencia<=5e-6, exterior<=1e-7, oscuro<=1e-10. Ninguna fase
alineada ni selección de píxeles por resultado; máscara2e-6 previa.
Auditor local recalcula84crudos y exige acuerdo de métricas1e-14 con el
motor NumPy1.26.4 frente a Windows2.2.6, con fuentes/perfil publicados.

Los nuevos controles CPU sólo prueban rechazo de prerrequisitos P1
incompletos/alterados y discrepancias de ruta; no leen T96 ni generan
campos ópticos. P0 de lectura/reloj/cierre sigue fijada por hash. Nuevas
fuentes/perfiles/carpetas exclusivas, publicar y verificar antes de GPU.
Conservar y publicar negativos, todos los84pares y crudos por backend,
compilación/batches/preparación/readback/arranque/supervisor; no elegir
mejores muestras. Un ensayo por backend no demuestra ventaja general.

FIFO vigente, RAM8GiB/floor6/VRAMtotal4/80C/RSS1.5/unhilo, espera1min,
child120/timer115/worker110, deadline13:45UTC. Guard Python directo, sin
instalaciones/compras/PYTHONPATH/cierre ajeno ni extensión de límites.
Fuentes congeladas durante ambos ensayos. F1 permanece desconocida y
sin productos recuperados; S16 bloqueada. Tarea1 sigue abierta. R3 es
representación manufacturada auxiliar, no red, RT, energía o física.
JEV remoto bloqueado; fallback local identificado.
