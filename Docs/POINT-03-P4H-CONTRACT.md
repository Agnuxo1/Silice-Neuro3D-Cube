# P4H: integrador independiente L-estable de orden5

Registrar antes de pruebas. Padé6/Gauss conserva norma en sistemas
no amortiguados pero puede no amortiguar frecuencias no resueltas.
Añadir Padé[2/3],equivalente aRadauIIAorden5,L-estable. No cambia el
operador físico ni normaliza salidas; su amortiguación numérica se informa.

p(z)=60+24z+3z²,q(z)=60-36z+9z²-z³. Factorizar raíces para resolver
tres sistemasM-dtB/r denominador;dos numeradoresM-dtB/a y unoM.
Contrastar contra la MISMA referencia densa exacta de P4D en n127 y
semilla953,2mm,Sigma0/variable,mismo pozo y masas.8192/16384/32768pasos.
Hipótesis:errorcampoM caso fino<=1e-7,órdenes[4,5;5,5],pasividad<=1+1e-9,
norma fina respectoexacta<=1e-7. No exigir conservaciónexacta delcaso
grueso paraunmétodoL-estable; registrar sus pérdidas numéricas.

Guardar campos/raíces/hashes. CPUunhilo,180s,noGPU. NoT96propagación.
Si falla,no adoptar;no ajustarumbrales. Antes deT96Gaussian a2mm se
registrarán comparación propia en la matriz real ycontrol de potencia.
Toda convergencia espacial necesita cuatro mallas/holdout, auditor y
preservar todoslos FAIL anteriores. JEVlocal/bloqueoheredado.
