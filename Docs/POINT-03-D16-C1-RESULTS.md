# D16-C1: ejecución íntegra, precisión temporal negativa

El ensayo de la malla h0,546875µm con K Duffy16 terminó en7621,698s.
Padé32768 y Radau32768 completaron2mm cada uno:64tramos de1024pasos,
65536pasos en total. Las auditorías Linux y Windows confirman integridad
y dictamen, con máximo residuo de potencia de los informes igual a0.
La tarea1/punto3 sigue abierta y ninguna malla posterior se lanzó.

| Criterio | Medido | Límite | Resultado |
|---|---:|---:|---|
| Diferencia relativa del campo en normaM | 1,8853079e-5 | 1e-4 | Aprobado |
| Diferencia de potencia, campo | 3,2896483e-9 | 1e-6 | Aprobado |
| Diferencia de potencia, intensidad | 1,8441870e-7 | 1e-6 | Aprobado |
| CotaPSD del observable de campo | 6,7681995e-6 | 1e-5 | Aprobado |
| CotaPSD del observable de intensidad | 1,3491078e-5 | 1e-5 | Fallo |

No se descarta el observable que falla ni se ajustan sus límites. Las
cotasPSD miden discrepancia entre soluciones, no error absoluto probado
frente al continuo. El resultado temporal es negativo aunque las diferencias
directas de potencia sean pequeñas. No se atribuye la causa a fabricación
o al modelo vectorial, que todavía no han sido contrastados.

Potencias fraccionales, entrada normalizada auno:

| Solución | Campo | Intensidad reconstruida |
|---|---:|---:|
| Padé32768 | 0,3329298439715965 | 0,33238268314436925 |
| Radau32768 | 0,3329298406819482 | 0,3323828675630689 |

## Recuperación y procedencia

El ZIP contiene198archivos,30429527bytes y SHA256
154c97d008acb69c766cd4e802e932e42317f4b7a42e1b6cf985b0374e83064e.
CRC y archivo completo verificados. Se recuperó mediante salida visible
del cuaderno HTTPS:7bloques iniciales64KiB y rangos posteriores dehasta
512KiB, comprobados antes de escribirlos. No se modificó ningún campo.
El auditor remoto y todos los informes originales permanecen intactos;
la auditoría Windows se guarda por separado como local_integrity_audit.json.

El selector de carga incrustado falló y se conservó su AssertionError;
la carga por panel de archivos sí terminó. La descarga habitual no entregó
ruta local verificable. La petición de visitar chrome://downloads fue
rechazada por política de protocolo; no se accedió a esa página o historial.
La alternativa de salida visible sólo leyó el ZIP científico autorizado.
Un intento de reemplazo del índice con fill añadió texto en el editor;
se corrigió mediante selección completa. Índices/tamaños y SHA final
impidieron adoptar bloques erróneos. Estos incidentes son de transporte,
no fallos o aprobados de la propagación.

## Reproducción limitada entre plataformas D16-X1

Referencias Windows: primer1024pasos de cada familia,62,5µm; sin repetir
otro ensayo completo. Duraciones72,003s y71,306s. Tras recuperar Linux:

| Familia | Campo relativo en normaM | Diferencia potencia física | Resultado |
|---|---:|---:|---|
| Padé | 1,7703663e-14 | 1,8873791e-15 | Aprobado |
| Radau | 1,7743073e-14 | 3,4416914e-15 | Aprobado |

Límites fijados1e-10 y1e-12. Es reproducción del primer tramo, no validación
experimental ni demostración de error absoluto del dispositivo.

## Siguiente ensayo, sin alterar este negativo

D16-C2 registrado en3de7556: únicamente Radau65536 nuevo y Padé32768
retenido por hash, mismo operador y datos, mismos límites. Trabajador
manufacturado3DOF y rechazo de hash corrupto aprobados. La malla intermedia
M1 queda sin iniciar porque su requisito C1temporalPASS es falso. Si C2
aprueba, su nueva dependencia deberá registrarse antes de campos posteriores.
JEV fallback local por bloqueo heredado; ningún aval físico o Nobel atribuido.
