# P4: controles previos del nuevo método, aún sin cierre espacial

| Control | Evidencia | Alcance |
|---|---|---|
| P4A | 36casos conocidos; ensamblaje/normas PASS, estabilidad FEM consistente FAIL | La forma débil sola no confirmó el intervalo no alineado |
| P4B | 16casos enjerarquíaalineada; FEM consistente PASS:órdenes campo2,0308/2,0197,intensidad1,9808/1,9840 e indicadores cubrenerror conocido | Respalda importancia de malla conforme en el contraste1D; no T96 |
| P4C | Malla curva74785DOF/37208triángulos; CADvsuniónanalítica3,775e-15rel;errorgeométricoP2 2,471e-6;Jacobianos/simetría/rigidez constante PASS | Sólo geometría ymatrices2D |
| P4D | Padé6vsreferenciadensa:errores finos1,42e-8/1,81e-8,órdenes~6 | Control temporal pequeño |
| P4E | Pasividad/coste viable;diferencia campo1,779e-5>1e-5 FAIL | No precisión temporal real demostrada desde el primer paso |
| P4E2 | Extensión sin repetir niveles:últimadiff9,638e-7,decrece PASS;órdenes1,268/1,742 | No presumir orden6 para el espectro T96 desde ese controlcorto |
| P4F | DetectorCircular/proyecciónL2 PASS;quadMnorm7,757e-14,inputq12/16diff4,926e-15,coreinputerror3,378e-9 | Integración/entrada sin propagación |
| P4G | Amortiguador integrado porpartes PASS;D8/12Mbound2,107e-8m^-1 | Perfil físico igual, cuadratura controlada en diagonales/umbrales |
| P4H | Radau5Lestablevsdense:errores5,16e-8/6,44e-8,órdenes~5 PASS | Segunda familia temporal independiente |
| P4I | Terminado: 224 campos auditados, integridad aprobada; cotas PSD 1,024906e-5 y 1,592164e-5 frente al límite 1e-5 | Precisión temporal fallida; se conserva el resultado negativo |
| P4I2 | Terminado y auditado: 128 campos nuevos y 224 retenidos; cota PSD de intensidad 1,169059e-5 >1e-5 | Integridad aprobada; dictamen temporal negativo conservado |
| P4I3 | En curso: añade sólo Radau5 con 65536 pasos y conserva Padé6 de P4I2 | Mismos límites; todavía pendiente |

Nueva dependencia sólo en entorno separado
D:/PROJECTS/.cognition/silice_fem_env_20261008. NumPy2.2.6/SciPy1.15.1
pinned,Gmsh4.15.2/scikit-fem12.0.2/meshio5.3.5, licencias abiertas y
metadatos/hashes oficiales en reporte de instalación. El entorno CPU
original y el checkout principal no se modificaron para esta instalación.

Incidentes conservados:P4C calculó controles correctos y guardó matrices,
pero su JSON se truncó por NumPyint32; recuperación independiente desde
artefactos sin regenerar, report_recovered.json. Importador meshio emitió
advertencia de tags:se usa el array físico explícito para materiales y
coordenadas para el contorno, comprobados, sin depender de esos tags.

P4B fuente generada usó tambiénh=1µm en el control auxiliar de seis
momentos, frente alh=128/401µm de P4A, por transformación del literal401.
Los límites y algoritmo de integración no cambiaron; fuente comprometida
antes de datos. Se declara esta diferencia adicional al cambio de niveles;
no se reescribe el resultado ni se atribuye igualdad exacta de controles.

La comparaciónFEM busca el MISMO límite continuo escalar de trazos,
dominio y entrada; cambia discretización/integración/inicialización
numérica. No se afirma éxitoT96 desde pruebas1D, geometría o tiempo corto.
P3/P4A/P4E y todos los fallos anteriores siguen negativos. Punto3abierto.

Fuentes consultadas: [Gmsh](https://gmsh.info/doc/texinfo/gmsh.html),
[scikit-fem](https://scikit-fem.readthedocs.io/en/stable/api.html),
[SciPy:eigh](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.linalg.eigh.html).
Uso local,no servicio externo de fabricación ni simulación atribuida al
laboratorio virtual. JEVfallbacklocal por bloqueo heredado.
