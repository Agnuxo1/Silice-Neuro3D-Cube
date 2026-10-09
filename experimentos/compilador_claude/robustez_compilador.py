"""Diagnostics for the compiler (NOT pre-registered criteria; see CONTRATO-COMPILADOR.md, E-1).

(a) Robustness of C3 over K coupler draws (sigma 0.02, common seed 20261100).
(b) Uncalibrated but code-optimised: codes optimised on the ideal mesh, applied to the non-ideal mesh.
    Separates the effect of calibration from the effect of discrete code optimisation.
(c) DAC resolution (8, 9, 10 bits) with optimised codes on the ideal mesh, for the C2 threshold.
Run: python -B robustez_compilador.py [K]   -> robustez_compilador.json
"""
import json, pathlib, sys
import numpy as np
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compilar as C  # noqa: E402

K = int(sys.argv[1]) if len(sys.argv) > 1 else 12
SEED = 20261100


def summary(rows, key):
    v = [r[key] for r in rows]
    return {"min": min(v), "median": float(np.median(v)), "max": max(v)}


def main():
    z = np.zeros(12)
    res = {}
    for name, UT in C.targets().items():
        p_ideal = C.fit(UT, z, np.zeros(16))
        dac = {}
        for b in (8, 9, 10):
            _, e_b = C.best_discrete(UT, z, [p_ideal], bits=b)
            dac[str(b)] = {"ideal_rounding": C.eps(C.mesh(C.quant(p_ideal, b), z), UT), "ideal_discrete": e_b}
        codes_ideal8, _ = C.best_discrete(UT, z, [p_ideal, C.quant(p_ideal)], bits=8)
        rng = np.random.default_rng(SEED)
        rows = []
        for d in range(K):
            dlt = rng.normal(0.0, C.SIGMA_DELTA, 12)
            e1 = C.eps(C.mesh(C.quant(p_ideal), dlt), UT)
            e_uo = C.eps(C.mesh(codes_ideal8 * C.lattice(8), dlt), UT)
            p_cal = C.fit(UT, dlt, p_ideal)
            _, e2 = C.best_discrete(UT, dlt, [p_cal, p_ideal, C.quant(p_ideal)])
            row = {"draw": d, "eps1_naive": e1, "eps_uncal_code_opt": e_uo, "eps2_cal_discrete": e2,
                   "C3": bool(e2 < 1e-2 and e2 < e1 / 3)}
            rows.append(row)
            print(name, d, f"eps1={e1:.3e} uncal_opt={e_uo:.3e} eps2={e2:.3e} C3={row['C3']}", flush=True)
        res[name] = {"dac_bits_diagnostic": dac, "draws": rows,
                     "summary": {k: summary(rows, k) for k in ("eps1_naive", "eps_uncal_code_opt", "eps2_cal_discrete")},
                     "C3_pass_fraction": float(np.mean([r["C3"] for r in rows]))}
    out = {"K": K, "seed": SEED, "sigma_delta": C.SIGMA_DELTA, "results": res}
    (HERE / "robustez_compilador.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                   encoding="utf-8", newline="\n")
    print("done", flush=True)


if __name__ == "__main__":
    main()
