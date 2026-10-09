"""Manufactured controls for retention auditing; no T96 fields read or advanced."""
from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from audit_point03_d16_fine_partial import ROOT, STEPS, audit_fields, sha
import numpy as np
from scipy.sparse import eye


def write(path, value):
    path.write_text(json.dumps(value), encoding='utf-8')


def make_fixture(out):
    manifest = dict(created_utc='2026-10-09T03:22:29+00:00', purpose='Manufactured three-dimensional vector, no optical propagation')
    initial = np.array([1., 0., 0.], dtype=np.complex128)
    free = np.arange(3)
    resources = dict(available_ram_bytes=4*1024**3, free_disk_bytes=3*1024**3)
    for case, count in (('P6_32768', 64), ('R5_65536', 1)):
        folder = out/case
        folder.mkdir()
        previous, previous_sha, power = None, None, 1.
        for index in range(1, count+1):
            field = initial*(.999**index)
            field_path = folder/f'part{index:03d}.npz'
            np.savez(field_path, field=field)
            actual = float(np.vdot(field, field).real)
            report = dict(status='completed', case=case, index=index,
                          previous_report_path=previous, previous_report_sha256=previous_sha,
                          field_path=f'{case}/part{index:03d}.npz', field_sha256=sha(field_path),
                          physical_power=actual, previous_power=power, steps_done=index*512,
                          dt_m=.002/STEPS[case], elapsed_s=.1,
                          started_utc='2026-10-09T03:23:00+00:00',
                          resource_start=resources, resource_end=resources)
            path = folder/f'part{index:03d}.json'
            write(path, report)
            previous, previous_sha, power = path.relative_to(out).as_posix(), sha(path), actual
    return manifest, eye(3, format='csc'), initial, free


if __name__ == '__main__':
    controls = {}
    # Every fixture is retained in D: only for the lifetime of its bounded software check.
    scratch = ROOT/'resultados/codex/point03_d16_fine_partial_controls_20261009'
    scratch.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix='fixture_', dir=scratch) as temp:
        out = Path(temp)
        assert out.resolve().is_relative_to(scratch.resolve())
        inputs = make_fixture(out)
        counts = {'P6_32768':64, 'R5_65536':1}
        positive = audit_fields(out, counts, *inputs)
        assert positive['partial_integrity_pass'] and positive['checkpoints_checked'] == 65
        assert not positive['full_temporal_assessment'] and not positive['point03_closed']
        assert not positive['resource_reservations_audited']
        controls['valid_chains_both_families'] = True
        path = out/'P6_32768/part001.json'
        original = json.loads(path.read_text(encoding='utf-8'))
        changes = {
            'previous_hash':dict(previous_report_sha256='0'*64),
            'field_hash':dict(field_sha256='0'*64),
            'external_field_path':dict(field_path='../outside.npz'),
            'wrong_time_step':dict(dt_m=.002/65536),
            'wrong_steps_done':dict(steps_done=1024),
            'power_residual':dict(physical_power=.9),
            'previous_power':dict(previous_power=.9),
            'worker_timeout':dict(elapsed_s=361),
            'worker_low_memory':dict(resource_start={'available_ram_bytes':3*1024**3,'free_disk_bytes':3*1024**3}),
            'worker_low_disk':dict(resource_end={'available_ram_bytes':4*1024**3,'free_disk_bytes':2*1024**3}),
            'worker_started_before_manifest':dict(started_utc='2026-10-09T03:00:00+00:00'),
            'worker_started_after_deadline':dict(started_utc='2026-10-09T13:46:00+00:00'),
            'failed_report':dict(status='failed'),
        }
        for label, change in changes.items():
            write(path, dict(original, **change))
            try:
                audit_fields(out, counts, *inputs)
            except AssertionError:
                controls[label+'_rejected'] = True
            else:
                raise AssertionError(label+' accepted')
        write(path, original)
        for bad_counts in ({'P6_32768':63,'R5_65536':1}, {'P6_32768':65,'R5_65536':0}, {'P6_32768':0,'R5_65536':0}):
            try:
                audit_fields(out, bad_counts, *inputs)
            except AssertionError:
                pass
            else:
                raise AssertionError('Invalid retained counts accepted')
        controls['invalid_counts_rejected'] = True
        field_path = out/'P6_32768/part001.npz'
        for label, field in (
            ('dtype',np.array([.999,0,0],dtype=np.float64)),
            ('shape',np.array([.999,0],dtype=np.complex128)),
            ('nonfinite',np.array([float('nan'),0,0],dtype=np.complex128)),
        ):
            np.savez(field_path, field=field)
            write(path, dict(original,field_sha256=sha(field_path)))
            try:
                audit_fields(out, counts, *inputs)
            except AssertionError:
                controls[label+'_rejected'] = True
            else:
                raise AssertionError(label+' accepted')
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(), controls_pass=True,
                  controls=controls, no_T96_results_read=True, optical_fields_created=0,
                  full_temporal_assessment=False, point03_closed=False,
                  source_sha256={name:sha(ROOT/'scripts'/name) for name in (
                      'audit_point03_d16_fine_partial.py','check_point03_d16_fine_partial.py')})
    with (ROOT/'resultados/codex/point03_d16_fine_partial_controls_20261009.json').open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(report))
