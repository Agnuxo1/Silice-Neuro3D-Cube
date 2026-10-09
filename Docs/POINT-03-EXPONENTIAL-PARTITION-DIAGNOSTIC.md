# Control del incremento interno de la referencia exponencial

Registro antes de reconstruir los parámetros internos, durante H2.
Sin propagación ni lectura de potencias N640. No altera H2 ni aceptación.

Usar SciPy1.15.1 y el operador/entradas congelados. Para N500R4/R8 y
N640R11/R17 reproducir la selección de m_star/s de `_expm_multiply_simple`:
restar traceA/n, norma1 exacta CSR, LazyOperatorNormInfo y fragment3.1,
n0=1, tolerancia2^-53, ell2, semilla0. Guardar hashes de entrada y fuente.

Registrar z/(particiones*s), igualdades exactas y diferencia relativa.
Es reconstrucción de la selección del algoritmo, no instrumentación de
cada hijo ni conteo de términos Taylor realmente usados: el bucle interno
puede parar antes de m_star dependiendo del campo. No prueba independencia
si los incrementos son distintos, ni que los resultados deban coincidir
si son iguales. No llamar a `_expm_multiply_simple_core` ni propagar.

El diagnóstico precisa el alcance del contraste entre particiones de
un solo algoritmo; una cota certificada sigue ausente. Si aparecen
incrementos iguales, conservar esa dependencia explícita junto al PASS
de consistencia; no reinterpretarlo como dos solvers independientes.
