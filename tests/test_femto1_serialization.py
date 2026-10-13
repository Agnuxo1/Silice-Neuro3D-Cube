import json
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'/'femto1'))
from compile_v2 import native

class ScalarSerialization(unittest.TestCase):
    def test_numpy_scalars_keep_values_and_types(self):
        x={'class':np.int64(3),'coordinate':[np.float64(1e-6)],'passed':np.bool_(False)}
        y=json.loads(json.dumps(native(x),allow_nan=False))
        self.assertEqual(y,{'class':3,'coordinate':[1e-6],'passed':False})

if __name__=='__main__':unittest.main()
