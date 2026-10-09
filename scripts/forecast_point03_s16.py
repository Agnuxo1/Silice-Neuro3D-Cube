"""Forecast only after three local K16 temporal approvals; no reserved mesh."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from point03_fem_spatial import forecast

ROOT = Path(__file__).resolve().parents[1]
AUDITS = [
    'resultados/codex/point03_d16_refine_recovery_20261008/integrity_audit.json',
    'resultados/codex/point03_d16_mid_recovery_20261009/local_integrity_audit.json',
    'resultados/codex/point03_d16_fine_time_20261009/local_integrity_audit.json',
]
K_FILES = [
    'resultados/codex/point03_fem_duffy_coarse_retry_20261008/stiffness_duffy16.npz',
    'resultados/codex/point03_fem_duffy_mid_20261008/stiffness_duffy16.npz',
    'resultados/codex/point03_fem_duffy_prototype_20261008/stiffness_duffy16.npz',
]
K_HASHES = ['51a273ef6a14dbcc425e1d5f22820963c2c9bc219f26fa56447115b06acef981',
            'd90b53ab2fb53538596b31871050a80cd50cfdc73cf096fb5d5b0e736c88408e',
            'f251ae68f374cb6ae98288caed1984d528a6147c7b74ada3229e7aa98771074f']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def make_forecasts(audits):
    assert len(audits) == 3
    assert all(a['integrity_pass'] and a['temporal_precision_pass'] for a in audits)
    values = {detector:forecast([a['powers']['P6_32768'][detector] for a in audits],
                               [a['power_differences'][detector] for a in audits])
              for detector in ('field','intensity')}
    return dict(primary='P6_32768', observables=values,
                forecast_eligible=all(v['eligible'] for v in values.values()),
                reserved_mesh_generation_allowed=all(v['eligible'] for v in values.values()),
                point03_closed=False)


def run(out):
    assert out.is_relative_to(ROOT/'resultados/codex') and not out.exists()
    assert all((ROOT/path).exists() for path in AUDITS), 'All three local temporal audits are required'
    audits = [read(ROOT/path) for path in AUDITS]
    assert all(a['local_recalculation'] for a in audits[1:])
    controls_path = ROOT/'resultados/codex/point03_p5d_evaluator_controls_20261008.json'
    old_controls = read(controls_path)
    assert old_controls['controls_pass'] and old_controls['cases_checked'] == 11
    assert old_controls['no_T96_results_read']
    assert sha(ROOT/'scripts/point03_fem_spatial.py') == old_controls['source_sha256'][str(ROOT/'scripts/point03_fem_spatial.py')]
    new_controls_path=ROOT/'resultados/codex/point03_s16_controls_run2_20261009.json'
    new_controls=read(new_controls_path)
    assert new_controls['controls_pass'] and new_controls['altered_series_metadata_rejected']
    for name,digest in new_controls['sources'].items():
        assert sha(ROOT/'scripts'/name)==digest
    for path, digest in zip(K_FILES,K_HASHES):
        assert sha(ROOT/path) == digest
    old_manifest = read(ROOT/'resultados/codex/point03_d16_refine_recovery_20261008/manifest.json')
    old_report = ROOT/old_manifest['retained_P6_report']
    old_field = ROOT/old_manifest['retained_P6_field']
    assert sha(old_report) == old_manifest['retained_P6_report_sha256']
    assert sha(old_field) == old_manifest['retained_P6_field_sha256']
    cp = read(old_report)
    assert cp['case'] == 'P6_32768' and cp['index'] == 32 and cp['steps_done'] == 32768 and cp['status'] == 'completed'
    primary_files = [old_report,old_field]
    for folder, index in (('point03_d16_mid_refined_time_20261008',32),
                          ('point03_d16_fine_time_20261009',64)):
        report = ROOT/'resultados/codex'/folder/'P6_32768'/f'part{index:03d}.json'
        cp = read(report)
        assert cp['case'] == 'P6_32768' and cp['index'] == index and cp['steps_done'] == 32768 and cp['status'] == 'completed'
        field = report.parent/f'part{index:03d}.npz'
        assert sha(field) == cp['field_sha256']
        primary_files.extend([report,field])
    result = make_forecasts(audits)
    result.update(created_utc=datetime.now(timezone.utc).isoformat(),
                  h_um=[.546875,.4375,.35], nominal_refinement_ratio=1.25,
                  status='eligible' if result['forecast_eligible'] else 'negative',
                  reserved_mesh_generated=False, optical_fields_generated=False,
                  temporal_discrepancy_scope='Maximum across the three meshes separately for each observable, as in the registered scalar forecast function.',
                  audit_paths=AUDITS,
                  scope='Conditional prospective numerical forecast, not an absolute continuum error or physical validation.')
    sources = [ROOT/p for p in AUDITS+K_FILES]+primary_files+[
        Path(__file__).resolve(),ROOT/'scripts/point03_fem_spatial.py',
        ROOT/'scripts/audit_point03_s16_forecast.py',ROOT/'scripts/check_point03_s16.py',
        ROOT/'Docs/POINT-03-D16-SPATIAL-CONTRACT.md',ROOT/'Docs/POINT-03-S16-EXECUTION-CONTRACT.md',
        controls_path,new_controls_path]
    result['source_sha256']={p.relative_to(ROOT).as_posix():sha(p) for p in sources}
    out.mkdir()
    with (out/'forecast.json').open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2,allow_nan=False)
        stream.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','observables')}))
    return 0 if result['forecast_eligible'] else 2


if __name__ == '__main__':
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--out',type=Path,required=True)
    raise SystemExit(run(parser.parse_args().out.resolve()))
