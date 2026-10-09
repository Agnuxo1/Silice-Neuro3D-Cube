"""CPU controls of fixed analytic markers and the C/F stride diagnosis."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import numpy as np
from point03_render_buffer_reference import expected, old_export_prediction, check_marker, SIZES, CASES


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(); rows = []
    for width, height in SIZES:
        for case in CASES:
            a = expected(case, width, height).astype(np.float32)
            assert check_marker(a, expected(case, width, height))['pass']
            old = old_export_prediction(a)
            assert not check_marker(old, expected(case, width, height))['pass']
            # The simulated export is a permutation, not a changed physical field.
            assert np.array_equal(np.sort(old.ravel()), np.sort(a.ravel()))
            for altered in (a[::-1], a[:, ::-1], a[..., [1, 0, 2, 3]]):
                if case == 'coordinates':
                    assert not check_marker(altered, expected(case, width, height))['pass']
            rows.append({'case': case, 'width': width, 'height': height,
                         'analytic_pass': True, 'old_stride_rejected': True})
    for case, w, h in [('unknown', 8, 5), ('constant', 8, 8)]:
        try: expected(case, w, h)
        except ValueError: pass
        else: raise AssertionError('invalid marker accepted')
    for actual in (np.zeros((5, 8, 3), np.float32),
                   np.zeros((5, 8, 4), np.float64),
                   np.full((5, 8, 4), np.nan, np.float32)):
        try: check_marker(actual, expected('constant', 8, 5))
        except ValueError: pass
        else: raise AssertionError('invalid readback accepted')
    result = {'created_utc': datetime.now(timezone.utc).isoformat(), 'pass': True,
              'marker_groups': rows, 'invalid_groups': 5, 'gpu_execution': False,
              'reads_prior_gpu_frames': False, 'new_t96_field': False,
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with args.output.open('x', encoding='utf-8') as f: json.dump(result, f, indent=2)
    print(json.dumps({'pass': True, 'marker_groups': len(rows), 'gpu_execution': False}))


if __name__ == '__main__': main()
