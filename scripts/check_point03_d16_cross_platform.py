"""Limited real-input Windows reference: first 1024 steps only."""
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys
import time
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import psutil
import run_point03_d16_time as base


def main():
    out = base.ROOT/'resultados/codex/point03_d16_cross_platform_20261008'
    assert not out.exists()
    out.mkdir()
    start = time.monotonic()
    assert psutil.virtual_memory().available > 6*1024**3
    transfer = base.read(base.ROOT/'resultados/codex/point03_d16_cloud_package_retry_20261008/transfer_manifest.json')
    source = {row['path']: row['sha256'] for row in transfer['files']}
    for name, digest in source.items():
        assert base.sha(base.ROOT/name) == digest
    for name in ('scripts/check_point03_d16_cross_platform.py', 'Docs/POINT-03-D16-CROSS-PLATFORM-CONTRACT.md'):
        source[name] = base.sha(base.ROOT/name)
    base.write(out/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
               source_sha256=source, purpose='Real-input first1024steps only; full2mm trial is remote and is not duplicated'))
    digest = base.sha(out/'manifest.json')
    records = {}
    for case in ('P6_32768', 'R5_32768'):
        assert psutil.virtual_memory().available > 6*1024**3
        folder = out/case
        folder.mkdir()
        prefix = folder/'part001'
        command = [sys.executable, str(base.ROOT/'scripts/run_point03_d16_time.py'), '--worker',
                   '--manifest', str(out/'manifest.json'), '--manifest-sha', digest,
                   '--case', case, '--index', '1', '--prefix', str(prefix)]
        with Path(str(prefix)+'.log').open('xb') as log:
            child = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=370)
        cp = base.read(Path(str(prefix)+'.json'))
        assert child.returncode == 0 and cp['status'] == 'completed' and cp['steps_done'] == 1024
        assert base.sha(out/cp['field_path']) == cp['field_sha256']
        records[case] = dict(report=Path(str(prefix)+'.json').relative_to(out).as_posix(),
                             report_sha256=base.sha(Path(str(prefix)+'.json')), physical_power=cp['physical_power'],
                             elapsed_s=cp['elapsed_s'])
        print({'case': case, 'limited_reference_completed': True, 'elapsed_s': cp['elapsed_s']}, flush=True)
    assert time.monotonic()-start <= 900
    base.write(out/'report.json', dict(local_reference_complete=True, remote_comparison_performed=False,
               full_optical_experiment=False, point03_closed=False, distance_m=.002*1024/32768,
               records=records, elapsed_s=time.monotonic()-start))


if __name__ == '__main__':
    main()
