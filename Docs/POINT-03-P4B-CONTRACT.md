# P4B: mismo pozo conocido, jerarquía alineada con la interfaz

P4A conserva su hipótesis negativa aunque sus controles pasaron. Registrar
fuente generada y este contrato antes del nuevo contraste. No modificar
P4A ni sus entradas/umbrales. No se realiza propagación T96.

Mismo problema1D analítico y convenciones de P4A:cuatro discretizaciones,
masa consistente para normalizar únicamente la entrada, tiempo2mm y
diagonalización temporal. Cambio único de diseño:jerarquía anidada
N127/255/511/1023, h1/0,5/0,25/0,125µm; las interfaces±6µm son nodos
en todos los niveles. No elegir nuevos niveles después de los resultados.

Hipótesis primaria:FEM masa consistente cumple órdenes positivos y
estables20% en127/255/511 frente255/511/1023, y el indicador fino con
r=2 y min(p,2),factor1,25 cubre el error conocido del núcleo para ambos
detectores. Si falla, retener FAIL sin escoger otro tiempo/normalización.
Las otras tres variantes son diagnósticos, no sustituyen a la primaria.

Mantener los mismos controles analíticos, de momentos/eigenpares y norma
de P4A,semilla941,unhilo,180s. Se generará código por cambios AST
exclusivos de niveles/ternas/r y referencia a este contrato, conservando
el resto del algoritmo. Guardar y comprometer la fuente antes de ejecutar.
Guardar campos iniciales/finales,axis y tres eigenpares para16casos.

Un resultado favorable sólo respalda este contraste1D y su jerarquía.
No cierra T96/Q4, no prueba causalidad exclusiva y no convierte P4A en
PASS. Antes de adoptar interfaces conformes2D deben validarse geometría,
masas,operadores,inicialización y tiempo; todo criterio nuevo antes de datos.
JEVfallbacklocal por bloqueoheredado, registroGit local.
