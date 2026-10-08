# Uso acotado de BlenderPhotonics y Optics Simulator

La convergencia T96/Q4 sigue abierta. Se han inspeccionado y fijado las dos
plataformas propuestas por el usuario y ejecutado un control auxiliar
con código original de Optics Simulator. No se ha iniciado la tarea siguiente.

| Plataforma | Fuente fijada | Utilidad para Silice | Límites relevantes |
|---|---|---|---|
| [BlenderPhotonics](https://github.com/NeuroJSON/BlenderPhotonics/tree/732799f9e3ebe10e013e316b8a21d88452755dc8) | 732799f9 | Intercambio de superficies etiquetadas; preparación futura de volúmenes tetraédricos con Iso2Mesh | runmmc.py configura fluencia/energía y propiedades mua,mus,g,n; este transporte Monte Carlo no proporciona el campo coherente guiado requerido por T96/Q4 |
| [Blender Optics Simulator](https://github.com/emircbngl/blender-optics-simulator/tree/2b488e2e99dff4f56d67f57f9674bd00f812dda1) | 2b488e2e, manifiesto0.31.0 | Espectro angular escalar homogéneo como control independiente; posteriormente banco de entrada/salida, Gaussianas, alineación y polarización | El trazador principal usa rayos/ABCD; field.py no acepta un perfil de índice T96 ni resuelve por sí solo sus modos vectoriales |

Ambos indican GPLv3; la segunda licencia admite versiones posteriores.
Se usan clones externos fijados, sin copiar código de terceros al repositorio
ni activar instaladores/actualizadores de complementos. Las instalaciones
completas requieren Blender4.4+ y4.2+ respectivamente; no se ejecutaron.
Los ensayos locales importaron únicamente el módulo autónomo field.py.

## Evidencia local preregistrada

Contrato y ejecutor: commit5f2d9c3, previo al informe de2026-10-08T16:55:58UTC.
Python3.13.7, NumPy2.2.6. Índice homogéneo1,444, lambda efectiva1550/1,444nm,
ventana256µm, propagación0,2mm, radio gaussiano30µm. Sin ajustar fase ni
renormalizar la salida. No se propaga el dispositivo T96 en este ensayo.

- Onda constante: error complejo0 en ambas mallas.
- Modo Fourier(3,2): errores1,042e-15 y8,314e-16, límite1e-10.
- Gaussiana256/512: diferencia compleja1,490e-10, límite1e-8.
- Diferencia contra solución paraxial:3,0161e-6, límite2e-4.
  Compara espectro angular con una aproximación paraxial, no dos soluciones
  del dispositivo y no un error de discretización FEM.
- Potencia relativa conservada hasta2,22e-16; ida/vuelta hasta3,773e-11,
  ambos dentro del límite1e-10 para estas entradas. No implica reversibilidad
  de componentes evanescentes o eliminados por un filtro de frecuencias.
- Dos formas inválidas rechazadas. field.py convierte NaN a cero; el adaptador
  debe rechazar datos no finitos antes de llamarlo para conservar su trazabilidad.

Intercambio JMesh preparado:74785 vértices,148832 caras subdivididas en dos
regiones (122080 y26752), coordenadas enmm, índices base1. Reconstrucción de
coordenadas con diferencia máxima1,355e-20m. Los bordes curvos se representan
por segmentos: sección planar de visualización, no volumen3D ni sustitución
de la geometría de producción. Importación real en BlenderPhotonics pendiente.
Su cargador regional resta1 a los índices; unidades y desplazamiento de la
escena deben verificarse durante la importación real.

## Posibilidades posteriores, pendientes

Optics Simulator incluye fdtd_bridge.py que llama a Meep o devuelve
backend="fallback-closedform" si falta el motor. La presencia del puente no
prueba una ejecución Maxwell: no se ejecutó aquí ni se validó para T96.
Podría servir para componentes ópticos externos en el punto correspondiente.
Las afirmaciones de los autores sobre sus regresiones no se contabilizan
como pruebas ejecutadas en esta sesión.

Faltan para tarea1: regla de cuadratura común validada en las mallas,
control longitudinal completo, predicción espacial prospectiva, malla fina
posterior a esa predicción y control de dominio. Banco físico, fabricación,
metrología y validación externa permanecen pendientes en el orden del usuario.

JEV: fallback local identificado por el bloqueo heredado. Colab sólo tiene
una prueba genérica de recursos; paquete científico preparado sin transferir.
