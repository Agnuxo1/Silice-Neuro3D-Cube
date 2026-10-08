"""Sequential coarse FEM paths; never choose a method from its output."""
import argparse
from datetime import datetime, timezone
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
from scipy.sparse import load_npz
from run_point03_exponential import ROOT, sha, write
import run_point03_p4i as base
from audit_point03_p5c import audit


def assess(m, e):
    M, B, initial, free = base.matrices(m)
    det = Path(m['detector_folder'])
    C = load_npz(det / 'core_q32.npz')[free, :][:, free]
    w = np.load(det / 'intensity_q32.npy', allow_pickle=False)[free]
    fields = {}
    for label, solution in e['solutions'].items():
        cp = base.read(solution['checkpoints'][-1]['path'])
        assert sha(cp['field_path']) == cp['field_sha256']
        with np.load(cp['field_path'], allow_pickle=False) as data:
            fields[label] = data['field'].copy()
    powers = {label: dict(field=float(np.vdot(f, C @ f).real), intensity=float(w @ abs(f)**2)) for label, f in fields.items()}
    d = fields['P6_32768'] - fields['R5_32768']
    ref = fields['R5_32768']
    relative = math.sqrt(float(np.vdot(d, M @ d).real) / float(np.vdot(ref, M @ ref).real))
    bounds = {}
    changes = {}
    for method in ('field', 'intensity'):
        squared = float(np.vdot(d, C @ d).real) if method == 'field' else float(w @ abs(d)**2)
        assert squared >= -1e-20
        bounds[method] = sum(math.sqrt(p[method]) for p in powers.values()) * math.sqrt(max(0., squared))
        changes[method] = abs(powers['P6_32768'][method] - powers['R5_32768'][method])
    passed = relative <= 1e-4 and max(bounds.values()) <= 1e-5 and max(changes.values()) <= 1e-6
    return dict(created_utc=datetime.now(timezone.utc).isoformat(), temporal_precision_pass=passed, point03_closed=False,
                powers=powers, relative_field_difference=relative, PSD_observable_bounds=bounds, power_differences=changes)


def run(out):
    start = time.monotonic()
    assert not out.exists() and out.is_relative_to(ROOT / 'resultados/codex')
    prerequisite = ROOT / 'resultados/codex/point03_p4i2_gaussian_time_20261008/integrity_audit.json'
    prior = base.read(prerequisite)
    assert prior['integrity_pass'] and prior['temporal_precision_pass']
    out.mkdir()
    total = dict(status='running', started_utc=datetime.now(timezone.utc).isoformat(), meshes={}, point03_closed=False)
    try:
        for label, h in (('coarse', .546875), ('mid', .4375)):
            mesh_start = time.monotonic()
            folder = out / label
            folder.mkdir()
            geom = ROOT / f'resultados/codex/point03_p5a_mesh_{label}_20261008'
            det = ROOT / f'resultados/codex/point03_p5b_detector_{label}_20261008'
            damp = ROOT / f'resultados/codex/point03_p5b_damping_{label}_20261008'
            damp_report = damp / ('report_recovered.json' if label == 'coarse' else 'report.json')
            assert base.read(geom / 'report.json')['controls_pass'] and base.read(det / 'report.json')['controls_pass']
            assert base.read(damp_report)['controls_pass']
            sources = [Path(__file__).resolve(), ROOT / 'scripts/audit_point03_p5c.py', ROOT / 'Docs/POINT-03-P5C-COARSE-TIME-CONTRACT.md',
                       ROOT / 'scripts/run_point03_p4i.py', ROOT / 'scripts/point03_fem_time.py', ROOT / 'scripts/point03_fem_radau.py', prerequisite,
                       geom / 'report.json', geom / 'mass.npz', geom / 'stiffness.npz', geom / 'cladding_mass.npz', det / 'report.json',
                       det / 'gaussian_q16.npz', det / 'core_q32.npz', det / 'intensity_q32.npy', damp_report, damp / 'damping_q12.npz']
            m = dict(created_utc=datetime.now(timezone.utc).isoformat(), h_local_um=h, geometry_folder=str(geom), detector_folder=str(det),
                     damping_folder=str(damp), source_sha256={str(p): sha(p) for p in sources}, numerical_threads=1,
                     plan=[dict(id='P6_32768', method='P6', steps=32768), dict(id='R5_32768', method='R5', steps=32768)])
            M, B, initial, free = base.matrices(m)
            m['P_in'] = float(np.vdot(initial, M @ initial).real)
            assert abs(m['P_in'] - 1) <= 1e-12
            del M, B, initial, free
            write(folder / 'manifest.json', m)
            e = dict(status='running', started_utc=datetime.now(timezone.utc).isoformat(), manifest_sha256=sha(folder / 'manifest.json'),
                     children=[], solutions={}, point03_closed=False)
            for case in m['plan']:
                case_folder = folder / case['id']
                case_folder.mkdir()
                previous = None
                links = []
                for index in range(1, 129):
                    assert time.monotonic() - start <= 36000
                    base.guard(out)
                    prefix = case_folder / f'part{index:03d}'
                    command = [sys.executable, str(ROOT / 'scripts/run_point03_p4i.py'), '--worker', '--manifest', str(folder / 'manifest.json'),
                               '--manifest-sha', e['manifest_sha256'], '--case', case['id'], '--index', str(index), '--prefix', str(prefix)]
                    if previous:
                        command += ['--previous', str(previous)]
                    before = time.monotonic()
                    with Path(str(prefix) + '.log').open('xb') as log:
                        child = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=370)
                    cp = Path(str(prefix) + '.json')
                    e['children'].append(dict(case=case['id'], index=index, returncode=child.returncode, elapsed_s=time.monotonic() - before))
                    assert child.returncode == 0 and base.read(cp)['status'] == 'completed'
                    links.append(dict(path=str(cp), sha256=sha(cp)))
                    previous = cp
                    # Separate replaceable progress file; raw records stay exclusive.
                    (folder / 'progress.json').write_text(__import__('json').dumps(dict(mesh=label, case=case['id'], index=index, total=128,
                        elapsed_s=time.monotonic() - start, checkpoints=links), indent=2), encoding='utf-8')
                    print(f'P5C {label} {case["id"]} {index}/128 elapsed {time.monotonic()-start:.1f}s', flush=True)
                e['solutions'][case['id']] = dict(checkpoints=links)
            a = assess(m, e)
            write(folder / 'assessment.json', a)
            e.update(status='completed', temporal_precision_pass=a['temporal_precision_pass'], assessment_sha256=sha(folder / 'assessment.json'),
                     sources_unchanged=all(sha(p) == v for p, v in m['source_sha256'].items()), finished_utc=datetime.now(timezone.utc).isoformat(),
                     elapsed_s=time.monotonic()-mesh_start)
            write(folder / 'execution.json', e)
            independent = audit(folder)
            write(folder / 'integrity_audit.json', independent)
            total['meshes'][label] = dict(folder=str(folder), audit_sha256=sha(folder / 'integrity_audit.json'), temporal_precision_pass=independent['temporal_precision_pass'])
            assert independent['integrity_pass']
            if not independent['temporal_precision_pass']:
                total.update(status='completed_negative', coarse_temporal_precision_pass=False, stopped_before_next_mesh=True)
                break
        else:
            total.update(status='completed', coarse_temporal_precision_pass=True)
        assert time.monotonic()-start <= 36000
    except Exception as error:
        total.update(status='failed', error=str(error), error_type=type(error).__name__, diagnostic=traceback.format_exc())
        if 'e' in locals() and not (folder / 'execution.json').exists():
            e.update(status='failed', diagnostic=traceback.format_exc(), elapsed_s=time.monotonic()-mesh_start,
                     finished_utc=datetime.now(timezone.utc).isoformat())
            write(folder / 'partial_execution.json', e)
    total.update(finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_s=time.monotonic() - start)
    write(out / 'execution.json', total)
    print({k: total.get(k) for k in ('status', 'coarse_temporal_precision_pass', 'elapsed_s', 'error')}, flush=True)
    return 0 if total['status'] == 'completed' else 2 if total['status'] == 'completed_negative' else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    raise SystemExit(run(args.out.resolve()))
