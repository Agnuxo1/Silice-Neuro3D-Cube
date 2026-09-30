# GLASS-003-v2 — observable de confinamiento y refinamiento

2026-09-30. Prospectivo, posterior al fallo V1, anterior al ensayo V2.
V1 queda congelado en6f1db10: su fallo NO se convierte en aprobación.

Hallazgo de V1: fracción de potencia en núcleo/potencia superviviente
dependía del dominio porque el amortiguador retiraba radiación exterior.
V2 cambia a `potencia_nucleo_final/potencia_total_entrada` y registra ambas.
No renormalizar después de pasos ni interpretar potencia removida como
absorción del material. Solver bpm.py sin cambios.

Para camisa6um, radio6um, lambda1550nm, n0=1.444, cintura6um y z2mm:
explorar delta_n=-0.001/-0.003/-0.005 (todos supuestos). Por cada contraste
simular 96/144/192um a dx0.75um; comparar última pareja144→192. En el
dominio96, comparar dz10→5um y dx0.75→0.5um. Esto son15casos, no red3D.
Las variaciones temporales/espaciales en dominio96 son gates parciales,
NO convergencia combinada en el dominio más grande. No atribuir modos
propios, pérdidas porcm ni óptimo global a esta exploración.

Gates: balance<1e-10; cambio relativo de potencia_nucleo/input<0.10 Y
cambio absoluto<0.005 para cada refinamiento. Si el valor de referencia
<1e-6, reportar sin certificar por gate relativo. No relajar tras ejecución.
Todos los casos/fallos se retienen. No seleccionar solo el ganador.
Guard CPU40s, grids<=256²,steps<=1000. NoGPU/Blender.

Control negativo de guiado: comparar con vidrio uniforme V1 solo como
orientación porque la frontera/domino difiere. No usar ese contraste como
comparación final hasta un ensayo uniforme en mismo dominio. Siguiente
ensayo debe ser segundo solver/modelos de trazos y modos reales.
