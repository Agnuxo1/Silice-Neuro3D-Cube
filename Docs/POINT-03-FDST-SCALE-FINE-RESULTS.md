# Extensión conocida: orden cuatro recuperado a pasos pequeños

Registro e1ba068 antes de ejecutar. Completa49,849s; tres trayectorias
fabricadas nuevas, sin repetir las cuatro anteriores y sin T96. Todas
las fuentes del diagnóstico inicial verificadas por hash y conservadas.

| dz (um) | dz*rho | Error relativo de campo | Error relativo de norma |
|---:|---:|---:|---:|
|0,0390625|0,638456|2,30002e-5|3,33114e-11|
|0,01953125|0,319228|1,49987e-6|6,65896e-11|
|0,009765625|0,159614|9,47364e-8|1,74325e-10|

Órdenes3,93873/3,98478 dentro[3,8;4,2]; error fino<1e-6, todas las normas
<1e-9, referencia y presupuesto pasan. Extensión PASS. El campo no se
renormalizó ni se alineó su fase. La salida inicial conserva el error
no monótono y órdenes diferentes a cuatro en su rango de pasos grandes.

Conclusión acotada: para ESTA matriz y entrada conocidas, los pasos más
pequeños recuperan el orden nominal del kernel. No hay criterio CFL
universal extraído de estos datos, ni causa demostrada para T96, ni una
validación de su campo o potencia. Piloto L1 y punto3 conservan su alcance.
