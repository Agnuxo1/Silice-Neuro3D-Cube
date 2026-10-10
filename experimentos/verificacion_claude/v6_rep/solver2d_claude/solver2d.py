"""Solver 2D escalar independiente por diferencias finitas (Laplaciano de 5 puntos).

Interfaz fija:
    solve(shapes, n_bg, lam_um, L_um, h_um, n_modes=1, s_sub=8, index_fn=None) -> dict

Ecuacion: (d2/dx2 + d2/dy2 + k0^2 n^2(x, y)) psi = beta^2 psi, con k0 = 2 pi / lam.
Malla: N = 2 round(L/h) + 1 nodos por eje, x_i = (i - (N-1)/2) h, incluidos los contornos.
Dirichlet psi = 0 en el contorno. Incognitas: nodos interiores (N-2)^2.
Promediado subpixel: cada celda h x h centrada en un nodo promedia n^2 sobre una malla s x s de subpuntos.
s_sub = 1 muestrea n^2 en el nodo (escalonado).
Convencion de matrices: psi[iy, ix] (fila = y, columna = x).
Autovalores: eigsh en shift-invert con sigma = k0^2 max(n^2_celda), which = 'LM'.

Modelo numerico. No es un dispositivo ni una medida.
"""
import math

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla


def _index_from_shapes(shapes, n_bg, X, Y):
    """Indice de refraccion en los puntos (X, Y). Las formas posteriores sobrescriben a las anteriores."""
    n = np.full(X.shape, float(n_bg))
    for sh in shapes:
        kind = sh["kind"]
        r = np.hypot(X - float(sh["x0"]), Y - float(sh["y0"]))
        if kind == "disk":
            m = r <= float(sh["r"])
        elif kind == "annulus":
            m = (r >= float(sh["r_in"])) & (r <= float(sh["r_out"]))
        else:
            raise ValueError(f"forma desconocida: {kind!r}")
        n[m] = float(sh["n"])
    return n


def cell_average(func, x, h, s, block=64):
    """Media de func(X, Y) sobre cada celda h x h centrada en (x_i, x_j).

    Usa una malla s x s de subpuntos por celda (punto medio de cada subceda).
    Devuelve matriz [iy, ix] de forma (N, N).
    """
    x = np.asarray(x, dtype=float)
    N = x.size
    s = int(s)
    if s < 1:
        raise ValueError("s_sub debe ser >= 1")
    offs = (np.arange(s) + 0.5) / s * h - 0.5 * h  # posiciones de subpuntos dentro de la celda
    xf = (x[:, None] + offs[None, :]).ravel()       # columnas: (celda ix, subpunto p)
    out = np.empty((N, N), dtype=float)
    for j0 in range(0, N, block):
        j1 = min(N, j0 + block)
        yf = (x[j0:j1, None] + offs[None, :]).ravel()  # filas: (celda iy, subpunto q)
        X, Y = np.meshgrid(xf, yf)
        F = np.asarray(func(X, Y), dtype=float)
        out[j0:j1, :] = F.reshape(j1 - j0, s, N, s).mean(axis=(1, 3))
    return out


def solve(shapes, n_bg, lam_um, L_um, h_um, n_modes=1, s_sub=8, index_fn=None):
    """Modos escalares 2D. Devuelve dict con neff (descendente), beta_um, x, y, psi, cell_n2.

    shapes: lista de dicts {"kind":"disk","x0","y0","r","n"} o {"kind":"annulus","x0","y0","r_in","r_out","n"} (um).
    n_bg: indice de fondo. Si index_fn no es None, es una funcion vectorizada n(X, Y) que sustituye a shapes.
    psi: lista de matrices 2D reales [iy, ix], normalizadas con sum |psi|^2 h^2 = 1, signo con maximo positivo.
    """
    h = float(h_um)
    L = float(L_um)
    lam = float(lam_um)
    k0 = 2.0 * np.pi / lam
    nh = int(round(L / h))
    N = 2 * nh + 1
    x = (np.arange(N) - (N - 1) / 2.0) * h
    y = x.copy()

    if index_fn is not None:
        def f(X, Y):
            return np.asarray(index_fn(X, Y), dtype=float) ** 2
    else:
        shp = list(shapes)

        def f(X, Y):
            return _index_from_shapes(shp, n_bg, X, Y) ** 2

    cell_n2 = cell_average(f, x, h, s_sub)

    M = N - 2  # incognitas interiores por eje
    n2_int = cell_n2[1:-1, 1:-1]
    sigma = k0 ** 2 * float(cell_n2.max())

    T = sp.diags([np.ones(M - 1), -2.0 * np.ones(M), np.ones(M - 1)], [-1, 0, 1], format="csr") / h ** 2
    I = sp.identity(M, format="csr")
    # P psi = beta^2 psi, con P = Laplaciano + k0^2 n^2 (simetrico, real)
    P = (sp.kron(I, T) + sp.kron(T, I) + sp.diags(k0 ** 2 * n2_int.ravel())).tocsc()

    vals, vecs = sla.eigsh(P, k=int(n_modes), sigma=sigma, which="LM")
    order = np.argsort(vals.real)[::-1]
    beta2 = vals.real[order]
    vecs = vecs[:, order]

    beta = np.sqrt(beta2)
    neff = beta / k0

    psi_list = []
    for m in range(int(n_modes)):
        full = np.zeros((N, N), dtype=float)
        full[1:-1, 1:-1] = vecs[:, m].real.reshape(M, M)
        norm = math.sqrt(float(np.sum(full * full)) * h * h)
        full = full / norm
        imax = np.unravel_index(int(np.argmax(np.abs(full))), full.shape)
        if full[imax] < 0.0:
            full = -full
        psi_list.append(full)

    return {
        "neff": [float(v) for v in neff],
        "beta_um": [float(v) for v in beta],
        "x": x,
        "y": y,
        "psi": psi_list,
        "cell_n2": cell_n2,
        "k0_um": k0,
        "h_um": h,
        "L_um": L,
        "N": N,
        "unknowns": M * M,
        "s_sub": int(s_sub),
        "sigma_um2": sigma,
    }
