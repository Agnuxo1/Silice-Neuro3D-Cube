import time
import unittest
import numpy as np
from silice.gpu_bpm import operators, validate_field


class GPUPreparationTests(unittest.TestCase):
    def test_vacuum_and_passive_sponge(self):
        h, d, s = operators(16, 128e-6, 1e-3, 400, np.zeros((16,16)))
        np.testing.assert_array_equal(h, np.ones_like(h))
        np.testing.assert_allclose(abs(d), 1, atol=2e-16)
        self.assertTrue(np.all((s > 0) & (s <= 1)))
        self.assertEqual(s[8,8], 1)

    def test_uniform_phase_sign(self):
        h, _, _ = operators(16, 128e-6, 1e-3, 400, np.full((16,16), -.005))
        expected = np.exp(.5j*2*np.pi/1550e-9*(-.005)*1e-3/400)
        np.testing.assert_allclose(h, expected, rtol=1e-15)

    def test_validation(self):
        for n, steps in ((True,10),(321,10),(16,True),(16,1001)):
            with self.assertRaises(ValueError):
                operators(n,128e-6,1e-3,steps,np.zeros((16,16)))
        for dn in (np.zeros((15,15)),np.ones((16,16))*.02,
                   np.ones((16,16))*np.nan,np.ones((16,16))*1j):
            with self.assertRaises(ValueError):
                operators(16,128e-6,1e-3,400,dn)

    def test_field_validation(self):
        for a in (np.zeros((16,16)),np.ones((15,15)),np.full((16,16),np.inf)):
            with self.assertRaises(ValueError):
                validate_field(a,16)
        self.assertEqual(validate_field(np.ones((16,16)),16).shape,(16,16))
