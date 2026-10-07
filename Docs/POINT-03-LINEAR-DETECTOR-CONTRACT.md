# K: detectores lineales y prueba prospectiva adicional, dentro del punto3

Registro2026-10-07 antes de medir potencias con las nuevas reconstrucciones.
H2 sigue calculandoN640; sus campos finales no son conocidos. E/G y los
resultados de detectores cúbicos sí son conocidos. Mantener esos dictámenes.
No modificar física/entradas/solver ni fuentesH2. J sigue sólo diagnóstico.

Hipótesis: un funcional con error de reconstrucción de segundo orden
conocido permite una estimación coherente de convergencia de potencia.
La reconstrucción lineal puede tener mayor error por malla que la cúbica;
no se presenta como aumento de precisión. Ambas aproximan la misma
integral continua del núcleo si los campos convergen. No acredita campo/
fase/frontera ni perfiles medidos. No basta para cierre sustituir un detector
por otro después de conocer su resultado: se exige una prueba nuevaN626.

## Dos representaciones y momentos

1. Interpolar bilinealmente el campo complejo nodal y integrar |A_lin|².
2. Interpolar bilinealmente |A_nodal|² e integrar I_lin.

Cuadrados de la malla entre nodos, no celdas centradas. El núcleo sigue
discoR6um. Integrar mediante sus nueve momentos locales t^p u^q, p,q0..2.
Rectángulos interiores: h²/[(p+1)(q+1)]. Parciales: dividir en cruces con
y0/y1 y transformar x=Rsin(theta), integrar y polinómicamente, Gauss–Legendre
16/32 en theta. Comparar ambas precisiones, error por momento<=1e-13
normalizado al disco, área global relativa<=1e-12. No clipping/padding/
alineación de fase ni normalización de salida. Dividir por P_in original.

Verificación previa: círculo constante; campo afín x+iy y bilineal conxy
contra momentos exactos; densidadbilineal positiva con integral exacta;
16celdas parciales seleccionadas uniformemente antes de discrepancias,
contraste independiente adaptivequad en x<=1e-10 de área local. Verificar
Jensen P_campo<=P_intensidad+1e-12 en todos los controles y resultados.

## Controles de precisión y registro previo

Gaussianascontinuas normalizadasw6um con fase exp(ikx), k0/2e5/4e5 m^-1,
N256/320/400/500/640. VerdadPcore=1-exp(-2), independiente de fase.
Exigir para ambas reconstrucciones órdenespositivos/estabilidad20%, residual
N500<=10% último incremento, y que indicadorRichardson conFs1.25 cubra
el error exactoN500. No imponerles error1e-6 por malla: el método es de
segundo orden y el presupuesto de la óptica se comprueba por separado.
Retener todos los controles, incluidos los fallidos. Congelar fuentes y
contrato antes de medir nuevos observables ópticos; no propagaciónK todavía.

## Óptica, predicciones y aceptación

PrimariasN256/320/400/500: referenciafinaH1 R8. Dos métodos por separado.
Exigir mismos criteriosespaciales positivos, estabilidad20%, predicciónN500
10% del incremento que H. Usar fórmula última terna para extrapolar aN640
yN626; congelar ambas predicciones ANTES de medir los campos finalesN640
y ANTES de cualquier preparación/propagaciónN626. H2N640 ya iniciado se
declara: la comprobaciónK640 es de un nuevo funcional, no nueva trayectoria
independiente. No usarN640 para ajustar la predicciónN626.

Después de H2completo y auditado, evaluar ambos detectores en referencia
H2640R17. Exigir residualK640<=10% de|P640-P500|. Estimador másfino:
u_space640=1.25*|P640-P500|/(1.28^p_ind-1), p_ind=min(p_último,2).
ReferenciaP640 correspondiente a cada método. ErrorADI directoP640<=1e-6;
consistenciaH2Pcore reconstruida<=1e-10. Diferencia de momentos16/32<=1e-10.
Sumar u_space640+errorADI+|P_campo-P_intensidad|640+errorcuadratura+errorref;
para ambos exigir<=1e-3 y<=1%P640. Estos son indicadores condicionales,
no cotas rigurosas. Los límites anteriores que no se aplican a reconstrucción
lineal se conservan en H/G, no se cambian retroactivamente.

Sólo si pasan controles, primarias yK640, y H2 no cerró ya el punto3,
preparar una nueva referenciaN626 con el mismo modelo128um/z2mm y geometría
analítica D. Verificar las mismas48celdas/área/entrada que G. Dos particiones
11/17, worker exponencialH1 inmutable, consistenciarel1e-9/Pcore1e-10.
El estudioN626 tiene presupuesto7200s/hijos360–370s, CPUunhilo/RAM>1.5GiB/
disco>2GiB; conservar checkpoints y fallos. No reanudar automáticamente.
Fuente/modelo/entradas/criterios se congelan de nuevo antes del primer paso.

ProbeN626 verdaderamente nueva: congelar predicción desde320/400/500
con exponente registrado; residual<=10% de|P626-P500| en ambos métodos.
No refit ni escoger entre casos. Exigir consistencia/positividad/integridad
y presupuestos640 anteriores. Aceptación local del punto3 sólo si pasan
TODOS estos criterios y el nuevo probe. E/G/H2 conservan PASS/FAIL propios.
Si H2 pasa ya sus criterios, no añadir propagaciónN626 por costumbre: K
queda diagnóstico de detector y el cierre es el alcance H validado.

No crear N626 ni nuevos arrays de propagación mientras H2 está activo.
No ejecutar barrido modal ni posteriores antes de cierre. JEV fallbacklocal
identificado, bloqueo de seguridad remoto heredado, mainpreservado.

Marco de convergencia: [NASA](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html).
Una estimación por refinamiento no constituye medida física ni prueba de
cobertura probabilística; observados altos se limitan a2 como indicador.
