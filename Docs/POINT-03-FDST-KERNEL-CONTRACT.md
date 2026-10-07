# Nuevo propagador de contraste: difracción FD por transformada seno

Registro antes de pruebas nuevas del kernel, tras FAIL K626. No relanzar E
ni modificar E/G/H/K. Punto3 sigue abierto; no trabajo modal posterior.

Motivación: N626 revela variación espacial no monótona también con detector
cúbico. Además, las referencias Taylor difieren en potencia3,9e-10 frente
al límite1e-10. Evaluar otra integración temporal del MISMO operador FD,
con posible menor coste para mallas más finas, sin cambiar la física.

DST-I ortonormal diagonaliza el laplaciano FD con ghost cero. Autovalores
unidimensionales -4*sin²(pi*j/[2(N+1)])/dx². Aplicar fase cinética exacta
i*z*lambda/(2beta0). Potencial local ik0*dn-sigma, mismo input congelado.

Composición simétrica de cuarto orden: S2(w1*dz) S2(w0*dz) S2(w1*dz),
w1=1/(2-2^(1/3)), w0=1-2*w1. Fusionar fases locales contiguas; mantener
dos fases positivas y dos negativas. Registrar amplificación máxima local
exp(sigma_max*abs(coef_neg)*dz), exigir<=1,10. No renormalización/phasealign.
La subetapa negativa no representa ganancia del material; es numérica.

Controles antes de usar campos ópticos: equivalencia cinética con expm
densoN7<=1e-11; norma con sigma0/fase uniforme<=1e-10; modos senoN9
con sigma0/12000 y dnconstante frente solución exacta<=1e-10. Perfil
aleatorioN7 semilla937, dx2um, z200um, pasos400/800/1600 frenteexpm denso:
orden de error de campo entre3,8–4,2 y error másfino<=1e-7. Conservar FAIL.
Comprobar identidades de coeficientes suma1 y cubos0<=1e-13.

Sólo tras controlesPASS, registrar piloto óptico/inputs/límites antes de
propagar. Este kernel no cierra punto3 ni atenúa los criterios anteriores.
CPUunhilo, sinGPU/instalaciones, fuentes antiguas inmutables. JEVfallback
local por bloqueo remoto heredado. Operador fuenteH usado sólo como
oráculo de la pequeña matriz; DST implementado sin códigoADI.
