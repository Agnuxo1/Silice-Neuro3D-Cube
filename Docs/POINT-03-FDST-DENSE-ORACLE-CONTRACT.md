# Contraste independiente de la referencia fabricada

Registro antes de calcular. Misma matrizN9, dx/rho y tablero alternante
con sigma0 de3ab1a13. No nuevas trayectorias FDST, no T96 ni cambios de
criterios L1. El semigrupo de un mismo algoritmo no basta para afirmar
independencia entre referencias.

Como L=iH y H es real simétrica, contrastar expm(L*z) por diagonalización
real simétrica eigh(H), e^(i*z*lambda), z2mm. Sin normalizar ni phasealign.
Entrada modo seno(1,2) del diagnóstico original. Verificar fuentes del
informe previo y sus hashes. Residuo espectral relativo y ortogonalidad
<=1e-13; diferencia relativa de campos<=1e-9, diferencia de proyección
normalizada sobre entrada<=1e-9; norma espectral<=1e-9.
CPU1, sólo81x81. Guardar PASS/FAIL nuevo; no sustituir datos anteriores
ni afirmar exactitud ilimitada de expm en las mallas ópticas grandes.
