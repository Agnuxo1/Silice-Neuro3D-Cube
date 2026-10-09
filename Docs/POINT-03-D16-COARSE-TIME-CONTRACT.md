# D16-C1: nuevo control longitudinal con cuadratura validada

La matriz histórica K8 y todos sus ensayos se conservan. Se inicia una
familia distinta, identificada por el hash de K Duffy16. No se prolonga
el presupuesto agotado de P4I3 ni se cambia retrospectivamente su dictamen.

Primera malla: h0,546875µm, dominio±64µm, geometría/masa/entrada/detector/
amortiguación existentes e intactos. K procede de
point03_fem_duffy_coarse_retry_20261008/stiffness_duffy16.npz,
SHA25651a273ef6a14dbcc425e1d5f22820963c2c9bc219f26fa56447115b06acef981.
Su control Duffy16–24 y los controles geométricos previos deben aprobar.

M a'=B a, B=-i K/(2 n0 k0)-i k0·0,003 Cclad-D, n0=1,444,
lambda_vacío1550nm. Entrada gaussiana proyectada existente, potencia
inicial1; propagación2mm. Sin ajustar fase ni renormalizar salidas.

Dos soluciones completas y primarias fijadas antes de resultados:
Padé[3/3]32768pasos y Radau[2/3]32768pasos. Tramos1024pasos,
32 por solución, cada hijo aislado. Los métodos ya tienen controles
manufacturados; se ejecutará además un control denso del nuevo evaluador.

Criterios simultáneos conservados: diferencia relativa en norma M≤1e-4;
ambas diferencias de potencia≤1e-6; ambas cotas PSD≤1e-5. Observables:
campo cuadrático Ccore y reconstrucción nodal de intensidad w.
Las diferencias entre familias son consistencia práctica, no error
absoluto demostrado frente al continuo. No seleccionar el observable
favorable. La auditoría independiente recalculará todos los campos,
potencias, cadenas y dictamen, también si el resultado es negativo.

Recursos: un hilo; reserva previa≥4,5GiB, guard durante/final>3GiB,
disco>2GiB. Hijo≤360s, corte370s, global22000s desde lanzamiento,
incluidas interrupciones. Espera previa total≤900s. Esta reserva nueva
corresponde a una malla menor y un experimento distinto, sin alterar el
guard3GiB ni el contrato antiguo. Una parada conserva datos y no permite
ampliar límites; no reanudar automáticamente ni sobrescribir salidas.
Se permite CPU local o CPU estándar Colab autorizado: fijar dependencias,
verificar hashes y entorno antes de ejecutar. Sin GPU ni recursos de pago.

Si aprueba y la auditoría confirma, registrar el ensayo de la malla
intermedia; si falla, conservarlo y diagnosticar antes de un nuevo contrato.
No generar h0,28 ni calcular una predicción espacial con datos mezclados
K8/K16. Esto sigue dentro de tarea1/punto3, que no se cierra con este control.
Las tareas2–22 permanecen pendientes. JEV fallback local, sin aval remoto.
