import math
import unittest

import numpy as np
from silice.bpm import Grid, gaussian, index_profile, metrics, power, propagate


class BPMTests(unittest.TestCase):
    def setUp(self):
        self.g = Grid(96, 96e-6)
        self.a = gaussian(self.g, 6e-6)
        self.dn = np.zeros_like(self.a.real)

    def test_input_unit_power(self):
        self.assertAlmostEqual(power(self.a, self.g), 1.0, places=13)

    def test_gaussian_diffraction_analytic(self):
        # Infinite-domain analytic oracle needs a box wide enough for the
        # diffracted beam. The initial 96 um box wrapped at z=0.5 mm.
        grid = Grid(192, 192e-6)
        initial = gaussian(grid, 6e-6)
        length = 0.5e-3
        b, budget = propagate(initial, np.zeros((192,192)), grid, length_m=length,
                              steps=50, sponge=False)
        zr = math.pi*1.444*(6e-6)**2/1550e-9
        expected = 6e-6*math.sqrt(1+(length/zr)**2)/math.sqrt(2)
        got = metrics(b, grid, 6e-6)["rms_radius_m"]
        self.assertLess(abs(got/expected-1), 1e-5)
        self.assertLess(budget["balance_relative"], 1e-10)

    def test_uniform_index_phase_not_intensity_only(self):
        b, _ = propagate(self.a, self.dn, self.g, steps=50, sponge=False)
        c, _ = propagate(self.a, self.dn+1e-4, self.g, steps=50, sponge=False)
        expected = b*np.exp(1j*2*math.pi/1550e-9*1e-4*2e-3)
        self.assertLess(np.linalg.norm(c-expected)/np.linalg.norm(b), 1e-10)

    def test_loss_power_not_amplitude(self):
        b, budget = propagate(self.a, self.dn, self.g, length_m=1e-3,
                              steps=20, sponge=False, material_loss_db_per_m=1000)
        self.assertAlmostEqual(power(b,self.g),10**(-0.1),places=12)
        self.assertLess(budget["balance_relative"],1e-10)

    def test_sponge_budget_not_material(self):
        _, budget = propagate(self.a, self.dn, self.g, length_m=2e-3, steps=80)
        self.assertGreater(budget["boundary_removed"], 0)
        self.assertEqual(budget["material_removed"],0)
        self.assertLess(budget["balance_relative"],1e-10)

    def test_superposition(self):
        dn = index_profile(self.g,6e-6,6e-6,-0.001)
        x,y = self.g.coordinates()
        a2 = self.a*np.exp(1j*x/5e-6)
        args = dict(steps=40,length_m=0.2e-3)
        b1,_=propagate(self.a,dn,self.g,**args)
        b2,_=propagate(a2,dn,self.g,**args)
        both,_=propagate(self.a+0.3j*a2,dn,self.g,**args)
        self.assertLess(np.linalg.norm(both-b1-0.3j*b2),1e-8)

    def test_profile_core_untouched_and_outside_untouched(self):
        p=index_profile(self.g,6e-6,6e-6,-0.001)
        self.assertEqual(p[48,48],0)
        self.assertEqual(p[48,57],-0.001)
        self.assertEqual(p[48,70],0)

    def test_invalid_grid(self):
        for n,w in [(512,96e-6),(True,96e-6),(64,float('nan')),(64,-1)]:
            with self.subTest(n=n,w=w),self.assertRaises(ValueError): Grid(n,w)

    def test_invalid_profile(self):
        for args in [(6e-6,-1,-0.001),(50e-6,6e-6,-0.001),(6e-6,6e-6,float('nan'))]:
            with self.subTest(args=args),self.assertRaises(ValueError): index_profile(self.g,*args)

    def test_invalid_propagation(self):
        for kw in [dict(steps=1001),dict(steps=True),dict(length_m=0),
                   dict(wavelength_m=float('nan')),dict(material_loss_db_per_m=-1)]:
            with self.subTest(kw=kw),self.assertRaises(ValueError): propagate(self.a,self.dn,self.g,**kw)
        with self.assertRaises(ValueError): propagate(self.a,self.dn+0.1,self.g)
        with self.assertRaises(ValueError): propagate(self.a,self.dn+1j,self.g)
        with self.assertRaises(ValueError): propagate(self.a[:3],self.dn,self.g)
        with self.assertRaises(ValueError): propagate(self.a*0,self.dn,self.g)

    def test_deadline(self):
        with self.assertRaises(TimeoutError): propagate(self.a,self.dn,self.g,deadline=0)


if __name__ == "__main__": unittest.main()
