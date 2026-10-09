# Control adicional de cuadratura de la rigidez FEM curva

Registrar fuente y criterios antes de ensamblar las matrices alternativas.
La matriz histórica usa orden de integración 8. La masa y el potencial
tienen integrandos polinómicos en coordenadas de referencia; la rigidez
de elementos curvos contiene inversas del Jacobiano y requiere un
contraste propio. Los controles de simetría y constante son necesarios
pero no equivalen a comprobar esa precisión.

No editar ni sustituir matrices o resultados históricos. Usar la malla
guardada, sin generar geometría nueva, y ensamblar rigidez con órdenes
8, 12 y 16 en otro directorio. Reproducir la matriz 8 histórica con error
relativo máximo de coeficientes ≤1e-13. En cada orden exigir simetría
≤1e-12, residuo de constante ≤1e-10 y energías de los campos físicos
lineales x,y iguales al área del cuadrado dentro de 1e-10 relativo;
producto cruzado igual a cero dentro de 1e-10 veces esa área.

Calcular una diagonal positiva D con M≥D a partir del mínimo del Jacobiano
en cada triángulo y el menor autovalor de la masa P2 de referencia.
Para los pares 8–16 y 12–16, guardar la cota de norma de
D^(-1/2)*(Kq-K16)*D^(-1/2)/(2*beta), mediante la máxima suma de valores
absolutos por fila, beta=1,444*2*pi/(1550 nm). Unidades: m^-1.

Para 2 mm, eta=z*cota es una cota de discrepancia en norma de masa entre
los operadores semidiscretos contractivos correspondientes, con entrada
de norma uno. Calcular también cotas L del operador de cada detector
en norma de masa usando D. La discrepancia de potencia está acotada
conservadoramente por 2*L*eta cuando ambas normas de campo son ≤1.
Registrar todos los valores, aunque el criterio no se supere.

Exigir eta≤1e-6 y las dos cotas de potencia ≤1e-5 para marcar el par como
consistente con esta comprobación conservadora. Un fallo de esa cota
no demuestra que la potencia calculada sea errónea: significa que este
control no la certifica. Requerirá otro contraste registrado, por ejemplo
una propagación con rigidez refinada, antes de declarar muestreo cerrado.
El par 12–16 tampoco es una verdad exacta del integrando continuo.

Aplicable a prototipo h0,35 y a las dos mallas gruesas preparadas; cada
una necesita su propia comprobación. No probar la malla reservada h0,28
antes de la predicción espacial registrada. Ejecutar sólo después de que
termine o falle la recuperación longitudinal, sin competir con su memoria.
Un hilo, RAM inicial ≥5 GiB y final >3 GiB, disco >2 GiB, 900 s por malla.
Guardar matrices alternativas, controles, cotas, fuentes y hashes.
La tarea 1 permanece abierta; JEV fallback local.
