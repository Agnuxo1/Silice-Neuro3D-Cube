"""New, portable coarse-mesh temporal experiment with immutable Duffy16 K."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
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
from point03_fem_time import Pade6
from point03_fem_radau import Radau5

ROOT = Path(__file__).resolve().parents[1]
G = 'resultados/codex/point03_p5a_mesh_coarse_20261008'
T = 'resultados/codex/point03_p5b_detector_coarse_20261008'
D = 'resultados/codex/point03_p5b_damping_coarse_20261008'
Q = 'resultados/codex/point03_fem_duffy_coarse_retry_20261008'
K_SHA = '51a273ef6a14dbcc425e1d5f22820963c2c9bc219f26fa56447115b06acef981'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def guard(folder, minimum=3.):
    ram = psutil.virtual_memory().available
    disk = psutil.disk_usage(str(folder)).free
    assert ram > minimum*1024**3 and disk > 2*1024**3
    return dict(utc=datetime.now(timezone.utc).isoformat(), available_ram_bytes=ram, free_disk_bytes=disk)


def matrices():
    with np.load(ROOT/T/'gaussian_q16.npz', allow_pickle=False) as a:
        free, initial = a['free_dofs'].copy(), a['field'].copy()
    M = load_npz(ROOT/G/'mass.npz')[free, :][:, free].tocsc()
    K = load_npz(ROOT/Q/'stiffness_duffy16.npz')[free, :][:, free]
    C = load_npz(ROOT/G/'cladding_mass.npz')[free, :][:, free]
    damping = load_npz(ROOT/D/'damping_q12.npz')[free, :][:, free]
    k0 = 2*math.pi/1550e-9
    return M, -1j*K/(2*1.444*k0)-1j*k0*.003*C-damping, initial[free], free


def evaluate(M, C, w, a, b):
    powers = {label: dict(field=float(np.vdot(f, C@f).real), intensity=float(w@abs(f)**2))
              for label, f in (('P6_32768', a), ('R5_32768', b))}
    diff = a-b
    relative = math.sqrt(float(np.vdot(diff, M@diff).real)/float(np.vdot(b, M@b).real))
    errors, bounds = {}, {}
    for label in ('field', 'intensity'):
        square = float(np.vdot(diff, C@diff).real) if label == 'field' else float(w@abs(diff)**2)
        assert square >= -1e-20
        bounds[label] = sum(math.sqrt(p[label]) for p in powers.values())*math.sqrt(max(0., square))
        errors[label] = abs(powers['P6_32768'][label]-powers['R5_32768'][label])
    passed = relative <= 1e-4 and max(errors.values()) <= 1e-6 and max(bounds.values()) <= 1e-5
    return dict(powers=powers, relative_field_difference=relative, power_differences=errors,
                PSD_observable_bounds=bounds, temporal_precision_pass=passed, point03_closed=False)


def worker(args):
    start = time.monotonic()
    record = dict(status='failed', case=args.case, index=args.index,
                  started_utc=datetime.now(timezone.utc).isoformat(), previous_report_path=None,
                  previous_report_sha256=None)
    try:
        record['resource_start'] = guard(args.prefix.parent)
        manifest = read(args.manifest)
        assert sha(args.manifest) == args.manifest_sha
        for name, digest in manifest['source_sha256'].items():
            assert sha(ROOT/name) == digest
        M, B, initial, free = matrices()
        power = float(np.vdot(initial, M@initial).real)
        assert abs(power-1) <= 1e-12
        if args.previous:
            old = read(args.previous)
            assert old['status'] == 'completed' and old['case'] == args.case and old['index'] == args.index-1
            assert sha(old['field_path']) == old['field_sha256']
            with np.load(old['field_path'], allow_pickle=False) as a:
                initial = a['field'].copy()
            power = old['physical_power']
            record.update(previous_report_path=str(args.previous), previous_report_sha256=sha(args.previous))
        else:
            assert args.index == 1
        solver = (Pade6 if args.case == 'P6_32768' else Radau5)(M, B, .002/32768)
        value = solver.advance(initial, 1024)
        actual = float(np.vdot(value, M@value).real)
        assert np.isfinite(value).all() and 0 < actual <= power+1e-9
        record.update(status='completed', physical_power=actual, previous_power=power,
                      steps_done=args.index*1024, dt_m=.002/32768, resource_end=guard(args.prefix.parent))
    except Exception as error:
        record.update(error_type=type(error).__name__, diagnostic=traceback.format_exc())
    if 'value' in locals():
        target = Path(str(args.prefix)+'.npz')
        assert not target.exists()
        np.savez(target, field=value)
        record.update(field_path=str(target), field_sha256=sha(target))
    record['elapsed_s'] = time.monotonic()-start
    if record['elapsed_s'] > 360:
        record.update(status='failed', error_type='ChildBudgetExceeded')
    write(str(args.prefix)+'.json', record)
    return 0 if record['status'] == 'completed' else 1


def run(out):
    assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex')
    out.mkdir()
    start = time.monotonic()
    e = dict(status='running', started_utc=datetime.now(timezone.utc).isoformat(), children=[],
             solutions={}, point03_closed=False)
    try:
        for folder, report in ((G, 'report.json'), (T, 'report.json'), (D, 'report_recovered.json')):
            assert read(ROOT/folder/report)['controls_pass']
        quad = read(ROOT/Q/'report.json')
        assert quad['assembly_controls_pass'] and quad['pairs']['duffy16_vs_duffy24']['conservative_consistency_pass']
        assert sha(ROOT/Q/'stiffness_duffy16.npz') == K_SHA == quad['artifacts']['stiffness_duffy16.npz']
        for name in ('mass.npz', 'cladding_mass.npz'):
            assert sha(ROOT/G/name) == read(ROOT/G/'report.json')['hashes'][name]
        assert sha(ROOT/D/'damping_q12.npz') == read(ROOT/D/'report_recovered.json')['artifacts']['damping_q12.npz']
        source_files = [f'{G}/mass.npz', f'{G}/cladding_mass.npz', f'{Q}/stiffness_duffy16.npz',
                        f'{T}/gaussian_q16.npz', f'{T}/core_q32.npz', f'{T}/intensity_q32.npy', f'{D}/damping_q12.npz',
                        f'{G}/report.json', f'{T}/report.json', f'{D}/report_recovered.json', f'{Q}/report.json',
                        'scripts/run_point03_d16_time.py', 'scripts/audit_point03_d16_time.py',
                        'scripts/point03_fem_time.py', 'scripts/point03_fem_radau.py',
                        'Docs/POINT-03-D16-COARSE-TIME-CONTRACT.md']
        manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                        source_sha256={p: sha(ROOT/p) for p in source_files}, numerical_threads=1,
                        python=sys.version, numpy=np.__version__, steps=32768, chunk_steps=1024,
                        mesh='coarse', stiffness_sha256=K_SHA)
        write(out/'manifest.json', manifest)
        e['manifest_sha256'] = sha(out/'manifest.json')
        for case in ('P6_32768', 'R5_32768'):
            folder = out/case
            folder.mkdir()
            previous, chain = None, []
            for index in range(1, 33):
                wait_start = time.monotonic()
                while True:
                    reservation = dict(available_ram_bytes=psutil.virtual_memory().available,
                                       free_disk_bytes=psutil.disk_usage(str(out)).free)
                    assert time.monotonic()-start <= 22000
                    assert e.get('wait_s', 0.)+time.monotonic()-wait_start <= 900
                    if reservation['available_ram_bytes'] > 4.5*1024**3 and reservation['free_disk_bytes'] > 2*1024**3:
                        break
                    remaining = 900-e.get('wait_s', 0.)-(time.monotonic()-wait_start)
                    assert remaining > 0
                    time.sleep(min(2., remaining))
                e['wait_s'] = e.get('wait_s', 0.)+time.monotonic()-wait_start
                assert time.monotonic()-start <= 22000
                prefix = folder/f'part{index:03d}'
                command = [sys.executable, str(Path(__file__).resolve()), '--worker', '--manifest', str(out/'manifest.json'),
                           '--manifest-sha', e['manifest_sha256'], '--case', case, '--index', str(index), '--prefix', str(prefix)]
                if previous:
                    command += ['--previous', str(previous)]
                before = time.monotonic()
                with Path(str(prefix)+'.log').open('xb') as log:
                    child = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=370)
                cp = Path(str(prefix)+'.json')
                e['children'].append(dict(case=case, index=index, returncode=child.returncode,
                                         reservation=reservation, elapsed_s=time.monotonic()-before))
                assert child.returncode == 0 and read(cp)['status'] == 'completed'
                chain.append(dict(path=str(cp), sha256=sha(cp)))
                previous = cp
                (out/'progress.json').write_text(json.dumps(dict(case=case, index=index, total=32, elapsed_s=time.monotonic()-start)), encoding='utf-8')
                print(f'D16 {case} {index}/32', flush=True)
            e['solutions'][case] = dict(checkpoints=chain)
        M, B, initial, free = matrices()
        C = load_npz(ROOT/T/'core_q32.npz')[free, :][:, free]
        w = np.load(ROOT/T/'intensity_q32.npy', allow_pickle=False)[free]
        final = []
        for case in ('P6_32768', 'R5_32768'):
            cp = read(e['solutions'][case]['checkpoints'][-1]['path'])
            with np.load(cp['field_path'], allow_pickle=False) as data:
                final.append(data['field'].copy())
        assessment = evaluate(M, C, w, *final)
        write(out/'assessment.json', assessment)
        assert time.monotonic()-start <= 22000
        guard(out)
        e.update(status='completed', temporal_precision_pass=assessment['temporal_precision_pass'],
                 assessment_sha256=sha(out/'assessment.json'))
    except Exception as error:
        e.update(status='failed', error_type=type(error).__name__, diagnostic=traceback.format_exc())
    e.update(elapsed_s=time.monotonic()-start, finished_utc=datetime.now(timezone.utc).isoformat())
    write(out/'execution.json', e)
    print(json.dumps({k: e.get(k) for k in ('status', 'temporal_precision_pass', 'elapsed_s', 'error_type')}), flush=True)
    return 0 if e.get('temporal_precision_pass') else 2 if e['status'] == 'completed' else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--out', type=Path)
    p.add_argument('--worker', action='store_true')
    p.add_argument('--manifest', type=Path)
    p.add_argument('--manifest-sha')
    p.add_argument('--case', choices=('P6_32768', 'R5_32768'))
    p.add_argument('--index', type=int)
    p.add_argument('--prefix', type=Path)
    p.add_argument('--previous', type=Path)
    args = p.parse_args()
    raise SystemExit(worker(args) if args.worker else run(args.out.resolve()))
