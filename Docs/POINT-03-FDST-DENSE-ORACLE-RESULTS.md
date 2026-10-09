# Referencia conocida contrastada con otro algoritmo

Contrato4c04b4f antes de calcular. Matriz real simétrica81x81 del control
fabricado, sigma0; sin T96 ni nuevas trayectorias del integrador.

La acción por diagonalización y la acción expm difieren en campo relativo
2,90004e-12, frente al límite1e-9. Residuo espectral1,15946e-15 y
ortogonalidad1,41331e-14 frente1e-13. Diferencia de proyección7,81597e-14,
error de norma espectral3,33067e-16. Todos los criterios pasan. Fuentes
del diagnóstico previo verificadas sin cambios y hash enlazado.

Esto respalda la precisión de la referencia de ESTE control muy por
debajo de sus errores FDST registrados. La comprobación usa un algoritmo
distinto y no se limita al semigrupo del mismo expm. No demuestra exactitud
de la referencia dispersa N626 con absorción, ni cierra el punto3.
