# Alcance del indicador de incertidumbre del punto 3

Nota registrada durante G, antes de calcular su holdout N640. No modifica
el contrato G, los datos E/F ni los criterios de aceptación.

En F el funcional reconstruido muestra órdenes4.42/4.61, superiores al
orden formal2 del stencil. Pueden aparecer cancelaciones de términos de
error para un observable particular. El contraste de varios órdenes y
la nueva predicción N640 discriminan esa posibilidad, pero no prueban una
cota rigurosa o un orden universal del campo complejo.

La lectura del artículo de [Eça–Hoekstra,JCP262,p.108](https://doi.org/10.1016/j.jcp.2014.01.006)
advierte que usar un orden observado superior al formal puede producir una
estimación de error demasiado pequeña. La extrapolación se debe acompañar
de ese límite, incluso si satisface los umbrales locales.

Para la revisión final se mostrará adicionalmente la sensibilidad a usar
`p_indicador=min(p_observado,2)` en la fórmula
`u_espacio=1.25*abs(D2)/(1.25**p_indicador-1)`, si el orden es positivo.
Esta sustitución no aprueba E, no cambia el ajuste/predicción ni es la
implementación del procedimiento completo de Eça–Hoekstra. Es una
comparación descriptiva fijada antes del resultado G; tampoco es una cota
certificada. Un radio longitudinal inválido conserva el combinado nulo.

La geometría analítica reduce el error de cobertura respecto a la
cuadratura de áreas, pero no elimina el error de representar un potencial
discontinuo por valores celulares. No se asigna a ese término una potencia
de error cero por el PASS geométrico. El presupuesto combina indicadores
condicionales y controles concretos, no todas las fuentes físicas.

Una aceptación local G se restringiría al observable de potencia dentro
del núcleo a2 mm, con la geometría ideal, entrada y dominio fijados.
Dominio/frontera, campo complejo y fase se evalúan después en su punto
propio. El punto de material medido requiere datos experimentales de
perfiles y geometrías, con incertidumbre y procedencia; no se sustituye
por valores de otra receta publicados en la literatura.
