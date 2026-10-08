# P4C: geometría/ensamblaje2D conforme a interfaces, antes de propagación

Registrar fuente/contrato antes de generar malla. No calcular aún potencia
T96 ni adoptar cierre. P4B1D respaldó jerarquía alineada; P4A/P3 conservan
sus resultados negativos. Nueva implementación geométrica2D se valida.

Entorno separado D:/PROJECTS/.cognition/silice_fem_env_20261008:
Python3.13,NumPy2.2.6,SciPy1.15.1,psutil6.1.1,Gmsh4.15.2,
scikit-fem12.0.2,meshio5.3.5. Wheels oficiales/versiones y SHA registrados
por pip--report; el entorno CPU anterior no se modifica. Herramientas
abiertas usadas localmente, sin compra/GPU/publicación de binarios.

Mismo caso96discos del fichero centres.json, radio1,25µm,dominio cuadrado
±64µm. Geometría en unidadesµm para evitar tolerancias CAD macroscópicas.
Unir discos con OCC y fragmentar el cuadrado; asignar material por mapas
de fragmentación, no por puntos centroides. Para este caso, los discos
están contenidos en6<=r<=12 salvo redondeos microscópicos:comprobar
área CAD contra la unión recortada analítica antes de aceptar omitir
arcos tangentes redundantes del recorte. Diferencia relativa<=1e-8.

Malla triangular cuadrática, nodos intermedios en curvas. Tamaño declarado
0,35µm dentro de r15µm; transición lineal hasta1,4µm en r25µm; exterior
1,4µm. Un hilo, semilla de malla1, sin ventanas interactivas. No cambiar
tamaños para mejorar una potencia aún no calculada. Presupuesto600s,
RAMdisponible>2GiB/disco>2GiB. Registrar fallo y conservar artefactos.

Importar triangle6 a MeshTri2 y coordenadasSI. Ensamblar masa/rigidez
P2 con cuadratura8; cladding por tags materiales. Controles:
- Área CAD cladding vs geometría analítica<=1e-8rel; área totalCAD128².
- Jacobianos finitos y no nulos, signo constante por elemento; una
  orientación horaria es válida y se integra con valor absoluto.
  Verificar también mínimo de determinante cuadrático en el triángulo
  de referencia, no sólo en puntos de cuadratura.
- Área de masa total vs128²µm²<=1e-10rel.
- Área de masa cladding vsCAD<=1e-5rel (aproximación geométrica P2,
  no identidad exacta con círculos); informar error sin ocultarlo.
- Masas/rigideces simétricas<=1e-12rel; masa diagonalpositiva.
- Campo constante tiene rigidez residualmáxima<=1e-10.
- Partición de materiales completa/disjunta y extremosDirichletfijos.

Guardar mesh/arrays/matrices/informe/hashes y versiones. Ningún PASS
geométrico sustituye validación de inicialización/tiempo/detector ni
convergenciaT96. Para propagación se necesita otro protocolo antes de
campos nuevos. JEVfallbacklocal por bloqueo heredado.
Fuentes:gmsh.info,scikit-fem.readthedocs.io,PyPI oficial.
