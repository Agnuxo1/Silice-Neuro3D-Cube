# L2: precisión directa en dos mallas, sin afirmar orden cuatro

Nuevo registro tras L1 completo/auditado y negativo. L1 conserva TODOS
sus criterios y FAIL. La precisión de su paso fino motiva una hipótesis
distinta: precisión práctica del integrador en casos fijos, sin inferencia
de orden temporal ni espacial. No cierra punto3.

Reutilizar N626L1/12800pasos y ambas referencias K62611/17 por hash.
ÚNICA trayectoria óptica nueva: N400, entrada E/H ya auditada, z2mm,
12800pasos,dz0,15625um,32chunks400. Referencia primaria H R8 y controlR4.
No nueva geometría ni otro input físico. N400 elegido por existencia de
referencia y coste fabricado22,612s/100pasos; N64060,370s/100pasos no
se propaga. La selección se realiza antes de calcular potencia FDST N400.

Condiciones: L1integridadPASS/ejecución completa/fine_accuracyPASS y
orderFAIL; controles kernel/matriz conocida/bench400PASS; H2auditoríaPASS.
Adaptar exclusivamente los tres literales626 del worker L1 a400; preservar
el archivo original, guardar AST generado y su hash antes del primer paso.
CPU1, presupuesto7200s (coste previsto~2900s), hijo360/corte370,
RAM>1,5GiB/disco>2GiB. Fuentes/inputs/referencias/manifiesto congelados.
No repetir E ni ninguna trayectoria completa. Auditar32campos/cadenas.

Criterios prácticos en AMBAS mallas, definidos antes de N400 nuevo:
1. Campo fino relativo a la referencia primaria<=1e-4, sin phasealign.
2. Diferencia de potencia<=1e-6 en ambos detectores bilineales K.
3. Cuadratura16/32 cambia<=1e-10; referencias de campo difieren<=1e-9.
4. Cota de diferencia del observable respecto al campo de referencia,
   más el control de consistencia de referencias y cuadratura,<=1e-5.
5. Todos los hashes, finitos, balance porchunk<=1e-9 y recursos pasan.

Fundamento de4: funciones bilineales phi_i no negativas y partición de
unidad en el disco interior. Integral total de cada hat<=dx². Jensen da
||D||<=dx² para el operador de potencia de campo; para intensidad nodal
las ponderaciones diagonales también<=dx². Cauchy-Schwarz implica
|P(A)-P(B)| <= dx²*(||A||+||B||)*||A-B||/P_in.
Se evalúa con las normas crudas. Es una cota RESPECTO A LA REFERENCIA
COMPUTADA, no una cota de error contra el continuo. La diferencia entre
referencias y la diferencia de cuadraturas siguen siendo controles
empíricos; no convertirlos en una garantía probabilística ni exactitud
ilimitada. Se registra la discrepancia de potencia de K626 (~3,91e-10)
y su FAIL anterior; este estudio usa el control de campo y lo incorpora.

Si algún criterio falla, retener FAIL. Un PASS sólo respalda precisión
práctica en estos dos casos y permite diseñar un estudio espacial aparte
con controles propios. No declara orden4 T96, no convierte L1 en PASS,
no acepta retrospectivamente E/G/H/K ni habilita el barrido modal.
JEVfallbacklocal por bloqueo heredado; checkout principal preservado.
