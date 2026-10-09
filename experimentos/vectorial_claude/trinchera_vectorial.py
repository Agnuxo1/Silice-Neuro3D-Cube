"""Exact vector leaky modes of the effective trench geometry (CONTRATO-VECTORIAL-GEOMETRIA.md).

Core n0 (r<a), trench n0+dn (a<r<a+t), bulk n0 (r>a+t, outgoing). Prints n_eff,
loss (dB/cm) from Im(beta) for HE11, TE01, TM01, HE21 and writes a JSON.
"""
import json, math, pathlib, sys
import mpmath as m
sys.stdout.reconfigure(encoding='utf-8')
HERE = pathlib.Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from vector_layers import ThreeLayer  # noqa: E402

LAM, N0, A = 1.55e-6, 1.444, 6e-6
K0 = 2 * math.pi / LAM
GUESS = {"HE11": (1, 1.44219), "TE01": (0, 1.43977), "TM01": (0, 1.43976), "HE21": (2, 1.43976)}


def solve_family(dn, t_um, name, kind="full"):
    """Multistart search over real n_eff; returns the most confined valid root."""
    nu = GUESS[name][0]
    T = ThreeLayer(LAM, N0, N0 + dn, N0, A, A + t_um * 1e-6, nu)
    fun = {"full": T.det, "te": T.det_te, "tm": T.det_tm}[kind]
    roots = []
    for n_start in [1.4385 + 0.00025 * i for i in range(20)]:  # 1.4385 .. 1.44325
        try:
            beta = m.findroot(fun, m.mpc(K0 * n_start), tol=m.mpf(10) ** (-18), maxsteps=80)
        except (ValueError, ZeroDivisionError, ArithmeticError):
            continue
        neff = beta / K0
        re, im = float(m.re(neff)), float(m.im(neff))
        if not (N0 - 0.0055 < re < N0 + 1e-9) or abs(im) > 1e-3:
            continue
        if all(abs(re - r["n_eff_re"]) > 1e-9 for r in roots):
            roots.append({"n_eff_re": re, "n_eff_im": im, "beta": beta})
    if not roots:
        return None
    best = max(roots, key=lambda r: r["n_eff_re"])
    loss = 0.08686 * float(m.im(best["beta"]))  # dB/cm: 8.686 dB/m * Im(beta) / 100
    return {"nu": nu, "n_eff_re": best["n_eff_re"], "n_eff_im": best["n_eff_im"], "loss_dB_per_cm": loss,
            "n_valid_roots": len(roots)}


def solve(dn, t_um, name):
    kind = {"TE01": "te", "TM01": "tm"}.get(name, "full")
    return solve_family(dn, t_um, name, kind)


if __name__ == "__main__":
    out = {}
    for dn in (-0.005, -0.003):
        for t in (6.0, 12.0):
            key = f"dn{dn}_t{t:g}"
            out[key] = {name: solve(dn, t, name) for name in GUESS}
            print(key, {k: (round(v["n_eff_re"], 9), round(v["loss_dB_per_cm"], 5)) for k, v in out[key].items()})
    (HERE / "trinchera_vectorial.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                  encoding="utf-8", newline="\n")
