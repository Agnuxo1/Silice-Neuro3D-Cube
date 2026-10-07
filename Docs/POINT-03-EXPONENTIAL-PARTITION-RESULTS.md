# Resultado del diagnóstico de particiones internas

Registro previo b8a062e; ejecución 2026-10-07T10:10:25 UTC, 19,705s.
Sin acción exponencial ni nuevos campos. SciPy1.15.1/entradas congeladas.

| N | Particiones | Grado máximo m_star | Subincrementos por tramo s | Longitud interna nominal (µm) |
|---:|---:|---:|---:|---:|
|500|4|55|264|1,893939393939394|
|500|8|55|132|1,893939393939394|
|640|11|55|158|1,1507479861910242|
|640|17|55|102|1,1534025374855824|

La reconstrucción de selección confirma incremento nominal idéntico en
N500R4/R8. En N640R11/R17 difiere relativamente 0,002301496 (0,23015%).
Se precisa así la dependencia anticipada durante la revisión del código.
No se instrumentaron términos realmente usados por cada hijo: el bucle
Taylor puede parar antes del grado máximo dependiendo del campo.

No atribuir independencia algorítmica a las particiones; tampoco interpretar
igualdad de resultados como dos confirmaciones independientes. La referencia
exponencial sí usa un algoritmo distinto del ADI. No hay cota certificada
de su error óptico continuo. Los criterios H2/K registrados se mantienen.

Evidencia completa: `resultados/codex/point03_exponential_partition_diagnostic_20261007.json`,
incluye hashes de entradas, manifiesto y fuente SciPy seleccionadora.
