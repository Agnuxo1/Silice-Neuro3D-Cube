# M1: nueva prueba prospectiva N767, registrada antes de geometría

L2 completo y auditado pasa precisión práctica; L1 conserva su FAIL de
orden y E/G/H/K conservan sus dictámenes. M0 ofrece sólo diagnósticos
amplios. M1 exige una predicción estricta distinta, antes de una NUEVA
geometría/propagación N767. No repetir casos anteriores.

Hipótesis: las mallas bilineales más finas empiezan un régimen consistente
de potencia del núcleo. Primarias fijas N320/400/500/640, referencias H.
N626 negativo se conserva en M0 y en el informe; no se incluye como nueva
razón de refinamiento desde640 porque626/640 no cumple separación1,1.
No escoger datos después de N767 ni cambiar ninguno de estos criterios.

Para cada detector bilineal: orden generalizado positivo de las ternas
320/400/500 y400/500/640, resolviendo la razón de incrementos con los
espaciados reales. Buscar p en[0,05;8]. Exigir monotonía, incrementos>1e-12
y discrepancia de órdenes<=20%. Predecir N767 con la última terna y
congelar fuente/contrato/valores/hashes ANTES de preparar su geometría.
Si los prerrequisitos fallan, no iniciar óptica M1.

Geometría analítica D original, cambiando sólo N y nombres de salida en
el generador G. Área global<=1e-12 relativa y48celdas seleccionadas antes
del contraste independiente: error local<=1e-12, calidad<=1e-13. Mismos
96trazos, radio6µm, dn=-0,003,1550nm,2mm y dominio nominal128µm. Misma
fórmula de coordenadas centradas en índice entero y fantasmas Dirichlet
cero. N impar cambia la posición discreta de los bordes O(dx); es parte
de la secuencia del mismo algoritmo, no una validación de frontera física.

Referencia nueva: worker exponencial H SIN modificar, particiones19/31,
50checkpoints. Segundo integrador: worker L1 adaptado exclusivamente
626→767 (tres literales) y400→512 (dos tamaños de tramo),20480pasos,
dz=0,09765625µm,40checkpoints. Kernel FDST sin modificaciones.
Guardar las dos fuentes adaptadas y hashes antes del primer paso.

Antes del primer campo óptico, congelar manifiesto con todos los inputs,
contratos, fuentes, predicción y geometría. CPU un hilo, RAM>1,5GiB,
disco>2GiB; hijos360s/corte370s. Presupuesto GLOBAL18000s (5h), incluyendo
geometría, referencias y FDST; control por trabajador y antes de cada hijo.
La previsión FDST es4510s desde el control sintético. La referencia se
estima en~9000s por escala de H2; esa estimación no garantiza ejecución.
Conservar fallos, no recuperación automática ni ampliación durante M1.

Criterios nuevos, locales y prospectivos, para AMBOS detectores:
1. Todos90campos, cadenas, fuentes, geometría, finitos, recursos y balance
   pasan; cuadratura16/32 cambia<=1e-10. Gaussianas K previas aprobadas.
2. Referencias19/31: campo relativo<=1e-9; potencia cambia<=1e-8;
   cota de diferencia de observable por normas crudas<=1e-6.
   Este límite de potencia nuevo es un control del presupuesto práctico;
   NO convierte el FAIL de referencia1e-10 de K626 en PASS.
3. FDST frente R31: campo relativo<=1e-4; diferencia de ambas potencias
   <=1e-6; cota del observable respecto a R31 + consistencia + cuadratura
   <=1e-5. Sin renormalizar salidas ni alinear fases. No afirmar orden4.
4. Residuo de la predicción N767<=10% de |P767-P640|. La nueva terna
   500/640/767 tiene p positivo, monotonicidad y discrepancia<=20% frente
   a400/500/640. Informar también M0, sin usar su banda amplia para aprobar.
5. Indicador espacial fino=1,25*|P767-P640|/(r^min(p_nuevo,2)-1),
   r=767/640. Sumar diferencia FDST/R31, referencia, cuadratura y la
   diferencia entre reconstrucciones de campo/intensidad. Exigir total
   <=1e-3 y<=1% deP767. Indicador CONDICIONAL, no cota rigurosa/cobertura.

M1 sólo puede respaldar convergencia LOCAL de potencia escalar para este
input/geometría/dominio/longitud. Exigir auditor independiente antes de
adoptar cualquier cierre. Si un criterio falla, retener FAIL y punto3
abierto. Si todos pasan, conservar todos los FAIL históricos y documentar
el nuevo alcance; frontera/campo/fase general, Maxwell y fabricación
siguen en sus puntos posteriores. JEV fallback local, bloqueo heredado.

Fuentes: [NASA](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html),
[SciPy acción exponencial](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.sparse.linalg.expm_multiply.html),
[Yoshida1990](https://tlakoba.w3.uvm.edu/math6737/for_final_topics/SSM_1990_Yoshida.pdf).
