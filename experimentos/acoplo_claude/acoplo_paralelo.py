"""T8 (partial): parallel-guide coupling, weakly guiding scalar model (CONTRATO-ACOPLO.md).

Analog step fiber: lambda = 1.55 um, a = 6 um, n1 = 1.444, n2 = 1.439, V = 2.9202.
kappa(d) = (k0^2 / 2 beta) (n1^2 - n2^2) I(d),  I(d) = int_core2 psi1 psi2 dA,  psi normalised.
Identical guides, phase-matched: P2(L) = sin^2(kappa L).
Run: python -B acoplo_paralelo.py   -> acoplo_resultados.json (same folder).
"""
import json, pathlib, sys
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import j0, j1, k0 as K0, k1 as K1

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
LAM, A, N1, N2 = 1.55, 6.0, 1.444, 1.439
KW = 2 * np.pi / LAM
V = KW * A * np.sqrt(N1**2 - N2**2)
D_LIST = [12, 14, 16, 18, 20, 25, 30, 35, 40, 50, 60]
LENGTHS_MM = [1, 5, 10]


def solve_U():
    def f(U):
        W = np.sqrt(V**2 - U**2)
        return U * j1(U) * K0(W) - W * K1(W) * j0(U)
    return brentq(f, 1e-6, V - 1e-9)


U = solve_U()
W = np.sqrt(V**2 - U**2)
BETA = np.sqrt(KW**2 * N1**2 - (U / A) ** 2)
# closed form from int_core J0^2 = (a^2/2)(J0^2+J1^2) and int_clad K0^2 = (a^2/2)(K1^2-K0^2) (see CONTRATO-ACOPLO.md, E-1)
N2_CLOSED = np.pi * A**2 * (j1(U)**2 / j0(U)**2 + K1(W)**2 / K0(W)**2)


def psi_raw(r):
    r = np.asarray(r, dtype=float)
    core = j0(U * r / A) / j0(U)
    clad = K0(W * r / A) / K0(W)
    return np.where(r <= A, core, clad)


def psi_n(r):
    return psi_raw(r) / np.sqrt(N2_CLOSED)


def norm_numeric():
    core, _ = quad(lambda r: 2 * np.pi * r * psi_raw(r) ** 2, 0, A)
    clad, _ = quad(lambda r: 2 * np.pi * r * psi_raw(r) ** 2, A, np.inf)
    return core + clad


def overlap(d, nr=160, nphi=256):
    x, w = np.polynomial.legendre.leggauss(nr)
    rho, wr = 0.5 * A * (x + 1), 0.5 * A * w
    phi = 2 * np.pi * np.arange(nphi) / nphi
    R, P = np.meshgrid(rho, phi, indexing="ij")
    X, Y = d + R * np.cos(P), R * np.sin(P)
    integrand = psi_n(np.hypot(X, Y)) * psi_n(R) * R
    return float(np.sum(integrand * wr[:, None]) * (2 * np.pi / nphi))


def kappa(d, **kw):
    return (KW**2 / (2 * BETA)) * (N1**2 - N2**2) * overlap(d, **kw)


if __name__ == "__main__":
    out = {"params": {"lambda_um": LAM, "a_um": A, "n1": N1, "n2": N2, "V": V, "U": U, "W": W,
                      "beta_per_um": BETA, "N2_closed": N2_CLOSED}}
    # V1: normalisation, closed form vs numerical quadrature
    n_quad = norm_numeric()
    v1 = abs(n_quad - N2_CLOSED) / N2_CLOSED
    # V2: quadrature convergence at d = 20 um
    i_a = overlap(20.0, nr=160, nphi=256)
    i_b = overlap(20.0, nr=320, nphi=512)
    v2 = abs(i_a - i_b) / abs(i_b)
    # V4: weak-guidance parameter
    v4 = (N1**2 - N2**2) / (2 * N1**2)
    # tabulate
    table = []
    for d in D_LIST:
        k = kappa(float(d))
        Lc_mm = np.pi / (2 * k) / 1000.0
        P2 = {f"P2_L{L}mm": float(np.sin(k * L * 1000.0) ** 2) for L in LENGTHS_MM}
        table.append({"d_um": d, "I": overlap(float(d)), "kappa_per_mm": k * 1000.0, "Lc_mm": float(Lc_mm), **P2})
    # V3: slope test on d = 30..60 um, compared with -W/a - 1/(2d)
    ds = [30.0, 40.0, 50.0, 60.0]
    ks = {d: kappa(d) for d in ds}
    slopes = []
    for d0, d1 in zip(ds[:-1], ds[1:]):
        dm = 0.5 * (d0 + d1)
        s_num = (np.log(ks[d1]) - np.log(ks[d0])) / (d1 - d0)
        s_exp = -W / A - 1.0 / (2 * dm)
        slopes.append({"d_mid_um": dm, "slope_num": float(s_num), "slope_expected": float(s_exp),
                       "rel_err_vs_WA": float(abs(s_num - s_exp) / (W / A))})
    v3 = max(s["rel_err_vs_WA"] for s in slopes)
    p2 = {r["d_um"]: r["P2_L10mm"] for r in table}
    out["V"] = {"V1_norm_rel_err": v1, "V1_pass": bool(v1 < 1e-6),
                "V2_quad_rel_diff": v2, "V2_pass": bool(v2 < 1e-6),
                "V3_max_slope_rel_err": v3, "V3_pass": bool(v3 < 0.03), "V3_slopes": slopes,
                "V4_delta_weak": v4, "V4_pass": bool(v4 < 0.01)}
    out["table"] = table
    out["H"] = {"H-T8-1_d20_L10_P2_le_0.10": {"P2": p2[20], "pass": bool(p2[20] <= 0.10)},
                "H-T8-2_d40_L10_P2_le_1e-3": {"P2": p2[40], "pass": bool(p2[40] <= 1e-3)}}
    (HERE / "acoplo_resultados.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                 encoding="utf-8", newline="\n")
    print(f"V={V:.5f} U={U:.5f} W={W:.5f} beta={BETA:.5f}/um N2={N2_CLOSED:.5f}")
    print(f"V1 {v1:.2e} {'ok' if v1 < 1e-6 else 'NO'} | V2 {v2:.2e} {'ok' if v2 < 1e-6 else 'NO'} | "
          f"V3 {v3:.3f} {'ok' if v3 < 0.03 else 'NO'} | V4 {v4:.4f} {'ok' if v4 < 0.01 else 'NO'}")
    for r in table:
        print(f"d={r['d_um']:>3} um  kappa={r['kappa_per_mm']:.4e}/mm  Lc={r['Lc_mm']:.3e} mm  "
              f"P2(1mm)={r['P2_L1mm']:.2e}  P2(5mm)={r['P2_L5mm']:.2e}  P2(10mm)={r['P2_L10mm']:.2e}")
    print("H-T8-1", out["H"]["H-T8-1_d20_L10_P2_le_0.10"], "| H-T8-2", out["H"]["H-T8-2_d40_L10_P2_le_1e-3"])
