import importlib.util
from pathlib import Path
import unittest
from silice.gpu_bpm import cuda_propagate

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gpu_pilot_guard',ROOT/'scripts/run_glass_gpu001.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class GuardTests(unittest.TestCase):
    def test_resource_floor_and_budget(self):
        s=dict(ram_gib=5,vram_gib=2,temperature_c=35)
        self.assertFalse(module.unsafe(s,reserve=1))
        self.assertTrue(module.unsafe({**s,'ram_gib':4.99},reserve=1))
        self.assertTrue(module.unsafe({**s,'ram_gib':3.99}))

    def test_limits(self):
        s=dict(ram_gib=8,vram_gib=18,temperature_c=80)
        self.assertFalse(module.unsafe(s))
        self.assertTrue(module.unsafe({**s,'vram_gib':18.01}))
        self.assertTrue(module.unsafe({**s,'temperature_c':81}))

    def test_missing_telemetry_does_not_pass(self):
        with self.assertRaises(KeyError): module.unsafe({})

    def test_no_cpu_fallback(self):
        class Tensor:
            class device:
                type='cpu'
        with self.assertRaises(ValueError):
            cuda_propagate(None,*[Tensor()]*4,steps=1,dx_m=1,deadline=0)
