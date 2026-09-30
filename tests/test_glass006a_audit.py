import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/audit_glass006a.py"
SPEC = importlib.util.spec_from_file_location("glass006a_audit", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class RadiusSamplingTests(unittest.TestCase):
    def test_aligned_core_retains_radius(self):
        for count, extent in AUDIT.CONFIGS.values():
            self.assertAlmostEqual(AUDIT.effective_radius(6, count, extent), 6)

    def test_ten_micron_core_drift_is_explicit(self):
        values = [AUDIT.effective_radius(10, *cfg) for cfg in AUDIT.CONFIGS.values()]
        for value, expected in zip(values, [9.9, 9.9375, 10]):
            self.assertAlmostEqual(value, expected)


if __name__ == "__main__":
    unittest.main()
