"""radial2: solver de disparo para el problema escalar radial de modos LP_l (Tarea C).

Metodo: integracion RK4 de psi'' + psi'/r - l^2 psi/r^2 + Phi(r) psi = 0 desde r0 (serie de Frobenius)
hasta la frontera exterior R, con emparejamiento a una funcion de Bessel exacta del revestimiento:
  - modo ligado (Phi_out < 0 real): K_l(q r);
  - modo cuasi-ligado (Phi_out complejo): H^(1)_l(k r), Re k >= 0 (salida radiante).
Modelos:
  'P' paraxial radial: Phi = 2 b0 (k0 dn - g), g = k0 (n_eff - n0)   (mismo modelo que GLASS-006a)
  'E' escalar exacto (solo verificacion frente a ecuaciones cerradas): Phi = k0^2 (n^2 - n_eff^2)
No usa diferencias finitas ni escalado complejo. Solo numpy y scipy.
"""
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
import numpy as np
from scipy import special as sp

LAM = 1550e-9
N0 = 1.444
K0 = 2.0 * np.pi / LAM
B0 = K0 * N0
UM = 1e-6
R0_DEFAULT = 0.02 * UM
DB_PER_NP = 2.0 * 10.0 / np.log(10.0) / 100.0  # dB/cm por (1/m) de Im g: 2 Im g * 4,343e-2


_trap = getattr(np, 'trapezoid', None) or np.trapz


def phi_layer(model, dn, x):
    """Kappa^2 de una capa con perturbacion dn. x = g (modelo P) o n_eff (modelo E)."""
    if model == 'P':
        return 2.0 * B0 * (K0 * dn - x)
    return K0 ** 2 * ((N0 + dn) ** 2 - x ** 2)


def frob_start(phi, l, r0):
    """psi = r^l sum_k a_k r^(2k), a_0 = 1, a_k = -phi a_(k-1) / (4 k (k+l)), k <= 3."""
    a = [np.ones_like(phi)]
    for k in range(1, 4):
        a.append(-phi * a[-1] / (4.0 * k * (k + l)))
    psi = np.zeros_like(phi)
    dpsi = np.zeros_like(phi)
    for k, ak in enumerate(a):
        m = l + 2 * k
        psi = psi + ak * r0 ** m
        if m != 0:
            dpsi = dpsi + ak * m * r0 ** (m - 1)
    return psi, dpsi


def integrate(x, layers, l, model, h, r0=R0_DEFAULT, store=False):
    """RK4 de (psi, psi') desde r0 hasta el ultimo borde. layers: lista (r_a, r_b, dn) contigua.
    x puede ser un array; devuelve psi(R), psi'(R) (y perfil si store, solo para un x)."""
    x = np.atleast_1d(np.asarray(x)).astype(complex)
    phi0 = phi_layer(model, layers[0][2], x)
    psi, dpsi = frob_start(phi0, l, r0)
    r = r0
    rec_r = [r0]
    rec_psi = [psi[0]] if store else None
    ll = float(l * l)
    for (ra, rb, dn) in layers:
        phi = phi_layer(model, dn, x)

        def f(rr, y0, y1):
            return y1, -y1 / rr + (ll / (rr * rr)) * y0 - phi * y0

        while r < rb * (1.0 - 1e-15):
            hh = min(h, r / 40.0, rb - r)
            a0, a1 = f(r, psi, dpsi)
            b0, b1 = f(r + hh / 2, psi + hh / 2 * a0, dpsi + hh / 2 * a1)
            c0, c1 = f(r + hh / 2, psi + hh / 2 * b0, dpsi + hh / 2 * b1)
            d0, d1 = f(r + hh, psi + hh * c0, dpsi + hh * c1)
            psi = psi + hh / 6.0 * (a0 + 2 * b0 + 2 * c0 + d0)
            dpsi = dpsi + hh / 6.0 * (a1 + 2 * b1 + 2 * c1 + d1)
            r = r + hh
            if store:
                rec_r.append(r)
                rec_psi.append(psi[0])
    R = layers[-1][1]
    if store:
        return psi, dpsi, np.array(rec_r), np.array(rec_psi)
    return psi, dpsi, R


def outer(x, R, l, model, real_bound=False):
    """Funcion exterior f(R) y f'(R) para el revestimiento (dn = 0)."""
    x = np.atleast_1d(np.asarray(x)).astype(complex)
    phi = phi_layer(model, 0.0, x)
    if real_bound:
        q = np.sqrt(-phi.real)
        f = sp.kv(l, q * R)
        fp = q * sp.kvp(l, q * R)
        return f.astype(complex), fp.astype(complex)
    k = np.sqrt(phi)
    k = np.where(k.real < 0, -k, k)
    f = sp.hankel1(l, k * R)
    fp = k * sp.h1vp(l, k * R)
    return f, fp


def mismatch(x, layers, l, model, h, r0=R0_DEFAULT, real_bound=False):
    """Devuelve M = p f - psi f' (sin normalizar), F = p/psi - f'/f, y psi, p, f, f' en R."""
    psi, dpsi, R = integrate(x, layers, l, model, h, r0=r0)
    f, fp = outer(x, R, l, model, real_bound=real_bound)
    M = dpsi * f - psi * fp
    with np.errstate(all='ignore'):
        F = dpsi / psi - fp / f
    return M, F, psi, dpsi, f, fp


def bisect_real(fun, lo, hi, n=80):
    """Biseccion sobre una funcion real escalar fun(x) con signo cambiado en [lo, hi]."""
    flo = fun(lo)
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        fm = fun(mid)
        if flo * fm <= 0:
            hi = mid
        else:
            lo = mid
            flo = fm
    return 0.5 * (lo + hi)


def real_roots(xs, layers, l, model, h, r0=R0_DEFAULT):
    """Raices reales de M(x) (modelo ligado, K_l) por cambio de signo en malla + biseccion."""
    M = mismatch(xs, layers, l, model, h, r0=r0, real_bound=True)[0]
    s = np.sign(M.real)
    roots = []

    def fun(xx):
        return float(mismatch(np.array([xx]), layers, l, model, h, r0=r0, real_bound=True)[0][0].real)

    for i in range(len(xs) - 1):
        if s[i] != 0 and s[i + 1] != 0 and s[i] != s[i + 1]:
            roots.append(float(bisect_real(fun, float(xs[i]), float(xs[i + 1]))))
    return roots


def core_fraction(g, layers, l, a, h, r0=R0_DEFAULT):
    """Fraccion de potencia |psi|^2 r dr en r<a dentro de r<R (region fisica del modelo)."""
    psi, dpsi, rr, pp = integrate(np.array([g]), layers, l, 'P', h, r0=r0, store=True)
    w = np.abs(pp) ** 2 * rr
    tot = _trap(w, rr)
    core = _trap(w[rr <= a], rr[rr <= a])
    return float(core / tot)


def Fc(gs, layers, l, h, r0=R0_DEFAULT):
    _, F, _, _, _, _ = mismatch(gs, layers, l, 'P', h, r0=r0, real_bound=False)
    return F


def quasibound_roots(layers, a, l, h, dn, r0=R0_DEFAULT, nre=150, nim=141,
                     im_lo=-100.0, im_hi=600.0, max_cand=40):
    """Raices complejas de F(g) (paraxial, salida radiante) por escaneo + secante compleja vectorizada."""
    re_lo = K0 * dn
    re_hi = -1.0
    re = np.linspace(re_lo, re_hi, nre)
    im = np.linspace(im_lo, im_hi, nim)
    G = (re[:, None] + 1j * im[None, :]).ravel()
    with np.errstate(all='ignore'):
        F = Fc(G, layers, l, h, r0=r0)
    A = np.nan_to_num(np.abs(F), nan=np.inf, posinf=np.inf).reshape(nre, nim)
    P = np.pad(A, 1, constant_values=np.inf)
    is_min = np.ones_like(A, dtype=bool)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == 0 and dj == 0:
                continue
            is_min &= A <= P[1 + di:1 + di + nre, 1 + dj:1 + dj + nim]
    idx = np.argwhere(is_min & np.isfinite(A))
    if len(idx) == 0:
        return [], {"n_grid_minima": 0}
    vals = A[idx[:, 0], idx[:, 1]]
    order = np.argsort(vals)[:max_cand]
    cand = np.array([re[idx[o, 0]] + 1j * im[idx[o, 1]] for o in order])
    g0 = cand.copy()
    g1 = cand + 1.0
    with np.errstate(all='ignore'):
        F0 = Fc(g0, layers, l, h, r0=r0)
        F1 = Fc(g1, layers, l, h, r0=r0)
        conv = np.zeros(len(cand), dtype=bool)
        for it in range(80):
            den = F1 - F0
            den = np.where(den == 0, 1e-30, den)
            g2 = g1 - F1 * (g1 - g0) / den
            g2 = np.where(np.isfinite(g2), g2, g1)
            conv = np.abs(g2 - g1) < 1e-11 * np.abs(g2) + 1e-9
            g0, F0 = g1, F1
            g1 = g2
            F1 = Fc(g1, layers, l, h, r0=r0)
            if np.all(conv):
                break
    # residuo relativo y deduplicacion
    res = []
    n_rejected = 0
    for gg, cv in zip(g1, conv):
        in_window = (np.isfinite(gg) and cv and (3.0 * K0 * dn < gg.real < 1.0) and (-500.0 < gg.imag < 2000.0))
        if not in_window:
            n_rejected += 1
            continue
        res.append(gg)
    uniq = []
    for gg in sorted(res, key=lambda z: -z.real):
        if all(abs(gg - u) > 1.0 for u in uniq):
            uniq.append(gg)
    out = []
    for gg in uniq:
        _, F, psi, dpsi, f, fp = mismatch(np.array([gg]), layers, l, 'P', h, r0=r0, real_bound=False)
        with np.errstate(all='ignore'):
            rF = abs(F[0]) / (abs(dpsi[0] / psi[0]) + abs(fp[0] / f[0]))
        out.append(dict(g=complex(gg), rF=float(rF)))
    info = {"n_grid_minima": int(len(idx)), "n_candidates": int(len(cand)),
            "n_converged": int(np.sum(conv)), "n_rejected_outside_window_or_unconverged": int(n_rejected)}
    return out, info


def closed_LP(neff, a, n1, n2, lp):
    """Ecuaciones cerradas escalares (LP0m: l=0; LP1m: l=1) con U, W del enunciado."""
    U = a * K0 * np.sqrt(n1 ** 2 - neff ** 2)
    W = a * K0 * np.sqrt(neff ** 2 - n2 ** 2)
    if lp == 0:
        return U * sp.j1(U) * sp.k0(W) - W * sp.k1(W) * sp.j0(U)
    return U * sp.j0(U) * sp.k1(W) + W * sp.k0(W) * sp.j1(U)


def closed_roots(a, n1, n2, lp, n_scan=4000):
    from scipy.optimize import brentq
    xs = np.linspace(n2 + 1e-12, n1 - 1e-12, n_scan)
    vals = closed_LP(xs, a, n1, n2, lp)
    roots = []
    for i in range(len(xs) - 1):
        if np.isfinite(vals[i]) and np.isfinite(vals[i + 1]) and vals[i] * vals[i + 1] < 0:
            roots.append(brentq(lambda z: closed_LP(z, a, n1, n2, lp), xs[i], xs[i + 1], xtol=1e-15, rtol=1e-15))
    return roots


def loss_dB_cm(g):
    return float(2.0 * np.imag(g) * 4.343e-2)
