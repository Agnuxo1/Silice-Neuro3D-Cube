# Coste ADI sintético en N767, antes de nueva óptica

Ejecutar sólo después de L2 completo, secuencialmente. Reutilizar el
operador ADI histórico y su backend disperso validado, sin modificaciones.
N767, dominio nominal128µm, dn=0 y sigma=0, seno producto1/2,
dz=2mm/32000,100pasos. Referencia cerrada: producto de factores Cayley
de los dos autovalores discretos para el esquema Peaceman–Rachford.
No comparar este coste con un operador de física distinta ni usar el
modo liso para certificar T96.

Exigir error de campo frente a esa referencia <=1e-10, finitos,
tiempo total <=180s, guardas RAM>1,5GiB/disco>2GiB antes/después.
CPU un hilo, sin GPU ni instalaciones. Conservar factores y fuentes por
hash. Informar previsiones para32000/64000pasos, pero no garantizar
coste ni precisión para el potencial abrupto. No preparar geometría.
JEV fallback local identificado; preservar checkout principal y fallos.
