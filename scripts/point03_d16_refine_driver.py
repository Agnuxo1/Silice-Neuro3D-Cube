"""Template for only a new R5_65536 trajectory, retaining immutable P6_32768."""
import argparse
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
import scipy
from point03_fem_radau import Radau5
import run_point03_d16_time as base
from run_point03_d16_time import ROOT, G, T, D, Q, K_SHA, read, sha, write, guard, matrices

# WORKER_INSERTION


def run(out):
    assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    out.mkdir()
    start = time.monotonic()
    e = dict(status='running', started_utc=datetime.now(timezone.utc).isoformat(),
             children=[], checkpoints=[], point03_closed=False)
    try:
        old = ROOT/'resultados/codex/point03_d16_cloud_recovery_20261008/resultados/codex/cloud_d16_c1_20261008'
        prior = read(old/'local_integrity_audit.json')
        assert prior['integrity_pass'] and not prior['temporal_precision_pass']
        ref_report = old/'P6_32768/part032.json'
        assert sha(ref_report) == 'a6b060faaff0d02ea6ee6cb2b7b0331d3962d5815bd97548af95e6d4830877a3'
        reference = read(ref_report)
        ref_field = old/reference['field_path']
        assert reference['status'] == 'completed' and sha(ref_field) == reference['field_sha256']
        original = read(old/'manifest.json')
        source = dict(original['source_sha256'])
        for name, digest in source.items():
            assert sha(ROOT/name) == digest
        extras = [Path(__file__).resolve(), ROOT/'scripts/audit_point03_d16_refine.py',
                  ROOT/'Docs/POINT-03-D16-REFINE-CONTRACT.md', old/'local_integrity_audit.json', ref_report, ref_field]
        source.update({p.relative_to(ROOT).as_posix(): sha(p) for p in extras})
        m = dict(created_utc=datetime.now(timezone.utc).isoformat(), source_sha256=source,
                 numerical_threads=1, steps=65536, chunk_steps=1024, method='R5', mesh='coarse',
                 python=sys.version, numpy=np.__version__, scipy=scipy.__version__, psutil=psutil.__version__,
                 retained_P6_field=ref_field.relative_to(ROOT).as_posix(), retained_P6_field_sha256=sha(ref_field),
                 retained_P6_report=ref_report.relative_to(ROOT).as_posix(), retained_P6_report_sha256=sha(ref_report))
        write(out/'manifest.json', m)
        e['manifest_sha256'] = sha(out/'manifest.json')
        folder = out/'R5_65536'
        folder.mkdir()
        previous = None
        for index in range(1, 65):
            waiting = time.monotonic()
            while True:
                reservation = dict(available_ram_bytes=psutil.virtual_memory().available,
                                   free_disk_bytes=psutil.disk_usage(str(out)).free)
                assert time.monotonic()-start <= 22000 and e.get('wait_s', 0.)+time.monotonic()-waiting <= 900
                if reservation['available_ram_bytes'] > 6*1024**3 and reservation['free_disk_bytes'] > 2*1024**3:
                    break
                remaining = 900-e.get('wait_s', 0.)-(time.monotonic()-waiting)
                assert remaining > 0
                time.sleep(min(2., remaining))
            e['wait_s'] = e.get('wait_s', 0.)+time.monotonic()-waiting
            prefix = folder/f'part{index:03d}'
            command = [sys.executable, str(Path(__file__).resolve()), '--worker', '--manifest', str(out/'manifest.json'),
                       '--manifest-sha', e['manifest_sha256'], '--case', 'R5_65536', '--index', str(index), '--prefix', str(prefix)]
            if previous:
                command += ['--previous', str(previous)]
            before = time.monotonic()
            with Path(str(prefix)+'.log').open('xb') as log:
                child = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=370)
            cp = Path(str(prefix)+'.json')
            e['children'].append(dict(case='R5_65536', index=index, returncode=child.returncode,
                                     elapsed_s=time.monotonic()-before, reservation=reservation))
            assert child.returncode == 0 and read(cp)['status'] == 'completed'
            e['checkpoints'].append(dict(path=cp.relative_to(out).as_posix(), sha256=sha(cp)))
            previous = cp
            (out/'progress.json').write_text(__import__('json').dumps(dict(case='R5_65536', index=index, total=64,
                                            elapsed_s=time.monotonic()-start)), encoding='utf-8')
            print(f'D16-C2 R5_65536 {index}/64 elapsed {time.monotonic()-start:.1f}s', flush=True)
        M, B, initial, free = matrices()
        from scipy.sparse import load_npz
        C = load_npz(ROOT/T/'core_q32.npz')[free, :][:, free]
        w = np.load(ROOT/T/'intensity_q32.npy', allow_pickle=False)[free]
        with np.load(ref_field, allow_pickle=False) as data:
            a = data['field'].copy()
        terminal = read(previous)
        with np.load(out/terminal['field_path'], allow_pickle=False) as data:
            b = data['field'].copy()
        assessment = base.evaluate(M, C, w, a, b)
        assessment['powers']['R5_65536'] = assessment['powers'].pop('R5_32768')
        assessment['retained_P6_field_sha256'] = sha(ref_field)
        write(out/'assessment.json', assessment)
        assert time.monotonic()-start <= 22000
        guard(out)
        e.update(status='completed', temporal_precision_pass=assessment['temporal_precision_pass'],
                 assessment_sha256=sha(out/'assessment.json'))
    except Exception as error:
        e.update(status='failed', error_type=type(error).__name__, diagnostic=traceback.format_exc())
    e.update(elapsed_s=time.monotonic()-start, finished_utc=datetime.now(timezone.utc).isoformat())
    write(out/'execution.json', e)
    print({k: e.get(k) for k in ('status', 'temporal_precision_pass', 'elapsed_s', 'error_type')}, flush=True)
    return 0 if e.get('temporal_precision_pass') else 2 if e['status'] == 'completed' else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--out', type=Path)
    p.add_argument('--worker', action='store_true')
    p.add_argument('--manifest', type=Path)
    p.add_argument('--manifest-sha')
    p.add_argument('--case', choices=('R5_65536',))
    p.add_argument('--index', type=int)
    p.add_argument('--prefix', type=Path)
    p.add_argument('--previous', type=Path)
    args = p.parse_args()
    raise SystemExit(worker(args) if args.worker else run(args.out.resolve()))
