# P5B: controles del detector/entrada/amortiguador en mallas gruesas

Registrar antes de medir. Mallas P5A h0,546875 y0,4375 ya controlesgeoPASS;
no propagaciones Gaussian en esasmallas. Reutilizar algoritmosP4F/P4G
sin cambiar límites/cálculos; adaptación exclusiva de ruta de entrada
y claves de informe geométrico(no recuperación cuando nohubo fallo).
Guardar fuente generada antes de ejecutar. No reutilizar matrices
del prototipo como si validasen otra malla.

Exigir en cada detector curvas/cuerdas fuera deR6,quadMnorm<=1e-10,
momentos lineales/polinomios/PSD,proyecciónGaussianq12/16<=1e-9.
AmortiguadorporpartesD8/12Mnorm<=1e-6m^-1,integralesanalíticas<=1e-10.
CPUunhilo,1800sdetector/600samortiguador,RAM>2GiB/disco>2GiB.
Todosresultados/fallos se conservan;ningún cambio de tamaño/tolerancia
después. No propagar ni afirmar convergencia, nohardware/Maxwell.
Estudiosespacialesopticos requierenotroprotocolo antesdecampos.
JEVlocal/bloqueoheredado.
