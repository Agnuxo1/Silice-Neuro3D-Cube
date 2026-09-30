# GLASS-007 V2 — réplica prospectiva con cobertura y área parcial

2026-09-30. Congelar este contrato y las fuentes propias en Git ANTES de
ejecutar los casos. Fallos originales007/009/009b/009d permanecen intactos.
No se adopta0.3631 como constante de calibración ni se ajusta a ese número.

PDE, longitud2mm, lambda1550nm, n0=1.444, cintura6um, radio6um,
camisa6um/dn=-0.003: iguales007. Solver original bpm.py queda INMUTABLE.
Nueva retícula opt-in<=320², sin alterar Grid original<=256².
FFT+esponja original: amplitud exp(-q^4*dz/50um), borde70% central;
ADIClaude emplea otra esponja (80% central/4e4m^-1): diferencia explícita.
No se equipara esponja con absorción material.009c sigue pendiente.

Detector: área analítica de intersección círculo-píxel (primitiva geométrica
por cuadrantes), intensidad constante por píxel; no integral exacta del
campo dentro de cada píxel. Reportar también observable antiguo del mismo
campo, separando cambio de detector y cambio de perfil/propagación.
Índice continuo: área analítica de anillo por píxel. Índice de trazos:
fracción de unión de discos intersectada con anillo,16x16subpíxeles,
calculada solo en cajas útiles. No sumar índice dos veces donde se solapan.
Geometría original de tracks.py; no es receta de escritura ni dosis.
Control igualintegral: escalar al área analítica del anillo, reportar pico;
no reutilizar escala antigua. Cuña sigue omisión de centros, no apertura30°.

Casos: los diez007 originales (seis nominales, coarse192/128um,
wide256/170.6667um a igualdx, tracks/continuous dz2um), más vacío0.5mm,
continuo320/128um y tracks32 320/128um (dx0.4um).13casos en total.
Nominal256/128um/dz2.5um,800pasos. dz2um=1000pasos.
Todos se ejecutan como hijos separados, CPU un hilo, timeout duro30s
incluyendo arranque, construcción de perfiles, propagación y escritura.
Presupuesto conservador160MiB/hijo, RAM libre>=1GiB tras presupuesto.
Sin GPU/Blender/instalaciones. Supervisor cuenta suma y tiempo total.
Preparación de área64x64subpíxeles incluida por caso, NO coste escondido
en caché ni denominación de área_exacta para trama aproximada.

Gates previos, sin relajación posterior:

- Área detector círculo relativa<1e-10, cobertura[0,1]; ninguna modificación
  en celdas totalmente interiores/exteriores (celdas de frontera mixtas
  pueden tener centro en el núcleo y dn promedio no nulo: no confundir).
- Integral trazos16vs64 relativa<1e-3; en continuo usar área analítica;
  igualintegral error<1e-12; balance propagación<1e-10.
- Vacío frente a fracción gaussiana analítica a0.5mm: errorabs<1e-3.
- Refinamientos dx, dominio igualdx y dz: cada diferenciaabs<0.005 yrel<10%,
  referencia>=1e-6. Registrar todos, no convergencia conjunta/orden.
- Mismos refinamientosdx0.5→0.4 para continuo/tracks32; comparación propia
  frente a ADI009d dx0.5/0.4: errorabs<0.005. Comparar contra archivos leídos,
  no ejecutar ni editar códigoClaude. No gate de campo compartido inexistente.
- Referencia radial0.363706793 solo para continuo: abs<0.003, sin promover
  frontera a validada ni pérdida modal porcm.
- Exponer Q4ClaudeFAIL separado. Q4 en propia secuencia192/256/320 es
  diagnóstico: los intervalosdx no son iguales; no orden ni certificación.

Guard fail-closed: si falta RAM, hashes cambian, hijo excede30s o falla,
retener salida/fallo y estado incompleto; no ocultar en agregado PASS.
Inputs/hashes de contratos/fuentes/resultados peer conservados en informe.
Sólo versionar propios; README editadoClaude y assets no se publican aquí.
JEV bloqueado por seguridad: fallback local, sin consulta/aval remoto.
