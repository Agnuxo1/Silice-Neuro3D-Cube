# Punto 3, ensayo H: referencia temporal sin separación

Registro 2026-10-07 antes de calcular campos nuevos. G continúa y su control
N400 incumple q: aproximadamente2.7527 frente[1.8,2.2]. Mantener G completo,
sus criterios y FAIL aunque H pase. No relanzar E. H comprueba directamente
el error ADI respecto a la misma ecuación semidiscreta, sin inferirlo de q.

## Operador y soluciones

Entradas E/G inmutables N256/320/400/500/640. Construir independientemente
una matriz CSR complex128 con stencil cinco puntos y ceros fantasma:
L=i/(2*beta0*dx²)*Lap_discreta+i*k0*dn-sigma, k0=2pi/1550nm,
beta0=1.444*k0. dn, sigma y A0 byte a byte de las entradas congeladas.
No importar el solver ADI para construir L. Flatten C, sin enlaces entre
el final de una fila y el inicio de la siguiente. Usar SciPy1.15.1
expm_multiply, traceA exacta; las operaciones internas de Taylor/escalado
no constituyen pasos físicos ni una solución analítica del continuo.

Para cada N calcular z2mm mediante cuatro segmentos500um (referencia R4)
y ocho segmentos250um (R8), desde A0 separados. Retener ambos y todos los
checkpoints. Exigir ||R4-R8||_2/||R8||_2<=1e-9 y discrepancia Pcore<=1e-10
en ambos funcionales. Esto controla sensibilidad de redondeo/algoritmo;
no es certificación formal de error backward. No alinear fase ni normalizar
salidas. Potencia inicial1±1e-12; final entre0 y1.001. RAM>1.5GiB/disco>2GiB
antes/después de cada segmento; un hilo; máximo360s por hijo370s externo,
total7200s. Si falla un límite operativo, conservar datos y parar sin retry.
H inicia solamente tras terminar G para evitar competencia por CPU/RAM.

## Verificaciones previas y criterios

Antes de campos ópticos: contrastar stencilCSR con stencil de bucles
independientes; modos seno discretos con eigenvalores analíticos y potencial
constante complejo; matriz densa expm de un caso pequeño con perfil variable;
propiedad semigrupo; normaconstante cuando sigma=0 y disipación sigma>0.
Errores relativos<=1e-11, semigrupo<=1e-11, potencia<=1e-11. Congelar contrato,
runner y controles por commit/SHA antes de la primera propagación óptica.

Usar sin modificar los dos detectores/cuadraturas de G. Controles gaussianos
y tolerancias de cuadratura de G; diferencia de detectores N500/640<=1e-7.
Error temporal directo absoluto de Pcore: ADI dz0.3125 frente R8<=1e-6
en N256/320/400/500/640; ADI dz0.15625 frente R8<=2.5e-7 en N400/500.
Retener errores del campo complejo sin usarlos para certificar el hito
posterior de campo/fase/frontera. No reemplazar el FAIL q de G por un PASS q.

Primarias espaciales H=R8 en N256/320/400/500, r1.25. Exigir incrementos
resolubles>1e-12, mismo signo, órdenes positivos, discrepancia relativa de
órdenes<=20%. Predicción N500 desde N256/320/400: residual<=10% del último
incremento. Aplicar a ambos detectores. Usar las fórmulas de Richardson
originales sin refit ni selección. Antes de cualquier H N640 congelar
predicción desde el último trío320/400/500, fórmula de G; residual H640
<=10% de |P640-P500|. El campo aproximado G640 ya puede ser conocido:
H640 es una predicción prospectiva del nuevo resultado semidiscreto,
no un conjunto de datos físicos independiente ni un holdout completamente
desconocido. Mostrar esta dependencia.

Indicador espacial conservador: Fs1.25 y p_ind=min(p_último,2);
u_space=1.25*|P500-P400|/(1.25^p_ind-1). Indicador temporal=error directo
N500 dz0.3125; u_detector=discrepancia métodosN500; u_quad=último cambio;
u_ref=discrepanciaR4/R8; sumar, exigir<=1e-3 y<=1% de P500 para ambos.
Son indicadores locales, no cota rigurosa ni probabilidad de cobertura.
El perfil abrupto y la geometría subcelda limitan inferencias de orden.

Aceptación H requiere todos los controles de ambas reconstrucciones,
integridad, predicciones y errores directos. Si pasa, puede cerrar únicamente
la convergencia local de potencia del núcleo T96/Q4 para esta entrada,
z2mm, ancho128um y ecuación escalar, mediante referencia temporal explícita.
E/G siguen fallidos; H no valida Maxwell, fabricación, fase, fronteras ni
otros perfiles. Si falla, punto3 sigue abierto y no iniciar barrido modal.

Fuentes consultadas: [SciPy1.15.1 expm_multiply](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.sparse.linalg.expm_multiply.html),
Al-Mohy/Higham2011, SIAM JSC33:488–511, citado por la documentación SciPy;
se consultó documentación y metadatos, los dos accesos al PDF fallaron.
[NASA](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html) y
[Eça/Hoekstra2014](https://doi.org/10.1016/j.jcp.2014.01.006) para las reservas
de Richardson/órdenes elevados. Ninguna fuente certifica este dispositivo.
JEV fallback local identificado: bloqueo de seguridad heredado preservado.
