"""PML reflection vs incidence angle, 1D full-wave (CONTRATO-ABSORBENTE.md).
Equation: (1/s) d/dx[(1/s) du/dx] + kappa^2 u = 0, s = 1 + i sigma/k, i.e. u' = s v, v' = -s kappa^2 u."""
import json, math, pathlib, sys
import numpy as np
from scipy.integrate import solve_ivp
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
LAM, N0 = 1.55e-6, 1.444
K = 2 * math.pi * N0 / LAM
L = 0.0  # interface placed at x = 0 (the physical region is x < 0)
def R_of(theta, D, sig_max, p=2):
    kap = K * math.sin(theta)
    def rhs(x, y):
        u, v = y[0] + 1j * y[1], y[2] + 1j * y[3]
        xi = min(max(x / D, 0.0), 1.0)  # x in [0, D] inside the PML
        sig = sig_max * xi ** p
        s = 1 + 1j * sig / K  # local decay of exp(i kappa x) is kappa*sigma/k: sign + damps the wave
        du = s * v
        dv = -s * (kap ** 2) * u  # (1/s) d/dx[(1/s) du/dx] + kappa^2 u = 0  with  v = (1/s) du/dx
        return [du.real, du.imag, dv.real, dv.imag]
    # start at the outer wall x = D: u = 0, v = 1
    sol = solve_ivp(rhs, [D, 0.0], [0.0, 0.0, 1.0, 0.0], rtol=1e-10, atol=1e-14, method="DOP853")
    u0 = sol.y[0, -1] + 1j * sol.y[1, -1]
    v0 = sol.y[2, -1] + 1j * sol.y[3, -1]
    dudx = v0  # s(0) = 1
    if kap == 0:
        return float("nan")
    U, W = u0, dudx / (1j * kap)
    return float(abs(U - W) / abs(U + W))
def sig_for(D, R0=1e-4, p=2):
    """sigma_max [1/m] so that the round-trip amplitude attenuation is R0: int sigma dx = ln(1/R0)/2."""
    return (p + 1) * math.log(1 / R0) / (2 * D)

if __name__ == "__main__":
    thetas = [0.005, 0.01, 0.02, 0.04, 0.08, 0.16]
    out = {"V0_no_absorber": [R_of(t, 10e-6, 0.0) for t in thetas], "rows": {}}
    for D in (5e-6, 10e-6, 20e-6):
        sm = sig_for(D)
        out["rows"][f"D{D*1e6:g}"] = {f"{t:g}": R_of(t, D, sm) for t in thetas}
    out["sigma_max_per_m"] = {f"D{D*1e6:g}": sig_for(D) for D in (5e-6, 10e-6, 20e-6)}
    out["V0_pass"] = all(abs(r - 1.0) < 1e-6 for r in out["V0_no_absorber"])
    out["P_T1"] = out["rows"]["D10"]["0.04"] < 1e-3
    out["P_T2"] = out["rows"]["D10"]["0.01"] > out["rows"]["D10"]["0.04"]
    out["P_T3"] = all(out["rows"]["D20"][f"{t:g}"] < out["rows"]["D10"][f"{t:g}"] for t in thetas)
    (HERE / "absorbente_resultados.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("V0 (no absorber R=1):", out["V0_pass"], [round(r, 8) for r in out["V0_no_absorber"]])
    for k, v in out["rows"].items(): print(k, {t: f"{r:.3e}" for t, r in v.items()})
    print("P-T1", out["P_T1"], "P-T2", out["P_T2"], "P-T3", out["P_T3"])
