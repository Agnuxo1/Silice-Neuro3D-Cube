"""CPU analytical gates only; no driver query or GPU workload in tests."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

spec = importlib.util.spec_from_file_location("mega_audit", Path(__file__).resolve().parents[1] /
                                             "scripts/audit_megageometry_optics.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class MegaGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.analytical_checks()

    def test_all_frozen_gates(self):
        self.assertTrue(all(self.report["gates"].values()))

    def test_24_independent_coordinate_hits(self):
        self.assertEqual(len(self.report["affine_hits"]), 24)
        self.assertEqual(len({r["transform"] for r in self.report["affine_hits"]}), 6)

    def test_scale_does_not_preserve_physical_path(self):
        rows = [r for r in self.report["affine_hits"] if r["transform"] == "uniform_scale"]
        for r in rows:
            self.assertAlmostEqual(r["world_length_m"] / r["rest_length_m"], 1.001, places=12)
            self.assertGreater(r["wrong_rest_length_phase_error_rad"], .01)

    def test_dark_port_and_small_angle(self):
        rows = self.report["two_arm_interference"]
        self.assertEqual(rows[0]["dark_port_power"], 0)
        self.assertAlmostEqual(rows[1]["dark_port_power"], rows[1]["phase_rad"]**2/4, delta=1e-10)
        self.assertGreater(rows[-1]["dark_port_power"], .25)

    def test_optical_budget_is_not_triangle_count(self):
        self.assertAlmostEqual(self.report["budget"]["physical_length_nm"], 1.708, delta=.001)
        self.assertFalse(self.report["illustrative_image_rays"]["measured"])
        self.assertAlmostEqual(self.report["illustrative_memory_GiB"]["500M_8edges_16byte_each"],
                               59.604644775390625)

    def test_parallel_ray_rejected(self):
        tri = np.array([[0., 0, 0], [1, 0, 0], [0, 1, 0]])
        with self.assertRaises(ValueError):
            audit.triangle_hit(np.array([.1, .1, -1]), np.array([1., 0, 0]), tri)


if __name__ == "__main__":
    unittest.main()
