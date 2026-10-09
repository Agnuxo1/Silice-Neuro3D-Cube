# MEGA-001: contrato de diagnóstico analítico (CPU)

Fijado el 2026-10-05 antes de ejecutar el nuevo script. No modifica los
contratos GLASS ni certifica un trazador GPU, una guía o hardware óptico.

Hipótesis: compartir geometría mediante transformaciones afines puede conservar
impactos, pero reutilizar la longitud de referencia como longitud física altera
la fase. Una simplificación visual tampoco garantiza interferencia correcta.

Ensayos propios, NumPy float64, un hilo, matrices 3x3 y vectores solamente:

- Seis transformaciones: identidad, rotación, traslación, escala uniforme,
  escala anisótropa y cizalla; cuatro rayos interiores por triángulo.
- Contrastar intersección directa del triángulo transformado con intersección
  en referencia, conservando el parámetro mediante dirección no renormalizada.
- Contrastar normales con inversa transpuesta; longitud física calculada en
  coordenadas del mundo, índice homogéneo 1.444 y longitud de onda 1550 nm.
- Presupuesto ilustrativo de fase 0.01 rad; diferencias de camino 0, 1, 10,
  200 nm en dos brazos ideales de igual amplitud. La fórmula analítica del
  puerto oscuro es sin²(delta_fase/2), sin ajuste de fase posterior.
- Memoria hipotética de 500 millones de estados, tamaños declarados, sin
  reservarlos. Ejemplo de rayos de imagen, NO medida de rayos/s de AMD.
- Consultas de capacidades del controlador: solo metadatos de nvidia-smi y
  vulkaninfo, timeout 20 s cada una, sin construir BVH ni lanzar kernels.

Gates congelados: error de impacto <=1e-12 m, error de parámetro <=1e-12 m
con dirección mundial unitaria, error de normal <=1e-12; diferencia entre
intensidad compleja y fórmula <=1e-12; presupuesto de camino reproduce fase
0.01 a error <=1e-12. El adversario de escala debe cambiar fase >0.01 rad:
un PASS significa detectar el error, no aprobar la aproximación.

Conservar JSON nuevo con SHA del contrato/script. No sobrescribir resultados.
Fallo de consultas se registra separado; no convertirlo en soporte hardware.
Salida bajo resultados/codex. Límite interno 30 s, subprocess acotados; sin
GPU, Blender, SDKs ni descargas. Este script no ejecuta Maxwell/BPM ni usa
los archivos de Claude. No registro externo ni publicación incidental.
