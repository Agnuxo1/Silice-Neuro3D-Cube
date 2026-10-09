# Fundamento y alcance del contraste FDST

Consultado el 7 de octubre de 2026, durante el piloto temporal registrado.
No cambia su contrato, coeficientes, entradas ni criterios.

[Yoshida (1990), artículo original](https://tlakoba.w3.uvm.edu/math6737/for_final_topics/SSM_1990_Yoshida.pdf),
Physics Letters A150,262–268, secciones2–4, ecuaciones2.11 y4.1–4.6:
composición simétrica de tres operadores de segundo orden. Las dos
condiciones son 2w1+w0=1 y2w1³+w0³=0; corresponden a los coeficientes
implementados. El artículo formula también el problema general de
productos de exponenciales de operadores no conmutativos. La aplicación
a nuestras matrices complejas con absorción es una inferencia algebraica
y se verifica por controles densos, no una certificación física del autor.
Las subetapas negativas exigen comprobar amplificación y estabilidad.
El orden nominal no garantiza estar en régimen asintótico en mallas finas
con coeficientes no suaves; eso se comprueba mediante el piloto temporal.

[SciPy1.15.1, dstn](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.fft.dstn.html)
documenta la transformada seno multidimensional, selección de tipo,
normalización ortogonal y número de trabajadores. Se usan tipoI,
axes(0,1), normortho, workers1; la implementación se contrastó con el
exponencial de la matriz FD y modos seno conocidos, incluyendo campos
complejos. No sustituye el laplaciano FD por el operador espectral continuo.

El PASS del kernel fabricado prueba esas propiedades en los casos
registrados. La potencia T96, el error temporal en N626 y posteriormente
la convergencia espacial requieren su evidencia óptica propia.
