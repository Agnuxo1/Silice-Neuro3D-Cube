import json
import math
import unittest

import numpy as np

from silice.bpm import power, propagate
from silice.coverage import CellGrid
from silice.coupler import geometry, gaussian_ports, project, galerkin_generator, reduced_prediction


class CouplerTests(unittest.TestCase):
    def setUp(self):
        self.g = CellGrid(64, 128e-6)

    def test_geometry_intact_cores_and_no_double_index(self):
        dn, w, meta = geometry(self.g)
        self.assertTrue(meta['fully_core_untouched'])
        self.assertTrue(meta['no_double_index'])
        self.assertLess(max(meta['detector_area_errors']), 1e-12)
        self.assertTrue(np.all((w >= 0) & (w <= 1)))
        self.assertEqual(dn.min(), -.005)
        json.dumps(meta, allow_nan=False)

    def test_geometry_invalid_or_expired(self):
        for kwargs in ({'separation_m': 12e-6}, {'delta_n': .001}, {'samples': 8},
                       {'separation_m': float('nan')}, {'separation_m': 100e-6}):
            with self.assertRaises(ValueError):
                geometry(self.g, **kwargs)
        with self.assertRaises(TimeoutError):
            geometry(self.g, deadline=0)

    def test_orthogonal_ports_projection(self):
        q, meta = gaussian_ports(self.g)
        self.assertLess(meta['orthogonality_error'], 1e-12)
        c = np.array([1, 1j])/math.sqrt(2)
        field = np.einsum('a,aij->ij', c, q)
        np.testing.assert_allclose(project(field, q, self.g), c, atol=1e-13)
        self.assertAlmostEqual(power(field, self.g), 1, places=12)

    def test_reduction_hermitian_zero_and_lossless(self):
        q, _ = gaussian_ports(self.g)
        dn, _, _ = geometry(self.g)
        h, meta = galerkin_generator(q, dn, self.g)
        self.assertLess(meta['hermiticity_error_per_m'], 1e-8)
        np.testing.assert_allclose(reduced_prediction(h, 0, [1, 0]), [1, 0], atol=1e-13)
        c = reduced_prediction(h, 1e-3, [1, 0])
        self.assertAlmostEqual(float(np.vdot(c, c).real), 1, places=12)
        with self.assertRaises(ValueError):
            reduced_prediction(np.array([[0, 1j], [1j, 0]]), 1, [1, 0])

    def test_short_field_linearity_no_renormalization(self):
        q, _ = gaussian_ports(self.g)
        dn, _, _ = geometry(self.g)
        left, _ = propagate(q[0], dn, self.g, length_m=5e-6, steps=2)
        right, _ = propagate(q[1], dn, self.g, length_m=5e-6, steps=2)
        coherent, _ = propagate((q[0]+1j*q[1])/math.sqrt(2), dn, self.g, length_m=5e-6, steps=2)
        np.testing.assert_allclose(coherent, (left+1j*right)/math.sqrt(2), rtol=1e-12, atol=1e-10)
