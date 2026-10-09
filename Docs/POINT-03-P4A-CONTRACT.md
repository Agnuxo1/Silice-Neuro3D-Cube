# P4A: producto potencial-campo integrado, solución conocida

P3 completo/auditado FAIL se conserva. Antes de otra propagación T96,
registrar fuente y contrato en Git y contrastar una discretización débil
del potencial, no sólo su promedio geométrico. No cambiar fuentes P1/P2/P3.

Problema conocido1D: pozo finito N1,1550nm,n0=1,444,a=6µm,L=64µm,
potencial exteriork0*0,003,Dirichlet±L,2mm. Modo fundamental analítico
par, misma ecuación k*tan(k*a)=q*coth(q*(L-a)), norma y potencia exactas.
N256/320/400/500/626/640/767/959/1199 interiores;h=128µm/(N+1).

Cuatro variantes registradas:nodal, promedio por celda, FEM P1 masa
concentrada, FEM P1 masa consistente. Las últimas integran exactamente
V(x)*phi_i(x)*phi_j(x) en los elementos cortados por la interfaz.
Rigidez y masa1D lineales estándar; no alisar ni mover la interfaz.
La forma débil y el ensamblaje se derivan explícitamente; no se atribuyen
a la formulación de un artículo del que sólo se leyó el abstract.

Evolución temporal mediante diagonalización simétrica/exponencial exacta
de cada matriz (generalizada H v=lambda M v para masa consistente).
Para comparación física uniforme, todas las entradas muestreadas se
normalizan en su reconstrucción lineal continua por la MISMA masa
consistente. Esa convención difiere de N1 y se declara; no se compara
el resultado como repetición idéntica ni se modifica N1.
No normalizar salida/alinear fase. Medir núcleo con campo lineal y
reconstrucción lineal de intensidad; guardar normas físicas y del esquema.

Controles:empalme/norma/integral analítica<=1e-12;integral de potencial
por polinomios cuadráticos contrastada con cuadratura independiente,
6elementos parciales escogidos por posiciones fijas antes de calcular;
<=1e-12 relativo aV*h. Masas/rigideces simétricas, masa positiva;
residuos de3eigenpares por matriz<=1e-11;norma del esquema conservada
<=1e-10. Semilla941;CPUunhilo,presupuesto180s,sin GPU/instalaciones.

Hipótesis primaria:FEM masa consistente muestra orden positivo y estable
20% entre las ternas400/500/640 y500/640/767 en AMBOS detectores, y
su indicador fino1,25*|P767-P640|/(r^min(p,2)-1),r=768/641,
cubre el error real frente a la potencia analítica. Si falla, guardar
hipótesis no respaldada, sin ajustar20% ni escoger otro intervalo.
Registrar también las otras variantes y todas las mallas como diagnósticos,
sin seleccionarlas retrospectivamente como confirmación de la primaria.

Alcance:contraste del esquema en una solución conocida1D. No cierra
T96/Q4, no demuestra que ésta sea su única causa y no certifica2D/Maxwell.
Toda adopción paraT96 requiere controles geométricos/de ensamblaje2D,
criterios/holdout nuevos registrados antes de datos, y auditor separado.
JEVfallbacklocal por bloqueoheredado. RegistroGit local,sinIPFS externo.
