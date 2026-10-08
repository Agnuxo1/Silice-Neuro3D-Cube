"""Continue only 16..64 with unchanged numerical worker and original wall budget."""
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
import psutil
from scipy.sparse import load_npz
import run_point03_d16_time as base
from run_point03_d16_time import ROOT, T, read, sha, write, matrices, guard


def main():
    original = ROOT/'resultados/codex/point03_d16_refine_20261008'
    out = ROOT/'resultados/codex/point03_d16_refine_recovery_20261008'
    assert not out.exists()
    out.mkdir()
    old = read(original/'execution.json')
    old_m = read(original/'manifest.json')
    prior = read(original/'partial15_integrity_audit.json')
    assert old['status'] == 'failed' and len(old['checkpoints']) == 15 and prior['partial_integrity_pass']
    assert prior['checkpoints_checked'] == 15 and not (original/'R5_65536/part016.json').exists()
    begin = datetime.fromisoformat(old['started_utc'])
    def elapsed():
        return (datetime.now(timezone.utc)-begin).total_seconds()
    sources = dict(old_m['source_sha256'])
    extras = [Path(__file__).resolve(), ROOT/'scripts/audit_point03_d16_recovery.py',
              ROOT/'Docs/POINT-03-D16-RECOVERY-CONTRACT.md', original/'execution.json',
              original/'manifest.json', original/'partial15_integrity_audit.json']
    for link in old['checkpoints']:
        path = original/link['path']
        assert sha(path) == link['sha256']
        cp = read(path)
        assert cp['status'] == 'completed' and sha(original/cp['field_path']) == cp['field_sha256']
        extras += [path, original/cp['field_path']]
    sources.update({p.relative_to(ROOT).as_posix(): sha(p) for p in extras})
    manifest = dict(old_m, source_sha256=sources, continuation_out_dir=original.relative_to(ROOT).as_posix(),
                    recovery_created_utc=datetime.now(timezone.utc).isoformat(), original_started_utc=old['started_utc'])
    write(out/'manifest.json', manifest)
    e = dict(status='running', started_utc=old['started_utc'], recovery_started_utc=datetime.now(timezone.utc).isoformat(),
             manifest_sha256=sha(out/'manifest.json'), original_wait_budget_exhausted=True, recovery_wait_s=0.,
             original_wait_s_recorded=old.get('wait_s'), retained_checkpoints=15,
             children=list(old['children']), checkpoints=list(old['checkpoints']), point03_closed=False)
    try:
        for path, digest in sources.items():
            assert sha(ROOT/path) == digest
        worker = ROOT/'scripts/run_point03_d16_refine.py'
        assert sha(worker) == 'def715416c077fa120755e671199491a3a454a8c369645e5c45e3b2d9103e2d3'
        previous = original/old['checkpoints'][-1]['path']
        for index in range(16, 65):
            assert elapsed() <= 22000
            reservation = dict(available_ram_bytes=psutil.virtual_memory().available,
                               free_disk_bytes=psutil.disk_usage(str(out)).free)
            assert reservation['available_ram_bytes'] > 4.5*1024**3 and reservation['free_disk_bytes'] > 2*1024**3
            for path, digest in sources.items():
                assert sha(ROOT/path) == digest
            prefix = original/'R5_65536'/f'part{index:03d}'
            assert not Path(str(prefix)+'.json').exists() and not Path(str(prefix)+'.npz').exists()
            command = [sys.executable, str(worker), '--worker', '--manifest', str(original/'manifest.json'),
                       '--manifest-sha', sha(original/'manifest.json'), '--case', 'R5_65536',
                       '--index', str(index), '--prefix', str(prefix), '--previous', str(previous)]
            before = time.monotonic()
            with Path(str(prefix)+'.log').open('xb') as log:
                child = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=370)
            cp = Path(str(prefix)+'.json')
            e['children'].append(dict(case='R5_65536', index=index, returncode=child.returncode,
                                     elapsed_s=time.monotonic()-before, reservation=reservation))
            assert child.returncode == 0 and read(cp)['status'] == 'completed'
            e['checkpoints'].append(dict(path=cp.relative_to(original).as_posix(), sha256=sha(cp)))
            previous = cp
            (out/'progress.json').write_text(__import__('json').dumps(dict(index=index, total=64, retained=15,
                                                   original_elapsed_s=elapsed())), encoding='utf-8')
            print(f'C2-R1 {index}/64 retained15 elapsed_original {elapsed():.1f}s', flush=True)
        M, B, initial, free = matrices()
        C = load_npz(ROOT/T/'core_q32.npz')[free, :][:, free]
        w = np.load(ROOT/T/'intensity_q32.npy', allow_pickle=False)[free]
        with np.load(ROOT/manifest['retained_P6_field'], allow_pickle=False) as data:
            p6 = data['field'].copy()
        last = read(previous)
        with np.load(original/last['field_path'], allow_pickle=False) as data:
            r5 = data['field'].copy()
        assessment = base.evaluate(M, C, w, p6, r5)
        assessment['powers']['R5_65536'] = assessment['powers'].pop('R5_32768')
        write(out/'assessment.json', assessment)
        assert elapsed() <= 22000
        guard(out)
        e.update(status='completed', temporal_precision_pass=assessment['temporal_precision_pass'],
                 assessment_sha256=sha(out/'assessment.json'))
    except Exception as error:
        e.update(status='failed', error_type=type(error).__name__, diagnostic=traceback.format_exc())
    e.update(elapsed_s=elapsed(), finished_utc=datetime.now(timezone.utc).isoformat())
    write(out/'execution.json', e)
    print({k: e.get(k) for k in ('status', 'temporal_precision_pass', 'elapsed_s', 'error_type')}, flush=True)
    return 0 if e.get('temporal_precision_pass') else 2 if e['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
