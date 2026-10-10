# CONTRATO - Cierre del acoplador: base modal y contraste independiente (TAREA G)

Escrito antes de ejecutar ningun calculo. Hora de escritura: 2026-10-10 04:01 UTC. Plazo: 05:50 UTC.
Repositorio: D:/PROJECTS/.cognition/audit/silice-origin-main. Carpeta: experimentos/acoplador_claude/.
Naturaleza: MODELO NUMERICO escalar. No es un dispositivo, no es una medida, no es un dato de laboratorio.
Ninguna cifra de aqui debe leerse como fabricacion, eficiencia o rendimiento de la red 3D.

## 0. Estado del piloto GLASS-006b (lectura, sin calculo)

- Artefactos leidos: `Docs/GLASS-006B-PILOT-RESULTS.md`, `Docs/GLASS-006B-PILOT-CONTRACT.md`, `coordinacion/tareas/GLASS-006B-PILOT-CLAUDE.md`, `resultados/codex/glass006b_pilot_v1.json` (+ `__NAME.json/npz`).
- Que se ejecuto: 9 casos originales (near/far/vacuum, dx, dz, dominio) y 3 casos de refinamiento. Propagacion BPM/cobertura escalar paraxial de Codex, sin normalizar.
- Base modal usada: Gaussianas ortogonalizadas por Gram en los puertos de lectura y de lanzamiento. **No son modos guiados ni autovectores.** Geometria: nucleos a +-d/2 con d = 14 um, a = 6 um, t = 6 um, dn = -0,005, cladding "carved" (union de circulos externos sin los nucleos).
- Fallos conservados (no se reemplazan): dx grueso->nominal 0,0065448 (> 0,005); Galerkin de dos Gaussianas, error complejo de puerto 0,16283 (> 0,05).
- Pendiente que esta tarea sí cubre: base modal guiada (G1) y contraste independiente de la fase de acoplo (G2, G3).
- Pendiente que esta tarea NO cubre: el contraste ADI del near_left/near_coherent que pide `GLASS-006B-PILOT-CLAUDE.md`. No esta en la lista G1-G4 y no se ejecuta aqui.
- Relacion con G1: el caso d = 14 comparte a, dn y d con el piloto, pero el piloto usa cladding carved y G1 usa cladding de fondo uniforme. No son la misma geometria.

## 1. Hipotesis

- H-G1 (base modal). Los supermodos par e impar de dos nucleos identicos de salto (a = 6 um, n1 = 1,444, fondo n2 = 1,439, lambda = 1,55 um, centros en +-d/2) se obtienen con solver2d por diferencias finitas con convergencia en h y en dominio. kappa_FD = k0 (n_par - n_impar)/2.
- H-G2 (prefactor, T8). kappa_FD coincide con kappa(d) de `experimentos/acoplo_claude/acoplo_paralelo.py`, que implementa kappa = (k0^2/2 beta)(n1^2 - n2^2) * integral_core2 psi1 psi2 dA, dentro del 10 % para d en {14, 16, 20} um.
- H-G3 (BPM). Un modo de un solo nucleo, propagado en la guia doble con el propagador BPM de `experimentos/bpm_claude/bpm.py`, alcanza su primer maximo de P2 en z = L_c = pi/(2 kappa_FD), dentro del 10 %.
- H-G4 (informativa). P2 a 20 um y 10 mm, calculada como sin^2(kappa_FD * 10 mm), frente a la prediccion H-T8-1 (P2 <= 0,10).

Hipotesis nula de cada una: que la discrepancia supere el umbral. Si una falla, se publica asi.

## 2. Modelo y convenciones

- Unidades: um. k0 = 2 pi / 1,55 um^-1. V = k0 a sqrt(n1^2 - n2^2) = 2,92016.
- Operador de solver2d: (d2/dx2 + d2/dy2 + k0^2 n^2) psi = beta^2 psi, n_eff = beta/k0, Dirichlet en el contorno.
- Malla: h = 0,125 um para G1/G2 (N = 641, L = 40 um); h = 0,25 um para la comprobacion de h; h = 0,2 um para G3 (N = 401, igual que la malla del BPM).
- Promediado subpixel del indice, s_sub = 8 (solver2d por defecto).
- Index de cada supermodo: n_par > n_impar esperado (el par tiene mayor beta).
- Acoplo de referencia: kappa_model(d) = `acoplo_paralelo.kappa(d)` en um^-1 (la funcion importada, no reimplementada).
- Nota de documentacion: `CONTRATO-ACOPLO.md` describe I(d) = integral_core2 2 psi1 psi2 dA, con un factor 2 que el codigo de `acoplo_paralelo.py` no tiene (el codigo calcula integral_core2 psi1 psi2 dA). Se usa el codigo como referencia, porque es lo que pide la tarea (kappa(d) importable). El valor con el factor 2 literal se reporta solo como informacion, sin criterio de paso.
- BPM (G3): ecuacion del enunciado 2 i k0 n_ref dA/dz = lap A + k0^2 (n^2 - n_ref^2) A, con n_ref = n1 = 1,444 y CAP por defecto del propagador. Malla h = 0,2 um, dz = 1 um. Indice = raiz de la media celda a celda de n^2 (la del solver), no muestreo nodal.
- Observable P2 (definicion del BPM, P2m): P2(z) = |<psi_R | A(z)>|^2 / (<psi_R|psi_R> <A0|A0>), con inner products h^2 y psi_R el modo de un nucleo en +d/2 (solver2d, un disco). A0 = modo de un nucleo en -d/2 (lanzamiento). Tambien se registra P_total(z)/P0.
- kappa_FD y L_c. L_c = pi/(2 kappa_FD), con kappa_FD de G1 (h = 0,125 um).

## 3. Criterios numericos (umbrales fijados AHORA)

G1 (base modal, solver2d):
- G1.1 paridad: max|psi_par(x,y) - psi_par(-x,y)| / max|psi_par| <= 1e-5, y max|psi_imp(x,y) + psi_imp(-x,y)| / max|psi_imp| <= 1e-5, para d en {14, 16, 20}, h = 0,125.
- G1.2 signo: n_par - n_imp > 0 para d en {14, 16, 20}, h = 0,125.
- G1.3 convergencia en h: |kappa_FD(h = 0,125) - kappa_FD(h = 0,25)| / kappa_FD(h = 0,125) <= 0,05, para d en {14, 16, 20}.
- G1.4 dominio: |kappa_FD(L = 40) - kappa_FD(L = 50)| / kappa_FD(L = 40) <= 0,05, con h = 0,25, para d = 20 (el caso mas debil).
- G1.5 nucleo unico (lanzamiento de G3): |n_eff(un nucleo, h = 0,2, L = 40) - 1,4421921654570133| <= 1e-5.

G2 (prefactor, comparacion con kappa(d)):
- G2.1: |kappa_FD(h = 0,125) / kappa_model(d) - 1| < 0,10 para d en {14, 16, 20} um.
- G2.2 (informativa, sin criterio de paso): kappa_FD / (2 kappa_model) y kappa_FD / kappa_model, para indicar cual de las dos lecturas del factor 2 se cumple.

G3 (BPM, primer maximo de P2):
- G3.1: |z_max - L_c| / L_c <= 0,10, con z_max = primer maximo local de P2(z) en z en (0, z_end], muestreado cada dz = 1 um, y L_c = pi/(2 kappa_FD(h = 0,125)). Se evalua para d en {14, 16} um, y para d = 20 um si da tiempo.
- G3.2: P2(z_max) >= 0,90.
- G3.3: 1 - P_total(z_max)/P0 <= 1e-3 (el CAP no debe absorber la luz guiada).
- G3.4 (sensibilidad dz, solo d = 14): |z_max(dz = 0,5) - z_max(dz = 1)| / z_max(dz = 1) <= 0,01. Si no da tiempo, se declara no evaluable.

G4 (lectura, sin umbral nuevo):
- Prefactor confirmado si G2.1 pasa para los tres d.
- H-T8-1 queda como: refutada en el modelo (P2 = 0,141 > 0,10), y el contraste la rescata solo si P2_FD(20 um, 10 mm) <= 0,10. Se reporta tambien P2 del BPM a 10 mm para d = 20 um (informativa).

## 4. Metodos

- solver2d: `experimentos/solver2d_claude/solver2d.py` (importado, no copiado), con solve(shapes, n_bg, lam_um, L_um, h_um, n_modes, s_sub=8). Se registra el SHA256 del archivo usado.
- Analitico de referencia: `experimentos/solver2d_claude/analitico_lp01.py` (solo para G1.5; valor de n_eff 1,4421921654570133).
- kappa_model: `experimentos/acoplo_claude/acoplo_paralelo.py` (importado).
- BPM: `experimentos/bpm_claude/bpm.py` (importado; se usa `propagate` con callback observe, porque `run` no expone P2 a cada paso). Se registra el SHA256.
- Todos los calculos en CPU, un solo hilo (OMP_NUM_THREADS = 1), python -B. Sin GPU, sin instalacion. Sin ninguna copia de codigo de src/silice/.

## 5. Lo que NO afirmo

- No afirmo nada vectorial (TE/TM, birrefringencia, delta n = -0,003 de T6).
- No afirmo nada sobre la escritura fs ni sobre la anisotropia del perfil de escritura.
- No afirmo nada sobre la geometria del piloto GLASS-006b (cladding carved). Solo su parametro d = 14 um se parece.
- No afirmo que el contraste ADI del piloto (near_left) este hecho: no esta en la lista G.
- No afirmo que la base modal o el BPM describan una red 3D ni una medida. Son modelos numericos.
- El prefactor se contrasta frente al modelo de acoplo de primer orden. No se verifica la forma completa del acoplo de la red ni las perdidas de curva o de cruce.
- No hay medida de laboratorio. Las cifras son de un modelo sin calibrar.

## 6. Entregables

- `CONTRATO-acoplador.md` (este archivo).
- `g1_g2_modal.py`: G1 y G2. Salidas: `resultados_g1_g2.json`, `log_g1_g2.txt`.
- `g3_bpm_p2.py`: G3. Salidas: `resultados_g3_bpm.json`, `log_g3_bpm.txt`.
- `resultados_g1_g2.json` y `resultados_g3_bpm.json` con pass/fail evaluados por el codigo.
- Sin git add, commit ni push. Sin escribir en otras carpetas.

## 7. Enmienda E-1 (2026-10-10 04:12 UTC, antes de cualquier cifra de G1 a G4)

- Malla del BPM y de la base modal de G3: N = 405 con h = 0,2 um (semilado 40,4 um), en lugar de N = 401 (semilado 40). Motivo: 401 es primo y la FFT de scipy en un solo hilo es lenta con ese tamano; 405 = 3^4 · 5 es rapido. El CAP de `bpm.py` (inicio en s = 28 um, final en s = 40 um) queda dentro de la ventana. Los solvers de esta malla usan L = 40,4 um.
- G1.5 se evalua con L = 40,4 um (no 40 um).
- G3: "primer maximo local" significa primer maximo local de P2 con P2 > 0,05, para descartar el arranque cerca de z = 0.
- No cambian los umbrales de G1.1 a G1.4, G2.1, G3.1 a G3.4 ni G4.
