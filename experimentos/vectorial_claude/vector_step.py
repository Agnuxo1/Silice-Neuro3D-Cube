"""Exact characteristic equations of a circular step-index fibre (bound limit).

Independent reference for the vectorial check in Docs/VECTORIAL-CONTRATO.md.
Exact modes: TE01, TM01 and hybrid HE11, HE21. Scalar weak-guidance modes
for comparison: LP01 and LP11.

Each guided mode is labelled by b = W^2 / V^2 in (0, 1), with
U^2 = V^2 (1 - b), W^2 = V^2 b and n_eff^2 = n2^2 + b (n1^2 - n2^2).

Equations: arXiv:2005.01363 and arXiv:1706.04291, hybrid form
[A + B][A + (n2/n1)^2 B] = (nu beta / (k0 n1))^2 (1/U^2 + 1/W^2)^2,
with A = J'_nu(U)/(U J_nu(U)) and B = K'_nu(W)/(W K_nu(W)). Each function
here is pole-free: the Bessel ratios are cleared (see Guide.hybrid).

Units: lengths in metres. Pure numpy/scipy, no GPU, no I/O.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import brentq
from scipy.special import jv, jvp, kv, kvp

RESIDUAL_RTOL = 1e-9  # V3: |F(root)| <= RESIDUAL_RTOL * local scale


def v_number(wavelength_m: float, n1: float, n2: float, radius_m: float) -> float:
    """V = k0 a sqrt(n1^2 - n2^2)."""
    k0 = 2.0 * math.pi / wavelength_m
    return k0 * radius_m * math.sqrt(n1 * n1 - n2 * n2)


def radius_for_v(wavelength_m: float, n1: float, n2: float, v: float) -> float:
    """Core radius that gives the requested V for the given indices."""
    k0 = 2.0 * math.pi / wavelength_m
    return v / (k0 * math.sqrt(n1 * n1 - n2 * n2))


def guide_grid() -> np.ndarray:
    """Grid in b that resolves modes close to cutoff (log) and bulk (linear)."""
    near_zero = np.logspace(-12, -2, 4000)
    bulk = np.linspace(1e-2, 1.0 - 1e-12, 20000)
    return np.unique(np.concatenate([near_zero, bulk]))


class Guide:
    """Circular step-index guide at fixed V with index n1 (core) and n2 (cladding)."""

    def __init__(self, n1: float, n2: float, v: float):
        if not 0.0 < n2 < n1:
            raise ValueError("require 0 < n2 < n1")
        if v <= 0.0:
            raise ValueError("require V > 0")
        self.n1 = float(n1)
        self.n2 = float(n2)
        self.v = float(v)
        self.rho = (self.n2 / self.n1) ** 2
        self.diff = self.n1 * self.n1 - self.n2 * self.n2

    # Mode-label maps -------------------------------------------------------
    def U(self, b):
        return self.v * np.sqrt(1.0 - b)

    def W(self, b):
        return self.v * np.sqrt(b)

    def n_eff(self, b):
        return np.sqrt(self.n2 * self.n2 + b * self.diff)

    # Exact TE and TM (nu = 0) -----------------------------------------------
    def te01(self, b):
        """J1(U)/(U J0(U)) + K1(W)/(W K0(W)) = 0, cleared of denominators."""
        U, W = self.U(b), self.W(b)
        return W * kv(0, W) * jv(1, U) + U * jv(0, U) * kv(1, W)

    def tm01(self, b):
        """J1(U)/(U J0(U)) + rho K1(W)/(W K0(W)) = 0, cleared of denominators."""
        U, W = self.U(b), self.W(b)
        return W * kv(0, W) * jv(1, U) + self.rho * U * jv(0, U) * kv(1, W)

    # Exact hybrid HE/EH (nu >= 1) -------------------------------------------
    def hybrid(self, b, nu: int):
        """Characteristic function of HE_nu,m / EH_nu,m.

        With p = J'_nu(U), J = J_nu(U), q = K'_nu(W), K = K_nu(W):
        (pWK + qUJ)(pWK + rho q U J) - nu^2 (beta/(k0 n1))^2 (U^2+W^2)^2 J^2 K^2 / (U^2 W^2)
        equals U^2 W^2 J^2 K^2 times the bracket form, so it has no poles.
        """
        U, W = self.U(b), self.W(b)
        J, p = jv(nu, U), jvp(nu, U)
        K, q = kv(nu, W), kvp(nu, W)
        beta_ratio_sq = (self.n2 * self.n2 + b * self.diff) / (self.n1 * self.n1)
        lhs = (p * W * K + q * U * J) * (p * W * K + self.rho * q * U * J)
        rhs = nu * nu * beta_ratio_sq * (U * U + W * W) ** 2 * J * J * K * K / (U * U * W * W)
        return lhs - rhs

    # Scalar weak-guidance modes ---------------------------------------------
    def lp01(self, b):
        """U J1(U)/J0(U) = W K1(W)/K0(W), cleared of denominators."""
        U, W = self.U(b), self.W(b)
        return U * jv(1, U) * kv(0, W) - W * kv(1, W) * jv(0, U)

    def lp11(self, b):
        """U J0(U)/J1(U) = -W K0(W)/K1(W), cleared. Identical to te01."""
        U, W = self.U(b), self.W(b)
        return U * jv(0, U) * kv(1, W) + W * kv(0, W) * jv(1, U)


def sign_change_roots(func, grid: np.ndarray | None = None):
    """Roots of func(b) on (0, 1) from sign changes, refined by brentq.

    Returns a list of (b_root, local_scale) with local_scale = max |func| at
    the bracket ends, for the residual check V3.
    """
    b = guide_grid() if grid is None else grid
    f = np.asarray(func(b), dtype=float)
    if not np.all(np.isfinite(f)):
        raise FloatingPointError("non-finite characteristic function on grid")
    out = []
    for i in np.nonzero(np.sign(f[:-1]) * np.sign(f[1:]) < 0)[0]:
        def scalar(x, _func=func):
            return float(_func(np.array([x]))[0])
        r = brentq(scalar, b[i], b[i + 1], xtol=np.finfo(float).tiny, rtol=4 * np.finfo(float).eps, maxiter=500)
        scale = max(abs(f[i]), abs(f[i + 1]))
        out.append((float(r), float(scale)))
    return out


def top_root(func) -> tuple[float, float] | None:
    """Most confined root (largest b) of a family, or None if no guided mode."""
    roots = sign_change_roots(func)
    if not roots:
        return None
    return max(roots, key=lambda rs: rs[0])


def residual_ok(func, root: tuple[float, float]) -> bool:
    """V3 test for one root: |F(root)| small relative to its bracket scale."""
    r, scale = root
    value = abs(float(func(np.array([r]))[0]))
    return value <= RESIDUAL_RTOL * max(scale, 1e-300)
