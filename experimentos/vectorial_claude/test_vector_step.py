"""Validation gates V1-V5 of Docs/VECTORIAL-CONTRATO.md.

run_contrast.py refuses to report H1-H3 unless these tests pass.
"""
from __future__ import annotations

import unittest

from vector_step import Guide, radius_for_v, residual_ok, top_root, v_number

LAM = 1.55e-6
N1 = 1.444
N2_PROJECT = N1 - 0.005
A_PROJECT = 6e-6
V_STAR = v_number(LAM, N1, N2_PROJECT, A_PROJECT)
J0_FIRST_ZERO = 2.404825557695773  # first zero of J0: TE01 / TM01 cutoff


def modes(n1: float, n2: float, v: float) -> dict:
    """Most confined root of each family: (b, n_eff, residual_ok) or None."""
    g = Guide(n1, n2, v)
    families = {
        "HE11": lambda b: g.hybrid(b, 1),
        "LP01": g.lp01,
        "TE01": g.te01,
        "TM01": g.tm01,
        "HE21": lambda b: g.hybrid(b, 2),
        "LP11": g.lp11,
    }
    out = {}
    for name, func in families.items():
        top = top_root(func)
        if top is None:
            out[name] = None
        else:
            out[name] = (top[0], float(g.n_eff(top[0])), residual_ok(func, top))
    return out


def te01_exists(v: float) -> bool:
    return top_root(Guide(N1, N2_PROJECT, v).te01) is not None


class GateV1ScalarLimit(unittest.TestCase):
    """V1: as dn -> 0 the vector modes coincide with the scalar ones (rel. 1e-6)."""

    def test_scalar_limit_at_v_star(self):
        m = modes(N1, N1 - 1e-7, V_STAR)
        for name, value in m.items():
            self.assertIsNotNone(value, name)
            self.assertTrue(value[2], f"residual gate failed for {name}")
        ref = m["TE01"][1]
        for name in ("TM01", "HE21", "LP11"):
            self.assertLessEqual(abs(m[name][1] - ref) / N1, 1e-6, name)
        self.assertLessEqual(abs(m["HE11"][1] - m["LP01"][1]) / N1, 1e-6)


class GateV2TE01Cutoff(unittest.TestCase):
    """V2: TE01 appears at V = 2.4048 (first zero of J0), error <= 1e-4 in V."""

    def test_te01_cutoff_location(self):
        lo, hi = 2.30, 2.50  # TE01 absent at lo, present at hi
        self.assertFalse(te01_exists(lo))
        self.assertTrue(te01_exists(hi))
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if te01_exists(mid):
                hi = mid
            else:
                lo = mid
        self.assertLessEqual(abs(0.5 * (lo + hi) - J0_FIRST_ZERO), 1e-4)


class GateV3Residuals(unittest.TestCase):
    """V3: every reported root satisfies |F| <= 1e-9 relative to its bracket."""

    def test_residuals_at_project_contrast(self):
        m = modes(N1, N2_PROJECT, V_STAR)
        for name, value in m.items():
            self.assertIsNotNone(value, name)
            self.assertTrue(value[2], f"residual gate failed for {name}")


class GateV4FundamentalAtLowV(unittest.TestCase):
    """V4: HE11 has no cutoff; it is guided at V = 0.5."""

    def test_he11_present_at_low_v(self):
        g = Guide(N1, N2_PROJECT, 0.5)
        top = top_root(lambda b: g.hybrid(b, 1))
        self.assertIsNotNone(top)
        self.assertTrue(residual_ok(lambda b: g.hybrid(b, 1), top))


class GateV5Bounds(unittest.TestCase):
    """V5: n2 < n_eff < n1 for every reported mode."""

    def test_neff_between_cladding_and_core(self):
        m = modes(N1, N2_PROJECT, V_STAR)
        for name, value in m.items():
            self.assertIsNotNone(value, name)
            self.assertGreater(value[1], N2_PROJECT, name)
            self.assertLess(value[1], N1, name)


class ConsistencyChecks(unittest.TestCase):
    """Identities that must hold exactly, not only in the limit."""

    def test_te01_and_scalar_lp11_share_one_equation(self):
        g = Guide(N1, N2_PROJECT, V_STAR)
        for b in (0.05, 0.3, 0.6, 0.9):
            self.assertAlmostEqual(float(g.te01(b)), float(g.lp11(b)), places=14)

    def test_hybrid_at_nu0_is_product_of_te_and_tm(self):
        g = Guide(N1, N2_PROJECT, V_STAR)
        for b in (0.05, 0.3, 0.6, 0.9):
            lhs = float(g.hybrid(b, 0))
            rhs = float(g.te01(b)) * float(g.tm01(b))
            self.assertAlmostEqual(lhs, rhs, delta=1e-12 * max(1.0, abs(rhs)))

    def test_radius_for_v_round_trip(self):
        a = radius_for_v(LAM, N1, N2_PROJECT, V_STAR)
        self.assertAlmostEqual(a, A_PROJECT, places=12)


if __name__ == "__main__":
    unittest.main()
