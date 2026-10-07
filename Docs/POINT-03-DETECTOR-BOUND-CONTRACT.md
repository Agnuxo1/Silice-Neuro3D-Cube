# Verificación algebraica de la cota del observable

Registro antes de calcular, separado de las trayectorias T96. No cambia
L1/L2 ni sus criterios. Verificar la premisa de la cota que usa L2 con
N400/N626 y ambas cuadraturas16/32 del detector ya congelado.

Construir matrices del observable a partir de las cuatro funciones hat
bilineales, por un camino algebraico distinto a la contracción de campo
de Detector.measure. Momentos originales de cada celda usados como datos.
Comprobar: matrices locales4x4 semidefinidas positivas, entradas>=0 y
ponderaciones de intensidad>=0 dentro redondeo1e-12 relativo a dx²;
máximo de sumas de fila global<=dx²*(1+1e-12), diferencia de suma de
fila y pesos intensidad<=dx²*1e-12. Área disco relativa<=1e-12.

Cuatro pares de campos complejos fabricados por N, semilla917, sin T96:
energía calculada con matriz y Detector.measure difiere<=1e-12; ambas
variaciones de potencia respetan dx²*(normA+normB)*norm(A-B), tolerancia
de redondeo1e-12. Normalizar sólo el inputA fabricado a potencia1; B es
una perturbación y no se normaliza. No lectura de campos ópticos nuevos.
CPU1, presupuesto120s. Guardar resultados y FAIL si aparece. El teorema
acota diferencia respecto a un campo computado, no el continuo exacto.
