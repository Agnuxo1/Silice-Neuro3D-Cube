import math
import unittest
import numpy as np
from silice.bpm import Grid,index_profile
from silice.tracks import track_centres,discrete_profile


class TrackTests(unittest.TestCase):
    def test_geometry_counts(self):
        c=track_centres(per_ring=32)
        self.assertEqual(len(c),96)
        for x,y in c:
            self.assertGreaterEqual(math.hypot(x,y)-1.25e-6,6e-6-1e-20)
            self.assertLessEqual(math.hypot(x,y)+1.25e-6,12e-6+1e-20)

    def test_wedge_really_omits_centres(self):
        c=track_centres(per_ring=32,missing_wedge_rad=math.pi/6)
        self.assertLess(len(c),96)
        self.assertTrue(all(abs(math.atan2(y,x))>=math.pi/12-1e-15 for x,y in c))

    def test_overlap_not_summed(self):
        p,m=discrete_profile(Grid(256,128e-6),per_ring=64)
        self.assertEqual(float(p.min()),-0.003)
        self.assertTrue(m['core_untouched']);self.assertTrue(m['outside_untouched'])

    def test_equal_integral(self):
        g=Grid(256,128e-6)
        p,m=discrete_profile(g,match_integral=True)
        ref=index_profile(g,6e-6,6e-6,-0.003)
        self.assertAlmostEqual(float(np.abs(p).sum()/np.abs(ref).sum()),1,places=13)
        self.assertLessEqual(abs(m['peak_delta_n']),0.01)

    def test_invalid_tracks(self):
        for kw in [dict(per_ring=1),dict(per_ring=True),dict(track_radius_m=0),
            dict(thickness_m=1e-6),dict(missing_wedge_rad=2*math.pi),
            dict(missing_wedge_rad=float('nan'))]:
            with self.subTest(kw=kw),self.assertRaises(ValueError):track_centres(**kw)
        for dn in [0,.001,-.1,float('inf')]:
            with self.subTest(dn=dn),self.assertRaises(ValueError):discrete_profile(Grid(),delta_n=dn)


if __name__=="__main__":unittest.main()
