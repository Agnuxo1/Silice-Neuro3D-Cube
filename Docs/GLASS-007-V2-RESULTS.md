# Réplica GLASS-007 V2 — cobertura y detector de área parcial

2026-09-30. Contrato2439bf4 anterior a ejecución. Reparaciones operativas
d7e5e95/d9fa4f7 retenidas, sin alterar física ni umbrales. BPMoriginalSHA
71ef25b7... y cobertura48f53bad... permanecen inmutables durante medidas.
Informe final `resultados/codex/glass007_v2_run3.json`, SHA256
ff8ce69b8ef991cf2a4df0ac8f2248f527b8d2aa5fe9d9df10baa701526a8fec.
Auditor propio `scripts/audit_glass007_v2.py` verifica13casos/lineage/gates;
no es un cuarto solver físico.

## Resultado a2mm, potencia en núcleo dividida por potencia de entrada

| Perfil | V1, detector/index pixelados | V2, cobertura/área parcial | Relleno de anillo V2 |
|---|---|---|---|
| Continuo | 34.879% | 36.177% | 100% |
| 48trazos | 13.581% | 14.292% | 68.704% |
| 96trazos | 33.261% | 33.109% | 95.214% |
| 192trazos | 34.761% | 35.494% | 98.899% |
| 96, integral igualada | 35.540% | 36.601% | 95.214% |
| 88, centros omitidos en cuña | 21.114% | 21.388% | 88.228% |

V2nominal:256²/128um/dx0.5um/dz2.5um. Vacío analítico a0.5mm pasa:
error8.78e-6. Detector usa área geométrica analítica círculo-píxel, error
relativo de área<=7.8e-16; intensidad aún constante por píxel. El perfil
discreto usa16x16subpíxeles y referencia64incluida; diferencia de integral
máxima2.875e-4. Referencia raster64 NO es área exacta.

96trazos/continuo=0.915195: ~8.48% menos potencia en núcleo, relativo al
continuo. NO es pérdida material ni eficacia neuronal. Integral igualada
requiere pico dn=-0.003150785, distinto de V1(-0.00309855); el aumento de
potencia no demuestra ventaja de fabricación ni misma dosis de escritura.
La cuña sigue omisión de centros;17.7° informado porClaude es diagnóstico
de su muestreo, no una abertura exacta impuesta en estos nuevos perfiles.

## Separar los cambios, no aplicar un factor universal de área

Continuo V1=0.348790106. Con perfil promediado pero MISMO detector antiguo,
el campo V2 da0.357292784; con detector de área parcial da0.361771430.
Efecto perfil/propagación=+0.008502678; efecto detector del mismo campo
=+0.004478647. El área pixelada96.6% no equivale a multiplicar por ese
factor toda la potencia: la intensidad no es uniforme sobre el núcleo.
96trazos V2 es ligeramente inferior aV1: el sesgo no es idéntico porperfil.

## Gates y contraste independiente

Todos los gates propios prefijados pasan, NO convergencia global certificada:

- dxcoarse→nominal96: diferencia0.00126216; dominio aigualdx0.00018676.
- dz2.5→2um:96 cambia0.00026406; continuo0.00020490.
- dx0.5→0.4um a128um:96 cambia0.00044398; continuo0.00035519.
- Cuatro comparaciones con ADI009d: error máximo0.00131811 (<0.005).
  Las esponjas difieren: FFT central70%/damping50um frente aADI central80%/
  sigma4e4. No atribuir esa diferencia sólo al método de propagación.
- Continuo contra radial0.363706793: diferencia0.00193536 (<0.003).
  0.3631 deClaude es referencia provisional útil, NO valor exacto adoptado.
- Balance máximo2.09e-13; perfil pasivo/igualintegral/gates de área pasan.

Q4Claude96 sigueFAIL según su contrato; no convertirlo en convergencia
aprobada.009c/frontera radiativa, fase modal y convergencia conjunta quedan
abiertos. La cercanía de tres propagadores dentro del modelo escalar no
valida un cubo real, Maxwell vectorial ni escritura láser.

## Coste y fallos retenidos

Run1:13fallos por duplicar backend al construir informe;93.6372s perdidos.
Run2:cuatro resultados válidos; quinto JSONtruncado por NumPybool. El
supervisor abortó sin escribir walltime agregado: coste completo desconocido.
Scripts/fallos retenidos en Git; no borrar ni arreglar el JSONtruncado.
Run3:reutiliza exactamente esos cuatro informes porSHA/inputs; sólo9hijos
nuevos,56.2399s total,55.9981s suma de hijos, máximo10.6394s (<30s).
Preparación de todoslos13casos=2.26784s incluida, sin caché que esconda coste.
Los cuatro cálculos válidos reutilizados suman26.1557s de cómputo reportado;
esto NO reconstruye arranques/coste fallido ni rendimiento end-to-end limpio.
RSS máximo MUESTREADO tras cálculo36.24MiB, no pico de memoria certificado.
RAM mínima previa2.586GiB, reserva160MiB/hijo y1GiB libre adicional.

29tests CPU pasan. Sin GPU/Blender/instalación ni publicación de esta entrega.
JEVsecurityblocked, fallbacklocal sin aval. Siguiente:009cClaude y006bCodex.

Integridad Git: tres inputsClaude revisados (resultados009d.json,
run009d.py y resultados006a.json) estaban normalizadosLF en elblob pero
conCRLF en disco. Se preservan sus bytes reales mediante atributosexactos
y reindexación, SIN editar archivosClaude ni sustituirSHA en informes.
LosJSONpropios siguen -text. Verificar índice/HEAD contra disco antescierre;
no cambiar hashes científicos para acomodar conversiones de fin de línea.
