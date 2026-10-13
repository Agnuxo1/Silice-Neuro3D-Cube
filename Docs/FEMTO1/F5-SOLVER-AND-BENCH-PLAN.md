# F5/F9 — protocolo preparado; medidas y perfil pendientes

No convertir el análogo de núcleo escalón de 12 um y V=2,92 en un perfil de FEMTOPRINT. El perfil propio de su proceso, su dependencia de profundidad y la polarización requieren respuesta/documentación o cupones K1. El Blender es representación geométrica; su render no resuelve ondas.

## Entradas obligatorias del fabricante

Perfil 2D de índice o modelo medido con dimensiones e índices; distribución elíptica y orientación; propagación/loss, modo y MFD a 1550 nm; valores o límites de birrefringencia/coupling entre polarizaciones; variación con profundidad; banda y tolerancias relativas. Si no hay perfil publicable, proponer K1/K2/K3 con caracterización del fabricante antes de N1. Guardar respuesta literal y procedencia/hash; una cifra de marketing no reemplaza un perfil.

## Solver independiente

1. Control vacío gaussiano y fase uniforme, error <=1e-5, balance <=1e-10; un hilo, casos acotados. No renormalizar campos para ocultar fuga.
2. Eigenmodos del perfil real y de dos guías: LP01 y modos superiores, delta-beta/2 frente a kappa. Refinar dx/dz/dominio por separado; exigir estabilidad de razón <=0,005 para respaldar discrepancia CMT/BPM <=0,02.
3. Propagar campo complejo en SSFM/BPM independiente, incluyendo curvas de acceso del layout y modos verdaderos de entrada; verificar amplitud, potencia y pérdidas. La diferencia de beta por sí sola no valida el acoplo de las curvas ni un árbol completo.
4. Un árbol 1->4 por rango de pesos, sin reasignar puertos ni ajustar al resultado. Comparar las cuatro razones (incluido descarte) con el árbol geométrico.
5. 1530/1550/1570 nm como controles y barrido suficiente para integrar el espectro medido. Dos polarizaciones, pares laterales/verticales y dos profundidades. Un BPM escalar con dos perfiles efectivos solo es admisible si su aproximación vectorial está justificada; no declarar que un solver escalar sin polarización prueba la peor polarización.
6. Coherencia: espectro de la fuente real e integral de términos cruzados de todos los pares; max interferencia integrada <=1%. No usar únicamente lambda^2/Delta-lambda como certificado. El layout v2 no satisface el escalonado de 0,1 mm y no está listo para esta validación.
7. Si hay corrección de kappa, nueva versión/prerregistro y rehacer F3 y controles F4. La prueba sellada final sigue cerrada hasta terminar esa iteración.

## Banco F9 (después de fabricación)

Recepción/microscopía e identificación del chip. Medir cupones accesibles K1 (longitudes adaptadas a gap, orientación y profundidad), K2 (cutback con pérdidas de acoplo controladas) y K3 (bends); actualizar el modelo con enmienda previa a N1. El layout debe ofrecer puertos reales para estos cupones: el boceto v2 no los completa.

C1: barrer cada entrada y registrar las cuatro salidas más descartes cuando sea posible, lambda/polarización/potencia de referencia y oscuridad. RMS relativo W<=5%, fuga de cero<=1%. Calibrar ocho ganancias/offsets únicamente con etiquetas de entrenamiento. Conservar raw ADC antes de corregir.

C2: registrar predicciones antes de revelar >=2000 etiquetas; comparar chip y logística en las mismas imágenes con IC95% pareado y margen de no inferioridad de 3 pp. Tras revelar no se puede optimizar ni repetir esa prueba como confirmatoria.

C3: respuesta temporal de entrada a salida TIA <=2 ns a la potencia/SNR que permite C2, con osciloscopio y trazas crudas; no inferirla solo de longitud o ancho de banda. C4: modelo de energía >=3x frente a cadena digital equivalente con componentes y consumos citados, incluyendo fuente/frontera y precisión/ritmo iguales. No hay demostración actual de energía o latencia física.

NDA, IP, datos y autoría se negocian por separado con el titular. Ningún encargo o medida de banco existe todavía.
