import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'/'femto1'))
from geometry import sbend,route,coupler_design,coupler_paths,path_length

class GeometryControls(unittest.TestCase):
    def test_s_bend_matches_two_arc_formula_and_endpoint(self):
        radius=.025;h=.0005
        p=sbend([0,0,0],[h,0],radius)
        expected_x=2*np.sqrt(radius*h-h*h/4)
        self.assertAlmostEqual(p[-1,0],expected_x,places=13)
        self.assertAlmostEqual(p[-1,1],h,places=13)
        self.assertLessEqual(np.linalg.norm(np.diff(p,axis=0),axis=1).max(),10e-6*(1+1e-9))
        theta=np.arccos(1-h/(2*radius))
        self.assertLess(abs(path_length(p)-2*radius*theta),1e-9)

    def test_impossible_route_retained_as_failure(self):
        p,ok=route([0,0,0],[.001,.001,0])
        self.assertFalse(ok);self.assertGreater(p[-1,0],.001)

    def test_coupler_parallel_geometry_matches_gap_and_length(self):
        c=coupler_design(.5);lo,up=coupler_paths([.01,.002,.001],c)
        self.assertTrue(c['length_nonnegative'])
        self.assertAlmostEqual(np.min(up[:,1])-np.max(lo[:,1]),c['gap_m'],places=13)
        self.assertAlmostEqual(np.sin(c['kappa_per_m']*c['length_m']+c['access_angle_rad'])**2,.5,places=13)

    def test_access_floor_cannot_silently_realize_zero_split(self):
        self.assertFalse(coupler_design(0)['length_nonnegative'])

if __name__=='__main__':unittest.main()
