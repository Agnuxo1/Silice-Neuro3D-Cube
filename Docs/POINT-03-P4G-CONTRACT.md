# P4G: integración exacta por partes del amortiguador

Registrar fuente antes de ensamblar. No propagarGaussianT96. El perfil
sigma físico sigueidéntico al de todosloscasos, pero max(absx,absy) cambia
de polinomio en diagonales/umbral; integrar sobre triángulos sin cortar
esa función puede añadir error de muestreo. No cambiarperfilparaaprobar.

Regiones4:±x>=|y| y±x>=51,2µm;±y>=|x| y±y>=51,2µm.
Recortar cada triángulo con semiplanos y triangular polígonos; en cada
subtriángulo sigma es polinomio grado4 y basesP2 grado2. Fuera de estas
regiones sigma=0. Verificar elementos activos afines, sin curvas materiales
a r>51,2µm. Gauss8/12 exacto para grado8. Todoslos pesospositivos.

Controles:simetríaD<=1e-12rel,semidefiniciónpositiva por12vectoresaleatorios,
campo constante y6camposlinealescomplexos(seed967) contra integrales
analíticas delcuadrado,error<=1e-10rel. Referencia constante
8*S*d*(a/5+d/6),a=51,2µm,d=12,8µm. Momento x²:
(16/3)*S*d*(a³/5+3a²d/6+3ad²/7+d³/8).
ComparaciónD8/D12 normalizada por cota inferiorM deP4F<=1e-6m^-1;
informar también diferencia respectoDnocortadoP4E,sin revocar controles.

GuardarD8/D12,matrices/hash/informe. CPUunhilo,600s,RAM>2GiB/disco>2GiB.
No cierre espacial/temporal, no absorciónmaterialmedida. JEVlocal/bloqueo.
