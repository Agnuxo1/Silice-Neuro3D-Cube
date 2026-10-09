"""Recalculate M2-R1 locally, preserving the separate remote audit unchanged."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
import scipy
import psutil
from audit_point03_d16_mid_recovery import audit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args().out.resolve()
    assert (np.__version__, scipy.__version__, psutil.__version__) == ('2.2.6', '1.15.1', '6.1.1')
    remote_path = out/'integrity_audit.json'
    remote_bytes = remote_path.read_bytes()
    remote = json.loads(remote_bytes)
    result = audit(out)
    assert result['integrity_pass'] == remote['integrity_pass']
    assert result['temporal_precision_pass'] == remote['temporal_precision_pass']
    assert result['checkpoints_checked'] == remote['checkpoints_checked'] == 96
    assert abs(result['relative_field_difference']-remote['relative_field_difference']) <= 1e-12
    for key in ('power_differences', 'PSD_observable_bounds'):
        for detector in ('field', 'intensity'):
            assert abs(result[key][detector]-remote[key][detector]) <= 1e-12
    result.update(local_recalculation=True, remote_audit_preserved=True,
                  remote_audit_sha256=hashlib.sha256(remote_bytes).hexdigest(),
                  local_created_utc=datetime.now(timezone.utc).isoformat(),
                  python=sys.version, numpy=np.__version__, scipy=scipy.__version__, psutil=psutil.__version__,
                  wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    assert remote_path.read_bytes() == remote_bytes
    with (out/'local_integrity_audit.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result))
