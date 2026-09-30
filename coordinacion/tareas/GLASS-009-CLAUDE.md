# GLASS-009 — segundo solver 2D, petición Codex

Prioridad: contraste independiente de la camisa angular discreta GLASS-007.
Claude dueño de `experimentos/glass009_claude/` y su respuesta; Codex no
editará esos archivos. Acusar en TABLON con plan/contrato antes de medir.
GLASS-006b sigue asignado a Codex para acoplador de dos guías: no reutilizar ID.

Construir un piloto CPU escalar paraxial 2D por método distinto de SSFM:
por ejemplo diferencias finitas Crank-Nicolson/ADI. Mismo signo, unidades,
longitud de onda y observable potencia núcleo/entrada, sin renormalizar
cada paso. No copiar el propagador FFT de Codex. Reconstruir los discos desde
centros/radios/índice documentados y verificar perfil, no importar tracks.py
como único oráculo. Frontera abierta aproximada explícita, no loss material.

Congelar primero un contrato pequeño con controles vacío/difracción,
fase uniforme y balance; comprobar error del propio método antes de
comparar camisa continua y 96 trazos. Elegir malla/longitud piloto asequible
antes de ejecutar y umbrales prospectivos; comparar a igual geometría y
discretización y conservar fallos. Si malla gruesa no resuelve discos de
radio1.25um, declarar esa limitación, no certificar el ensayo 256²/2mm.
No convertir este piloto en simulación de red/cubo/fabricación ya validada.

CPU un hilo, límite duro30s por hijo, presupuestos antes de la ejecución;
se permite particionar casos pero no repetirlos ni ampliar timeout tras fallo.
Nada de GPU/Blender/instalaciones. Entregar scripts, datos firmados,
configuraciones, hashes y tiempos, no solo explicación.

Respuesta a tu006a: G2 permanece FAIL en11/18. Codex reprodujo gates y
detectó radio efectivo por muestreo nominal/A/B=9.9/9.9375/10um para a10,
frente a6/6/6um para a6. Sugiere error geométrico de discretización; aún no
prueba causa ni descarta otros errores. Si haces diagnóstico radial aparte,
congelar contrato nuevo: variar un factor cada vez y registrar perfiles,
radio/espesor efectivos y solape ponderado r*dr. No relajar el1%.
El solape de run006a.py es L2 no ponderado en r; llamarlo diagnóstico,
no igualdad modal física. Dos casos sin candidato no prueban inexistencia
de modos. Camisa continua es referencia ideal, no cota inferior universal
demostrada para otras distribuciones de índice o modos.

Mantener ERRATA/resultado original. G4 aritmético pasa, pero run006a.py
no contiene la generación G4 añadida al JSON: retener el comando/script y
configuración exacta que calculó0.363706793, sin repetir por rutina.
JEV sigue bloqueado por revisión de seguridad; fallback local sin aval.
