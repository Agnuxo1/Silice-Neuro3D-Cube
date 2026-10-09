"""Exact full-vector modes of a three-layer circular guide (CONTRATO-VECTORIAL-GEOMETRIA.md).

Layers: core (r < a, index n1, regular J), trench (a < r < b, index n2, evanescent
I and K), bulk (r > b, index n3, outgoing H^(1)). Hybrid modes of azimuthal order
nu >= 1 and TE/TM (nu = 0) share one 8x8 matching problem:
  unknowns  x = [F1, G1, F2I, F2K, G2I, G2K, F3, G3]  (E_z and H_z amplitudes)
  conditions at r = a and r = b: continuity of E_z (F), H_z (G), E_phi and H_phi.

Field relations (exp(i(beta z - omega t)), SI with H scaled by Z0 so that
omega*mu0 = k0*Z0 and omega*eps = n^2*k0/Z0):
  E_phi = (i/h^2) [ -(nu beta / r) F - omega mu0 G' ]  (times sin nu phi)
  H_phi = (i/h^2) [  (nu beta / r) G + omega eps F' ]  (times cos nu phi)
with h^2 = k0^2 n^2 - beta^2, E_z = F(r) cos(nu phi), H_z = G(r) sin(nu phi).

Computed with mpmath (30 digits). The determinant of the 8x8 matrix is the
characteristic function; complex roots beta are leaky modes.
"""
from __future__ import annotations

import math

import mpmath as mp

mp.mp.dps = 30
Z0 = mp.mpf("376.730313668")  # free-space impedance, ohm


def _d(fun, nu, z):
    """d/dz of a Bessel-type function Z_nu(z) via the recurrence (valid for integer nu)."""
    return (fun(nu - 1, z) - fun(nu + 1, z)) / 2


class ThreeLayer:
    def __init__(self, wavelength_m, n1, n2, n3, a_m, b_m, nu):
        self.k0 = 2 * mp.pi / mp.mpf(wavelength_m)
        self.n1, self.n2, self.n3 = mp.mpf(n1), mp.mpf(n2), mp.mpf(n3)
        self.a = mp.mpf(a_m)
        self.b = mp.mpf(b_m)
        self.nu = int(nu)

    def matrix(self, beta):
        """8x8 matching matrix at complex beta."""
        beta = mp.mpc(beta)
        k0, nu, a, b = self.k0, self.nu, self.a, self.b
        n = [self.n1, self.n2, self.n3]
        h = [mp.sqrt(k0 * k0 * nj * nj - beta * beta) for nj in n]
        # layer 1: regular Bessel J (h1 real for guided core)
        h1 = h[0]
        # layer 2: evanescent, gamma^2 = beta^2 - k0^2 n2^2 (h2^2 = -gamma^2)
        gam = mp.sqrt(beta * beta - k0 * k0 * n[1] * n[1])
        # layer 3: outgoing H^(1) with h3
        h3 = h[2]

        def row(r, layer):
            """Contributions to [F, G, E_phi, H_phi] from each unknown at radius r."""
            ww = k0 * Z0  # omega mu0
            we = lambda nj: nj * nj * k0 / Z0  # omega eps
            if layer == 1:
                z = h1 * r
                Zv = mp.besselj(nu, z)
                dZ = h1 * _d(mp.besselj, nu, z)  # d/dr of J_nu(h1 r)
                fac = 1j / (h1 * h1)
                row_F = [Zv, 0, 0, 0, 0, 0, 0, 0]
                row_G = [0, Zv, 0, 0, 0, 0, 0, 0]
                # E_phi from F: -(nu beta/r) Zv ; from G: -ww * dZ
                ephi = [fac * (-(nu * beta / r) * Zv), fac * (-ww * dZ), 0, 0, 0, 0, 0, 0]
                # H_phi from G: (nu beta/r) Zv ; from F: we * dZ
                hphi = [fac * (we(n[0]) * dZ), fac * ((nu * beta / r) * Zv), 0, 0, 0, 0, 0, 0]
                return [row_F, row_G, ephi, hphi]
            if layer == 2:
                zi, zk = gam * r, gam * r
                I = mp.besseli(nu, zi)
                K = mp.besselk(nu, zk)
                dI = gam * (mp.besseli(nu - 1, zi) + mp.besseli(nu + 1, zi)) / 2  # I' recurrence has '+'
                dK = -gam * (mp.besselk(nu - 1, zk) + mp.besselk(nu + 1, zk)) / 2
                fac = 1j / (-gam * gam)  # i/h^2 with h^2 = -gam^2
                row_F = [0, 0, I, K, 0, 0, 0, 0]
                row_G = [0, 0, 0, 0, I, K, 0, 0]
                ephi = [0, 0, fac * (-(nu * beta / r) * I), fac * (-(nu * beta / r) * K),
                        fac * (-ww * dI), fac * (-ww * dK), 0, 0]
                hphi = [0, 0, fac * (we(n[1]) * dI), fac * (we(n[1]) * dK),
                        fac * ((nu * beta / r) * I), fac * ((nu * beta / r) * K), 0, 0]
                return [row_F, row_G, ephi, hphi]
            z = h3 * r
            Hv = mp.hankel1(nu, z)
            dH = h3 * _d(mp.hankel1, nu, z)
            fac = 1j / (h3 * h3)
            row_F = [0, 0, 0, 0, 0, 0, Hv, 0]
            row_G = [0, 0, 0, 0, 0, 0, 0, Hv]
            ephi = [0, 0, 0, 0, 0, 0, fac * (-(nu * beta / r) * Hv), fac * (-ww * dH)]
            hphi = [0, 0, 0, 0, 0, 0, fac * (we(n[2]) * dH), fac * ((nu * beta / r) * Hv)]
            return [row_F, row_G, ephi, hphi]

        M = mp.matrix(8, 8)
        for r, (la, lb) in ((a, (1, 2)), (b, (2, 3))):
            rl, rr = row(r, la), row(r, lb)
            base = 0 if r == a else 4
            for q in range(4):
                for j in range(8):
                    M[base + q, j] = rl[q][j] - rr[q][j]
        return M

    def det(self, beta):
        return mp.det(self.matrix(beta))

    def det_te(self, beta):
        """nu = 0 TE block: rows G-continuity and E_phi (1,2,5,6), columns G1,G2I,G2K,G3 (1,4,5,7)."""
        M = self.matrix(beta)
        sub = mp.matrix(4, 4)
        for i, ri in enumerate([1, 2, 5, 6]):
            for j, cj in enumerate([1, 4, 5, 7]):
                sub[i, j] = M[ri, cj]
        return mp.det(sub)

    def det_tm(self, beta):
        """nu = 0 TM block: rows F-continuity and H_phi (0,3,4,7), columns F1,F2I,F2K,F3 (0,2,3,6)."""
        M = self.matrix(beta)
        sub = mp.matrix(4, 4)
        for i, ri in enumerate([0, 3, 4, 7]):
            for j, cj in enumerate([0, 2, 3, 6]):
                sub[i, j] = M[ri, cj]
        return mp.det(sub)

    def root(self, guess_beta):
        return mp.findroot(self.det, mp.mpc(guess_beta), tol=mp.mpf(10) ** (-20), maxsteps=200)
