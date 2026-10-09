"""Resume only absent M2 Radau chunks with unchanged worker and global budget."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys
import time
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
import psutil
import scipy
from scipy.sparse import load_npz
import run_point03_d16_mid_refined_time as base

ROOT = base.ROOT
ORIGINAL = ROOT/'resultados/codex/point03_d16_mid_refined_time_20261008'
PARTIAL = 'partial83_integrity_audit_20261009.json'


def prerequisites(original=ORIGINAL):
    old = base.read(original/'execution.json')
    manifest = base.read(original/'manifest.json')
    partial = base.read(original/PARTIAL)
    assert old['status'] == 'failed' and old['error_type'] == 'AssertionError'
    assert 'time.monotonic()-wait_start <= 900' in old['diagnostic']
    assert partial['partial_integrity_pass'] and partial['checkpoints_checked'] == 83
    assert len(old['children']) == 83 and partial['cases']['P6_32768']['checkpoints_checked'] == 32
    assert partial['cases']['R5_65536']['checkpoints_checked'] == 51
    assert base.sha(original/'manifest.json') == old['manifest_sha256'] == partial['original_manifest_sha256']
    assert np.__version__ == '2.2.6' and scipy.__version__ == '1.15.1' and psutil.__version__ == '6.1.1'
    for path, digest in manifest['source_sha256'].items():
        assert base.sha(ROOT/path) == digest
    for case, record in partial['cases'].items():
        for cp in record['checkpoints']:
            assert base.sha(original/cp['path']) == cp['sha256']
            assert base.sha(original/cp['field_path']) == cp['field_sha256']
    return old, manifest, partial


def allowed(elapsed_s, ram_bytes, disk_bytes, prefix):
    assert 0 <= elapsed_s <= 22000
    assert ram_bytes > 6*1024**3 and disk_bytes > 2*1024**3
    assert not any(Path(str(prefix)+suffix).exists() for suffix in ('.json', '.npz', '.log'))


def main(out):
    assert out.is_relative_to(ROOT/'resultados/codex') and not out.exists()
    old, original_manifest, partial = prerequisites()
    begin = datetime.fromisoformat(old['started_utc'])

    def elapsed():
        return (datetime.now(timezone.utc)-begin).total_seconds()

    assert elapsed() <= 22000
    control = ROOT/'resultados/codex/point03_d16_mid_recovery_controls_20261009.json'
    controls = base.read(control)
    assert controls['controls_pass'] and controls['worker_sha256'] == base.sha(Path(__file__))
    worker = ROOT/'scripts/run_point03_d16_mid_refined_time.py'
    assert base.sha(worker) == 'bd47274d4526c59f079ae399f086e7bd212c0b917d7b082cf46862a7e3a9ef93'
    out.mkdir()
    sources = dict(original_manifest['source_sha256'])
    extra = [Path(__file__), ROOT/'scripts/audit_point03_d16_mid_recovery.py',
             ROOT/'scripts/check_point03_d16_mid_recovery.py',
             ROOT/'Docs/POINT-03-D16-M2-RECOVERY-CONTRACT.md', control,
             ORIGINAL/'execution.json', ORIGINAL/'manifest.json', ORIGINAL/PARTIAL]
    for record in partial['cases'].values():
        for cp in record['checkpoints']:
            extra.extend([ORIGINAL/cp['path'], ORIGINAL/cp['field_path']])
    sources.update({p.relative_to(ROOT).as_posix(): base.sha(p) for p in extra})
    manifest = dict(original_manifest, source_sha256=sources,
                    continuation_out_dir=ORIGINAL.relative_to(ROOT).as_posix(),
                    recovery_created_utc=datetime.now(timezone.utc).isoformat(),
                    original_started_utc=old['started_utc'], retained_checkpoints=83,
                    recovery_reservation_GiB=6, recovery_wait_budget_s=0,
                    original_execution_sha256=base.sha(ORIGINAL/'execution.json'))
    base.write(out/'manifest.json', manifest)
    e = dict(status='running', started_utc=old['started_utc'],
             recovery_started_utc=datetime.now(timezone.utc).isoformat(),
             manifest_sha256=base.sha(out/'manifest.json'), original_wait_budget_exhausted=True,
             recovery_wait_s=0., original_wait_s_recorded=old.get('wait_s'),
             retained_checkpoints=83, children=list(old['children']),
             solutions={case: dict(checkpoints=[dict(path=c['path'], sha256=c['sha256'])
                        for c in record['checkpoints']]) for case, record in partial['cases'].items()},
             point03_closed=False)
    try:
        previous = ORIGINAL/'R5_65536/part051.json'
        for index in range(52, 65):
            reservation = dict(available_ram_bytes=psutil.virtual_memory().available,
                               free_disk_bytes=psutil.disk_usage(str(out)).free)
            prefix = ORIGINAL/'R5_65536'/f'part{index:03d}'
            allowed(elapsed(), reservation['available_ram_bytes'], reservation['free_disk_bytes'], prefix)
            for path, digest in sources.items():
                assert base.sha(ROOT/path) == digest
            command = [sys.executable, str(worker), '--worker', '--manifest', str(ORIGINAL/'manifest.json'),
                       '--manifest-sha', old['manifest_sha256'], '--case', 'R5_65536', '--index', str(index),
                       '--prefix', str(prefix), '--previous', str(previous)]
            before = time.monotonic()
            with Path(str(prefix)+'.log').open('xb') as log:
                child = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=370)
            cp = Path(str(prefix)+'.json')
            e['children'].append(dict(case='R5_65536', index=index, returncode=child.returncode,
                                     elapsed_s=time.monotonic()-before, reservation=reservation))
            assert child.returncode == 0 and base.read(cp)['status'] == 'completed'
            e['solutions']['R5_65536']['checkpoints'].append(dict(path=cp.relative_to(ORIGINAL).as_posix(), sha256=base.sha(cp)))
            previous = cp
            (out/'progress.json').write_text(__import__('json').dumps(dict(index=index, total=64,
                         retained=83, original_elapsed_s=elapsed())), encoding='utf-8')
            print(f'M2-R1 Radau {index}/64; elapsed_original={elapsed():.1f}s', flush=True)
        M, B, initial, free = base.matrices()
        C = load_npz(ROOT/base.T/'core_q32.npz')[free, :][:, free]
        w = np.load(ROOT/base.T/'intensity_q32.npy', allow_pickle=False)[free]
        final = []
        for case in ('P6_32768', 'R5_65536'):
            cp = base.read(ORIGINAL/e['solutions'][case]['checkpoints'][-1]['path'])
            with np.load(ORIGINAL/cp['field_path'], allow_pickle=False) as data:
                final.append(data['field'].copy())
        assessment = base.evaluate(M, C, w, *final)
        base.write(out/'assessment.json', assessment)
        assert elapsed() <= 22000
        base.guard(out)
        e.update(status='completed', temporal_precision_pass=assessment['temporal_precision_pass'],
                 assessment_sha256=base.sha(out/'assessment.json'))
    except Exception as error:
        e.update(status='failed', error_type=type(error).__name__)
    e.update(elapsed_s=elapsed(), finished_utc=datetime.now(timezone.utc).isoformat())
    base.write(out/'execution.json', e)
    print({k: e.get(k) for k in ('status', 'temporal_precision_pass', 'elapsed_s', 'error_type')}, flush=True)
    return 0 if e.get('temporal_precision_pass') else 2 if e['status'] == 'completed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--out', type=Path, required=True)
    raise SystemExit(main(parser.parse_args().out.resolve()))
