# Estado del control de cuadratura y de la capacidad de cálculo

La tarea 1 actual, convergencia T96/Q4 (punto 3 histórico), sigue abierta.
No se ha pasado al barrido modal ni a ninguna tarea posterior.

P4I3 conserva 100 tramos válidos de los 256 previstos: 25600 de 65536
pasos, longitud 0,78125 mm de los 2 mm requeridos. La última continuación
terminó por agotar la espera de memoria: 1800,000227 s registrados
(el exceso de 0,000227 s corresponde al retorno del temporizador).
No se calculó el tramo 101 y no existe dictamen temporal final.
Las interrupciones y todos los campos válidos se conservan.

El control adicional de rigidez aprobó reproducción de la matriz, simetría,
constante y energías físicas lineales. Las cotas de discrepancia permiten
evaluar la consistencia de la integración, no afirmar errores reales del
tamaño de una cota insuficiente ni atribuir los fallos históricos.

| Malla | Comparación | Cota potencia campo | Cota potencia intensidad | Límite | Resultado |
|---|---|---:|---:|---:|---|
| h0,35 | Triangular8–16 | 0,211409 | 0,186660 | 1e-5 | No certifica |
| h0,35 | Triangular12–16 | 6,13057e-6 | 5,41287e-6 | 1e-5 | Aprobado |
| h0,4375 | Triangular8–16 | 3,32654 | 2,94813 | 1e-5 | No certifica |
| h0,4375 | Triangular12–16 | 4,62803e-4 | 4,10157e-4 | 1e-5 | No certifica |
| h0,35 | Duffy12–24 | 4,32715e-7 | 3,82058e-7 | 1e-5 | Aprobado |
| h0,35 | Duffy16–24 | 8,68406e-7 | 7,66743e-7 | 1e-5 | Aprobado |

Las potencias son fracciones de una entrada inicial normalizada a uno.
El control Duffy se registró en 97a33b9 antes de las matrices nuevas;
emplea pesos positivos y bloques de 256 triángulos. El prototipo terminó
en 61,485 s, con los controles analíticos y ambos pares aprobados.
Los controles Duffy de las mallas gruesas siguen pendientes: el intento
coarse se detuvo por recursos antes de ensamblar matrices. No se relajan
umbrales ni se consideran aprobadas las mallas que todavía no se probaron.

La memoria local disponible fluctúa. Se identificó un proceso ComfyUI
perteneciente a Video-Character-Replacement, ajeno a esta tarea, con unos
6 GiB residentes. No se modifica ese proceso. Una lectura local mostró
2,13 GiB disponibles, insuficientes para los contratos vigentes.

Se preparó un cuaderno privado de CPU estándar en Google Colab y sólo
se ejecutó una prueba genérica de recursos, sin datos del proyecto:
12,6714 GiB totales y 11,6548 GiB disponibles, Linux, Python3.13.16,
NumPy2.1.3, SciPy1.16.3 y psutil5.9.5; scikit-fem y meshio ausentes.
El primer intento de insertar código tuvo un error de sangría, conservado
en el cuaderno; la prueba posterior de una línea terminó correctamente.
Eso verifica acceso y capacidad puntual, no ejecución científica externa.

Paquete local para autorizar la transferencia: 36 archivos científicos,
36.702.812 bytes comprimidos; SHA256
4ae9aa8e48b3176225fb004bee307985220d479c18f29462bacbd41dc427df22.
Contiene exclusivamente las tres mallas existentes, matrices, detectores,
entrada, informes de procedencia y módulos del control. CRC y hashes
verificados. No se ha subido a Colab. El cuaderno acompañante fue validado
con nbformat y sus celdas verificadas sintácticamente; ejecución con
datos pendiente de autorización y fijación de dependencias.

No se genera h0,28 antes de la predicción. Faltan todavía precisión longitudinal, contraste
espacial prospectivo y control de dominio. JEV fallback local; sin mediciones
de fabricación ni validación electromagnética vectorial derivadas.

## Actualización posterior: mallas pendientes completadas

Al mejorar la memoria disponible se repitió únicamente el control coarse
que había fallado por recursos, con carpeta nueva y sin cambiar el contrato
97a33b9. Se ejecutó después mid. Ambos terminaron con todos los controles
analíticos y de ensamblaje aprobados, en21,050 y36,058s respectivamente.
El primer fallo coarse se conserva. No se relanzó el ensayo E ni P4I3.

| Malla | Comparación | Cota potencia campo | Cota potencia intensidad | Resultado |
|---|---|---:|---:|---|
| h0,546875 | Duffy12–24 | 6,94202e-7 | 6,04499e-7 | Aprobado |
| h0,546875 | Duffy16–24 | 8,12080e-7 | 7,07145e-7 | Aprobado |
| h0,4375 | Duffy12–24 | 4,18839e-7 | 3,71194e-7 | Aprobado |
| h0,4375 | Duffy16–24 | 4,86969e-7 | 4,31574e-7 | Aprobado |

Se fija Duffy16 como regla común para futuras propagaciones en estas tres
mallas antes de observar ninguna potencia óptica con las matrices nuevas.
Su comparación con Duffy24 aprueba los umbrales preregistrados en las tres.
Son cotas de consistencia entre reglas; no un teorema de error frente a la
integral continua. La diferencia12–24 menor que16–24 en algunos casos
no prueba monotonicidad: puede estar dominada por redondeo y ensamblaje.

Los campos temporales anteriores usaban la matriz histórica triangular8:
se conservan, pero no se reutilizan como resultados primarios del nuevo
operador. Se necesita un protocolo longitudinal nuevo antes de propagar
con Duffy16; P5C/P5D anteriores conservan sus fuentes y dependencias.
La malla fina futura también deberá superar el control de cuadratura.
