# Contrato de investigación v0.1 — 2026-09-30

Objetivo: red óptica volumétrica fabricable en vidrio de sílice. No existe
todavía un cubo fabricado, una red completa ni una ventaja medida.
Backend Codex: **BPM escalar paraxial CPU**, no Blender/GPU/RT.
Backend Claude: modos acoplados por tramos y referencia DFT4.

## GLASS-003 — núcleo intacto y camisa deprimida

Comparar medio uniforme, camisa finita de índice menor alrededor del núcleo
intacto y núcleo de índice elevado. Secciones rectas independientes de z.
Es propagación de ondas, NO una red neuronal ni una receta de fabricación.

Con lambda de vacío, k0=2*pi/lambda, beta0=k0*n0:
`dA/dz = i/(2*beta0) laplaciano_xy(A) + i*k0*delta_n*A`.
Strang: media fase local, difracción Fourier, media fase local.
Se omiten O(delta_n²), polarización, reflexión, dispersión, curvaturas,
rugosidad, tensión y propiedades de trazos discretos. La camisa continua
ideal no demuestra escritura láser ni equivale a una camisa discreta.

Parámetros **supuestos**: lambda=1550 nm, n0=1.444, radio núcleo=6 um,
cintura de amplitud=6 um, camisa=3/6/9 um, delta_n=-0.001,
propagación=0.5/2 mm. Nominal dz=10 um, dominio=96 um, dx=0.75 um.
Refinar dz=5 um; dominio=144 um; dx=0.5 um en gates separados.
FFT periódica con amortiguador exterior suave: la potencia removida por
frontera es pérdida **numérica**, NO absorción del material medida.
El índice retorna a n0 fuera del anillo; no presumir confinamiento infinito.

Gates prospectivos: controles analíticos gaussiano/fase uniforme error<1e-5;
balance numérico<1e-10; cambio absoluto de potencia fraccional en núcleo
al reducir dz, ampliar dominio o refinar dx<0.02 por separado.
Todos los resultados se publican, incluidos fallos; no ajustar umbral
después para aprobar. Mejora de confinamiento es exploratoria, no pérdidas
por cm certificadas, ni validación Maxwell vectorial.
CPU: <=256² puntos/1000 pasos por caso, <=40 s/script, un hilo,
sin instalar dependencias. No GPU/Blender sin autorización vigente/reserva.

## GLASS-004 — auditoría del ensayo de Claude

Leer/importar módulos CMT/oráculo, nunca ejecutar montecarlo.py escritor.
Hashes de archivos antes/después. Comparar scipy CMT con cos/sin de
acopladores independientes, intensidades DFT4 y campos por separado.
Orden de puertos explícito. Semilla 7/400 piezas, sigma_fase=0.05/0.10,
sigma_kL=0.03/0.05. Registrar media/p95/fracción que supera 10%, así como
error absoluto en puertos objetivo<=0.05 omitidos por la métrica peer.
Una media<10% no garantiza rendimiento del 95% de piezas. No entrenar
ni ajustar fases sobre test. Ruido independiente de esta auditoría no
representa aún tolerancias correlacionadas de una máquina real.

## Fuentes y decisiones

- [Project Silica](https://www.microsoft.com/en-us/research/project/project-silica/):
  página oficial leída, almacenamiento y microscopía, no procesador.
- [Multiscan sílice PRA22,064079](https://journals.aps.org/prapplied/abstract/10.1103/PhysRevApplied.22.064079):
  abstract leído, 0.07 dB/cm de otra receta NO adoptado en nuestra camisa.
- [Camisa deprimida SK1310](https://www.sciencedirect.com/science/article/pii/S0925346725000102):
  extracto indexado del artículo; acceso completo403. Guiado a1550nm según
  abstract; delta_n/radio/pérdidas completos pendientes de fuente.
- [BPM Cambridge](https://www.cambridge.org/core/books/abs/classical-optics-and-its-applications/beam-propagation-method/E934C741F450CC38BE44C6F3E03363D9):
  resumen del autor leído: difracción y máscaras de fase por sección.

JEV: bloqueo de seguridad heredado, no reintentado; fallback local Codex,
sin aval remoto. Claude solicitado como revisor independiente.

Siguiente gate: segundo solver, perfiles medidos/trazos discretos,
acoplador dos guías vs CMT, curvas/registro caras, tolerancias/calibración.
Después red 3D pequeña y tarea congelada; etiquetar cualquier backend
matricial, separar detección/electrónica/no linealidad del cubo pasivo.
