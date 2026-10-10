"""VERIFICACION V3, parte E (ablacion F3). Reimplementacion INDEPENDIENTE (no importa run_f3 ni run_f3b ni ablacion).

Solo lee del repositorio: los JSON guardados (para comparar) y los numeros de semilla del contrato.
Uso: python -B verif_ablacion.py   (OMP_NUM_THREADS=1, CPU)
Salida: verif_ablacion_resultados.json
"""
import os, sys, json, time, pathlib
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "f3_red_pequena"
T0 = time.time()

# ---- tarea congelada, reescrita desde cero (semillas de CONTRATO-F3.md / run_f3.py) ----
X_TR = np.random.default_rng(20261009).standard_normal((2000, 4))
X_TE = np.random.default_rng(20261010).standard_normal((2000, 4))
rq = np.random.default_rng(20261011)
Qs = []
for _ in range(4):
    M = rq.standard_normal((4, 4)); Qs.append((M + M.T) / 2)
Q = np.stack(Qs)
lab = lambda X: np.einsum("ni,kij,nj->nk", X, Q, X).argmax(1)
Y_TR, Y_TE = lab(X_TR), lab(X_TE)

IU = np.triu_indices(4, 1)
def U_of(p):
    H = np.zeros((4, 4), complex)
    H[np.diag_indices(4)] = p[:4]
    H[IU] = p[4:10] + 1j * p[10:16]
    H = np.triu(H) + np.triu(H, 1).conj().T      # hermitica explicita (equivale a H + H^H - diag)
    return expm(1j * H)

def act(I, vpi=1.0, tb=0.0):
    return (1.0 + np.cos(np.pi * I / vpi + tb)) / 2.0

def L_full(p, X, vpi=1.0, tb=0.0):
    U1, U2 = U_of(p[:16]), U_of(p[16:])
    I1 = np.abs(X @ U1.T) ** 2
    a2 = np.sqrt(np.clip(act(I1, vpi, tb), 0, 1))
    return np.abs(a2 @ U2.T) ** 2
def L_nl_off(p, X):
    U1, U2 = U_of(p[:16]), U_of(p[16:])
    return np.abs(np.abs(X @ U1.T) @ U2.T) ** 2
def L_det_off(p, X):
    U1, U2 = U_of(p[:16]), U_of(p[16:])
    return np.abs((X @ U1.T) @ U2.T) ** 2
def L_real(p, X):
    W1, W2 = p[:16].reshape(4, 4), p[16:].reshape(4, 4)
    a2 = np.sqrt(np.clip(act((X @ W1.T) ** 2), 0, 1))
    return (a2 @ W2.T) ** 2
def L_m1(p, X):
    return np.abs(X @ U_of(p).T) ** 2

def xent(p, fn, X, y):
    z = fn(p, X); z = z - z.max(1, keepdims=True)
    return float((np.log(np.exp(z).sum(1)) - z[np.arange(len(y)), y]).mean())

def fit(fn, n, seeds=range(1, 9), maxiter=300):
    rows = []
    for s in seeds:
        p0 = 0.5 * np.random.default_rng(s).standard_normal(n)
        r = minimize(xent, p0, args=(fn, X_TR, Y_TR), method="L-BFGS-B", options={"maxiter": maxiter})
        pr = fn(r.x, X_TE).argmax(1)
        rows.append(dict(seed=s, loss=float(r.fun), succ=bool(r.success), nit=int(r.nit),
                         tr=float((fn(r.x, X_TR).argmax(1) == Y_TR).mean()), te=float((pr == Y_TE).mean()), pred=pr))
    best = min(rows, key=lambda r: r["loss"])
    return rows, best

def boot(pa, pb, seed, B):
    rng = np.random.default_rng(seed)
    ca, cb = (pa == Y_TE).astype(float), (pb == Y_TE).astype(float)
    d = ca - cb
    n = len(d); idx = rng.integers(0, n, (B, n))
    ds = d[idx].mean(1)
    return float(d.mean()), float(ds.mean()), [float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))]

out = {}
# 0. igualdad de funciones con las del autor (solo comprobacion; no se usan para entrenar)
sys.path.insert(0, str(SRC))
import run_f3 as F, run_f3b as F3B   # noqa  (solo para cross-check de funcion)
rg = np.random.default_rng(99)
cc = {}
p32 = rg.standard_normal(32) * 1.5
cc["unitary_diff"] = float(np.abs(U_of(p32[:16]) - F.unpack_unitary(p32[:16])).max())
cc["logits_full_diff"] = float(np.abs(L_full(p32, X_TE) - F3B.logits_A(p32, X_TE)).max())
cc["logits_real_diff"] = float(np.abs(L_real(p32, X_TE) - F3B.logits_B(p32, X_TE)).max())
cc["logits_m1_diff"] = float(np.abs(L_m1(p32[:16], X_TE) - F.logits("m1", p32[:16], X_TE)).max())
cc["task_Y_TR_equal"] = bool((Y_TR == F.Y_TR).all()); cc["task_Y_TE_equal"] = bool((Y_TE == F.Y_TE).all())
cc["X_equal"] = bool((X_TR == F.X_TR).all() and (X_TE == F.X_TE).all())
cc["class_balance_test"] = np.bincount(Y_TE, minlength=4).tolist()
cc["chance_majority_test"] = float(np.bincount(Y_TE).max() / len(Y_TE))
out["crosscheck_funciones"] = cc
print("crosscheck", cc, flush=True)

# 1. entrenar los 4 modelos + M1, mi implementacion
fits = {}
for name, fn, n in [("M_full", L_full, 32), ("M_nonlin_off", L_nl_off, 32), ("M_det_off", L_det_off, 32),
                    ("M_real", L_real, 32), ("M1", L_m1, 16)]:
    rows, best = fit(fn, n)
    fits[name] = (rows, best)
    out.setdefault("modelos", {})[name] = dict(
        best_seed=best["seed"], train_acc=best["tr"], test_acc=best["te"], train_loss=best["loss"],
        selected_success=best["succ"], selected_nit=best["nit"],
        n_restarts_maxiter=int(sum(r["nit"] >= 300 for r in rows)), n_success=int(sum(r["succ"] for r in rows)),
        test_range=[min(r["te"] for r in rows), max(r["te"] for r in rows)],
        per_seed=[dict(seed=r["seed"], loss=r["loss"], te=r["te"], nit=r["nit"], succ=r["succ"]) for r in rows])
    print(name, "seed", best["seed"], "train", best["tr"], "test", best["te"], "loss", round(best["loss"], 9),
          "succ", best["succ"], "nit", best["nit"], round(time.time() - T0), "s", flush=True)

# 2. comparaciones con el guardado del autor
st_a = [json.load(open(SRC / "f3b_seeds" / f"a_s{s}.json")) for s in range(1, 9)]
st_b = json.load(open(SRC / "f3b_resultados.json"))
f3 = json.load(open(SRC / "f3_resultados.json"))
out["E0"] = dict(test_acc=fits["M_full"][1]["te"], dif_vs_0_6425=abs(fits["M_full"][1]["te"] - 0.6425),
                 best_seed=fits["M_full"][1]["seed"],
                 max_dif_loss_8_semillas=max(abs(r["loss"] - s["train_loss"]) for r, s in zip(fits["M_full"][0], st_a)),
                 max_dif_test_acc_8_semillas=max(abs(r["te"] - s["test_acc"]) for r, s in zip(fits["M_full"][0], st_a)),
                 pred_mismatch_best=int((fits["M_full"][1]["pred"] != np.array(min(st_a, key=lambda r: r["train_loss"])["test_pred"])).sum()))
out["E2"] = dict(test_acc=fits["M_real"][1]["te"], dif_vs_guardado=abs(fits["M_real"][1]["te"] - st_b["b"]["test_acc"]),
                 pred_mismatch=int((fits["M_real"][1]["pred"] != np.array(st_b["b"]["test_pred"])).sum()))
out["E1"] = dict(test_acc=fits["M1"][1]["te"], dif_vs_0_5905=abs(fits["M1"][1]["te"] - 0.5905),
                 pred_mismatch=int((fits["M1"][1]["pred"] != np.array(f3["m1"]["test_pred"])).sum()))
print("E0", out["E0"], "\nE1", out["E1"], "\nE2", out["E2"], flush=True)

# 3. bootstrap con otras semillas + metodo analitico (cuentas de discordancia)
P = {k: fits[k][1]["pred"] for k in fits}
pairs = {"H-A1 (M_full - M_nonlin_off)": ("M_full", "M_nonlin_off"),
         "H-A2 (M_nonlin_off - M_det_off)": ("M_nonlin_off", "M_det_off"),
         "H-A3 (M_det_off - M1)": ("M_det_off", "M1")}
bs = {}
for h, (a, b) in pairs.items():
    ca, cb = P[a] == Y_TE, P[b] == Y_TE
    n10, n01 = int((ca & ~cb).sum()), int((~ca & cb).sum())
    se = np.sqrt((n10 + n01 - (n10 - n01) ** 2 / 2000) / 2000 ** 2)   # error tipico pareado
    rec = dict(punto=float(ca.mean() - cb.mean()), n_a_ok_b_mal=n10, n_a_mal_b_ok=n01,
               ic_normal_pareado=[float(ca.mean() - cb.mean() - 1.96 * se), float(ca.mean() - cb.mean() + 1.96 * se)])
    from math import comb
    # McNemar exacto bilateral
    nn = n10 + n01
    if nn:
        k = min(n10, n01)
        pv = min(1.0, 2 * sum(comb(nn, i) for i in range(0, k + 1)) / 2 ** nn)
    else:
        pv = 1.0
    rec["mcnemar_exacto_p"] = pv
    for sd in (777, 4242, 20261013):
        pt, mb, ci = boot(P[a], P[b], sd, 10000 if sd != 20261013 else 1000)
        rec[f"boot_seed{sd}"] = dict(media=mb, ci95=ci)
    bs[h] = rec
    print(h, json.dumps(rec), flush=True)
out["bootstrap"] = bs
signo = {"H-A1": bs["H-A1 (M_full - M_nonlin_off)"]["boot_seed777"]["ci95"][1] < 0,
         "H-A2": bs["H-A2 (M_nonlin_off - M_det_off)"]["boot_seed777"]["ci95"][0] > 0,
         "H-A3": bs["H-A3 (M_det_off - M1)"]["boot_seed777"]["ci95"][0] <= 0 <= bs["H-A3 (M_det_off - M1)"]["boot_seed777"]["ci95"][1]}
out["signos"] = dict(H_A1_IC_enteramente_negativo=bool(signo["H-A1"]), H_A2_IC_inferior_positivo=bool(signo["H-A2"]),
                     H_A3_IC_contiene_0=bool(signo["H-A3"]))

# 4. diagnosticos citados en RESULTADOS (fraccion I1 >= 1, >= 2)
pf = fits["M_full"][1]
rowsA = None
# se reconstruye p del seleccionado re-entrenando solo la semilla 5 (determinista)
p0 = 0.5 * np.random.default_rng(fits["M_full"][1]["seed"]).standard_normal(32)
rs = minimize(xent, p0, args=(L_full, X_TR, Y_TR), method="L-BFGS-B", options={"maxiter": 300})
I1 = np.abs(X_TR @ U_of(rs.x[:16]).T) ** 2
out["diag_I1"] = dict(frac_ge1=float((I1 >= 1).mean()), frac_ge2=float((I1 >= 2).mean()),
                      mediana=float(np.median(I1)), p95=float(np.quantile(I1, .95)), max=float(I1.max()))
print("diag_I1", out["diag_I1"], flush=True)

# 5. unitariedad y analiticas propias
errs = [float(np.abs(U_of(rg.standard_normal(16) * 2) @ U_of(rg.standard_normal(16)).conj().T - np.eye(4)).max()) for _ in range(5)]
errU = max(float(np.abs((lambda U: U @ U.conj().T - np.eye(4))(U_of(rg.standard_normal(16) * 2))).max()) for _ in range(100))
errD = 0.0
for _ in range(20):
    p = rg.standard_normal(32) * 2
    U = U_of(p[16:]) @ U_of(p[:16])
    errD = max(errD, float(np.abs(L_det_off(p, X_TE) - np.abs(X_TE @ U.T) ** 2).max()))
out["analiticas"] = dict(unitariedad_max=errU, det_off_vs_cascada=errD)
print("analiticas", out["analiticas"], flush=True)

# 6. SONDA NO PREREGISTRADA (solo informativa): V_pi mayor para M_full
sonda = {}
for vpi in (4.0, 8.0):
    fn = (lambda v: (lambda p, X: L_full(p, X, vpi=v)))(vpi)
    rows, best = fit(fn, 32)
    pr = best["pred"]
    pt, mb, ci = boot(pr, P["M_nonlin_off"], 777, 10000)
    sonda[f"Vpi={vpi}"] = dict(best_seed=best["seed"], train_acc=best["tr"], test_acc=best["te"], nit=best["nit"],
                               succ=best["succ"], punto_vs_nonlin_off=pt, ci95=ci)
    print("sonda", vpi, sonda[f"Vpi={vpi}"], flush=True)
out["sonda_no_preregistrada"] = sonda
out["tiempo_s"] = time.time() - T0
json.dump(out, open(HERE / "verif_ablacion_resultados.json", "w"), indent=1, default=float)
print("OK", round(out["tiempo_s"]), "s")
