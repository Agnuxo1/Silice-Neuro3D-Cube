# CONTRATO: guia curvada por indice equivalente (Tarea I, curvas)

Escrito antes de ejecutar ningun calculo de este directorio. Hora de escritura: 2026-10-10 04:02 UTC. Hora limite de entrega: 05:50 UTC.
Repositorio: D:/PROJECTS/.cognition/audit/silice-origin-main (rama auditoria-20261009). Carpeta: experimentos/curvas_claude/.
Naturaleza: MODELO NUMERICO. No es un dispositivo ni una medida. Ninguna cifra de aqui es dato de laboratorio.

## 1. Hipotesis

- H1. Con el indice equivalente de Marcuse n_eq(x,y) = n(x,y)(1 + x/R), x hacia el exterior de la curva, el modo fundamental de solver2d se desplaza hacia el exterior (centroide <x> > 0) para R finito.
- H2. Para R grande el n_eff tiende al del recto, con diferencia de segundo orden en 1/R.
- H3. La cantidad n_eff(R) - n_eff(recto) escala como 1/R^2 (primer orden nulo por simetria del modo recto) y el centroide como 1/R (primer orden).
- H4. Existe un radio critico R_c en el que el punto de retorno exterior del modelo equivalente x_t(R) = R (n_eff/n_bg - 1) alcanza el borde del nucleo. Se estima de forma analitica y de forma numerica por fraccion de potencia en la region clasicamente permitida.
- H5 (no evaluada en este contrato): la perdida por radiacion. NO se calcula.

## 2. Modelo y metodo (fijados ahora)

- Unidades: um. lam = 1,55; k0 = 2 pi/lam. Nucleo a = 6 um, n1 = 1,444; fondo n_bg = n2 = 1,439. R en um: 5000, 10000, 20000, 50000 (5, 10, 20, 50 mm).
- Indice de la curva: n_xy = n1 si r < a, n2 si no. n_eq(X,Y) = n_xy(X,Y) (1 + X/R). Se pasa a solver2d como index_fn, con n_bg = n2. solver2d eleva n_eq al cuadrado internamente (n_eq^2 = n^2 (1+X/R)^2, sin truncar).
- Recto de referencia: index_fn = n_xy, mismo grid y mismo L.
- solver2d se importa desde experimentos/solver2d_claude/solver2d.py (no se copia codigo). Se usa s_sub = 8 (promediado subpixel).
- Dominio principal L = 40 um (dominio Dirichlet de +-20 um). Motivo: el borde esta en la region evanescente para R >= 10 mm. Para R = 5 mm el borde queda dentro de la region permitida (ver C6 y el limite L1).
- Malla principal: h = 0,25 y 0,125 um. Convergencia: h = 0,5 tambien.
- Modos: n_modes = 12 para todas las curvas y para el recto (solver2d devuelve los 12 valores mas altos; con R = 5 mm puede haber estados de caja en el borde exterior, por eso se selecciona por solapamiento y no por el valor mas alto).
- Modo fundamental: entre los 12 modos, el de mayor solapamiento S = |<psi_R, psi_recto>|^2 con el LP01 recto calculado en la misma malla (psi normalizada con sum|psi|^2 h^2 = 1).
- Medidas: n_eff del modo seleccionado; centroide <x> = sum x |psi|^2 h^2; x_t(R) = R (n_eff/n2 - 1); P_out = sum_{x > x_t} |psi|^2 h^2 (potencia clasicamente permitida en el lado exterior); P_core = sum_{r<a} |psi|^2 h^2.
- Radio critico analitico: R_c,A = a n2 / (n_eff,recto - n2) (x_t = a). Sensibilidad: R_c,A' = (a + 1/kappa) n2/(n_eff,recto - n2), con kappa = k0 sqrt(n_eff,recto^2 - n2^2).
- Radio critico numerico: barrido R en {2; 2,5; 3; 3,5; 4; 4,5; 5; 7,5; 10; 20; 50} mm con h = 0,25 y L = 40. R_c,num = R donde P_out cruza 1 %, por interpolacion log-lineal de P_out frente a R.
- Analitica recta (independiente de solver2d): LP01 de fibra de salto con U J1(U) K0(W) = W K1(W) J0(U), W = sqrt(V^2 - U^2), V = k0 a sqrt(n1^2 - n2^2) = 2,92017; n_eff = sqrt(n1^2 - U^2/(k0 a)^2) (raiz con brentq en scipy.special).

## 3. Criterios numericos (umbrales fijados AHORA, no se cambian despues de ver resultados)

- C0 (validacion del recto): |n_eff,recto(h=0,125) - n_eff,analitica| <= 1,0e-6.
- C1 (R grande -> recto, del encargo): |n_eff(R=50 mm, h=0,125) - n_eff,recto(h=0,125)| <= 1,0e-6.
- C2 (tendencia, del encargo): n_eff decrece al bajar R en h = 0,125: n_eff(50) > n_eff(20) > n_eff(10) > n_eff(5) mm.
- C3 (convergencia en h): para R = 5 mm y R = 10 mm, |D(h=0,25) - D(h=0,125)| <= 0,10 |D(h=0,125)|, con D(R,h) = n_eff(R,h) - n_eff,recto(h).
- C4 (centroide, orden 1/R): <x>(R=5 mm, h=0,125) > 0 (hacia el exterior) y 1,8 <= <x>(5)/<x>(10) <= 2,2.
- C5 (escala de n_eff, orden 1/R^2): 3,6 <= D(5 mm)/D(10 mm) <= 4,4 con h = 0,125 (D > 0 requerido).
- C6 (dominio): |n_eff(L=40, h=0,5) - n_eff(L=80, h=0,5)| <= 1,0e-7 para el recto y <= 1,0e-6 para R = 10 mm.
- C7 (radio critico): R_c,num / R_c,A en [0,67; 1,5] y ambos en [2; 5] mm.
- C8 (normalizacion y simetria): |sum|psi|^2 h^2 - 1| <= 1e-10 y max|psi(x,y) - psi(x,-y)| / max|psi| <= 1e-6 para el modo seleccionado en cada R y h = 0,125.
- C9 (identificacion del modo): S >= 0,90 en todos los casos con h = 0,125.

Si un criterio falla, se publica con sus cifras. Ningun umbral se mueve despues de ver resultados.

## 4. Lo que NO afirmo

- No calculo perdida por radiacion ni dB/cm. La cantidad n_eff no es perdida. Lee et al. (2021) no se verifica aqui; no se compara con ella.
- El modelo de caja (Dirichlet) no representa radiacion. Para R = 5 mm el lado exterior es permitido y el resultado es aproximado; las cifras de P_out lo cuantifican.
- No afirmo nada vectorial (TE/TM), ni acoplo entre nucleos, ni fabricacion, ni dispositivo fs, ni red 3D.
- No afirmo convergencia para L -> infinito mas alla de C6.
- No afirmo el signo de la literatura para el cambio de n_eff con la curvatura. Solo el del modelo tal como esta fijado en este contrato.
- No copio ni consulto codigo de src/silice/, tests/ ni scripts/. No toco coordinacion/ ni Docs/.
- No afirmo un radio critico de laboratorio.

## 5. Entregables

- CONTRATO-curvas.md (este fichero).
- curvas.py (barrido, criterios, analitica independiente) y resultados.json (pass = true/false calculado por el codigo).
- log_run.txt con la salida de la ejecucion.
- Salidas solo en D: (esta carpeta). Sin git add, commit ni push. Python con -B y OMP_NUM_THREADS=1.
