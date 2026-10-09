# S16: serie espacial y predicción reservada con la regla común K16

Se registra antes de los campos F1 h=0,35 y de generar h=0,28. Actualiza
las dependencias del contrato P5D, conservando sus observables, fórmulas
y criterios. No reutiliza sus campos K8 como K16 ni modifica sus resultados.
No se ha calculado una predicción espacial S16 al registrar este documento.

Serie fija h=0,546875/0,4375/0,35/0,28µm, razón nominal r=1,25, dominio±64µm.
Mismo generador Gmsh, semilla, campos de tamaño, materiales y controles.
Son mallas sistemáticas no anidadas: la pertenencia al régimen asintótico
debe contrastarse, no suponerse a partir del tamaño nominal.

Tres primarias: Padé32768 de C2-R1(coarse), M2-R1(mid) y F1(h0,35),
con K Duffy16 en todas. Cada una requiere auditoría local de integridad y
de los cinco criterios temporales, controles de geometría, entrada,
detector y amortiguación, y sus fuentes/matrices/campos por hash.
No sustituir una primaria por Radau ni elegir otra terna tras resultados.

Dos observables obligatorios: campo cuadrático integrado en el círculo
físico R=6µm e intensidad reconstruida linealmente, como en P5D. Las
potencias son fracciones respecto a la entrada normalizada, no vatios
medidos. Las discrepancias temporales entre métodos no son error absoluto.

Antes de generar el resultado reservado, para cada observable:
delta01=P1-P0, delta12=P2-P1, p=log(delta01/delta12)/log(r).
Exigir incrementos finitos, no nulos, del mismo signo;0,5<=p<=6; cada
incremento>20veces la mayor discrepancia temporal de potencia de las tres
mallas. Si falla cualquiera, conservar el resultado negativo y detener
antes de generar h=0,28. No ajustar índices, detectores ni umbrales.

Predicción fija: P3_pred=P2+delta12/r^p. Guardar potencias, p, predicción,
fuentes y hashes y publicar/verificar en Git antes de generar la malla
reservada. El controlador y auditor prospectivos deberán estar registrados
y superar controles con leyes conocidas y rechazos antes de usar T96.

Malla reservada: algoritmo P4C con hlocal0,28/fondo1,12µm; controles
geométricos originales, error de área curva<=1e-5relativo, y controles de
proyección/detector/amortiguación. Duffy16 requiere su control propio
contra Duffy24 en esa malla antes de propagación. No adoptar una regla
por resultados de potencia. Una insuficiencia de cuadratura se conserva.

Trayectorias reservadas: Padé65536 como primaria y Radau65536 como
contraste, mismos datos/modelo. La partición y límites de recursos deben
fijarse en un protocolo de ejecución previo y compatible con la ventana,
sin alterar esos pasos o umbrales por sus resultados. No comenzar una
ejecución que requiera extender el límite absoluto del usuario.

Después de la auditoría temporal local del resultado reservado, exigir
simultáneamente, para ambos observables:

- delta23=P3_real-P2 no nulo y del mismo signo que los incrementos previos.
- p_nuevo=log(delta12/delta23)/log(r) positivo y en[0,5;6].
- |p_nuevo-p|/max(p_nuevo,p)<=20%.
- |P3_real-P3_pred|<=10%de|delta23|.
- |delta23|>20veces la mayor discrepancia temporal de potencia.
- U=1,25*|delta23|/(r^min(p_nuevo,2)-1).
- U+cotaPSDtemporalmax+discrepancia entre reconstrucciones finas+
  indicador de cuadratura fino<=1e-3 y <=1%deP3_real.

El indicador de cuadratura del detector es su cota de operador en norma
de masa multiplicada por la potencia de masa. Informar cada término.
No son cotas rigurosas del error continuo ni intervalos estadísticos95%.

Un aprobado S16 no cierra la tarea1: queda sensibilidad al dominio,
con protocolo anterior a sus campos. La validación conjunta de frontera,
campo y fase es otra tarea posterior en el orden del usuario.
Conservar todos los negativos y no introducir una malla alternativa en
esta ejecución si falla la predicción.

Referencia metodológica:
[NASA, convergencia espacial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html).
No transfiere a T96 una garantía de error físico. JEV fallback local;
no hay campos reservados, muestras fabricadas o validación vectorial
derivados de registrar este contrato. Tarea1 abierta.
