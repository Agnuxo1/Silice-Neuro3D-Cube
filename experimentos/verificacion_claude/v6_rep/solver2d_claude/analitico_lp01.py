"""Referencia analitica del LP01 de fibra de salto (escalar, debil guiado).

U J1(U) K0(W) = W K1(W) J0(U), U^2 + W^2 = V^2, V = k0 a sqrt(n1^2 - n2^2).
Campo (sin normalizar): J0(U r/a) para r <= a; (J0(U)/K0(W)) K0(W r/a) para r >= a.
Fraccion de potencia en el nucleo, forma cerrada:
    Gamma = (J0^2 + J1^2) / (J1^2 + J0^2 K1^2/K0^2) evaluadas en (U) y (W).
Tambien se calcula por cuadratura numerica del campo analitico (control de coherencia).
"""
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import j0, j1, k0 as K0, k1 as K1

LAM_UM = 1.55
A_UM = 6.0
N1 = 1.444
N2 = 1.439
J0_FIRST_ZERO = 2.404825557695773


def lp01_params(lam=LAM_UM, a=A_UM, n1=N1, n2=N2):
    k = 2.0 * np.pi / lam
    V = k * a * np.sqrt(n1 ** 2 - n2 ** 2)
    return k, V


def lp01_analytic(lam=LAM_UM, a=A_UM, n1=N1, n2=N2):
    k, V = lp01_params(lam, a, n1, n2)

    def f(U):
        W = np.sqrt(V ** 2 - U ** 2)
        return U * j1(U) * K0(W) - W * K1(W) * j0(U)

    U = brentq(f, 1e-6, min(V, J0_FIRST_ZERO) - 1e-12, xtol=1e-15, rtol=4 * np.finfo(float).eps, maxiter=500)
    W = np.sqrt(V ** 2 - U ** 2)
    beta = np.sqrt(k ** 2 * n1 ** 2 - (U / a) ** 2)
    neff = beta / k
    gamma_closed = (j0(U) ** 2 + j1(U) ** 2) / (j1(U) ** 2 + j0(U) ** 2 * K1(W) ** 2 / K0(W) ** 2)

    C = j0(U) / K0(W)
    Pc = quad(lambda r: j0(U * r / a) ** 2 * r, 0.0, a, limit=400, epsabs=0, epsrel=1e-13)[0]
    Pcl = quad(lambda r: (C * K0(W * r / a)) ** 2 * r, a, np.inf, limit=400, epsabs=0, epsrel=1e-13)[0]
    gamma_quad = Pc / (Pc + Pcl)

    return {
        "lam_um": lam,
        "a_um": a,
        "n1": n1,
        "n2": n2,
        "k0_um": k,
        "V": float(V),
        "U": float(U),
        "W": float(W),
        "neff": float(neff),
        "gamma_core_closed": float(gamma_closed),
        "gamma_core_quad": float(gamma_quad),
        "C_clad_coef": float(C),
    }


def lp01_field(x, y, U, W, a=A_UM, C=None):
    """Campo analitico sin normalizar en (x, y); C = J0(U)/K0(W)."""
    r = np.hypot(x, y)
    if C is None:
        C = j0(U) / K0(W)
    inside = j0(U * r / a)
    outside = C * K0(W * r / a)
    return np.where(r <= a, inside, outside)


if __name__ == "__main__":
    import json

    res = lp01_analytic()
    print(json.dumps(res, indent=2))
