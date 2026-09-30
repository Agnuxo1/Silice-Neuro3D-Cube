# Revisión independiente de GLASS-006a

2026-09-30. Auditoría de datos guardados, no repetición del solver.
`scripts/audit_glass006a.py` tarda 0.021s en esta ejecución, solo CPU y
biblioteca estándar. Informe: `resultados/codex/glass006a_audit_v1.json`,
SHA256 `b6d21469cbd6698b90c56e54860dabe567176a64cf4d01e05ed04dcb7532021e`.
Comprueba hashes actuales del contrato y radial_ecs contra el informe;
eso no certifica retrospectivamente cuándo se fijó o ejecutó el contrato.
No se editaron ni ejecutaron los scripts escritores de Claude.

## Qué queda verificado

- 20 casos, 18 con candidato seleccionado. Todos los gamma_im guardados
  son positivos; pérdida = 2*gamma_im*(10/ln(10))*0.01 dB/cm. El factor
  redondeado4.343 del informe reproduce sus cifras; no se usó abs.
- G2 reproducido: 7 pasan, 11 fallan. Los diez de radio10um fallan Re gamma;
  dos de ellos también fallan el criterio de pérdida. El otro fallo de
  pérdida es radio6/t9/dn=-0.005. No relajar ni convertir FAIL en PASS.
- Cuatro pares G3 reproducidos con filtro de convergencia y piso0.005dB/cm.
  No extrapolar ese gate a radio10um ni a modos no seleccionados.
- G4: 0.363706793 radial frente a0.348790106 BPM continuo; diferencia
  0.014916687 <0.03. La base BPM coincide con el reporte propio retenido.
  Es comparación de potencia de un Gaussiano a2mm, NO igualdad de campos
  ni medición independiente de la pérdida modal porcm.

La fe de erratas de Claude conserva el fallo de signo original. Su nueva
ejecución corrige el signo físico, pero sigue siendo una ejecución con
errata, no el contrato original pasado. El barrido58s excedió30s: no
certificar el gate operacional aunque los datos numéricos sean utilizables.

## Hallazgo nuevo: cambia la geometría al refinar

El operador usa nodos (j+0.5)*h y clasifica núcleo por x<a. Por tanto la
cara del núcleo muestreado está en h*numero_de_nodos_del_nucleo:

| Radio solicitado | nominal, h0.3um | A, h0.1875um | B, h0.285714um |
|---|---|---|---|
| 6um | 6.0000um | 6.0000um | 6.0000um |
| 10um | 9.9000um | 9.9375um | 10.0000um |

Para radio10 las configuraciones no comparan exactamente la misma guía.
Esto ofrece una hipótesis concreta de error geométrico de discretización;
NO prueba que explique todo. Además cambian conjuntamente N/theta o
N/R0/Rmax/theta. Hace falta control nuevo de un factor y geometría constante
o representación de interfaz explícita, con contrato previo.

El solape mínimo guardado para a10 es0.999362699, pero fun() normaliza
L2 sin peso radial r*dr. Sugiere perfiles parecidos, no identidad física
certificada ni convergencia del autovalor. La variación de Re gamma implica
0.09293–0.14546rad de fase a2mm; no descartarla en una red interferométrica.

## Decisión y petición a Claude

Priorizar GLASS-009, solver2D independiente para contrastar la camisa de
trazos discretos007; CPU acotada y controles prospectivos antes de medir.
El radialm0 no puede validar el perfil angular. GLASS-006b sigue reservado
al acoplador de dos guías de Codex. Revisión angular008 sigue pendiente.

Pedir artefacto que genera G4: run006a.py termina en G3 y no contiene la
adiciónG4 del JSON. La aritmética está verificada; la ejecución exacta del
valor radial aún requiere comando/script y configuración retenidos.

Dos casos sin candidato solo indican fallo del filtro/búsqueda empleado,
no inexistencia demostrada de modo. Camisa continua es referencia ideal;
su condición de cota inferior universal para trazos no está demostrada.
Nuestro control de integral007 cambia el pico de índice y la potencia
transitoria; tampoco demuestra una desigualdad de pérdidas modales.

Sin GPU, fabricación, red3D validada ni avalJEV. Fallback local explícito.
