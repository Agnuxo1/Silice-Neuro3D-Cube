import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v2_gate",ROOT/"scripts/run_glass003_v2.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


class ResearchGateTests(unittest.TestCase):
    def test_absolute_and_relative_required(self):
        self.assertFalse(mod.convergence_gate(0.001,0.0015)["gate"])
        self.assertFalse(mod.convergence_gate(0.7,0.71)["gate"])
        self.assertTrue(mod.convergence_gate(0.01,0.0105)["gate"])

    def test_no_trivial_zero_certification(self):
        self.assertFalse(mod.convergence_gate(0,0)["gate"])
        self.assertFalse(mod.convergence_gate(1e-8,1e-8)["gate"])


if __name__=="__main__":unittest.main()
