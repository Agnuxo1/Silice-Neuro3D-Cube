# H2: recuperar sólo N640 tras timeout confirmado

Registro2026-10-07 después de H1FAILED y antes de nueva propagación.
H1 conservó cuatro mallas completas, dos particiones cadauna,48checkpoints,
y predicción previaH640. Primer segmento N640R4 superó370s; el proceso
hijo fue terminado por subprocess.run(timeout), no existe checkpoint válido
de ese segmento. H1executionFAILED y su log permanecen inmutables.

Reutilizar las cuatro soluciones/inputs/manifest/predicción de H1 por hash;
no relanzar E/G ni N256/320/400/500. Sólo nueva referencia N640 en carpetaH2.
Mismo operador semidiscreto y mismo expm_multiply/traceA/seed/CPUunhilo.
Modificar únicamente particiones N640: R11 yR17, segmentos2mm/11 y2mm/17.
Particiones más cortas que500um para respetar límites360/370s; los números
no relacionados por factor2 añaden un contraste del incremento interno.
Esto puede modificar redondeo, no la ecuación exacta ni la longitud final.
No se presume independencia de algoritmos ni precisión exacta.

Guardar los28checkpoints N640. Para primeras cuatro mallas usar R4/R8
originales; paraN640 R11/R17. Etiquetar número REAL de segmentos en cada
campo/tabla; referencia fina primaria8 enprimerascuatro y17 enN640.
No renombrarR17 comoR8. Reutilizar el workerH1 sin modificar código científico.
Nuevo evaluador copiaH con índices de partición variables, conservando
todos los umbrales/métodos/controles. Congelar contrato/runner/evaluador
y controles de particiones impares antes de calcular.

Límites sin cambios:360s hijo/370s externo, RAM>1.5GiB/disco>2GiB
muestreados antes/después. Nuevo presupuesto recuperación7200s. Stop al
primer fallo, sin retry automático. Las28llamadas se ejecutan en serie.
Contrastar semigrupo R11/R17 contra exponencial densa en caso fabricado
pequeño antes de uso óptico, tolerancias1e-11. No instalar dependencias.

PredicciónH640 originalcampo0.3329580848002981, intensidad
0.33295806306460385 permanece igual: no refit conG640 ni con estadosN640
parciales. Se registró antes de cualquier propagación H1N640, y por tanto
antes deH2. G640 ya conocido declarado como dependencia. Gate previo10%
del incrementoN500→N640 sin flexibilización.

Mantener todos los controlesH: referencia relativa<=1e-9/Pcore<=1e-10,
errorADI.3125um<=1e-6, finos400/500<=2.5e-7, Gaussianos/cuadraturas,
acuerdo de detectores500/640<=1e-7, estabilidadespacial20%, predicciónN500,
u_space conp_ind<=2 y total<=1e-3/<=1%P500. H1 sigueoperFAILED; H2 aporta
un dictamen científico nuevo. El punto3 sólo se acepta dentro del alcance
local registrado si pasan todos; unFAIL mantiene siguientes hitos pendientes.
J no se aplica a datos incompletos ni sustituye estos criterios.

JEV fallbacklocal identificado por bloqueo de seguridad heredado; main
preservado. Datos/arrays/logs localesD; noGPU/instalaciones/publicación.
