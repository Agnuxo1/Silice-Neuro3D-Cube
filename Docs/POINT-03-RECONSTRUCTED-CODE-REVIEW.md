# Revisión del ensayo G antes de interpretar sus resultados

Contrato y dos programas congelados antes de nuevas propagaciones en commit
40f46d0. El programa de propagación añade cinco cadenas y reutiliza cuatro
campos E por hash. El evaluador no importa el solver de ondas: lee arrays,
verifica enlaces y recalcula ambos observables de manera separada.

El preflight retuvo 18 controles del evaluador escalar original (aceptación
y rechazos de signos, órdenes, predicción, radios/esquinas, datos inválidos).
La fórmula de predicción de N640 reprodujo un funcional manufacturado con
error5.55e-17. El nuevo integrador, mediante una implementación distinta de
los nodos Gauss–Legendre, reprodujo las16 potencias reconstruidas de F a
máximo7.77e-16. Son pruebas del código, no propagaciones ópticas nuevas.

Revisión manual: ecuaciones ADI y orden x/y heredados, factory dispersa sin
cambios, complex128, entradas E idénticas entre controles, perfil nuevo solo
paraN640, checkpoints JSON enlazados a arrays200 pasos y hashes de fuentes
verificados por cada hijo. El evaluador reetiqueta las8 medidas al contrato
escalar E y conserva N/dz/ID/fuentes reales en cada registro. N640 no participa
en el ajuste de su predicción. No alinear fase ni normalizar campo final.

La preparación N640 finalizada contrastó48 celdas y el área global. Sus
resultados geométricos no son una cota del error óptico. Los muestreos de RAM,
disco y tiempos son observaciones locales; no acreditan máximos globales ni
ventajas de rendimiento.

Límites: ambos observables provienen de los mismos campos, por lo que su
acuerdo no es réplica de otro solver. La predicción nuevaN640 añade una prueba
prospectiva; las4 primarias ya conocidas no son4 réplicas independientes.
Los órdenes aparentes altos pueden producir indicadores demasiado optimistas
(Eça–Hoekstra,JCP262,p.108), por lo que cualquier indicador aprobado sigue
siendo condicional, restringido al funcional y a este modelo. Las pruebas
no cierran dominio/frontera/fase ni material/dispositivo físico.

No se modificaron las fuentes ni arrays congelados durante el ensayo.
El resultado final se publicará, tanto si pasa como si falla, en un informe
separado. No avanzar al punto4 antes del dictamen del punto3.
