import unittest
import numpy as np
from silice.gpu_refinement import FineGrid,fine_operators
from silice.gpu_bpm import operators
from silice.coverage import CellGrid
from silice.bpm import Grid


class FineGridTests(unittest.TestCase):
    def test_old_limits_unchanged(self):
        for grid in (CellGrid,Grid):
            with self.assertRaises(ValueError): grid(512,128e-6)
        with self.assertRaises(ValueError): operators(512,128e-6,1e-3,400,np.zeros((512,512)))

    def test_exact_old_operators(self):
        g=FineGrid(64); dn=np.full((64,64),-.005)
        for old,new in zip(operators(64,g.width_m,1e-3,400,dn),fine_operators(g,dn,400)):
            np.testing.assert_array_equal(old,new)

    def test_bounds(self):
        for n in (True,63,641):
            with self.assertRaises(ValueError): FineGrid(n)
        for width in (0,float('nan')):
            with self.assertRaises(ValueError): FineGrid(512,width)
        g=FineGrid(512)
        self.assertEqual(g.coordinates()[0].shape,(512,512))
        self.assertAlmostEqual(g.dx_m,.25e-6)
