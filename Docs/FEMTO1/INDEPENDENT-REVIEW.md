# FEMTO-1 — revisión crítica independiente de F1/F2, layout provisional y ruido

Fecha UTC: 2026-10-13T10:31:50.071874+00:00.
Repositorio: `D:/PROJECTS/Silice-FEMTO1-20261013`, rama `codex/femto1-20261013`.
Instantánea Git observada al cierre de la lectura: `ac05f670c1f428f750fe4d259ede6accae3dd97b`; el servidor anunció el mismo SHA mediante `git ls-remote`.

## Dictamen

La aritmética, las matrices guardadas y los resúmenes MC de F1/F2 son consistentes. No encontré acceso al test en el entrenamiento revisado ni calibración con etiquetas de validación. Esto es evidencia numérica y custodia procedural del mismo equipo, sobre MNIST con exploración previa. No certifica datos históricamente inéditos, un dispositivo ni fabricación.

**F3, F4, F5, F6, F7 y F8 no están cerrados.** El layout v2 falla su DRC; el presupuesto óptico es condicional y faltan las reglas/perfil/tolerancias del fabricante y el solver independiente. La futura liberación del test requiere fortalecer su comprobación de requisitos. No procede declarar listo para fabricación ni revelar etiquetas.

## Alcance y restricciones respetadas

Se leyeron AGENTS.md, contrato de investigación, checkpoint factual de FEMTO-1, guía v1.1, EXECUTION.md, protocolos F1/F2, layout/ruido y reparación v2, fuentes y recibos Git/prerregistro. Se verificaron archivos existentes con Python de `D:/SiliceAgentkit/.venv-closure/Scripts/python.exe`, `-B` y un hilo. Se calcularon de forma independiente transformación, árbol, potencias, resúmenes y distancias de segmentos. No se reentrenó ni se repitió el Monte Carlo/compilación/DRC, no hubo GPU, modificación de fuentes, push ni mensajes externos. No se abrió `test_X.npz`, ningún fichero bajo `sealed/`, ni el origen de etiquetas públicas MNIST. El único archivo escrito por esta revisión es este informe.

Esta revisión satisface una intervención crítica acotada de F6; no sustituye la reproducción completa con contexto independiente requerida por F8. JEV no se consultó por la instrucción expresa del encargo y no se atribuye aval remoto a estos resultados.

## Evidencia comprobada

- Los SHA-256 de los cinco archivos de entrada prerregistrados en F1/F2 coinciden con sus recibos. Los doce artefactos del recibo de auditoría coinciden; también los hashes de RUN.json para sus productos. No se encontró cambio de fuentes F1/F2 respecto al compromiso.
- Manifiesto SHA-256 `1324314d6d4b70884f038bd83c6196a2b40f50dd4fa98b578c7174dc33037bd5`: copia Git, copia pública y referencia del informe coinciden.
- Se verificaron hashes de `fit.npz`, `calibration.npz`, `validation.npz`: 11882, 2968 y 4949 registros; IDs mutuamente disjuntos, entradas finitas en [0,1]. Los 4955 registros de test y su sello se constatan solo como declaración del manifiesto/código, sin abrirlos ni verificarlos de nuevo.
- `W_main.npy = W_nominal.npy`, 4×16, no negativa, suma máxima por columna 1, exactamente un cero estructural por columna.
- Conversión manual `W=(S-min_k S_kj)/max_j sum_k(S_kj-min_k S_kj)` frente a matriz guardada: error 0. La resta añade el mismo término a los cuatro scores, y la única escala global conserva argmax. No se aplica normalización independiente por columna. Las decisiones de validación del modelo con signo y del pasivo coinciden exactamente.
- Reconstrucción manual del árbol con hojas `[a,b,c,descarte]`, razones `r1=a+b`, `r2=a/(a+b)`, `r3=c/(c+descarte)`, pesos `[r1*r2,r1*(1-r2),(1-r1)*r3]`: error máximo `1,1102230246251565e-16`. Los prototipos normalizados y su transformación pasiva producen decisiones idénticas en validación.
- `validation_power.npz` reproduce `X_validation @ W_main.T` con error 0; etiquetas idénticas a la partición de validación. Lectura guardada: cuatro ganancias estrictamente positivas y cuatro offsets, sin mezcla entre detectores. La normalización interna de fit_readout es una escala numérica absorbida en esas cuatro ganancias, no un noveno parámetro electrónico.
- Los 1000 registros de `MC_validation.npz` son 200 por cada sigma; índices completos 0–199. Media, desviación muestral, p05, mínimo y número de éxitos del optimizador coinciden exactamente con F2_validation.json.
- Los 1400 registros de `MC_noise.npz` son 200 por siete niveles de ruido. Las mismas estadísticas y gates coinciden exactamente con NOISE-POWER.json. Las fórmulas guardadas de potencia y ruido se reproducen con error 0 bajo sus supuestos.

| Resultado sobre la misma validación | Precisión |
|---|---:|
| Nominal sin lectura electrónica, C=10 | 87,3106 % (4321/4949) |
| Nominal con ocho parámetros | 89,3110 % (4420/4949) |
| κ sigma=0,1 sin recalibrar, MC200 | media 72,7042 % |
| κ sigma=0,1 con ocho parámetros, MC200 | media 88,1234 %; p05 86,3993 %; mínimo 81,0063 % |
| κ sigma=0,2 con ocho parámetros, MC200 | media 84,9505 % |
| κ sigma=0,1, TIA sigma=0,05, calibración sin ruido (F2) | media 50,1186 % |
| κ sigma=0,1, TIA sigma=0,005, calibración con ruido (nuevo barrido) | media 86,8498 %; p05 84,2574 %; mínimo 80,8648 % |
| κ sigma=0,1, TIA sigma=0,01, calibración con ruido | media 83,5076 % |
| κ sigma=0,1, TIA sigma=0,05, calibración con ruido | media 59,8456 % |

El IC Wilson nominal guardado [86,3542 %, 88,2091 %] se refiere al número de imágenes. No se debe sustituir por la desviación entre chips ni tratar los 1000 chips sobre las mismas imágenes como 1000 conjuntos de prueba independientes.

## Cronología y prerregistro: qué demuestra

Secuencia de commits y fechas registradas, en UTC:

| UTC | Registro |
|---|---|
| 10:07:25 | `2df24924`: protocolo/fuentes F1/F2 |
| 10:07:44,422 | recibo de compromiso: published_at_commitment=true, published_check=server |
| 10:07:45 | `229cce9f`: recibo |
| 10:07:58,467 | sello declarado por manifiesto |
| 10:08:20 | `3c08b9b3`: manifiesto de custodia |
| 10:09:32,447 | RUN.json: final F2, duración 63,893 s |
| 10:11:47 | `327d0449`: productos F2 |
| 10:16:55 | `65b53c5f`: auditoría mecánica y fallo de ruido conservado |
| 10:20:34 / 10:20:39 | `66183f21` / `1277d957`: protocolo/recibo layout y ruido |
| 10:22:19 / 10:22:23 | `18b396c7` / `ac05f670`: fallo de serialización conservado, reparación/recibo prospectivos |

Los recibos anclan protocolo/fuentes en blobs Git. `train.verify_commitment` lee el protocolo comprometido, comprueba los blobs actuales y consulta el servidor para exigir que el compromiso sea ancestro del head anunciado. Se confirma actualmente esa historia accesible en el servidor. El tiempo inicial aproximado deducido de duración/final de F2 es posterior al commit del manifiesto.

**Límite:** los tiempos Git y de los JSON son registros locales, y ls-remote actual no reconstruye por sí solo la hora histórica de publicación. No se aportó un sello externo independiente, firmado/inmutable, de la publicación anterior al entrenamiento. Los recibos y código muestran una disciplina prospectiva coherente; no constituyen prueba forense independiente de esa precedencia. La auditoría mecánica lo declara expresamente y no hay razón para convertir su passed=true en confirmación científica externa.

## Bloqueantes y correcciones necesarias

### B1. DRC provisional negativo; los conflictos no son todos artefactos del muestreo

`resultados/codex/femto1_layout_20261013_v2/DRC.json` conserva 18 entradas de error: una ruta de descarte incompleta (`N1-I8-leaf3`), una entrada agregada con 506 parejas de separación y 16 haces que incumplen el escalonado de coherencia de 0,1 mm. Radio mínimo guardado 24,9999999277 mm, compatible con la tolerancia numérica del gate. 941 guías, 192 acopladores de red. Matrices recompuestas bajo el modelo provisional: errores ≤1,11e-16. Esto demuestra aritmética de sus descriptores, no aislamiento ni transferencia óptica real.

Comprobación independiente de las 506 parejas:

- 314 ya tienen puntos de las polilíneas por debajo de la regla de 12 µm dentro de un haz o 30 µm entre otros trazos. Son violaciones geométricas reales de esas reglas.
- Las restantes 192 fueron marcadas por el margen conservador de 10 µm. Se calcularon distancias de segmentos completas para candidatos próximos: 2 infracciones adicionales y 190 parejas que cumplen la distancia de polilínea aunque el bound conservador las marque.
- Total: **316 parejas infractoras de la geometría guardada**, y 190 banderas conservadoras. Esto no altera el resultado ni los 506 registros del DRC prerregistrado, que sigue fallando. No se autoriza quitar margen/relajar umbral después de observar resultados.
- Ejemplo grave: `N3-I11-leaf0` y `N3-I11-leaf2`, haces distintos, distancia entre puntos ≤0,596003 µm frente a 30 µm.
- Infracciones adicionales: `N3-I5-leaf0` / `N3-I7-leaf0`, 11,247298 µm frente a 12; `N4-I8-leaf1` / `N4-I8-leaf2`, 29,615736 µm frente a 30.
- Ejemplo de bandera conservadora: `N1-I1-leaf0` / `N1-I1-leaf1`, distancia de segmentos 39,206442 µm frente a 30.

Método de distancia: para cada pareja se aplicaron las mismas exclusiones de 60 µm alrededor de extremos compartidos que usa el DRC. Un KD-tree de puntos medios selecciona todos los pares de segmentos cuya distancia podría ser menor que la regla, con radio igual al umbral más ambas semilongitudes máximas. Para esos candidatos se compara el punto estacionario interior válido de la distancia cuadrática y las cuatro proyecciones de extremos. Los pares restantes no pueden infringir la regla por desigualdad triangular. Es distancia de polilíneas, no solver de acoplo ni certificación de curvas continuas/fabricación.

Los desfases mínimos de camino de los haces son de unos 0,229–2,767 µm, inferiores a los 100 µm exigidos. Aunque se eliminasen las banderas conservadoras, siguen existiendo infracciones claras y coherencia insuficiente. Hace falta un layout nuevo con compromiso prospectivo y gates iguales.

### B2. Terminaciones de descarte y acceso a cupones incompletos

`geometry.py:156` fija el descarte en `[0.044, base, z]`. Para N2 y N3 los 32 extremos están estrictamente dentro del bloque, porque base=5/10 mm no es una cara lateral del bloque de 25 mm. No se modela una región de dispersión T. El DRC no exige que el descarte alcance una cara exterior o una terminación física de dispersión. N1 además conserva una ruta de descarte incompleta.

Los 104 trazos de K1/K2 tienen sus 208 extremos estrictamente interiores: comienzan x=0,5 mm y terminan antes de la cara x=45 mm. No se incluyen continuaciones a facetas/puertos ni un mecanismo de acceso óptico. Por tanto, la representación actual no demuestra cupones medibles por inyección y recogida externa o cutback. Requiere diseño de acceso y terminaciones, junto con pruebas DRC específicas. Estos defectos son independientes de la lista de separaciones.

### B3. F6 físico y presupuesto de potencia incompletos

`common.realization` usa perturbaciones gaussianas relativas de κ, correlación compartida 0,8, recorte de multiplicadores negativos y ley sin². No incluye geometría real, polarización, anisotropía/profundidad, banda, pérdidas variables, fuga a ceros, desalineación o no uniformidad de la codificación. Eso se declara y sigue pendiente. La escala κ de N2=1,1 es una hipótesis de compensación, no caracterización K1.

El mayor ruido ensayado que pasa el objetivo medio fijo de 85 % es 0,005; 0,01 falla. No se ha localizado el umbral continuo entre ambos, ni demostrado que todos los chips pasen. Con sigma κ=0,2, la media F2=84,9505 % está ligeramente por debajo de 85 %, por lo que ese caso no permite afirmar que pasa F6.

Presupuesto condicional: `sigma = NEP*sqrt(B)/(P_fuente/16*eta_in*eta_out*eta_prop)`, B=500 MHz, eficiencias de entrada/salida 0,5, pérdida 0,2 dB/cm y camino supuesto 55 mm. Para sigma=0,005 se requieren 0,368719 / 3,687185 / 36,871854 mW con NEP=1e-12 / 1e-11 / 1e-10 W/√Hz respectivamente. El último caso supera 10 mW. El camino máximo guardado del layout es 45,362912 mm; 55 mm es una hipótesis conservadora en ese presupuesto, no una medición ni el resultado de un layout válido.

No hay TIA/fotodiodo/fuente seleccionados con NEP, área y ancho de banda demostrados, ni ruido de disparo combinado, ni datos de peor polarización. La suma calculada propagación+rise=0,969136 ns excluye ADC, decisión y calibración; no demuestra latencia extremo a extremo ≤2 ns. NOISE-POWER.json mantiene correctamente F6_passed=false y sealed_test_ready=false. Deben mantenerse.

### B4. Fortalecer el guard de liberación antes de la prueba sellada

`custodian.py:107-112` acepta un literal backend y un booleano `sealed_test_ready` en dos JSON proporcionados por el llamador. Comprueba hash de predicciones, orden/longitud y sello de etiquetas, pero no vincula la liberación a hashes/identidad vigentes del modelo, geometría Blender, protocolos y pruebas reales F0/F3/F5/F6 ni verifica individualmente esos gates. Un recibo stale o un JSON mínimo puede permitir una liberación prematura. Es un bloqueo del procedimiento futuro, no evidencia de fuga actual.

Antes de invocar reveal, implementar y probar por separado un guard que rechace requisitos ausentes/falsos, artefactos modificados y versiones desparejadas, con recibo de liberación generado por verificación actual. El marcador de consumo debe ser atómico antes de exportar etiquetas: hoy el recibo se crea después de escribirlas, por lo que una interrupción o concurrencia podría revelar y no dejar el marcador normal. No ejecutar esos controles contra la bóveda real; usar datos sintéticos.

## Límites de selección, calibración y afirmaciones

La selección de C y del candidato nominal/ruidoso usa validación, como previsto. El candidato noise_aware no converge en 30 iteraciones y tiene 76,8034 % ideal, por debajo de la elegibilidad; el fallo se conserva. El MC de selección usa una semilla distinta del MC posterior. No se encontró reajuste con validación de las ocho ganancias/offsets: su ajuste usa la partición de calibración de entrenamiento. El nuevo barrido calibra con ruido, por lo que 59,8456 % a sigma=0,05 no reemplaza retrospectivamente el 50,1186 % original.

El IC de validación después de selección tiene un límite de selección/adaptación y no sustituye la prueba de una sola vez. El conjunto MNIST y sus etiquetas son públicos, ya tuvieron exploración previa y se almacenan en el mismo host: el nuevo reparto no establece un dataset independiente históricamente desconocido. La ausencia de test en train.py y la custodia declarada respaldan el procedimiento revisado; no certifican ausencia histórica de cualquier acceso en otro proceso.

Solo son defendibles ahora: clasificador numérico pasivo equivalente al logístico sin sesgo en la validación; ocho parámetros de lectura ajustados con entrenamiento; tolerancia simulada bajo una distribución supuesta; barrido de sensibilidad y requerimientos de potencia condicionales; layout fallido conservado. No afirmar chip autónomo pasivo tras añadir offsets, invariancia al brillo con offsets, 95 % en MNIST, robustez a tolerancia real del fabricante, dos polarizaciones verificadas, velocidad/energía física o fabricación lista. El objetivo F2 ideal no debe presentarse como superar la logística digital: la transformación está construida precisamente para reproducirla.

## Estado final para continuidad

Mantener test cerrado. Conservar fallo de serialización v1, reparación solo de escalares v2 y DRC negativo sin cambiar umbrales. Preparar por separado guard de liberación y layout/cupones/terminaciones revisados con registro previo. Esperar reglas/perfil/tolerancias F0 para F5 y el modelo completo F6. F4 sellado se ejecutará una sola vez tras resolver esas dependencias. F7 y la reproducción/revisión final F8 siguen pendientes; este informe no autoriza envío ni fabricación.
