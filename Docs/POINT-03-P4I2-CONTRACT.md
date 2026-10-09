# P4I2: refinamiento Padé6, reutilizando referencia Radau calculada

P4I mantiene FAIL:224campos auditados,potenciasdif<=6,262e-8 pero
cotasPSD1,025e-5/1,592e-5>1e-5. El diagnóstico de distancia de campo
apertural ya calculado muestra Padé8192/16384 significativamente distinto;
registrar antes de nuevosdatos un refinamiento único, no repetircasos.

Nueva trayectoriaPadé6_32768 hasta2mm,mismamatricestejada,entradaGaussian,
detector yperfil. Reutilizar Radau5_32768 y su cadena porhash;conservar
todosP4I. Comparación primariaP6_32768vsR5_32768 conLOS MISMOS límites:
campoMrel<=1e-4,potencias<=1e-6,cotasPSDlocal<=1e-5ambos;pasividad,
cuadratura/entrada/recursos/hashes y auditor independiente PASS.

128tramos de256pasos,CPUunhilo,child360/corte370,GLOBAL11000s,
RAM>3GiB/disco>2GiB. No extensión/recuperación automática durantetrial.
Si falla,no aprobarni cambiarumbrales. No afirmarerror exacto ni cerrar
espacio desde una malla. Estecontrol puedehabilitar estudios espaciales
conformes posteriores; éstosrequierennuevoprotocolo/predicción/holdout.
JEVlocal/bloqueoheredado.
