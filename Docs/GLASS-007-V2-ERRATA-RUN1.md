# Fallo operativo propio antes de réplica V2

Contrato científico2439bf4 permanece sin modificar. Primera ejecución
`glass007_v2_run1.json`:13hijos terminaron con TypeError al construir el
diccionario de salida, por backend duplicado (campo explícito y **budget).
No se guardaron valores científicos válidos;13informesfailure_retained
permanecen y el agregado own_gates_pass=false. Tiempo total93.6372s,
suma hijos93.4842s; coste desperdiciado reconocido, no oculto.
FuentesBPM y geometría originales no se alteraron. Fuente del runner
fallido retenida en commit2439bf4, SHA f0abb77b02ed054f65e4f46ec9ad4efa973236eae220487ad11cefc414de1880.

Detectado durante la pasada, pero finalizó antes de detenerla; diagnóstico
posterior no encontró procesos propios vivos. No se mataron procesosClaude.
Corregir SOLO construcción del reporte y cortar futuros lotes ante fallo
operativo del hijo. Añadir regresión con propagador simulado que conserva
backend en budget; no mide física ni sustituye la réplica científica.

Nueva pasada con prefijo run2, congelar corrección ANTES de medir. Mismos
13casos, parámetros, gates y30s porhijo, sin caché/coste excluido. Es una
réplica tras fallo de software sin resultado guardado, no una repetición
silenciosa de casos científicos aprobados. Conservar primer lote íntegro.
