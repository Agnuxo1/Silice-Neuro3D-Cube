# J: diagnÃ³stico de incertidumbre con dispersiÃ³n

Registro2026-10-07 mientras H calcula N500; antes de ajustar sus potencias.
G640 ya conocido; N256/320H sÃ³lo examinados para error temporal directo,
no usados en estos ajustes. No hay propagaciÃ³n nueva J ni cierre de punto3.
J sÃ³lo se aplica despuÃ©s de completar/revisar los cinco resultados H.

MotivaciÃ³n: Ã³rdenes altos observados no acreditan precisiÃ³n formal. Preparar
el diagnÃ³stico sobre datos con dispersiÃ³n sin reemplazar criterios/FAIL H/G/E.
El cÃ³digo no importa solvers; conservar ajustes/intervalos completos en JSON.

## Algoritmo fijo

h=128um/N, normalizado por h mÃ¡s fino. Ajustes por mínimos cuadrados/lstsq a phi0+alpha*h^p,
p en[-4,-.05] y[.05,8] (161nodos/rango y refinamiento de mÃ­nimos locales),
y tÃ©rminos fijos1,2,1+2. Dos pesos: uniformes y1/h normalizados. Guardar
condiciÃ³n, residuales y desviaciÃ³n con grados de libertad, descartando
Ã³rdenes negativos y mÃ­nimos en frontera para la selecciÃ³n de potencia.

SelecciÃ³n inspirada en EÃ§aâ€“Hoekstra: ajuste de potencia positivo si monÃ³tono
y0.5<=p<=2; para p>2 usar ajustes fijos1/2; bajo/anÃ³malo admitir tambiÃ©n1+2.
Fijar Fs=3 siempre, adaptaciÃ³n conservadora explÃ­cita. Para cada phi_i:
U=3*|phi_fit_i-phi0|+sigma+|phi_i-phi_fit_i| si sigma<rango/(n-1);
si no, U=3*sigma/[rango/(n-1)]*(|phi_fit_i-phi0|+sigma+|res_i|).
No atribuir cobertura95% ni cota rigurosa al estudio Ã³ptico.

Control inicial de p0.25 conocido: indicador seleccionadoU8.12203e-5 no
cubre error real1e-4. FAIL retenido antes de uso Ã³ptico, con fuente y JSON.
No es un bug corregido ni una refutaciÃ³n universal del artÃ­culo: identifica
una limitaciÃ³n de esta adaptaciÃ³n/selecciÃ³n bajo esas condiciones.

ExtensiÃ³n distinta: envolvente mÃ¡xima de los radios calculados para todos
los ajustes fijos y positivos finitos no fronterizos. El indicador seleccionado
permanece tal cual, incluido su FAIL. La envolvente cubre los9controles
sintÃ©ticos registrados (p0.25/0.5/1/2/3/4/6, mezcla1+2 y dispersiÃ³nconocida),
y pasa cambio de unidades/rechazo de constante. No prueba cobertura universal.

Reportar por separado indicador seleccionado y envolvente. PredicciÃ³n
diagnÃ³stica de una h nueva: centro del ajuste seleccionado; banda=max sobre
modelos de |pred_modelo-centro|+3sigma_modelo+max|res_modelo|. No propagar
ni evaluar nueva malla bajo J. Un ensayo prospectivo separado serÃ­a necesario
para probar esa banda; no elegir umbrales segÃºn valores ajustados J.

J requiere referenciasH consistentes, hashes originales, todos los campos
y dos detectores; si faltan, no sustituir con ADI ni completar silenciosamente.
Objetivo diagnÃ³stico, sin criterio propio de aceptaciÃ³n del punto3.

[EÃ§a/Hoekstra2014](https://doi.org/10.1016/j.jcp.2014.01.006), pÃ¡ginas106â€“109
y apÃ©ndiceB consultados en PDF MARIN: mÃ­nimos cuadrados, dispersiÃ³n y
alternativas a Ã³rdenes altos. Las adaptaciones Fs fijo, bÃºsqueda acotada y
envolvente estÃ¡n identificadas y no se presentan como el mÃ©todo exacto del
artÃ­culo ni como garantÃ­a para Ã³ptica. Fuente metodolÃ³gica de CFD, transferida
Ãºnicamente como hipÃ³tesis de diagnÃ³stico numÃ©rico.

Literatura reciente examinada sÃ³lo por resumen: [Carles2024](https://arxiv.org/abs/2408.14816)
usa Lieâ€“Trotter adaptado y localizaciÃ³n espectral; [Arranz-SimÃ³n/Cano2026](https://arxiv.org/abs/2607.08387)
trata condiciones Dirichlet dependientes del tiempo y splittings modificados.
Ninguna establece automÃ¡ticamente el orden del ADI/T96 con perfil abrupto
y frontera fija. No se han implementado esas tÃ©cnicas ni usado como prueba.
JEV fallbacklocal identificado; bloqueo remoto heredado preservado.
