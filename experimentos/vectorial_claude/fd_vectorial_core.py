"""T6 r5 nucleo FD de orden 2 con permitividad promediada en la interfaz (CONTRATO-T6-r5.md).

Formulacion declarada (semivectorial H_y):
    beta^2 H = eps d_x( (1/eps) d_x H ) + d_y^2 H + k0^2 eps H
Malla de celdas centradas, cuadrante [0,L]^2 con Neumann (x=0, y=0) o Dirichlet (sx/sy=-1),
Dirichlet en L. eps promediado en el area exacta de la celda (disco de radio R).
Caras de la parte x: u = 2/(eps_L + eps_R) (media armonica de 1/eps).
Modo escalar de control: beta^2 psi = (d_x^2 + d_y^2 + k0^2 eps) psi, mismo promediado.

Solo numpy/scipy y biblioteca estandar. Sin GPU. Un solo hilo (OMP_NUM_THREADS=1).
"""
from __future__ import annotations

import ctypes
import math
import time

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla


# ---------------------------------------------------------------- memoria (Windows, stdlib)
class _PMC(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def peak_memory_bytes() -> int:
    """Pico de working set del proceso actual (bytes). -1 si no esta disponible."""
    try:
        psapi = ctypes.WinDLL("psapi")
        kernel32 = ctypes.WinDLL("kernel32")
        pmc = _PMC()
        pmc.cb = ctypes.sizeof(_PMC)
        ok = psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
        return int(pmc.PeakWorkingSetSize) if ok else -1
    except OSError:
        return -1


# ---------------------------------------------------------------- area de disco en celda
def _disk_area_quadrant(x, y, R):
    """Area de {u,v >= 0 : u <= x, v <= y, u^2 + v^2 <= R^2} para x, y >= 0 (arrays de igual forma)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    def G(t):
        t = np.clip(t, 0.0, R)
        return 0.5 * (t * np.sqrt(np.maximum(R * R - t * t, 0.0))
                      + R * R * np.arcsin(np.clip(t / R, -1.0, 1.0)))

    xm = np.minimum(x, R)
    s = np.sqrt(np.maximum(R * R - y * y, 0.0))
    a_big = G(xm)
    a_small = y * np.minimum(x, s) + np.where(x > s, G(xm) - G(s), 0.0)
    return np.where(y >= R, a_big, a_small)


def cell_fraction(M: int, h: float, R: float) -> np.ndarray:
    """Fraccion de area de cada celda (i,j) del cuadrante [0,M h]^2 cubierta por el disco de radio R."""
    f = np.arange(M + 1, dtype=float) * h
    # X0[i,j] = x_i, X1[i,j] = x_{i+1}, Y0[i,j] = y_j, Y1[i,j] = y_{j+1}
    X0 = np.repeat(f[:-1, None], M, axis=1)
    X1 = np.repeat(f[1:, None], M, axis=1)
    Y0 = np.repeat(f[None, :-1], M, axis=0)
    Y1 = np.repeat(f[None, 1:], M, axis=0)
    area = (_disk_area_quadrant(X1, Y1, R) - _disk_area_quadrant(X0, Y1, R)
            - _disk_area_quadrant(X1, Y0, R) + _disk_area_quadrant(X0, Y0, R))
    return area / (h * h)


def eps_quadrant(M: int, h: float, a: float, n_core: float, n_out: float,
                 b: float | None = None, n_tr: float | None = None) -> np.ndarray:
    """Permitividad promediada en celda. Nucleo r<a (n_core), trinchera a<r<b (n_tr), exterior (n_out)."""
    Fa = cell_fraction(M, h, a)
    if b is None:
        return n_core ** 2 * Fa + n_out ** 2 * (1.0 - Fa)
    Fb = cell_fraction(M, h, b)
    return n_core ** 2 * Fa + n_tr ** 2 * (Fb - Fa) + n_out ** 2 * (1.0 - Fb)


def eps_full_from_quadrant(E: np.ndarray) -> np.ndarray:
    """Espejo a la malla completa [-L,L]^2 (2M x 2M) para la comprobacion de simetria V-d."""
    return np.block([[E[::-1, ::-1], E[::-1, :]], [E[:, ::-1], E]])


# ---------------------------------------------------------------- operadores
def assemble(E: np.ndarray, k0: float, h: float, sx: int, sy: int, semi: bool) -> sp.csr_matrix:
    """Matriz A con beta^2 H = A H.

    semi=True : A = diag(eps) Dx_u + Dy + k0^2 diag(eps), con u = 1/eps en caras (media armonica).
    semi=False: A = Dx + Dy + k0^2 diag(eps) (escalar, mismo promediado en eps).
    sx, sy = +1 Neumann (par) o -1 Dirichlet-impar en el borde inferior (x=0, y=0).
    En el borde superior (x=L, y=L) siempre Dirichlet (ghost = -H).
    """
    Mx, My = E.shape
    idx = np.arange(Mx * My).reshape(Mx, My)
    if semi:
        W = E
        Uix = 2.0 / (E[:-1, :] + E[1:, :])
        UL = 1.0 / E[0, :]
        UR = 1.0 / E[-1, :]
    else:
        W = np.ones_like(E)
        Uix = np.ones((Mx - 1, My))
        UL = np.ones(My)
        UR = np.ones(My)

    # --- Dx puro (sin 1/h^2)
    p = idx[:-1, :].ravel()
    q = idx[1:, :].ravel()
    u = Uix.ravel()
    rx = np.concatenate([p, p, q, q])
    cx = np.concatenate([p, q, q, p])
    vx = np.concatenate([-u, u, -u, u])
    p0 = idx[0, :]
    rx = np.concatenate([rx, p0])
    cx = np.concatenate([cx, p0])
    vx = np.concatenate([vx, -(1.0 - sx) * UL])
    pe = idx[-1, :]
    rx = np.concatenate([rx, pe])
    cx = np.concatenate([cx, pe])
    vx = np.concatenate([vx, -2.0 * UR])
    Dx = sp.coo_matrix((vx / (h * h), (rx, cx)), shape=(Mx * My, Mx * My)).tocsr()
    Ax = sp.diags(W.ravel()) @ Dx

    # --- Dy (coeficiente 1)
    p = idx[:, :-1].ravel()
    q = idx[:, 1:].ravel()
    ry = np.concatenate([p, p, q, q])
    cy = np.concatenate([p, q, q, p])
    vy = np.concatenate([-np.ones(p.size), np.ones(p.size), -np.ones(p.size), np.ones(p.size)])
    b0 = idx[:, 0]
    ry = np.concatenate([ry, b0])
    cy = np.concatenate([cy, b0])
    vy = np.concatenate([vy, np.full(b0.size, -(1.0 - sy))])
    bt = idx[:, -1]
    ry = np.concatenate([ry, bt])
    cy = np.concatenate([cy, bt])
    vy = np.concatenate([vy, np.full(bt.size, -2.0)])
    Dy = sp.coo_matrix((vy / (h * h), (ry, cy)), shape=(Mx * My, Mx * My)).tocsr()

    A = Ax + Dy + sp.diags((k0 * k0) * E.ravel())
    return A.tocsr()


def top_eigs(A, sigma: float, k: int = 3, symmetric: bool = False):
    """Autovalores de A mas cercanos a sigma (shift-invert). Devuelve (lam[], vec[:,0], lam_max_real)."""
    if symmetric:
        vals, vecs = sla.eigsh(A, k=k, sigma=sigma, which="LM", tol=1e-13)
    else:
        vals, vecs = sla.eigs(A, k=k, sigma=sigma, which="LM", tol=1e-13)
    order = np.argsort(-vals.real)
    vals = vals[order]
    vecs = vecs[:, order]
    return vals, vecs


def residual_rel(A, lam: complex, v: np.ndarray) -> float:
    r = A @ v - lam * v
    return float(np.linalg.norm(r) / np.linalg.norm(v))


def neff_from_beta2(beta2, k0: float) -> float:
    return math.sqrt(float(np.real(beta2))) / k0


def timed(fn, *args, **kwargs):
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    return out, time.perf_counter() - t0
