# P4I: primera entrada GaussianT96 real FEM, control temporal propio

Registrar controlador/auditor/contrato antes de propagar. No afirmar
convergenciaespacial desde una malla. MallaP4C recuperada75kDOF,
detector/proyecciónP4F y amortiguador exactoporpartesP4G verificados.
Mismo dominio±64µm,96trazos,1550nm,dn=-0,003,2mm yGaussian6µm.
Reutilizar entradaP4Fq16 normalizada sóloM y matrices por hashes.

B=-iK/(2beta)-i*k0*0,003*Cclad-Dsigmaexacta. Eliminar sóloDOFDirichlet.
Sin renormalización de salida/alineación. Tres casos fijados antesdedatos:
Padé6_8192(diagnóstico),Padé6_16384,Radau5_32768. Los dos últimos son
primarios y pertenecen a familias diferentes ya contrastadas contra
referenciasdensas. Guardar todosloscampos/casos;no escoger después.

Hipótesis de precisión práctica temporal paraambos detectores:
- Diferencia de potencias últimosdos<=1e-6.
- Diferencia de campo relativa enM<=1e-4,estado pasivo<=entrada+1e-9.
- Cota directaPSD delobservable<=1e-5:
  |a*Qa-b*Qb|<=(sqrt(a*Qa)+sqrt(b*Qb))*sqrt((a-b)*Q(a-b)),
  Q=Ccampo odiag(pesosintensidad),ambasPSD por construcción.
  Se elige esta cota local ANTES de resultados, no la cota global de
  losensayosCartesianos. Informar también la cota globalM separadamente.
- Quadratura/aproximaciónD8/12 e inicializaciónsegúncontrolesprevios;
  hashes/cadenas/finitos/recursos/masas y auditor independiente PASS.

Estecontrol mide precisión frente a solución computada, no referencia
exactaT96 ni régimen de orden temporal5/6 demostrado a2mm. Informar
diagnóstico8192 sin descartarlo. Si falla, guardarFAIL y no declarar cierre.

CPUunhilo,RAM>3GiB/disco>2GiB,GLOBAL18000s. Hijos<360s/corte370.
Tramos256pasos:32/64/128,224campos nuevos. Cada hijo reconstruye LU
estáticas y conserva hash de entrada/previo; coste incluye reconstrucción.
Estimación de avance~10000s más LU; no garantía. No ampliar/reanudar
automáticamente durante ensayo. Siguen todoslosfallos anteriores.

Antes de cierreT96 se requiere ESTUDIO ESPACIAL posterior con mallas
conformes,hierarquía/predicción nuevos antesdefine, controles temporales
aprobados y datos guardados. No cerrarhitosdeMaxwell/frontera general
ni fabricación. JEVlocal/bloqueoheredado.
