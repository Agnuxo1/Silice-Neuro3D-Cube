# SPEC-FEMTO1 — especificación preliminar para revisión

**NO FABRICAR.** F0/F3/F4/F5/F6/F7/F8 no están cerrados. Se conserva el boceto para corregirlo, no para enviar sus trayectorias a máquina.

Material objetivo: sílice fundida, lambda1550nm. Bloque supuesto45x25x2mm. Entradas4x4 con paso250um (por confirmar). Cuatro zonas: N1 entrenada nominal, N2 precompensación supuesta κ+10%, N3 control de prototipos normalizados con desplazamiento común por columna, N4 reparto uniforme. Cada zona tiene48acopladores de red; K1–K3 son controles de proceso adicionales. Radio de núcleos6um del análogo; MFD/índice/monomodo del proveedor no confirmados.

Fuente geométrica actual: `geometry_FEMTO1_candidate_v2.json` en SI, SHA256256beb164e5de411e728c111746c02694d4de7b8f852432eca7ee10aee17143d. La futura fuente definitiva será la geometría de propiedades científicas de Blender verificada y validada físicamente. Trayectorias de revisión en um, muestreo de curva<=10um. No se prescribe receta de láser.

Radio mínimo supuesto25mm; separación de distinto haz30um, margen de muestreo conservador10um. Los extremos útiles se agrupan por detector en cuadrícula4x4 de paso25um dentro de radio100um. La ruta provisional no resuelve el aislamiento ni coherencia. El descarte no debe acabar en una región interior sin terminación física de dispersión validada; los cupones deben ser accesibles desde puertos reales. Esas condiciones no están satisfechas.

Pesos N1: no negativos, suma por entrada<=1. Fracción media para entradas uniformes35,03%; para las imágenes de validación, media de(sumapotencias/sumaintensidades)29,35%, antes de pérdidas/acoplo, equivalente a unos5,32dB de reparto. Esto reemplaza solo para este modelo el ejemplo antiguo de46%/3,4dB. El presupuesto debe aplicar W y no contar dos veces el descarte.

Lectura: cuatro ganancias positivas y cuatro offsets en electrónica, ajustados con la partición de calibración de entrenamiento. Modelo completo se llama «chip +8parámetros electrónicos». El offset impide afirmar invariancia al brillo. Potencia y latencia son objetivos que deben medirse, no resultados demostrados.

Aceptación futura: C1 RMSrelativoW<=5%, fuga<=1%; C2 no inferioridad de3pp conIC95%pareado y>=2000imágenes; C3<=2ns entrada a salidaTIA a la potencia que permite C2; C4 razón modelada>=3 frente a cadena digital equivalente con coste total/fuente/frontera. PuertaF6:media>=85% también peor polarización, fuente<=10mW y sinobjecionesbloqueantes. No relajar después de medir.

Referencias y tolerancias por acoplador están en `coupler_specification.csv` del paquete de revisión. STEP/STL y reimportaciones CAD quedan pendientes del layout correcto/formatos confirmados. El manifiesto SHA256 de revisión no sustituye una firma ni una aprobación del titular.
