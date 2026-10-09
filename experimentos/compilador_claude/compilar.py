"""Calibration-aware compiler prototype (CONTRATO-COMPILADOR.md, amendment E-1).

Model only: rectangular 4x4 mesh, 6 MZI, 16 phases, 8-bit DAC, coupler ratios 0.5 + delta.
Run: python -B compilar.py   -> writes compilador_resultados.json next to this file.
"""
import json, pathlib, sys
import numpy as np
from scipy.optimize import least_squares

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
COLS = [(0, 1), (2, 3), (1, 2), (0, 1), (2, 3), (1, 2)]
N = 4
BITS = 8
SIGMA_DELTA = 0.02
SEED_DELTA = 20261040


def bs(r):
    t = np.sqrt(1 - r)
    k = np.sqrt(r)
    return np.array([[t, 1j * k], [1j * k, t]])


def mzi_block(i, j, th, ph, r):
    D1 = np.eye(N, dtype=complex)
    D1[i, i] = np.exp(1j * th)
    D2 = np.eye(N, dtype=complex)
    D2[i, i] = np.exp(1j * ph)
    B1 = np.eye(N, dtype=complex)
    B1[np.ix_([i, j], [i, j])] = bs(r[0])
    B2 = np.eye(N, dtype=complex)
    B2[np.ix_([i, j], [i, j])] = bs(r[1])
    return B2 @ D1 @ B1 @ D2


def mesh(p, dlt):
    """16 phases p (12 MZI + 4 output) and 12 coupler deviations dlt (two per MZI)."""
    U = np.eye(N, dtype=complex)
    for k, (i, j) in enumerate(COLS):
        r = (0.5 + dlt[2 * k], 0.5 + dlt[2 * k + 1])
        U = mzi_block(i, j, p[2 * k], p[2 * k + 1], r) @ U
    return np.diag(np.exp(1j * p[12:16])) @ U


def lattice(bits):
    return 2 * np.pi / (2 ** bits)


def quant(p, bits=BITS):
    step = lattice(bits)
    return np.round(p / step) * step


def dft4():
    return np.array([[np.exp(-2j * np.pi * j * k / N) for k in range(N)] for j in range(N)]) / 2.0


def haar(seed):
    A = np.random.default_rng(seed).standard_normal((N, N)) + 1j * np.random.default_rng(seed + 100).standard_normal((N, N))
    Q, _ = np.linalg.qr(A)
    return Q


def eps(U, UT):
    return float(np.linalg.norm(U - UT) / np.linalg.norm(UT))


def fit(UT, dlt, p0):
    """Continuous least-squares fit of the 16 phases (multistart, 20 starts)."""
    def res(p):
        d = mesh(p, dlt) - UT
        return np.concatenate([d.real.ravel(), d.imag.ravel()])
    best = None
    for s in range(20):
        start = p0 if s == 0 else 2 * np.pi * np.random.default_rng(s).random(16)
        r = least_squares(res, start, method="lm", xtol=1e-15, ftol=1e-15, gtol=1e-15)
        if best is None or r.cost < best.cost:
            best = r
    return best.x


def discrete_search(UT, dlt, codes0, bits=BITS, max_rounds=500):
    """Local search on the DAC lattice (amendment E-1): +-1 LSB in one phase, then in two phases."""
    M = 2 ** bits
    step = lattice(bits)
    codes = np.array(codes0, dtype=int) % M

    def err(c):
        return eps(mesh(c * step, dlt), UT)

    cur = err(codes)
    for _ in range(max_rounds):
        improved = False
        for k in range(16):
            for d in (1, -1):
                c = codes.copy()
                c[k] = (c[k] + d) % M
                e = err(c)
                if e < cur:
                    codes, cur, improved = c, e, True
        if not improved:
            for k in range(16):
                for m in range(k + 1, 16):
                    for dk in (1, -1):
                        for dm in (1, -1):
                            c = codes.copy()
                            c[k] = (c[k] + dk) % M
                            c[m] = (c[m] + dm) % M
                            e = err(c)
                            if e < cur:
                                codes, cur, improved = c, e, True
        if not improved:
            break
    return codes, cur


def best_discrete(UT, dlt, starts, bits=BITS):
    """Multistart discrete search: each start is a continuous phase vector, rounded to the lattice."""
    step = lattice(bits)
    best = None
    for p in starts:
        codes, e = discrete_search(UT, dlt, np.round(p / step).astype(int), bits)
        if best is None or e < best[1]:
            best = (codes, e)
    return best


def targets():
    return {"DFT4": dft4(), "haar1": haar(1), "haar2": haar(2)}


if __name__ == "__main__":
    z = np.zeros(12)
    rng = np.random.default_rng(SEED_DELTA)
    out = {}
    for name, UT in targets().items():
        p_ideal = fit(UT, z, np.zeros(16))                                   # step 1: continuous, ideal couplers
        e1 = eps(mesh(p_ideal, z), UT)                                       # C1
        p_q8 = quant(p_ideal, BITS)                                          # step 2: direct 8-bit quantization
        e2 = eps(mesh(p_q8, z), UT)                                          # C2
        dlt = rng.normal(0.0, SIGMA_DELTA, 12)                               # step 3: assumed coupler deviations
        e3 = eps(mesh(p_q8, dlt), UT)                                        # step 4: eps1, uncalibrated
        p_cal = fit(UT, dlt, p_ideal)                                        # diagnostic: continuous calibration
        e4 = eps(mesh(p_cal, dlt), UT)
        e4q = {b: eps(mesh(quant(p_cal, b), dlt), UT) for b in (8, 10, 12)}  # diagnostic: DAC sensitivity
        codes5, e5 = best_discrete(UT, dlt, [p_cal, p_ideal, p_q8])         # step 5: eps2 on the 8-bit lattice (E-1)
        codes2, e2d = best_discrete(UT, z, [p_ideal, p_q8])                  # diagnostic: discrete search, ideal mesh
        out[name] = {
            "C1_eps_ideal_continuous": e1,
            "C2_eps_dac8_direct_ideal": e2,
            "eps1_uncalibrated_dac8_direct": e3,
            "eps2_calibrated_dac8_discrete": e5,
            "diag_eps_calibrated_continuous": e4,
            "diag_eps_calibrated_rounded_dac8": e4q[8],
            "diag_eps_calibrated_rounded_dac10": e4q[10],
            "diag_eps_calibrated_rounded_dac12": e4q[12],
            "diag_eps_ideal_discrete_dac8": e2d,
            "C1": bool(e1 < 1e-9),
            "C2": bool(e2 < 5e-3),
            "C3": bool(e5 < 1e-2 and e5 < e3 / 3),
            "delta": dlt.tolist(),
            "codes_calibrated": codes5.tolist(),
            "codes_ideal_discrete": codes2.tolist(),
        }
        print(name, " ".join(f"{k}={v:.3e}" for k, v in out[name].items()
                             if k.startswith(("C1_", "C2_", "eps", "diag_")) and isinstance(v, float)), flush=True)
    codes = np.array(out["DFT4"]["codes_calibrated"])
    dlt = np.array(out["DFT4"]["delta"])
    step = lattice(BITS)
    netlist = {
        "mesh": "rectangular 4x4, 6 MZI; theta_code = inner phase (D1, between couplers), phi_code = input-arm phase (D2)",
        "columns": [{"mzi": k, "pair": list(COLS[k]),
                     "theta_code": int(codes[2 * k]), "phi_code": int(codes[2 * k + 1]),
                     "theta_rad": float(codes[2 * k] * step), "phi_rad": float(codes[2 * k + 1] * step),
                     "coupler_ratios": [float(0.5 + dlt[2 * k]), float(0.5 + dlt[2 * k + 1])]} for k in range(6)],
        "output_codes": [int(c) for c in codes[12:16]],
        "dac_bits": BITS,
        "layout_check": "not performed (declared limit)",
        "delta_status": f"assumed N(0; {SIGMA_DELTA}), to be measured in T14",
    }
    crit = {
        "C1_all_targets": all(v["C1"] for v in out.values()),
        "C2_all_targets": all(v["C2"] for v in out.values()),
        "C3_all_targets": all(v["C3"] for v in out.values()),
        "C4": "published as obtained; no thresholds relaxed",
    }
    result = {"contract": "CONTRATO-COMPILADOR.md (amendment E-1)", "bits": BITS, "sigma_delta": SIGMA_DELTA,
              "seed_delta": SEED_DELTA, "criteria": crit, "targets": out, "netlist_DFT4": netlist}
    (HERE / "compilador_resultados.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n",
                                                     encoding="utf-8", newline="\n")
    print("criteria", crit)
