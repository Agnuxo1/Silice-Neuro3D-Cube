# G2: recuperación operativa de G1, sin cambiar ciencia

Registro 2026-10-07 después del fallo confirmado y antes de nuevos pasos.
G1 falló en el hijoN640 previsto4600→4800: ejecutó195 pasos y alcanzó31s
de reserva interna. Guardó campo parcial4795, informe y logs; RAM/disco
muestreados superaron límites. No se observó fallo numérico en ese informe.
G1 execution permanece FAILED, sin editarlo ni reetiquetarlo como completo.

G2 reutiliza las ocho trayectorias terminadas (cuatro nuevas+cuatroE),
el input/geometríaN640, la predicción registrada ANTES de G1N640 y los23
checkpoints completos N640 hasta4600. No usar el campo parcial fallido.
Volver a calcular sólo los1800 pasos restantes desde el último checkpoint
completo. Esto repite195 pasos fallidos por necesidad operativa confirmada,
no relanza E ni las simulaciones ya completas. Carpeta nueva G2; conservar
todos los datos G1 y enlazar hashes de ejecución fallida y último checkpoint.

Mismo ADI/backend/modelo/dz/detector, fuentes originales congeladas40f46d0.
Único ajuste operativo: nuevos hijos100pasos en vez de200, con los mismos
límites31s+reserva4s,35s interno/40s externo, RAM>1.5GiB/disco>2GiB,
muestreo cada20pasos, un hilo. Presupuesto recuperación900s. Stop al primer
fallo, sin retry automático. Ningún criterio científico cambia.

Evaluador copia de G, sólo verifica cadenas mixtas100/200; mismo assess_values,
cuadraturas, límites, Gaussianos y comparaciónN640. Auditor adicional copia
de G, admite esos pasos y contrasta todas las identidades/dz/steps/arrays/
potencias/hashes/recursos. Verificar que fuentes/inputsE/G1 permanecen
inmutables. Predicción original inmutable, no recalcular con campo parcial.
Retener por separado G1FAILED operativo y dictamen científico G2.

Congelar contrato/runner/evaluador/auditor antes de continuar. H sólo inicia
tras recuperación G2 terminada y auditada; G2FAIL científico no impide H,
pero tampoco cierra punto3. JEV fallbacklocal, bloqueo heredado preservado.
