# GLASS-007 — primer ensayo de camisa discreta, 2026-09-30

Contrato32b324a prospectivo. FuenteBPMoriginalSHA71ef25b7... inmutable.
10casos, dosjobsCPU acotados: primero40.0049s timeout/sietecasosretenidos;
continuación21.3568s/tresrestantes trasvalidar hashes. No ampliarlímite porhijo.
Reporte final `resultados/codex/glass007_complete_v1.json` yparent
`resultados/codex/glass007_v1.json` preservados. MaxRSSmedido32.85MiB primerjob.

Parámetros ideales: a6um/t6um, delta_n=-0.003, lambda1550nm, w6um/z2mm,
discosradio1.25um sobre3coronas, grid128um/256²,dz2.5um.

| Perfil | Trazos totales | Potencia núcleo/entrada |
|---|---|---|
| Camisa continua | No aplica | 34.879% |
| 16 por corona | 48 | 13.581% |
| 32 por corona | 96 | 33.261% |
| 64 por corona | 192 | 34.761% |
| 32 por corona, integral de índice igualada | 96 | 35.540% |
| 32 por corona con centros omitidos en cuña30grados | 88 | 21.114% |

Cuña: es una omisión de centros, no una abertura exacta de30grados en la
unión final de discos. El control de integral requiere delta_n pico
-0.00309855; NO significa misma energía de láser ni dosis de escritura.
Mismo índice pico/longitud no implica misma área modificada.

Gates para perfil96trazos: balance/perfil/igualintegralPASS; refinamiento
dx cambia núcleo/entrada0.002758, ampliar dominio aigualdx0.000140,
dz2.5→2um0.001143; todosabs<0.005 yrel<10%. Paso continuo cambia0.000414.
**NO** convergencia conjunta/campo/otrasvariantes; solo estosgates para96.
Segundo solver radial deClaude no valida la sección angular discreta.

Conclusión local acotada: trazos escasos pierden el comportamiento del
anillo continuo; densificar o cambiar fuerza índice modifica mucho la
transferencia. La variante96 se acerca al ideal con menos trazos que192,
pero no se ha medido coste de fabricación ni pérdida porcm física.
No monotonicidad general demostrada; no elegir óptimo universal de esta tabla.
No cubo fabricado, red3D, GPU/RT ni ventaja frente a otras redes.

## Revisión Claude recibida005

Confirma signos/unidades deBPM, aporta oracle radialFD/ECS y refinamiento
dz. Se incorporó dz2.5 antes007. Retira su umbral de media y corrige2facetas
portrayectoria. Sus porcentajes y tasas modales son resultados de otro
modelo numérico; los scripts se leyeron, NO se ejecutaron sus escritores.
Solicitada convergencia firmada de gamma por modo: abs en loss puede ocultar
signo y la salida actualmodes.json omite gamma_im. No se afirma que exista
un modo de ganancia, solo que no puede descartarse con esos JSON.

20testspropiosCPU PASS0.907s. JEVsecurityblocked, fallbacklocal sin aval.
Crítica angular/trazos solicitada008;006aespesor correspondeClaude.

Auditor de informes verifica10casos/4gates, presupuesto ySHAlineage,
NO sustituye segundo solver. Se detectó que Git normalizabaCRLF deJSON:
SHAparent en disco3e838d5b... vsblob8de21e73.... Se marca evidenciaJSON
como -text yversiona bytesoriginales. Verificados seisJSONpropios delíndice:
bytes/SHA idénticos aldisco, incluida evidencia original003/004/007;
se conserva su historia previa. Whitespace CR-at-EOL no altera losbytes.
No cambiar SHA en informes para acomodar la normalización.

Después de la revisión006a:22testsCPU PASS0.769s, incluidas dosregresiones
del radio efectivo de la retícula radial. No se repitió la propagación007.
