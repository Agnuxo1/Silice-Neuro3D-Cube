# Controles analíticos del pronóstico y del auditor M1

Sólo potencias sintéticas P(h)=0,334+C*(h/h640)^p, p=0,5/1/2/3/6,
C=+/-1e-4. Sin leer campos ópticos M1 ni ejecutar geometrías.
Las funciones del controlador y del auditor deben recuperar p<=1e-8
absoluto. El pronóstico N767 desde400/500/640 debe diferir de la verdad
analítica<=1e-12. Constante, secuencia no monótona y orden negativo deben
ser rechazados por el controlador y producir None en el auditor.
No cambiar las fuentes ópticas ni los criterios según estos controles.
Este control adicional se registra durante M1, antes del dictamen final;
no se presenta como un prerequisito ejecutado antes de la propagación.
