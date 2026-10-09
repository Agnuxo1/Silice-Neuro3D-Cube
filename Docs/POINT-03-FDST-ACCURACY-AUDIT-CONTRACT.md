# Auditoría de L2, antes de completar la trayectoria

El auditor no invoca `assess` ni `contrast` del controlador L2. Relee los
32 campos crudos, las cadenas de hashes, entradas y referencias congeladas;
recalcula normas, balance y todos los criterios del contrato L2 mediante
NumPy y el detector bilineal previamente validado. Comprueba también los
códigos de salida y límites de cada hijo. Conserva el fallo L1.

Las tolerancias son las del contrato L2, sin cambios: campo 1e-4,
ambos errores de potencia 1e-6, consistencia del campo de referencia 1e-9,
cuadratura 1e-10 y cota relativa a la referencia calculada 1e-5.
La concordancia del auditor con el informe exige diferencias <=1e-12.

Esta es una comprobación independiente del evaluador, pero comparte NumPy
y el detector validado; no constituye una nueva solución electromagnética.
Incluso si L2 pasa, el punto 3 permanece abierto: no demuestra convergencia
espacial ni convierte el orden observado de L1 en un resultado positivo.
