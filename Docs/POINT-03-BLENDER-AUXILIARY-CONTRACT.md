# Controles auxiliares de las plataformas Blender — prerregistro

Se mantienen abiertos T96/Q4 y todas las tareas posteriores. Este ensayo
no propaga T96, no reemplaza FEM, no instala complementos globales y no
atribuye validación vectorial a un trazador de rayos ni a Monte Carlo.

Fuentes externas fijadas antes de ejecutar controles:

- BlenderPhotonics: 732799f9e3ebe10e013e316b8a21d88452755dc8.
- Blender Optics Simulator: 2b488e2e99dff4f56d67f57f9674bd00f812dda1.

Se importará directamente field.py de Optics Simulator, sin modificarlo ni
ejecutar el inicializador de Blender. Sus unidades son mm y nm. Se comprobará
el espectro angular homogéneo con n=1,444, longitud de onda en vacío1550nm,
longitud de onda efectiva1550/1,444nm, z=0,2mm y ventana256µm:

1. Onda plana constante y modo Fourier periódico (3,2): error relativo del
   campo complejo <=1e-10 frente a su autovalor analítico, sin ajustar fase.
2. Gaussiana de radio30µm, mallas256 y512: diferencia relativa <=1e-8;
   diferencia frente a solución paraxial analítica <=2e-4. Esta última compara
   dos aproximaciones distintas; no constituye convergencia de T96.
3. Potencia integral relativa e ida/vuelta sin filtro <=1e-10. La reversibilidad
   sólo se exige para estas entradas de espectro propagante efectivo, no para
   campos evanescentes ni para los componentes eliminados por band_limit.
4. Dos entradas de forma inválida deben producir ValueError. El módulo
   convierte NaN a cero: los adaptadores del proyecto deben rechazar datos
   no finitos antes de llamarlo; nunca usar ese saneamiento como auditoría.

Se preparará un JMesh de visualización regional desde la malla FEM existente:
subdivisión de cada triángulo P2 en cuatro caras usando sus nodos medios,
coordenadas convertidas de metros a milímetros, índices de caras base1.
Verificaciones: conteos, partición exhaustiva de dos regiones, índices,
orientación no degenerada, reconstrucción de coordenadas <=1e-18m.
Es una sección planar con bordes curvos aproximados por segmentos, NO un
volumen tetraédrico ni una nueva geometría de producción. La importación
real en BlenderPhotonics permanece pendiente mientras no se ejecute Blender.

Se conservarán hashes de fuentes, versiones, unidades, métricas y resultados.
JEV: fallback local por el bloqueo de seguridad heredado; ninguna
recomendación externa atribuida. Sin transferencia de datos a Colab.
