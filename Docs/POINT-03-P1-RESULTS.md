# P1: influencia de bordes discretos confirmada en el caso N400

Ensayo registrado `45545e3`, terminado en551,961s sin relanzamiento ni
error operativo.12tramos nuevos5/7; referencia original H2 N400 reutilizada
por hash. Auditor separado:integridad y precisión aprobadas, hipótesis de
cambio despreciable refutada. El punto3 sigue abierto.

| Observable | Dominio histórico | Fantasmas fijos±64µm | Cambio absoluto |
|---|---:|---:|---:|
| Campo bilineal | 0,332517364396726 | 0,332445023532911 | 7,23409e-5 |
| Intensidad bilineal | 0,332674767505038 | 0,332602421297077 | 7,23462e-5 |

Límite prospectivo1e-6:FAIL en ambos métodos, por factor~72,34.
Los arrays físicos interiores, el espaciado0,32µm, trazos, detector y
amortiguación no se movieron. Se retiró la primera fila/columna para
pasar de fantasmas[-64,32;64]µm a[-64;64]µm. La potencia inicial retirada
está por debajo de1e-12. No se renormalizó salida ni se alineó fase.

Concordancia de referencias:campo relativo1,84626e-10; ambas potencias
~1,057e-11; cota del observable por normas2,83205e-10. Cambio entre
cuadraturas5,55112e-17. Auditor verificó12campos y6fuentes; máximo
residuo de potencia total2,77556e-15. Control previo de submatriz principal
exacto; seno amortiguado con fase/potencia analíticas a2mm PASS.

La posición de los bordes discretos tiene una contribución medible en
esta configuración, muy superior al presupuesto práctico registrado.
Por tanto, no era legítimo presumirla despreciable al interpretar todas
las diferencias entre mallas como error espacial interior.

No identifica toda la causa de M1 ni cuantifica otras mallas, retornos del
absorbedor o la frontera física del dispositivo. P1 no cierra el hito
general de frontera/campo/fase. Los datos justifican el estudio P2 con
fantasmas físicos idénticos en toda la serie; sus criterios se mantienen
prospectivos y ningún FAIL anterior se revoca.

Evidencias:`resultados/codex/point03_fixed_domain_20261007_P1/`.
JEVfallbacklocal por bloqueo heredado, sin aval remoto nuevo.
