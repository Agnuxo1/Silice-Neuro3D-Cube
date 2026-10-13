"""FEMTO-1 physical/protocol invariants on synthetic inputs only."""
import importlib.util
import sys
import unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]/'scripts'/'femto1'
sys.path.insert(0,str(HERE))
from common import optical_weights,tree,from_ratios,realization,fit_readout,kappa

class Femto1Invariants(unittest.TestCase):
    def test_single_global_scale_preserves_decisions_and_power(self):
        rng=np.random.default_rng(8);scores=rng.normal(size=(4,16));x=rng.uniform(size=(100,16))
        w,_=optical_weights(scores)
        np.testing.assert_array_equal((x@scores.T).argmax(1),(x@w.T).argmax(1))
        self.assertTrue(np.all(w>=0));self.assertLessEqual(w.sum(0).max(),1+1e-15)

    def test_prototypes_need_common_column_shift_for_three_leaf_tree(self):
        rng=np.random.default_rng(9);proto=rng.uniform(.1,1,(4,16));proto/=np.linalg.norm(proto,axis=1)[:,None]
        with self.assertRaises(ValueError):tree(proto*.1)
        w,_=optical_weights(proto);order,r=tree(w)
        np.testing.assert_allclose(from_ratios(order,r),w,atol=1e-15)
        np.testing.assert_allclose(realization(w,0,rng),w,atol=1e-15)

    def test_zero_columns_and_equal_scores_are_handled(self):
        w=np.zeros((4,16));w[0,0]=.3;w[1,0]=.2;w[2,0]=.1
        o,r=tree(w);np.testing.assert_allclose(from_ratios(o,r),w,atol=1e-15)

    def test_positive_readout_is_exactly_eight_parameters(self):
        rng=np.random.default_rng(11);labels=np.repeat(np.arange(4),100)
        power=np.eye(4)[labels]+rng.normal(0,.03,(400,4))
        gains,offset,ok=fit_readout(power,labels)
        self.assertEqual(gains.size+offset.size,8);self.assertTrue(np.all(gains>0));self.assertTrue(ok)
        self.assertGreater(np.mean((power*gains+offset).argmax(1)==labels),.99)

    def test_kappa_refuses_extrapolation(self):
        self.assertAlmostEqual(kappa(14e-6),471.6394183216887)
        with self.assertRaises(ValueError):kappa(13e-6)

if __name__=='__main__':unittest.main()
