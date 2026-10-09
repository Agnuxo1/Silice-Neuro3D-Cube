# Ondas ópticas CUDA y refinamiento del acoplador — 2026-10-05

## Resultado y límites

Se implementó y ejecutó propagación de ondas SSFM en CUDA de la RTX3090,
no render decorativo ni multiplicación por una matriz precompilada.
Dos contratos/versiones congelados antes de GPU: a8b4b5b (001) y
64cd7ea (002). Ventana autorizada conservadora termina13:13:06UTC.
Operadores/detectores/geometría/preparación y validación siguen en CPU;
FFT/fase/amortiguación y presupuesto removido corren en GPU.
Simulación digital escalar paraxial: NO óptica física, RT ni Maxwell.

16 casos GPU nuevos: 8 de equivalencia (4fixtures×2precisiones), y
8 de refinamiento/controles en dobleprecisión. Ambas reservas gpuq
liberadas tras cada job; los hijos terminaron. Sin instalación ni push.

## GPU-001: equivalencia y fallo de precisión simple

Cuatro campos completos en128bits: error relativo máximo7.8068e-14,
puertos6.2356e-14, potencias9.4813e-14; balance<=7.80e-14.
Linealidad coherente5.4488e-15. Todos los gates128pasan.

Los cuatro casos64bits FALLAN el balance numérico:1.10e-4..2.22e-4
frente al umbral1e-4. El caso320² también falla campo1.14346e-4,
puerto1.00016e-4 y potencia1.52631e-4. No renormalizado ni gate relajado.
Linealidad64sí pasa3.02065e-6: linealidad sola NO certifica precisión.
Rc2 conserva este fallo científico, no fue crash ni corte del supervisor.

Tiempos descriptivos near_left256²/400pasos, 3repeticiones calientes:

| Variante | Todas las muestras de propagación+presupuesto (s) |
| --- | --- |
| CPU NumPy128,1hilo | 2.4329184;2.4656332;2.4527839 |
| CUDA128,residente | 0.0998778;0.1098203;0.1101299 |
| CUDA64,residente (FAIL numérico) | 0.1149121;0.1245488;0.1244908 |

Ratio medianas CPU/CUDA128≈22.3 descriptivo de SOLO ese núcleo/caso.
CPU y GPU usan FFT propias; no comparación con otra red neuronal ni
prueba de ventaja de dispositivo óptico. No paresAB/BA ni intervalos
de confianza: no presentar como benchmark general. CUDA fría128
near_left0.8353s; preparación/H2D/D2H/disco constan por separado enJSON.
El startup global/contextoGPU está incluido en elapsed del hijo, NO
aislado para afirmar coste de inferencia end-to-end. Sin medir energía.

Guard001:16.53s hijo, RAMmín6.922GiB/VRAMtotalmuestreada<=2.176GiB/
temperatura<=36C. Pico allocatorCUDA11.159MiB (NO memoriaGPUtotal).

## GPU-002: extensión explícita, no modificación de modelos antiguos

Nuevos grids384/512/640 (dx=.3333/.25/.2um) y controles512R/coherente,
512cobertura32 y512/640 con800pasos. Geometry continua ideal igual a006b.
Los límites originales de Grid/CellGrid y GPU001 quedaron intactos.
Contraste SSFMCPU sobre inputs nuevos512/640:campo3.1923e-14/4.3246e-14;
no es segundo solver independiente. Camposguardados completos porcaso.

| Gate | Error máximo complejo/potencia | Umbral | Resultado |
| --- | ---: | ---: | --- |
| dx320→384 | .00194887 | .005 | PASS descriptivo |
| dx384→512 | .00302594 | .005 | PASS descriptivo |
| dx512→640 | .000662141 | .005 | PASS requerido |
| dz512,400→800 | .00151372 | .005 | PASS |
| dz640,400→800 | .00153703 | .005 | PASS |
| Cobertura512,16→32 | .000459868 | .005 | PASS |
| Linealidad campo512 | 5.58054e-15 | 1e-10 | PASS |
| Simetría puertos512 | 3.00597e-14 | 1e-8 | PASS |

**Estabilidad local según contratoGPU002:PASS.** La secuencia de dx no
es monótona; NO certificar orden de convergencia ni extrapolación al
continuo. Gates anteriores256→320FAIL y reducciónGalerkinGaussianFAIL
permanecen retenidos, no se reescribe su conclusión retrospectivamente.
Puertos Gaussianos NO modos propios. Frontera abierta no certificada
universalmente, pérdidas materiales reales no medidas.

N640inputL/400pasos: potencia en núcleos respecto a entrada
izquierdo.6539532792/derecho.1730186268. En512inputcoherente:
.0856812543/.7416310828. Coherencia afecta salida, no es una red
neuronal entrenada ni demostración de fabricación de cubo.

Guard002:rc0,85.415s hijo/86.816s supervisor; RAMmín6.032GiB,
VRAMtotalmuestreada<=2.207GiB/temperatura<=37C. AllocatorCUDA46.877MiB.
Supervisión muestreada no garantiza picos instantáneos de todo el PC.

## Evidencia, auditoría y siguiente paso

JSON001SHA2a9b6e1158fb1e7e2c364feb88bb5458ff086d2f0887ffc061a0b4baded1410c.
JSON002SHA7996a996cafa3aa5f213f8d7990d5e3d2d5fbb8094fe53614500aa5d71998dbd.
16NPZnuevos+hijos/telemetría/hashes conservados en resultados/codex.
`scripts/audit_glass_gpu.py` recomputó métricas de arrays y todos los
gates002:29comprobaciones consistentes en auditoríaV2, incluidos losFAIL64.
La auditoríaV1de21comprobaciones se conserva. Es auditor de datos
NumPy, NO solver independiente ni validación física adicional.
45tests propiosCPU pasan sin inicializarGPU en la suite.

Método de tiempo: sincronización explícita antes/después de segmentos
CUDA, siguiendo [documentación oficialPyTorch2.6](https://docs.pytorch.org/docs/2.6/notes/cuda.html#asynchronous-execution).

Pedido concreto aClaude: revisar kernels y contrastar inputL/coherente
exactos, con campos COMPLEJOS y puertos, mediante ADI; retener su
contrato/script/resultados. Priorizar después base modal y dominio/sponge,
no una malla neuronal grande sobre reducción Gaussianosfallida.
JEVbloqueado por seguridad, fallbacklocal sin aval remoto.
No inferir sabotaje/intencionalidad de discrepancias: las pruebas y los
artefactos determinan qué se acepta, incluido nuestro propioFAIL64.
