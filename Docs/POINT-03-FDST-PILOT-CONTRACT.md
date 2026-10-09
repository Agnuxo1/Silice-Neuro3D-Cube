# Piloto temporal FDST N626: registro previo

Objetivo: contrastar el integrador DST de cuarto orden con la referencia
Taylor en la misma malla y operador FD. No es un nuevo estudio espacial
ni cierra el punto 3. K626 y todas las evaluaciones anteriores se conservan.

Requisitos antes de propagar: controles fabricados del kernel PASS,
integridad K626 PASS, ejecución K626 completa aunque científica FAIL.
La prueba de coste fabricada N626/100 pasos tardó 18,2423 s; error de campo
2,54118e-13. El campo era un modo seno de índice alto, sin perfil T96.
El metadato source_sha256 de esa salida contiene un nombre de módulo por
error; una auditoría separada registra el hash real, sin editar la salida.

Entrada única: n626_input.npz ya auditado en K626,
SHA256 c650f50e792d7062ed843f9d28241968406cb7bc10492d6e6527f0d7df82b81a.
Mismo dn, sigma, A0, dx=128um/626, z=2mm, lambda=1550nm, n0=1,444,
ghost cero. No modificar física, normalizar salidas ni alinear fase.

Tres trayectorias nuevas: dz=0,625/0,3125/0,15625um, respectivamente
3200/6400/12800 pasos. Chunks de 400 pasos, 8/16/32 checkpoints.
No relanzar una trayectoria completa. Fuentes y manifiesto congelados
antes del primer paso; cada checkpoint enlaza el anterior mediante hash.
CPU un hilo, RAM disponible>1,5GiB y disco>2GiB. Límite total7200s,
hijo360s y corte370s. Error operativo se retiene y detiene el piloto.

Antes de evaluar, auditar TODOS los campos, hashes y cadenas; finitos,
complex128, potencia cruda positiva y no aumenta más de1e-9 por chunk.
El amplificador local de subetapa negativa debe ser<=1,10.

Medir dos detectores bilineales del contrato K, cuadraturas16/32 con
diferencia<=1e-10. Referencia óptica K626 R17 primaria; R11 se informa
también, sin escogerlo retrospectivamente. Reconocer su discrepancia de
potencia~3,91e-10: no declarar la referencia exacta a ese nivel.

Criterios del piloto, independientes del cierre espacial:
1. Error relativo del campo fino frente R17<=1e-4, sin phasealign.
2. Diferencia de potencia del nudo fino frente R17<=1e-6 en AMBOS métodos.
3. Errores de campo y ambos errores de potencia positivos y decrecientes
   en las tres resoluciones; orden log2(error grueso/error medio) y
   log2(error medio/error fino) entre3,5 y4,5 para las tres cantidades.
4. Integridad, potencia, recursos y cuadratura pasan en las tres.

Conservar FAIL si algún criterio falla. No atribuirlo sin controles
aislados. Un PASS sólo habilita considerar un estudio espacial nuevo,
preregistrado por separado. Nunca sustituye E/G/H/K ni sus criterios.

JEV: fallback local identificado por bloqueo remoto de seguridad heredado.
Checkout principal preservado; no GPU, instalaciones, push ni subagentes.
