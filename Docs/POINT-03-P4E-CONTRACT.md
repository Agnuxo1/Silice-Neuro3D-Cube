# P4E: coste y consistencia temporal del operador débil T96

Registrar fuente antes de construir/amortiguar/propagar. Malla P4C
recuperada sin regenerarla,masa/rigidez/cladding guardadas por hashes.
No usar la entrada GaussianT96 ni medir su potencia de núcleo:esto es
un control de viabilidad del integrador sobre la matriz real, no cierre.

Ensamblar D=integral sigma phi_i phi_j; sigma=4e4*max((r_inf/64µm-0,8)/0,2,0)^4.
Cuadratura8. Eliminar grados de libertad en±64µm, mismo dominio físico.
B=-i*K/(2beta0)-i*k0*0,003*C-D. Verificar simetría de M/K/C/D;
diagonalMpositiva, coeficientesDPSD por cuadratura positiva. No cambiar
índice,malla o sigma para reducir coste. Inicial seno de bajo orden
sin(pi*(x+64µm)/128µm)*sin(pi*(y+64µm)/128µm),normalizado sóloM.

Padé6 ya contrastado P4D.100pasosdt=2mm/8192 y200pasosdt/2;
guardar campos,tiempos/factorización/LUmemoria y matrizD. Hipótesis
operativa:estado finito ypasivo<=1+1e-9,diferencia campo normaM<=1e-5,
previsión8192pasos<=7200s. No afirmar error exacto desde comparación
de dos pasos. Presupuesto600s/RAM>3GiB/disco>2GiB/unhilo/sinGPU.

Si falla, conservar resultado. Antes de propagación GaussianT96 real
se necesita detector/inicialización verificados y protocolo de espacio
y tiempo prospectivo. P4C/P4D controles no validan física Maxwell ni
material real. Todos los FAIL históricos se conservan. JEVlocal/bloqueo.
