# P5A: preparación geométrica de la futura serie espacial FEM

Registrar antes de generar, sin datos de potenciafinalGaussian aún.
Mismo caso T96/domain±64µm. Serie nominal de tamaño local en r15µm:
h=0,546875/0,4375/0,35/0,28µm,ratio1,25. Fondo4h ytransición15..25µm
idéntica,criterios de materiales yCAD idénticos. Se elige por continuar
refinamiento desde prototipo0,35 antes de su resultado, no por potencias.
Reutilizar malla0,35 P4C sin regenerarla. Preparar sólo0,546875 y0,4375
ahora;0,28 reservado comoholdout, NOgenerarlo aún.

Reutilizar algoritmoP4C por AST sin editarfuentevieja. Cambios permitidos:
expresión de tamaño,conversión de contadoresNumPy aint paraJSON y
tolerancia declarada de área geométrica cuadrática<=5e-5rel en las mallas
gruesas. Esta tolerancia distinta está registrada antes de geometría;
no se aplica retrospectivamente aP4C. CAD sigue<=1e-8,dominio<=1e-10,
Jacobianno plegado/simetría/constante/masa/materiales según P4C.
Guardar fuente generada antes de llamarGmsh ymatrices/mesh/reportes.

No son ensayos de propagación ni cambio deobservable. Esas nuevas
mallas requierendetector,proyección,amortiguaciónexacta ycontrol temporal
propios antes de ningún estudio espacial. El protocolo de potencia/predicción
se registrará aparte antes de campos. Si falla algúncontrol,conservarFAIL.
CPUunhilo,600s por malla,RAM>2GiB/disco>2GiB,noGPU. JEVlocal/bloqueo.
