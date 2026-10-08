# P4D: propagador racional de orden6 para matrices débiles

Registrar fuentes antes de pruebas. No propagar T96 ni afirmar convergencia
espacial. Control temporal del nuevo operador FEM consistente.

Sistema M*a'=B*a, con M SPD y B=-iH-D,H simétrica real,D PSD.
Usar aproximante Padé[3/3] de exp, factorizado en tres sistemas lineales
dispersos. Polinomio p(z)=120+60z+12z²+z³; raíces r_j. Cada factor
(M+dt*B/r_j)^-1*(M-dt*B/r_j). Matrices estáticas, sin renormalización
de salida/alinear fase. Guardar raíces y comprobar identidades polinomiales.

Control conocido n127,dominio±64µm,modelo1D P4A:FEM masa consistente,
pozo finitoV,2mm. Dos amortiguaciones:0 y perfil lineal positivo0..2000m^-1
integrado exactamente por Gauss3 con bases lineales. Inicial aleatoria
compleja,semilla953,normalizada sólo porM. Referencia scipy.linalg.expm
de matrizM^-1B completa, con balance físico pasivo verificado.

4096/8192/16384pasos. Hipótesis temporal:error relativo en normaM del
caso fino<=1e-7,órdenes observados en[5,5;6,5] para ambos casos. EnΣ0
conservar normaM<=1e-9;Σvariable estado final y referencia pasivos, y
diferencia de norma<=1e-7. Finitos/residuo de factorización controlados.
CPUunhilo,180s,sinGPU/instalaciones. Guardar campos y métricas/hashes.

No convierte controles de matrices pequeñas en validación del casoT96.
Ese caso requiere control temporal propio,detector y estudio espacial
prospectivo. P1/P2/P3/P4A negativos se conservan. JEVlocal/bloqueoheredado.
ReferenciaAPI https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.linalg.expm.html
