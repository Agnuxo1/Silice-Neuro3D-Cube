"""Tarea H1: observable de potencia en el nucleo con peso por cobertura (area parcial).

Implementacion independiente (no copia src/silice ni los scripts de 009b/009d).
Ningun archivo original se modifica. Solo CPU, un hilo.

Convenciones (las mismas que 009b/009d para poder comparar):
  x_i = (i - N//2) * h, malla N x N, centros de celda en los nodos.
  r_c = |x_i, y_j| del centro de la celda.
"""
import math
import numpy as np

A0 = 6e-6          # radio del nucleo (m), igual que 009b/009d
SQ = 1.0 / math.sqrt(2.0)


def grid(N, h):
    ax = (np.arange(N) - N // 2) * h
    x, y = np.meshgrid(ax, ax, indexing="xy")
    return x, y


def disk_coverage(N, h, a=A0, ss=64):
    """Peso w_ij = fraccion del area de la celda (lado h, centrada en el nodo) dentro de r<a.

    Clasificacion exacta de celdas interiores (r_c < a - h/sqrt2: w=1) y exteriores
    (r_c > a + h/sqrt2: w=0). Solo las celdas de frontera se submuestrean ss x ss.
    """
    x, y = grid(N, h)
    r = np.hypot(x, y)
    half_diag = h * SQ
    w = (r < a - half_diag).astype(float)
    band = np.abs(r - a) <= half_diag
    xb, yb = x[band], y[band]
    off = (np.arange(ss) + 0.5) / ss - 0.5
    acc = np.zeros(xb.shape)
    for oy in off:
        for ox in off:
            acc += ((xb + ox * h) ** 2 + (yb + oy * h) ** 2 < a * a)
    w[band] = acc / (ss * ss)
    return w


def disk_coverage_uniform(N, h, a=A0, ss=16):
    """Submuestreo uniforme ss x ss en todas las celdas (convencion de 009b/009d)."""
    x, y = grid(N, h)
    w = np.zeros((N, N))
    off = (np.arange(ss) + 0.5) / ss - 0.5
    for oy in off:
        for ox in off:
            w += ((x + ox * h) ** 2 + (y + oy * h) ** 2 < a * a)
    return w / (ss * ss)


def obs_center(psi, h, N=None, a=A0):
    """Observable original: indicador r<a evaluado en el centro de la celda (adi2d.core_fraction)."""
    x, y = grid(psi.shape[0], h)
    return float((np.abs(psi) ** 2 * (x * x + y * y < a * a)).sum() * h * h)


def obs_cov(psi, w, h):
    """Observable de cobertura: sum_ij w_ij |psi_ij|^2 h^2."""
    return float((w * np.abs(psi) ** 2).sum() * h * h)


def modified_mask_cov(N, dx, kind, ss=16, a=A0, t=6e-6, rad_disc=1.25e-6):
    """Perfil de 009d por cobertura: fraccion de cada celda dentro de la region modificada.

    kind 'Cd': anillo r in [a, a+t). kind 'T96d': anillo intersectado con la union de 96 discos
    (32 por corona, radios 7,25/9/10,75 um, offset pi/32 en corona impar).
    Solo se evalua en las celdas que pueden tocar el anillo (r en [a-dx, a+t+dx]).
    """
    x, y = grid(N, dx)
    r = np.hypot(x, y)
    cov = np.zeros((N, N))
    near = (r >= a - dx) & (r <= a + t + dx)
    xn, yn = x[near], y[near]
    rn = r[near]
    cs = []
    if kind == "T96d":
        for k, rad in enumerate([7.25e-6, 9e-6, 10.75e-6]):
            off = math.pi / 32 if k % 2 else 0.0
            for j in range(32):
                an = 2 * math.pi * j / 32 + off
                cs.append((rad * math.cos(an), rad * math.sin(an)))
    off = (np.arange(ss) + 0.5) / ss - 0.5
    acc = np.zeros(xn.shape)
    for oy in off:
        for ox in off:
            px, py = xn + ox * dx, yn + oy * dx
            pr = np.hypot(px, py)
            m = (pr >= a) & (pr < a + t)
            if kind == "T96d":
                u = np.zeros_like(m)
                for cx, cy in cs:
                    u |= (px - cx) ** 2 + (py - cy) ** 2 <= rad_disc ** 2
                m &= u
            acc += m
    cov[near] = acc / (ss * ss)
    return cov


def exact_area_disk_cells(N, h, a=A0):
    """Referencia de area: pi a^2 (la suma de w debe reproducirla)."""
    return math.pi * a * a
