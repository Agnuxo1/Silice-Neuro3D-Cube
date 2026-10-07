# Control fabricado de escala cinética: registro previo

No T96 ni geometría óptica nueva. Mantener kernel/piloto L1 y sus criterios.
Objetivo: comprobar campo y norma en una matriz pequeña con fase cinética
por paso comparable a N626. El orden nominal no basta para afirmar
precisión a pasos grandes; este control no atribuye una causa al T96.

N9; elegir dx algebraicamente para igualar el radio espectral cinético
de N626 y dx128um/626: rho=16344461,981064592 m^-1. Entrada modo seno
(1,2), sin normalizar salidas ni alinear fase. Longitud2mm.
Potencial alternante de tablero, dn0/-0,003, sigma0. Referencia matriz
FD81x81 y expm densa, además control constante dn=-0,003 con solución
analítica del modo seno. No usa un campo T96 ni resultados finales L1.

Control constante:3200pasos, error relativo<=1e-9, norma<=1e-9.
Tablero:3200/6400/12800/25600pasos; norma relativa<=1e-9, finitos.
Registrar errores crudos de campo y órdenes consecutivos sin exigir
orden4 a los pasos grandes ni usarlo como aceptación. Registrar también
error de la proyección sobre el modo inicial (observable distinto del
núcleo T96), normalizado por la potencia de entrada.
Control independiente de expm: semigrupo de dos medias acciones densas
frente una acción completa<=1e-9; norma densa<=1e-9.

CPU1, N9 únicamente; límite diagnóstico120s, RAM/disco existentes.
Retener toda salida y FAIL. No reescribir el contrato del piloto ni
tomar este diagnóstico como autorización de cierre espacial.
