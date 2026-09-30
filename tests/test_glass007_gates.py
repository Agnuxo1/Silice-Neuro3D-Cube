import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from run_glass007 import comparison
from complete_glass007 import validate_parent


class DiscreteGateTests(unittest.TestCase):
    def test_both_error_thresholds(self):
        self.assertFalse(comparison(.01,.012)["gate"])
        self.assertFalse(comparison(.8,.81)["gate"])
        self.assertTrue(comparison(.30,.303)["gate"])

    def test_parent_invalid(self):
        for p in [{},{"status":"completed","gpu_used":False},
                  {"status":"timeout_partial_retained","gpu_used":True}]:
            with self.subTest(p=p),self.assertRaises(ValueError):validate_parent(p)


if __name__=="__main__":unittest.main()
