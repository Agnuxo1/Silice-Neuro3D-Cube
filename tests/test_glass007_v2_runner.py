import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "glass007_v2_runner", Path(__file__).resolve().parents[1]/"scripts/run_glass007_v2.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class RunnerReportTests(unittest.TestCase):
    def test_budget_backend_does_not_collide_with_report_backend(self):
        def fake_propagate(field, dn, grid, **kwargs):
            return field, dict(input_power=1.0, output_power=1.0,
                               material_removed=0.0, boundary_removed=0.0,
                               balance_relative=0.0, backend="scalar_paraxial_cpu_ssfm",
                               steps=kwargs["steps"], dx_m=grid.dx_m,
                               dz_m=kwargs["length_m"]/kwargs["steps"])
        for name in ("vacuum", "tracks32_equal_integral"):
            with self.subTest(name=name), patch.object(RUNNER, "hashes", return_value={}), \
                 patch.object(RUNNER.psutil, "virtual_memory", return_value=SimpleNamespace(available=2*1024**3)), \
                 patch.object(RUNNER, "propagate", side_effect=fake_propagate):
                result = RUNNER.run_case(name)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["backend"], "scalar_paraxial_cpu_ssfm_cell_average")
            self.assertIsInstance(result["profile_gate"], bool)
            json.dumps(result, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
