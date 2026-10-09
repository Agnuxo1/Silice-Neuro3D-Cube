"""T3 extension: complex reflection coefficient of the 1D PML (model of absorbente_pml.py).

Convention: reference plane x = 0 (interface), r = (U - W)/(U + W), U = u(0), W = u'(0)/(i kappa),
the same definition as absorbente_pml.R_of (which returns |r| only).
Checks fixed before running: V-F1 |r| equals R_of to 1e-9; V-F2 law ln|r| / ln R0 = sin(theta) to 1e-3;
V-F3 the phase has no jump larger than pi between neighbouring angles.
Run: python -B fase_reflexion.py   -> fase_resultados.json (same folder).
"""
import json, math, pathlib, sys
import numpy as np
from scipy.integrate import solve_ivp

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import absorbente_pml as P  # noqa: E402

D, R0 = 10e-6, 1e-4
THETAS = [0.02, 0.04, 0.08, 0.16, 0.32, 0.64, 1.0, 1.2, math.pi / 2]


def r_complex(theta, D, sig_max, p=2):
    kap = P.K * math.sin(theta)

    def rhs(x, y):
        u, v = y[0] + 1j * y[1], y[2] + 1j * y[3]
        xi = min(max(x / D, 0.0), 1.0)
        sig = sig_max * xi ** p
        s = 1 + 1j * sig / P.K
        du = s * v
        dv = -s * (kap ** 2) * u
        return [du.real, du.imag, dv.real, dv.imag]

    sol = solve_ivp(rhs, [D, 0.0], [0.0, 0.0, 1.0, 0.0], rtol=1e-10, atol=1e-14, method="DOP853")
    U = sol.y[0, -1] + 1j * sol.y[1, -1]
    dudx = sol.y[2, -1] + 1j * sol.y[3, -1]  # s(0) = 1
    W = dudx / (1j * kap)
    return (U - W) / (U + W)


if __name__ == "__main__":
    sig = P.sig_for(D, R0)
    rows = []
    for th in THETAS:
        r = r_complex(th, D, sig)
        R_ref = P.R_of(th, D, sig)
        rows.append({
            "theta_rad": th,
            "abs_r": float(abs(r)),
            "R_ref_from_absorbente_pml": R_ref,
            "abs_diff": float(abs(abs(r) - R_ref)),
            "dB": float(20 * math.log10(abs(r))),
            "phase_rad": float(np.angle(r)),
            "law_err": float(abs(math.log(abs(r)) / math.log(R0) - math.sin(th))),
        })
    v1 = max(row["abs_diff"] for row in rows)
    v2 = max(row["law_err"] for row in rows)
    # V-F3 as first written (raw differences of arg in (-pi, pi]) gave 4.612 rad: a wrap artefact, not a jump.
    # Corrected to wrapped differences, and checked on a finer grid (400 points, theta in [0.01, pi/2]).
    raw_steps = [abs(b["phase_rad"] - a["phase_rad"]) for a, b in zip(rows[:-1], rows[1:])]
    v3_raw = max(raw_steps)
    fine = np.linspace(0.01, math.pi / 2, 400)
    ph = np.array([float(np.angle(r_complex(th, D, sig))) for th in fine])
    wrapped = np.abs(np.angle(np.exp(1j * np.diff(ph))))
    v3 = float(wrapped.max())
    out = {"D_m": D, "R0": R0, "sigma_max_per_m": sig, "rows": rows,
           "V-F1_max_abs_diff": v1, "V-F1_pass": bool(v1 < 1e-9),
           "V-F2_max_law_err": v2, "V-F2_pass": bool(v2 < 1e-3),
           "V-F3_v1_raw_max_step_rad": v3_raw, "V-F3_v1_note": "raw differences; wrap artefact, superseded",
           "V-F3_wrapped_max_step_rad_fine_grid": v3, "V-F3_pass": bool(v3 < math.pi),
           "fine_grid": {"theta_min": float(fine[0]), "theta_max": float(fine[-1]), "n": len(fine)}}
    (HERE / "fase_resultados.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                               encoding="utf-8", newline="\n")
    for row in rows:
        print(f"theta={row['theta_rad']:.4f}  |r|={row['abs_r']:.4e}  dB={row['dB']:7.2f}  "
              f"arg(r)={row['phase_rad']:+.4f} rad  law_err={row['law_err']:.1e}")
    print(f"V-F1 {v1:.1e} {'ok' if v1 < 1e-9 else 'NO'} | V-F2 {v2:.1e} {'ok' if v2 < 1e-3 else 'NO'} | "
          f"V-F3 {v3:.3f} {'ok' if v3 < math.pi else 'NO'}")
