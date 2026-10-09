"""T6 measurement: convergence of a standard second-order finite-difference solver (scalar LP01).

Purpose: measure the error that a standard FD solver makes on the analogue step fibre (lambda = 1.55 um,
a = 6 um, n1 = 1.444, n2 = 1.439, V = 2.9202), to compare it with the TE/TM splitting (~3e-6 in n_eff)
that the vector check must resolve. Scalar LP01 only: this is the discretisation error, not the vector
check itself.

Method: 5-point Laplacian on [-L, L]^2 with Dirichlet walls, operator (lap + k0^2 n^2) psi = beta^2 psi,
shift-invert eigsh around k0^2 n1^2. Analytic reference: U, W from the LP01 eigenvalue equation.
Run: python -B fd_escalar_convergencia.py   -> fd_escalar_convergencia.json (same folder).
"""
import json, pathlib, sys
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from scipy.optimize import brentq
from scipy.special import j0, j1, k0 as K0, k1 as K1

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
LAM, A, N1, N2 = 1.55, 6.0, 1.444, 1.439
K = 2 * np.pi / LAM
V = K * A * np.sqrt(N1**2 - N2**2)
L = 30.0
H_LIST = [0.5, 0.25, 0.125]


def analytic_neff():
    def f(U):
        W = np.sqrt(V**2 - U**2)
        return U * j1(U) * K0(W) - W * K1(W) * j0(U)
    U = brentq(f, 1e-6, V - 1e-9)
    beta = np.sqrt(K**2 * N1**2 - (U / A) ** 2)
    return beta / K, U


def fd_neff(h):
    x = np.arange(-L + h, L, h)  # interior nodes, symmetric about 0
    N = x.size
    X, Y = np.meshgrid(x, x, indexing="ij")
    n2 = np.where(np.hypot(X, Y) <= A, N1**2, N2**2)
    T = sp.diags([np.ones(N - 1), -2 * np.ones(N), np.ones(N - 1)], [-1, 0, 1]) / h**2
    I = sp.identity(N)
    M = (sp.kron(I, T) + sp.kron(T, I) + sp.diags((K**2 * n2).ravel())).tocsc()
    vals, _ = sla.eigsh(M, k=1, sigma=K**2 * N1**2, which="LM")
    return float(np.sqrt(vals[0].real) / K), N * N


if __name__ == "__main__":
    ref, U = analytic_neff()
    rows = []
    for h in H_LIST:
        neff, unknowns = fd_neff(h)
        rows.append({"h_um": h, "unknowns": unknowns, "neff_fd": neff, "err_abs": abs(neff - ref)})
        print(f"h={h:<6} unknowns={unknowns:>7}  n_eff_FD={neff:.10f}  |err|={abs(neff - ref):.3e}", flush=True)
    orders = [float(np.log2(rows[i]["err_abs"] / rows[i + 1]["err_abs"])) for i in range(len(rows) - 1)]
    richardson = (4 * rows[-1]["neff_fd"] - rows[-2]["neff_fd"]) / 3  # assumes order 2
    out = {"lambda_um": LAM, "a_um": A, "n1": N1, "n2": N2, "V": V, "U": U, "L_um": L,
           "neff_analytic": ref, "rows": rows, "observed_orders": orders,
           "richardson_neff_from_last_two": richardson,
           "richardson_err_abs": abs(richardson - ref),
           "TE_TM_splitting_reference": 3.1e-6}
    (HERE / "fd_escalar_convergencia.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                       encoding="utf-8", newline="\n")
    print(f"analytic n_eff={ref:.10f}  observed orders={[round(o, 2) for o in orders]}  "
          f"richardson |err|={abs(richardson - ref):.3e}")
