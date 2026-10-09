# GLASS-GPU-002 — refinement prospectivo, 2026-10-05

Pregunta: ¿refinar hasta dx=0.2um estabiliza los puertos COMPLEJOS del
acoplador, sin esconder la fase ni sustituirlo por una matriz?
Contrato local GPU-002-v1, fuentes congeladas antes de medir; sin
registro externo ni pretensión de publicación científica automática.
GPU-001 dobleprecisión pasó; simpleprecisión FALLÓ: NO se usa aquí.

Mismo perfil continuo ideal006b (union de camisas menos ambosnúcleos),
lambda1550nm/n1.444/a6um/t6um/D14um/dn-.005/waist6um/width128um/z1mm.
GridFine opt-in640, sin cambiar Grid/CellGrid ni CUDA001. Construcción
de geometría/detectores/Gaussianos por CPU; SSFM+presupuesto CUDA128.
Guardar input/dn/basis/detectores/output por caso y todos los hashes.

Ocho casos: 384L,512L,640L (400pasos/cobertura16);512R y512coherente
con los mismos parámetros;512L cobertura32;512L y640L con800pasos.
No repetir CPUantiguos: comparar320L con384L y sucesivos usando sus
JSON/NPZcongelados. Contrastes complejos puertos/potencia absoluta
sin alinear fase ni normalizar salida. Grid máximo640²/800pasos.

Gates prospectivos: último par512->640 máximoerrorpuerto/potencia<.005;
par400->800 en512 y640 <.005 porseparado; cobertura16->32 en512<.005;
simetría512L/R<1e-8 ylinealidadcampo512<1e-10; balance<1e-10;
ortogonalidadGaussianos<1e-12/detectorareaerror<1e-10. Todos necesarios
para aprobar SOLO estabilidad local de esta configuración, no convergencia
universal/orden ni fabricar cristal. Registrar cada parprevio aunque falle.
Dos contrapuntos CPU SSFM nuevos512L/640L, mismo input exacto, campo
relativo<1e-10; CPU no métodoindependiente, ADIClaude pendiente.

Guardgpuq exclusivo, mismo cutoff13:13:06UTC, hijo<=120s. RAM4GiB
tras presupuesto1GiB, VRAMtotal18GiB/80C. Estimación conservadora:
geometryCPU+campos<=512MiB; temporalesGPU+FFT<=512MiB, runtime/margen
restante dentro1GiB. Falla telemetría/deadline: abortar y conservarfallo.
Sin software nuevo ni cambios de modelosajenos. JEVblocked/fallbacklocal.
Tiempo exploratorio total yporcaso, no speedupinferenciacompleta.
Fracaso se conserva, no ampliar umbral después. Semilla7/determinista.
