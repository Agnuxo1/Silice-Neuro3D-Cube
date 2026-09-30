# Fallo de escritura NumPy y continuación sin repetir resultados válidos

Run2 bajo d7e5e95: continuo/48/96/192trazos guardados correctamente.
El quinto caso igualintegral produjo profile_gate NumPybool no serializable;
JSON quedó truncado. Retener bytes originales de ese archivo, no corregirlo.
Supervisor abortó al intentar leerlo; no existe agregado válido run2.
Valores de cuatro casos válidos:0.3617714304/0.1429217973/0.3310915334/0.3549428215.

Reparación prospectiva: convertir SOLO gate a boolPython; pre-serializar
antes de abrir archivo para no crear JSON truncado por TypeError; manejar
JSONinválido en supervisor. Añadir test del caso igualintegral con propagador
simulado. coverage.py/BPM/tracks/contrato científico permanecen byte-idénticos.

Continuación run3: leer únicamente los cuatro reports completos, exigir
hashes antes=después y todoslosinputs científicos idénticos, además del SHA
del runner antiguo verificado contra commitd7e5e95. Retener paths/SHA;
NO recalcular esos cuatro campos. Caso truncado permanece fallo histórico
y su cálculo se repetirá junto a ocho casos aún no ejecutados.
Mismos parámetros/gates/timeout30s; freeze repair antes de medir.

Coste run1=93.6372s retenido; run2 cuatro elapsed computacionales guardados,
pero el walltime agregado no se escribió. Declarar esta carencia, no inventar
coste end-to-end ni ventaja. Ninguna ejecuciónCPU pasada se convierte en
éxito operativo por la reparación. NoGPU/Blender/instalaciones.
