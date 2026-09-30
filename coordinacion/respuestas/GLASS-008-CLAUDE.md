# GLASS-008 — revisión del perfil discreto y modos firmados (Claude, 2026-09-30)

Leí `Docs/GLASS-007-DISCRETE-CONTRACT.md`, `Docs/GLASS-007-RESULTS.md` y `src/silice/tracks.py` sin editar. Salida de mis cálculos: `experimentos/glass009_claude/aperture_008.txt`. Sin GPU/Blender. JEV: sin aval.

## Hallazgos sobre el muestreo de discos y la geometría
1. **Relleno real del anillo**: 16 trazos/corona → 68,7 %; **32 → 95,2 %**; 64 → 98,9 % (trama fina de 1200²). Con 32/corona los discos se solapan en la circunferencia (paso 1,42 µm en r=7,25 µm frente a diámetro 2,5 µm): "96 trazos" **ya es casi una camisa continua**, por eso 96 ≈ continuo (33,3 % vs 34,9 %). "96 se acerca al ideal con menos trazos que 192" es cierto pero de poco contenido: 96 ya rellena el 95 %.
2. **Coronas solapadas radialmente**: pasos de 1,75 µm entre radios frente a diámetro 2,5 µm. Salvo quizá 16/corona, el ensayo no explora el régimen de trazos verdaderamente separados.
3. **La cuña nominal de 30° no es la apertura real**: omitir centros con |ángulo|<15° deja, tras la unión de discos, un canal radial libre de **17,7°** (medido rayo a rayo de r=6 a 12 µm). Las variantes de 16/32/64 sin cuña no tienen ningún rayo radial libre (0°). Conviene reportar "abertura efectiva 17,7°" y generar una variante con la abertura definida sobre la unión final.
4. **16 trazos/corona pierde ~61 % de la potencia en el núcleo (13,6 % vs 34,9 %) sin ningún canal radial abierto**: la fuga viene de tunelado entre discos y huecos parciales, no de una vía recta; coherente con el túnel evanescente de mi 006a.
5. **Discos circulares uniformes**: un trazo láser real tiene sección alargada según la dirección de escritura y Δn no uniforme (posibles halos positivos, nanogratings birrefringentes en sílice). El modelo es una hipótesis geométrica, no una receta.
6. **Igual integral ≠ igual dosis** (Codex ya lo dice). Además, el control de integral sube el pico a −0,0030986 (+3,3 %); como la fuga depende exponencialmente de κ ∝ √|Δn|, el 35,5 % frente a 33,3 % es coherente con ese reescalado y no prueba una ventaja.
7. **Convergencia parcial**: con el sesgo de píxel del núcleo (−3,4 % de área a dx=0,5 µm, ver GLASS-009) los cambios de dx en 007 mezclan geometría del observable con física.

## Control independiente barato que no propaga
(a) relleno del anillo, (b) canales radiales abiertos, (c) área modificada frente a la suma de discos: <2 s de CPU y detecta errores de máscara. Además `G0` de 009 muestra 0 píxeles de diferencia entre mi reconstrucción independiente y `silice.tracks` en los cinco perfiles.

## Modos firmados (006a)
`experimentos/glass006a_claude/resultados.json` contiene `gamma_re`, `gamma_im` firmados y `growth` por caso y configuración. Convención A∝exp(iγz): decaimiento ⇔ Im γ>0; el error de signo de mi contrato está reconocido en `ERRATA.md`. Ningún caso muestra Im γ<0. El emparejamiento entre retículas se hizo por solape L2 del vector en r<60 µm (sin peso r·dr, como notó Codex): es diagnóstico, no identidad modal física.

## Peticiones
Añadir a 007 (i) una variante con apertura efectiva controlada por la unión final, (ii) 16 trazos/corona con δn escalado para igualar la integral, y (iii) declarar el relleno del anillo (68,7 / 95,2 / 98,9 %) en la tabla de resultados.
