"""Phase-error budget of a rectangular 4x4 MZI mesh realising a DFT4 (CONTRATO-FASE.md).

Mesh: 6 MZIs in 4 columns (pairs (0,1),(2,3) / (1,2) / (0,1),(2,3) / (1,2)), each MZI = BS diag(e^{i th},1) BS diag(e^{i ph},1),
plus 4 output phases: 16 real parameters, a generic 4x4 unitary. Phases are fitted to a DFT4 target,
then perturbed (independent, correlated with length ell, and linear drift s).
Metrics: transfer error eps = ||U_err - U_t||_F / ||U_t||_F, and intensity error e = max_ij | |U_err,ij|^2 - |U_t,ij|^2 | / |U_t,ij|^2.
"""
import json, pathlib, sys
import numpy as np
from scipy.optimize import least_squares
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
BS = np.array([[1, 1j], [1j, 1]]) / np.sqrt(2)
COLS = [(0, 1), (2, 3), (1, 2), (0, 1), (2, 3), (1, 2)]  # 6 MZIs (rectangular 4-column pattern, pairs by column)
COLS = [(0, 1), (2, 3), (1, 2), (0, 1), (2, 3), (1, 2)]
def mzi_mat(i, j, th, ph):
    D1 = np.eye(4, dtype=complex); D1[i, i] = np.exp(1j * th)
    D2 = np.eye(4, dtype=complex); D2[i, i] = np.exp(1j * ph)
    B = np.eye(4, dtype=complex); B[np.ix_([i, j], [i, j])] = BS
    return B @ D1 @ B @ D2
def U_of(p):
    U = np.eye(4, dtype=complex)
    for k, (i, j) in enumerate(COLS):
        U = mzi_mat(i, j, p[2*k], p[2*k+1]) @ U
    return np.diag(np.exp(1j * p[12:16])) @ U
N = 4
UT = np.array([[np.exp(-2j*np.pi*j*k/N) for k in range(N)] for j in range(N)]) / 2.0
def residuals(p):
    d = U_of(p) - UT
    return np.concatenate([d.real.ravel(), d.imag.ravel()])
best = None
for seed in range(60):
    p0 = 2*np.pi*np.random.default_rng(seed).random(16)
    r = least_squares(residuals, p0, method="lm", xtol=1e-14, ftol=1e-14, gtol=1e-14)
    if best is None or r.cost < best.cost:
        best = r
p0 = best.x
fit_err = float(np.linalg.norm(U_of(p0) - UT) / np.linalg.norm(UT))
IT = np.abs(UT)**2
def metrics(p):
    U = U_of(p)
    eps = np.linalg.norm(U - UT) / np.linalg.norm(UT)
    e = float(np.max(np.abs(np.abs(U)**2 - IT) / IT))
    return eps, e
def run(sig, ell, s, n, seed=20261030):
    rng = np.random.default_rng(seed)
    idx = np.arange(16)
    C = np.eye(16) if ell == 0 else np.exp(-np.abs(np.subtract.outer(idx, idx)) / ell)
    L = np.linalg.cholesky(C + 1e-12*np.eye(16))
    dp = sig * (rng.standard_normal((n, 16)) @ L.T)
    if s > 0:
        dp = dp + s * rng.standard_normal((n, 16))
    eps = np.empty(n); e = np.empty(n)
    for k in range(n):
        eps[k], e[k] = metrics(p0 + dp[k])
    return {"sigma": sig, "ell": ell, "s": s, "n": n, "eps_mean": float(eps.mean()), "eps_p95": float(np.percentile(eps, 95)),
            "int_mean": float(e.mean()), "int_p95": float(np.percentile(e, 95))}
rows = [run(sig, ell, s, 3000) for sig in (0.02, 0.05, 0.10) for ell in (0, 1, 3) for s in (0.0, 0.01)]
get = lambda sig, ell, s: next(r for r in rows if r["sigma"] == sig and r["ell"] == ell and r["s"] == s)
rat_b = get(0.10, 3, 0.0)["eps_p95"] / get(0.10, 0, 0.0)["eps_p95"]
rat_c = get(0.02, 0, 0.01)["eps_mean"] / get(0.02, 0, 0.0)["eps_mean"]
# convergence of the Monte Carlo itself (H10a, replaces the GLASS-004 comparison, which uses a different model)
r_small = run(0.10, 0, 0.0, 3000, seed=1); r_big = run(0.10, 0, 0.0, 6000, seed=2)
rel_mc = abs(r_big["eps_mean"] - r_small["eps_mean"]) / r_big["eps_mean"]
out = {"model": "rectangular 4x4 MZI mesh, 16 phases, DFT4 target", "fit_rel_transfer_err": fit_err,
       "rows": rows,
       "H10a_mc_convergence": {"rel_diff_mean_3k_vs_6k": rel_mc, "passed": rel_mc < 0.05},
       "H10b_correlation": {"ratio_eps_p95_ell3_over_ell0": rat_b, "passed": 0.8 <= rat_b <= 1.25},
       "H10c_drift": {"ratio_eps_mean_drift_over_static_sig002": rat_c, "passed": rat_c < 1.5}}
(HERE / "fase_resultados.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print("fit rel transfer error: %.2e" % fit_err)
for r in rows: print("sig=%.2f ell=%d s=%.2f eps_mean=%.4f eps_p95=%.4f int_mean=%.4f int_p95=%.4f" % (r["sigma"], r["ell"], r["s"], r["eps_mean"], r["eps_p95"], r["int_mean"], r["int_p95"]))
print("H10a", out["H10a_mc_convergence"]); print("H10b", out["H10b_correlation"]); print("H10c", out["H10c_drift"])
