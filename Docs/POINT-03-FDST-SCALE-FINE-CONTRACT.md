# Extensión fabricada hacia pasos pequeños: registro previo

Sólo la matrizN9 y tablero del diagnóstico3ab1a13, misma rho, dx, dn,
sigma0, modo inicial(1,2), z2mm y kernel. No T96 ni mallas espaciales nuevas.
Conservar la salida anterior; no repetir sus cuatro trayectorias.

Calcular51200/102400/204800pasos (dz0,0390625/0,01953125/0,009765625um),
referencia expm densa81x81 reconstruida de los mismos parámetros. Guardar
hash del diagnóstico anterior y todos sus fuentes; norma y semigrupo
densos<=1e-9. Sin renormalización ni phasealign. CPU1, límite total120s.

Criterios nuevos, sólo para esta extensión: norma de las tres<=1e-9,
error de campo más fino<=1e-6, ambos órdenes consecutivos entre3,8 y4,2,
finitos y presupuesto. Si FAIL, conservar. Si PASS, prueba orden4 en este
rango del problema fabricado, no en T96. No cambia piloto L1 ni habilita
convergencia espacial por sí solo. Informar datos anteriores aparte.
