# N1: contraste analítico completo — 7 de octubre de 2026

Contrato y fuente registrados en `ca73a4c` antes de ejecutar. Tiempo
7,792s;18combinaciones:9mallas y2representaciones del potencial. No se
propagó T96 ni se repitió M1. El punto3 permanece **abierto**.

La potencia exacta continua del núcleo del pozo finito1D es
0,924546975110603. El empalme modal tiene residuo relativo5,25964e-16;
la norma continua integrada independientemente es0,9999999999999998.
Los seis controles polinómicos pasan. Máximo residuo relativo de los
eigenpares4,18926e-15 y error de norma discreta4,21885e-15. Estos
controles respaldan el contraste conocido y la evolución temporal
matricial, sin una comparación física con el cubo.

| Potencial / detector | Órdenes de las tres ternas registradas | Estabilidad |
|---|---|---|
| Nodal / campo | No admisible; no admisible;7,99865 | FAIL |
| Nodal / intensidad | No admisible; no admisible;7,80077 | FAIL |
| Promedio por celda / campo | 1,02927;0,92091;4,75536 | FAIL |
| Promedio por celda / intensidad | No admisible en las tres | FAIL |

Las ternas son320/400/500,400/500/640 y500/640/767, con espaciados reales
128µm/(N+1). «No admisible» significa que no existe un orden positivo
en el intervalo registrado o que los incrementos no son monótonos;
no significa un fallo del solucionador temporal.

La variante nodal cambia también el signo del error frente a la verdad
continua. En N400/N500 su error de campo es−0,00233498/+0,00334178.
El promedio por celda reduce esos errores a−0,000384078/−0,000253903,
pero no garantiza estabilidad de los órdenes locales. En N1199 el
error con promedio por celda es−4,27580e-5 para campo y−1,80548e-5
para intensidad. Se informan todos los resultados, incluidos626/640.

La hipótesis diagnóstica registrada queda respaldada en este problema
conocido. Una orden local inestable no demuestra por sí sola un error
de implementación temporal. El promedio geométrico tampoco basta para
presumir régimen asintótico en cualquier terna. La normalización de
entrada muestreada y la reconstrucción del detector forman parte del
error numérico y están explícitas en el registro.

Este contraste no reproduce los96trazos, el amortiguador, las mismas
posiciones discretas de frontera ni la solución óptica T96. No atribuye
M1 causalmente a una única contribución ni proporciona una cota de su
error. Hace falta un diseño que controle el muestreo y el dominio del
problema real antes de otra afirmación de convergencia. No relanzar una
serie idéntica ni escoger retrospectivamente sólo las mallas favorables.

Datos, parámetros y hashes: `point03_n1_analytic_contrast_20261007.json`.
JEVfallbacklocal, bloqueo heredado. Barrido modal y siguientes pendientes.
