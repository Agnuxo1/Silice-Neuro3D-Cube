# J: diagnóstico de incertidumbre con dispersión

Registro2026-10-07 mientras H calcula N500; antes de ajustar sus potencias.
G640 ya conocido; N256/320H sólo examinados para error temporal directo,
no usados en estos ajustes. No hay propagación nueva J ni cierre de punto3.
J sólo se aplica después de completar/revisar los cinco resultados H.

Motivación: órdenes altos observados no acreditan precisión formal. Preparar
el diagnóstico sobre datos con dispersión sin reemplazar criterios/FAIL H/G/E.
El código no importa solvers; conservar ajustes/intervalos completos en JSON.

## Algoritmo fijo

h=128um/N, normalizado por h más fino. Ajustes por mínimos cuadrados/lstsq a phi0+alpha*h^p,
p en[-4,-.05] y[.05,8] (161nodos/rango y refinamiento de mínimos locales),
y términos fijos1,2,1+2. Dos pesos: uniformes y1/h normalizados. Guardar
condición, residuales y desviación con grados de libertad, descartando
órdenes negativos y mínimos en frontera para la selección de potencia.

Selección inspirada en Eça–Hoekstra: ajuste de potencia positivo si monótono
y0.5<=p<=2; para p>2 usar ajustes fijos1/2; bajo/anómalo admitir también1+2.
Fijar Fs=3 siempre, adaptación conservadora explícita. Para cada phi_i:
U=3*|phi_fit_i-phi0|+sigma+|phi_i-phi_fit_i| si sigma<rango/(n-1);
si no, U=3*sigma/[rango/(n-1)]*(|phi_fit_i-phi0|+sigma+|res_i|).
No atribuir cobertura95% ni cota rigurosa al estudio óptico.

Control inicial de p0.25 conocido: indicador seleccionadoU8.12203e-5 no
cubre error real1e-4. FAIL retenido antes de uso óptico, con fuente y JSON.
No es un bug corregido ni una refutación universal del artículo: identifica
una limitación de esta adaptación/selección bajo esas condiciones.

Extensión distinta: envolvente máxima de los radios calculados para todos
los ajustes fijos y positivos finitos no fronterizos. El indicador seleccionado
permanece tal cual, incluido su FAIL. La envolvente cubre los9controles
sintéticos registrados (p0.25/0.5/1/2/3/4/6, mezcla1+2 y dispersiónconocida),
y pasa cambio de unidades/rechazo de constante. No prueba cobertura universal.

Reportar por separado indicador seleccionado y envolvente. Predicción
diagnóstica de una h nueva: centro del ajuste seleccionado; banda=max sobre
modelos de |pred_modelo-centro|+3sigma_modelo+max|res_modelo|. No propagar
ni evaluar nueva malla bajo J. Un ensayo prospectivo separado sería necesario
para probar esa banda; no elegir umbrales según valores ajustados J.

J requiere referenciasH consistentes, hashes originales, todos los campos
y dos detectores; si faltan, no sustituir con ADI ni completar silenciosamente.
Objetivo diagnóstico, sin criterio propio de aceptación del punto3.

[Eça/Hoekstra2014](https://doi.org/10.1016/j.jcp.2014.01.006), páginas106–109
y apéndiceB consultados en PDF MARIN: mínimos cuadrados, dispersión y
alternativas a órdenes altos. Las adaptaciones Fs fijo, búsqueda acotada y
envolvente están identificadas y no se presentan como el método exacto del
artículo ni como garantía para óptica. Fuente metodológica de CFD, transferida
únicamente como hipótesis de diagnóstico numérico.

Literatura reciente examinada sólo por resumen: [Carles2024](https://arxiv.org/abs/2408.14816)
usa Lie–Trotter adaptado y localización espectral; [Arranz-Simón/Cano2026](https://arxiv.org/abs/2607.08387)
trata condiciones Dirichlet dependientes del tiempo y splittings modificados.
Ninguna establece automáticamente el orden del ADI/T96 con perfil abrupto
y frontera fija. No se han implementado esas técnicas ni usado como prueba.
JEV fallbacklocal identificado; bloqueo remoto heredado preservado.
