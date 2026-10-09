# M2-R1: continuación registrada tras el fallo operativo M2

El controlador M2 original terminó a las 01:53:07,426068 UTC del
9 de octubre, con 32 tramos Padé y 51 Radau, por el límite de espera
acumulada de memoria de 900 s. Su execution.json y sus fuentes permanecen
intactos. La auditoría parcial independiente aprobó los 83 campos y las
25 fuentes congeladas; todavía no existe dictamen temporal completo.

Hipótesis: completar únicamente Radau 52–64 permite evaluar los cinco
criterios temporales originales de la malla intermedia. El resultado podrá
ser positivo o negativo; no se cambia ningún criterio tras verlo.

La recuperación comienza sólo después del fallo confirmado, la auditoría
parcial aprobada, las comprobaciones del controlador/auditor nuevos y la
publicación verificada de este protocolo en la rama y PR existentes.
Se ejecuta el trabajador original M2 con el manifiesto original, la misma
entrada, matrices, pasos, formato complex128 y fuente por hash. Se retienen
los 83 campos, sin volver a propagarlos. No se cambia la primaria Padé.

Se permite CPU estándar Colab en un cuaderno nuevo y separado, si los
recursos reales y las versiones NumPy 2.2.6, SciPy 1.15.1 y psutil 6.1.1
coinciden. Sin compra de recursos. Sólo se transfiere el paquete científico
revisado publicado en la rama autorizada. El control X1 histórico demuestra
reproducción limitada de esta familia entre plataformas; no certifica
anticipadamente los trece tramos nuevos ni el error frente al continuo.

Se conservan **todos los límites originales**: reserva previa >6 GiB,
guardia inicial/final del trabajador >3 GiB, disco >2 GiB, un hilo,
hijo <=360 s y corte externo 370 s. Presupuesto global 22000 s desde
2026-10-08T22:55:32,699189 UTC, incluidas interrupción, preparación y
transferencias. No se permite ninguna espera adicional por recursos:
el presupuesto de espera original está agotado, aunque wait_s en el
informe no incorpora la última espera interrumpida. Una insuficiencia
en la comprobación de recursos detiene y conserva la recuperación.

La ejecución original y la recuperación tienen manifiestos e informes
distintos. Los campos nuevos completan exclusivamente las posiciones
ausentes de la carpeta original; no sobreescriben ni el fallo ni los datos
conservados. Se verifica la cadena CP51 -> CP52 y todas las posteriores.
No ajustar fases ni renormalizar salidas. El evaluador original calcula
campo relativo en norma de masa <=1e-4, ambas diferencias de potencia
<=1e-6 y ambas cotas PSD <=1e-5, simultáneamente.

Antes de nuevos campos: control estructural del controlador y auditor,
rechazo de dependencia sin fallo confirmado, de recursos insuficientes,
de campos existentes y de presupuesto agotado. Son controles de software,
sin datos sintéticos presentados como resultados ópticos. Reutilizar por
hash los controles densos, trabajador y evaluador M2 ya aprobados.

Después: auditor independiente que recalcula los 96 campos y los cinco
criterios, comprueba ambas plataformas/recursos, las 83 reservas históricas
y las 13 nuevas, las cadenas, hashes, tiempos y el límite original. El
transporte de resultados exige SHA-256 y CRC, extracción segura a carpeta
nueva y comprobación antes de incorporar únicamente archivos ausentes.

JEV: fallback local explícito; doctor local ready, bloqueo remoto retenido.
Una eventual aprobación M2-R1 permite registrar h=0,35 con K16, y no cierra
por sí misma la convergencia espacial, la predicción ni el dominio. La
tarea 1 sigue abierta y las tareas 2–22 no se inician.
