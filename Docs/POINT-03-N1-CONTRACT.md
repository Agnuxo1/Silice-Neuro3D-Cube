# N1: diagnóstico con solución conocida, posterior al FAIL M1

Registrar fuente y contrato en Git antes de ejecutar. No propagar T96
ni repetir E/M1. Pregunta: ¿puede la posición de una interfaz discontinua
respecto de la malla producir órdenes locales inestables en un problema
con solución analítica conocida y evolución temporal matricial exacta?

Modelo de contraste unidimensional, no el cubo: ecuación escalar de
Schrödinger óptica, núcleo [-6,6]µm, dominio fijo [-64,64]µm con extremos
Dirichlet,1550nm,n0=1,444 y potencial exterior k0*0,003. Estado inicial:
modo fundamental par exacto del pozo finito en este dominio. Condición
analítica k*tan(k*a)=q*coth(q*(L-a)); la solución evoluciona sólo en fase.
Su potencia continua en el núcleo es conocida por integración cerrada.

Mallas interiores fijas N256/320/400/500/626/640/767/959/1199;
h=128µm/(N+1). Para cada N: potencial nodal y promedio exacto por celda.
Evolución2mm mediante diagonalización simétrica tridiagonal; no pasos
longitudinales, absorción ni ajuste de fases/salida. Normalizar únicamente
la entrada muestreada y registrar su discrepancia de norma frente a la
entrada continua. Integrar reconstrucciones lineales del campo y de su
intensidad en el mismo intervalo físico, con momentos polinómicos exactos.

Controles obligatorios: empalme modal y norma/integral independiente
<=1e-12; integral del detector en seis polinomios aleatorios, semilla941,
<=1e-12; residuo de tres eigenpares por matriz<=1e-12 relativo; conservación
de norma discreta<=1e-10. CPU un hilo, sin instalaciones/GPU, presupuesto
120s. Guardar todos los resultados y hashes; no escoger mallas después.

Hipótesis prospectiva de este diagnóstico: en la variante nodal, al menos
uno de los dos detectores muestra un cambio de signo en su error respecto
de la verdad continua, o al menos una de las tres ternas fijas
320/400/500,400/500/640,500/640/767 incumple estabilidad de orden20%.
Si no ocurre, conservar hipótesis no respaldada. Los resultados de
promedio por celda se informan igualmente, sin convertirlos en un gate
de convergencia T96. Registrar posición fraccional de interfaz y errores.

Alcance: posible sensibilidad espacial en un contraste conocido. No
identifica por sí solo la causa de M1, no reproduce los96trazos ni su
frontera amortiguadora y no revoca ningún FAIL. No demuestra que un
ajuste de dispersión estime correctamente el error del problema real.
Punto3 sigue abierto y no se pasa al barrido modal. JEVfallbacklocal
por bloqueo heredado. Registro Git local, sin identificador externo/IPFS.
