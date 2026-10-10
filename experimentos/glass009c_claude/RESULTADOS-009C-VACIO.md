# GLASS-009c-VACIO · validación en vacío de la frontera absorbente · resultados (2026-10-10)

Contrato: [`CONTRATO-VACIO.md`](CONTRATO-VACIO.md) (con Enmienda 1, añadida tras ver D1 y antes de correr los controles).
Código nuevo: `validacion_vacio_run.py` (una corrida por trozos), `validacion_vacio_lote.sh`, `validacion_vacio_controles.sh`, `validacion_vacio_analisis.py`. Salida del análisis: `vacio_analisis_salida.txt`. Datos: [`resultados009c_vacio.json`](resultados009c_vacio.json), `vacio_out/`, `vacio_estados/`.
Resultados previos (`out/`, `out2/`, `resultados009c*.json`, `CONTRACT*.md`) no se han modificado.

Todo es un modelo numérico (paraxial, δn = 0), no un dispositivo. Analítico = predicción sin frontera. Numérico = modelo discreto. No hay medida.

## Veredicto

| Criterio | Qué mide | Resultado | Veredicto |
|---|---|---|---|
| K0 | herramienta: reproduce 009c, σ, analítico en z=0, estados | todos cumplen | **pasa** |
| K1 | retorno en vacío: máx. \|ΔP_u\|/P0 < 1e-4 en la ventana (dx 0,5) | 1,5e-3 a 1,6e-2 en las 8 configuraciones | **no pasa** |
| K1-diag | igual con dx 1,0 (diagnóstico) | 6e-3 a 6,5e-2 | no pasa |
| K2 | el absorbente cambia el resultado; alguna configuración pasa K1 | dependencia sí (factor 6 a 14); ninguna pasa | **no pasa** |
| K3 | fase comparable con el 1D | no comparable (pre-declarado) | no comparable |
| K4 | malla fina: naturaleza del error y B1 en dx 0,25 | B1 falla (E = 2,0e-3 > 1e-3); el error temprano cae con la malla y el tardío no cambia | **no pasa** |
| K5 | energía total monótona | cumple (máx. violación 1,2e-14 P0) | **pasa** |
| K6 | ley 1D R0^(sin θ) aplicable | no aplicable (pre-declarado) | no aplicable |
| C-ref | descomposición con dominio 512 µm (enmienda 1) | sección 5 | (diagnóstico, sin gate) |

**Validado:** la herramienta de medida (K0), la conservación de energía sin absorbente (control), y el comportamiento de convergencia del error temprano (cociente 3,1–3,6 al pasar de dx 0,5 a 0,25; orden 2 daría 4).

**No validado:** la frontera 009c no cumple el criterio de retorno de −40 dB en vacío en ninguna de las configuraciones probadas. Hay dos causas independientes, medidas por separado en las secciones 5 y 7:
- (a) **discretización del haz inclinado** en z ≲ 1 mm: error de potencia 3e-4 a 1,9e-3 (θ ≤ 0,02) y 5e-3 a 1,6e-2 (θ = 0,05–0,08) con dx = 0,5 µm. Está presente igual en 128 y 512 µm y baja con la malla (cociente ~3,3 al pasar a dx = 0,25). Esta causa, sola, ya impide K1 con dx = 0,5 µm para θ ≥ 0,05;
- (b) **frontera tardía** en z ≳ 0,8–2 mm: no depende de la malla y decrece con la distancia del absorbente (θ = 0, z = 2 mm: 6,0e-3 con 128 µm y 1,7e-4 con 256 µm).

Sobre 009c: su criterio B4 (error de potencia < 1 %) se aplicó solo en la ventana de confianza (≤ 1,4 mm). A 2 mm el error relativo de potencia en el máximo es 2,8 % (θ = 0, 128 µm, dx 0,5) y 3,2 % (θ = 0,02).

## 1. Condiciones y definiciones

- P0 = Σ|A(0)|² dx² (normalizada, 1,000000). Todos los errores de potencia están en unidades de P0.
- ΔP_u(z) = P_u,num(z) − P_u,an(z). El máximo de |ΔP_u| es positivo (el núcleo recibe más potencia que el analítico) en las 44 configuraciones de D1, D2, D4 y controles. Solo 3 de 44 tienen además alguna muestra con pérdida (λ ≤ 2,7e-4 P0). El exceso se interpreta como retorno.
- Ventana W = { z ≥ z_arr }, z_arr con la definición del contrato (banda e > 1 − f). Muestreo cada 40 pasos (0,1 mm), 12–18 instantes por configuración. Los máximos entre muestras no se ven.
- Absorbente de línea de base: f = 0,2, p = 4, σmax = 4·10⁴ m⁻¹ (igual que 009c).

## 2. D1: retorno en vacío (malla 009c, dx = 0,5 µm, K1)

| dominio | θ (rad) | z_arr (mm) | máx. \|ΔP_u\|/P0 | z del máximo (mm) | ΔP/P_u,an en el máximo | E(2 mm) | K1 |
|---|---|---|---|---|---|---|---|
| 128 µm | 0 | 0,5 | 6,04e-3 | 2,0 | 2,8 % | 1,0e-1 | no |
| 128 µm | 0,02 | 0,4 | 5,55e-3 | 2,0 | 3,2 % | 1,1e-1 | no |
| 128 µm | 0,05 | 0,4 | 6,31e-3 | 0,5 | 0,80 % | 2,0e-1 | no |
| 128 µm | 0,08 | 0,3 | 1,63e-2 | 0,4 | 2,3 % | 4,4e-1 | no |
| 256 µm | 0 | 0,9 | 1,54e-3 | 0,9 | 0,22 % | 7,4e-4 | no |
| 256 µm | 0,02 | 0,9 | 1,61e-3 | 0,9 | 0,26 % | 1,6e-3 | no |
| 256 µm | 0,05 | 0,7 | 3,25e-3 | 0,7 | 0,67 % | 1,3e-2 | no |
| 256 µm | 0,08 | 0,6 | 4,38e-3 | 0,6 | 1,7 % | 1,2e-1 | no |

- Ningún caso pasa K1. El mínimo (1,5e-3) está 15 veces por encima del umbral (1e-4).
- Ampliar el dominio de 128 a 256 µm reduce el máximo entre 1,9 y 3,9 veces (θ = 0 a 0,08), pero no basta. El máximo en 256 µm está en la llegada (0,6–0,9 mm), donde domina la causa (a).
- Con dx = 1,0 µm (diagnóstico de 009c) el máximo sube a 6,2e-3 … 6,5e-2. Consistente con B5 fallido en 009c.

## 3. Controles (enmienda 1)

**Control negativo, sin absorbente (σmax = 0), dominio 128 µm, dx 0,5 µm:**

| θ (rad) | máx. \|ΔP_u\|/P0 sin esponja | con esponja (tabla de la sección 2) | cociente | E(2 mm) sin esponja |
|---|---|---|---|---|
| 0 | 9,24e-2 | 6,04e-3 | 15× | 6,8e-1 |
| 0,02 | 1,26e-1 | 5,55e-3 | 23× | 8,7e-1 |
| 0,05 | 2,52e-1 | 6,31e-3 | 40× | 2,1 |
| 0,08 | 3,95e-1 | 1,63e-2 | 24× | 6,7 |

- Sin absorbente, la pared de Dirichlet devuelve al núcleo entre el 9 % y el 39 % de la potencia de entrada. El absorbente reduce ese retorno entre 15 y 40 veces.
- Conservación de energía sin absorbente: |P_total(2 mm)/P0 − 1| < 1e-13. Es la comprobación de que el solver no pierde energía por sí mismo.

## 4. D2: barrido del absorbente (dominio 128 µm, dx 0,5 µm, σmax fijo)

Máx. |ΔP_u|/P0 en la ventana (entre paréntesis, z del máximo en mm):

| f | p | A_int (adim.) | θ = 0 | θ = 0,02 | θ = 0,05 | θ = 0,08 |
|---|---|---|---|---|---|---|
| 0,2 | 4 (009c) | 0,102 | 6,04e-3 (2,0) | 5,55e-3 (2,0) | 6,31e-3 (0,5) | 1,63e-2 (0,4) |
| 0,2 | 2 | 0,171 | 5,67e-3 (1,8) | 5,90e-3 (1,8) | 6,31e-3 (0,5) | 1,63e-2 (0,4) |
| 0,2 | 6 | 0,073 | 6,74e-3 (2,0) | 8,40e-3 (2,0) | 1,28e-2 (2,0) | 2,71e-2 (1,2) |
| 0,1 | 4 | 0,051 | 2,23e-2 (2,0) | 3,37e-2 (2,0) | 6,49e-2 (2,0) | 9,62e-2 (1,3) |
| 0,3 | 4 | 0,154 | 2,16e-3 (1,7) | 2,41e-3 (0,6) | 6,31e-3 (0,5) | 1,63e-2 (0,4) |

A_int = σmax·f·W/(p+1), con W = 64 µm: absorción integrada a lo largo de x de la banda. Es un índice de comparación entre configuraciones, no un invariante: el tiempo que un rayo pasa en la banda depende de θ.

- **K2, dependencia:** sí. El cociente máx./mín. del barrido es 10,3 (θ = 0), 14,0 (0,02), 10,3 (0,05) y 5,9 (0,08). El absorbente importa.
- **K2, criterio de paso:** no. Ninguna configuración alcanza 1e-4 en θ = 0,02, 0,05 y 0,08 a la vez. La mejor, (0,3; 4), da 6,3e-3 a θ = 0,05 y 1,6e-2 a θ = 0,08.
- Las bandas más estrechas y abruptas (f = 0,1; p = 6) devuelven más. Con f = 0,1 y θ = 0,05 la potencia del núcleo llega a 2,16 veces la analítica (ΔP/P_u,an = 116 %). El retorno crece con la pendiente de σ.
- A θ = 0,08, las configuraciones (0,2; 2), (0,2; 4) y (0,3; 4) dan 1,629e-2 (idénticos a 4 cifras) en z = 0,4 mm. En ese instante la potencia del núcleo no depende del absorbente. Es el error temprano de la causa (a). Por eso el cociente en θ = 0,08 es menor (5,9): el error temprano domina el máximo.

## 5. Descomposición con referencia de dominio 512 µm (enmienda 1)

Referencia: dominio 512 µm (N = 1024), dx = 0,5 µm, mismo absorbente de línea de base (f 0,2, p 4). La banda empieza en |x| = 205 µm. Corridas en vacío, 800 pasos, mismo muestreo.

Comparación por instantes (ΔP_u/P0 / E), mismo instante en todos:

| z (mm) | θ = 0,05: 128 µm dx 0,5 | θ = 0,05: 512 µm dx 0,5 | θ = 0,05: 128 µm dx 0,25 | θ = 0,08: 128 µm dx 0,5 | θ = 0,08: 512 µm dx 0,5 | θ = 0,08: 128 µm dx 0,25 |
|---|---|---|---|---|---|---|
| 0,4 | +5,34e-3 / 2,2e-2 | +5,34e-3 / 2,2e-2 | +1,64e-3 / 6,1e-3 | +1,63e-2 / 3,9e-2 | +1,63e-2 / 3,9e-2 | +5,00e-3 / 1,1e-2 |
| 0,5 | +6,31e-3 / 1,5e-2 | +6,32e-3 / 1,5e-2 | +1,78e-3 / 4,0e-3 | +9,34e-3 / 2,3e-2 | +9,39e-3 / 2,3e-2 | +2,49e-3 / 9,3e-3 |
| 0,8 | +1,89e-3 / 3,2e-2 | +2,10e-3 / 4,9e-3 | +3,81e-4 / 3,5e-2 | +4,02e-3 / 2,0e-1 | +9,91e-4 / 6,8e-3 | +3,82e-3 / 2,1e-1 |
| 1,0 | +2,55e-3 / 7,3e-2 | +9,08e-4 / 2,8e-3 | +1,91e-3 / 7,6e-2 | +8,16e-3 / 4,0e-1 | +2,87e-4 / 3,8e-3 | +8,36e-3 / 4,1e-1 |
| 1,4 | +1,18e-3 / 1,1e-1 | +2,28e-4 / 1,3e-3 | +1,07e-3 / 1,1e-1 | +4,52e-3 / 5,2e-1 | +4,52e-5 / 1,6e-3 | +4,48e-3 / 5,2e-1 |
| 2,0 | +3,88e-3 / 2,0e-1 | +5,12e-5 / 5,7e-4 | +3,82e-3 / 2,0e-1 | +1,67e-3 / 4,4e-1 | +7,17e-6 / 6,8e-4 | +1,69e-3 / 4,5e-1 |

Resumen de la descomposición:

| θ (rad) | máx. \|ΔP\| con 512 µm en su ventana propia (z_arr = 1,4 / 1,1 mm) | máx. \|ΔP\| con 512 µm desde z = 0,4 mm | máx. δ_frontera = (P_u,128 − P_u,512)/P0 | E(2 mm), 128 µm | E(2 mm), 512 µm |
|---|---|---|---|---|---|
| 0,05 | 2,28e-4 (z = 1,4) | 5,34e-3 (z = 0,4) | 3,8e-3 (z = 2,0) | 0,198 | 5,7e-4 |
| 0,08 | 1,69e-4 (z = 1,1) | 1,63e-2 (z = 0,4) | 7,9e-3 (z = 1,0) | 0,443 | 6,8e-4 |

Lectura:
1. **En 512 µm la frontera deja de influir.** El campo de 512 µm sigue al analítico al 0,06–0,07 % en z = 2 mm (E = 5,7e-4 y 6,8e-4). Con 128 µm, E sube a 0,20 y 0,44. La desviación tardía de 128 µm es efecto de frontera (absorbente más pared).
2. **El error temprano no es de frontera.** En z = 0,4–0,5 mm el ΔP es idéntico en 128 y 512 µm (5,34e-3 frente a 5,34e-3 a θ = 0,05; 1,63e-2 frente a 1,63e-2 a θ = 0,08). Ese error aparece antes de que el haz llegue a la banda y baja con dx: 5,3e-3 → 1,6e-3 a θ = 0,05 y 1,6e-2 → 5,0e-3 a θ = 0,08 (cociente ~3,3 al pasar a dx = 0,25).
3. **K1 no se cumple ni con la frontera lejana.** El máximo de 512 µm en su ventana propia (2,3e-4 y 1,7e-4) queda justo por encima de 1e-4, porque su ventana empieza tarde (z_arr = 1,1–1,4 mm). Si se evalúa en los mismos instantes que 128 µm (desde z = 0,4), el máximo es 5,3e-3 y 1,6e-2. La causa (a) impide K1 con dx = 0,5 µm incluso con dominio grande.
4. **Frontera de 0,8 a 2 mm en θ = 0,05 y 0,08.** δ_frontera tiene el mismo orden que el ΔP de 128 µm en esos instantes. El ΔP propio de 512 µm baja a 5e-5 o menos en z = 2 mm.

## 6. D3: fase frente al ángulo (estado final, z = 2 mm)

ψ_ov = arg⟨A_an, A_num⟩ sobre r < 40 µm; coherencia = |⟨A_an, A_num⟩|/√(P_an P_num). Fase 1D: `experimentos/frontera_claude/fase_resultados.json`, arg(r) en x = 0.

| malla | θ (rad) | ψ_ov (rad) | coherencia | arg r (1D) | diferencia envuelta (rad) |
|---|---|---|---|---|---|
| 128 µm, dx 0,5 | 0 | −0,0012 | 0,9952 | — | — |
| 128 µm, dx 0,25 | 0 | −0,0012 | 0,9956 | — | — |
| 128 µm, dx 0,5 | 0,02 | −0,0009 | 0,9941 | −0,8004 | 0,80 |
| 128 µm, dx 0,25 | 0,02 | −0,0009 | 0,9943 | −0,8004 | 0,80 |
| 128 µm, dx 0,5 | 0,05 | +0,0007 | 0,9817 | — | — |
| 128 µm, dx 0,25 | 0,05 | +0,0004 | 0,9818 | — | — |
| 128 µm, dx 0,5 | 0,08 | +0,0058 | 0,9190 | −0,0692 | 0,075 |
| 128 µm, dx 0,25 | 0,08 | +0,0043 | 0,9179 | −0,0692 | 0,073 |
| 256 µm, dx 0,5 | 0,02 | +0,0000 | 0,999999 | −0,8004 | 0,80 |
| 256 µm, dx 0,5 | 0,08 | −0,0006 | 0,9928 | −0,0692 | 0,069 |

**Comparable o no:** no. Son cantidades distintas en geometría y en observable:
1. El 1D es el coeficiente de reflexión complejo de una PML de coordenada compleja en onda completa, para una onda plana y referido al plano x = 0. Su fase depende de ese plano (lo dice su propio `fase_reflexion.py`). Aquí ψ_ov es la fase del solapamiento de un haz gaussiano 2D paraxial con el haz analítico en el plano z = 2 mm. No hay reflexión separada.
2. Los valores son pequeños y estables con la malla (ψ_ov cambia menos de 0,002 rad al pasar de dx 0,5 a 0,25). La diferencia de 0,80 rad con el 1D es de otra cantidad, no de un desacuerdo entre modelos.

ψ_err = arg⟨A_an, A_num − A_an⟩ se ha calculado pero no se interpreta: es la fase de un residuo pequeño. En dominio 256 a θ = 0,08 el residuo es ~12 % del haz (estimado a partir de la coherencia) y su fase (−2,50 rad) no tiene significado físico.

## 7. D4: malla fina dx = 0,25 µm (dominio 128 µm, f 0,2, p 4)

Máximo de la ventana y clasificación pre-declarada (CONTRATO-VACIO K4):

| θ (rad) | máx. dx 0,5 (z) | máx. dx 0,25 (z) | q | E_pre dx 0,5 | E_pre dx 0,25 | cociente E_pre | clasificación (pre-declarada) |
|---|---|---|---|---|---|---|---|
| 0 | 6,04e-3 (2,0) | 5,63e-3 (2,0) | 1,07 | 7,25e-3 | 1,99e-3 | 3,6 | retorno independiente de la malla |
| 0,02 | 5,55e-3 (2,0) | 5,30e-3 (2,0) | 1,05 | 9,42e-3 | 2,69e-3 | 3,5 | retorno independiente de la malla |
| 0,05 | 6,31e-3 (0,5) | 3,82e-3 (2,0) | 1,65 | 2,64e-2 | 7,80e-3 | 3,4 | indeterminado |
| 0,08 | 1,63e-2 (0,4) | 8,36e-3 (1,0) | 1,95 | 5,61e-2 | 1,83e-2 | 3,1 | indeterminado |

Lectura por instantes (los máximos de la tabla mezclan dos causas):
- **Error temprano (causa a), z ≈ 0,4–1,0 mm:** ΔP cae al pasar de dx 0,5 a 0,25 con factor ~3,3 (θ = 0: 1,1e-3 → 3,1e-4 en z = 0,5; θ = 0,02: 1,9e-3 → 5,4e-4). Exponente aproximado log₂(3,3) ≈ 1,7 (orden ~2).
- **Error tardío (causa b), z ≈ 2 mm en 128 µm:** ΔP no cambia con la malla (θ = 0: 6,0e-3 → 5,6e-3; θ = 0,02: 5,6e-3 → 5,3e-3). Es el efecto de frontera de la sección 5.
- Por eso q ≈ 1 en θ = 0 y 0,02 (el máximo es tardío) y q ≈ 1,7–2 en θ = 0,05 y 0,08 (el máximo es temprano para dx = 0,5 pero tardío para dx = 0,25). La clasificación pre-declarada no separa las dos causas; la lectura por instantes sí.
- **B1 en dx = 0,25 y θ = 0:** E_suelo = 1,99e-3 > 1e-3. B1 no se cumple ni en la malla fina. K4 falla.

## 8. Lectura de conjunto

1. **La frontera 009c no devuelve menos de 1e-4 P0 en vacío.** El retorno al núcleo es de 1,5e-3 a 1,6e-2 P0 con dominio 128 o 256 µm y dx = 0,5 µm. Es una cifra de modelo, pero debe tenerse en cuenta antes de usar el absorbente de 009c más allá de su ventana de confianza.
2. **Hay dos causas independientes, y ninguna se resuelve sola.**
   - (a) discretización del haz inclinado en z ≲ 1 mm: baja con la malla y está presente en cualquier dominio. A dx = 0,5 µm ya da 5e-3 a 1,6e-2 para θ ≥ 0,05, así que K1 no se cumple en esa malla aunque la frontera esté lejos;
   - (b) frontera tardía: independiente de la malla y decreciente con la distancia del absorbente (6,0e-3 con 128 µm → 1,7e-4 con 256 µm en θ = 0, z = 2 mm; 1–5e-3 con 128 µm y 5e-5 a 7e-6 con 512 µm a 2 mm en θ = 0,05–0,08).
3. **El absorbente importa y su forma domina.** Las bandas estrechas y abruptas devuelven más (f = 0,1 llega al 116 % de la potencia analítica en θ = 0,05). El barrido de σmax fijo no encuentra un absorbente que cumpla K1 en todo θ.
4. **Sin absorbente, la pared devuelve 9–39 % de la potencia de entrada.** El absorbente reduce ese retorno 15–40 veces. La frontera absorbente sí actúa, pero no basta con la malla y el dominio de 009c.
5. **La fase no se puede comparar con el 1D** (K3). El retorno 1D (|r| = R0^(sin θ)) y la fase de reflexión son magnitudes de otro modelo.
6. **La ley 1D no describe este absorbente** (K6). La dirección también es opuesta: la reflectancia 1D baja de 0,83 a 0,48 entre θ = 0,02 y 0,08, mientras el retorno 2D sube de 5,6e-3 a 1,6e-2 (con esponja) y de 0,13 a 0,39 (sin esponja). La magnitud no es comparable (ver K6).

## 9. Límites

- Ventana muestreada cada 0,1 mm: el máximo real puede estar entre muestras. Los máximos citados son los de la malla temporal de 009c.
- La ventana de la referencia de 512 µm empieza en su propio z_arr (1,1–1,4 mm), por eso su máximo propio excluye el error temprano. Por eso la sección 5 compara en los mismos instantes.
- Un solo cociente de malla (dx 0,5 → 0,25) y dos dominios para D1 (128 y 256 µm), más el 512 µm solo para θ = 0,05 y 0,08. No hay convergencia de tres niveles.
- Los trozos de 160 pasos a N = 512 tardaron 28–35 s en solitario y hasta 70 s con carga paralela (límite de 30 s por hijo superado en parte; `timeout` a 170 s no se alcanzó). La referencia N = 1024 usó trozos de 40 pasos (38–84 s).
- El runner recibió el parámetro opcional `VACIO_SMAX` (por defecto 4·10⁴, idéntico) mientras los lotes se ejecutaban. Cada JSON guarda el hash del runner con el que se generó. K0a se verificó contra 009c con la versión que generó las corridas de S1.
- El solver `adi2d.py` es el de 009c: la única referencia independiente es el analítico. No hay segundo esquema numérico.
- K3 y K6 son veredictos pre-declarados por sus condiciones, no umbrales numéricos.
- La enmienda 1 se redactó tras ver D1 (sin umbral nuevo). Está fechada en el contrato.
- **Coordinación con JEV:** la configuración global pide consultar a JEV antes de decisiones sustanciales. `router.py plan` devolvió una recomendación (esfuerzo xhigh, segunda opinión) sin campo `provenance`, así que no cuenta como decisión de JEV. Una consulta `router.py jev` falló en la validación local del esquema (`ValueError`, `stage: local_schema`) y no se reintentó. No hay decisión de JEV con `provenance=jev`.

## 10. Qué no afirmo

- No afirmo nada sobre un dispositivo, ni sobre la red 3D con guía (δn ≠ 0), ni sobre la esponja de `src/silice/bpm.py` (Codex).
- No afirmo que el error sea de una pared real. Es el de este modelo paraxial con este absorbente.
- No afirmo que el absorbente de 009c sea inválido para θ ≤ 0,08 dentro de su ventana de confianza. Sí que no cumple −40 dB en vacío.
- No afirmo que 512 µm cumpla K1: su error temprano es el mismo que el de 128 µm.

## 11. Pendiente

- Cerrar K1 exige dos cosas a la vez: malla más fina (la causa a baja con la malla, ~dx^1,7; con ese factor, 1e-4 pediría dx ≈ 0,12 µm, extrapolación no calculada) y una frontera lejos del haz (causa b). Ninguna sola basta.
- Una corrida dx = 0,125 µm y un dominio 512 µm pondrían a prueba esa extrapolación.
- Un solver con esquema distinto (p. ej., FFT o BPM de otro código) daría una referencia numérica independiente del ADI.
