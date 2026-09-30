import math
import unittest
import numpy as np
from silice.bpm import Grid
from silice.coverage import CellGrid, circle_coverage, union_coverage, averaged_profile, weighted_core_power
from silice.tracks import track_centres


class CoverageTests(unittest.TestCase):
    def test_opt_in_does_not_change_original_grid(self):
        with self.assertRaises(ValueError):
            Grid(320, 128e-6)
        self.assertEqual(CellGrid(320, 128e-6).points, 320)
        for points in (True, 321, 15):
            with self.assertRaises(ValueError):
                CellGrid(points, 128e-6)

    def test_analytic_disk_area_and_partial_pixels(self):
        for n, width in [(64, 64e-6), (192, 128e-6), (256, 128e-6), (320, 128e-6)]:
            g = CellGrid(n, width)
            w = circle_coverage(g, 6e-6)
            self.assertLess(abs(w.sum()*g.dx_m**2/(36*math.pi*1e-12)-1), 1e-12)
            self.assertGreater(np.count_nonzero((w > 0) & (w < 1)), 0)
            self.assertTrue(np.all((w >= 0) & (w <= 1)))

    def test_quarter_circle_cell_and_symmetry(self):
        g = CellGrid(64, 64e-6)
        w = circle_coverage(g, .5e-6)
        self.assertAlmostEqual(w[32, 32], math.pi/4, places=12)
        self.assertEqual(np.count_nonzero(w), 1)

    def test_union_duplicate_is_not_double_index(self):
        g = CellGrid(96, 96e-6)
        cs = ((7.25e-6, 0.0),)
        first = union_coverage(g, cs)
        duplicate = union_coverage(g, cs+cs)
        np.testing.assert_array_equal(first, duplicate)

    def test_profile_budget_and_equal_integral(self):
        g = CellGrid(128, 128e-6)
        dn, w, meta = averaged_profile(g, per_ring=32, match_integral=True)
        self.assertLess(meta["integral_match_relative_error"], 1e-12)
        self.assertTrue(meta["fully_core_cells_untouched"])
        self.assertTrue(meta["fully_outside_cells_untouched"])
        self.assertGreater(meta["ring_fill_fraction"], .9)
        self.assertLess(abs(dn.min()), .01)
        p = weighted_core_power(np.ones_like(dn), w, g, 1)
        self.assertAlmostEqual(p, 36*math.pi*1e-12, places=22)

    def test_geometry_deadline_and_detector_validation(self):
        g = CellGrid(64, 64e-6)
        with self.assertRaises(TimeoutError):
            union_coverage(g, track_centres(), deadline=0)
        for w in (np.full((64, 64), 2), np.full((64, 64), np.nan)):
            with self.assertRaises(ValueError):
                weighted_core_power(np.ones((64, 64)), w, g, 1)


if __name__ == "__main__":
    unittest.main()
