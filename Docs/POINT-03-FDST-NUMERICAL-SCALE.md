# Escala del paso temporal y alcance de estabilidad

Diagnóstico algebraico de parámetros conocidos, sin medir nuevos campos
ópticos ni modificar el piloto. N626, dx=128um/626, beta0=1,444*2pi/1550nm.
El radio espectral cinético FD es

rho = 4*cos²(pi/[2(N+1)])/(beta0*dx²) = 16344461,981064592 m^-1.

Los tres valores adimensionales dz*rho son 10,21529; 5,10764; 2,55382.
No prueban que los errores estén en régimen asintótico. El orden nominal
del kernel fabricado no sustituye al orden observado en el perfil T96.

Para sigma=0, dn real, cada factor cinético y local es unitario; su producto
es unitario en aritmética exacta para cualquier dz. Esto NO prueba precisión
de fase, ni ausencia de resonancias del error, ni contractividad con sigma>0.
Con absorción, las subetapas locales negativas pueden amplificar; el piloto
registra su amplificación y exige balance en cada checkpoint.

[Blanes–Casas–Murua (2011)](https://arxiv.org/abs/1005.4709), resumen del
artículo primario consultado: estudia otros esquemas que usan productos
matriz-vector para Schrödinger discretizada. No se importa su región de
estabilidad al producto cinética/potencial implementado aquí.

[Dujardin–Faou (2007)](https://www.numdam.org/articles/10.1016/j.crma.2006.11.024/),
resumen consultado: su conservación a largo plazo asume potencial pequeño
y analítico, no resonancia del paso y un toro unidimensional. Esas hipótesis
no describen nuestra malla bidimensional absorbente con perfil abrupto.

[Chin (2007)](https://arxiv.org/abs/0710.0396), resumen consultado: analiza
inestabilidades de algoritmos para Schrödinger NO LINEAL. No se convierte
su condición aproximada de paso en un criterio CFL universal para nuestro
operador lineal. No hay causa demostrada antes del contraste temporal.
