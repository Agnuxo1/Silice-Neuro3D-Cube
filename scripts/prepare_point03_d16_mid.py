"""Generate separate mid worker/auditor without changing running coarse code."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_K = '51a273ef6a14dbcc425e1d5f22820963c2c9bc219f26fa56447115b06acef981'
NEW_K = 'd90b53ab2fb53538596b31871050a80cd50cfdc73cf096fb5d5b0e736c88408e'
PRIOR = 'resultados/codex/point03_d16_cloud_recovery_20261008/resultados/codex/cloud_d16_c1_20261008/local_integrity_audit.json'


def main():
    control = json.loads((ROOT/'resultados/codex/point03_d16_worker_controls_20261008/report.json').read_text())
    original = ROOT/'scripts/run_point03_d16_time.py'
    assert hashlib.sha256(original.read_bytes()).hexdigest() == control['tested_worker_sha256']
    settings = [('run_point03_d16_time.py', 'run_point03_d16_mid_time.py'),
                ('audit_point03_d16_time.py', 'audit_point03_d16_mid_time.py'),
                ('check_point03_d16_worker.py', 'check_point03_d16_mid_worker.py')]
    rows = []
    for old_name, new_name in settings:
        source = ROOT/'scripts'/old_name
        text = source.read_text(encoding='utf-8')
        substitutions = {
            'point03_p5a_mesh_coarse_20261008': 'point03_p5a_mesh_mid_20261008',
            'point03_p5b_detector_coarse_20261008': 'point03_p5b_detector_mid_20261008',
            'point03_p5b_damping_coarse_20261008': 'point03_p5b_damping_mid_20261008',
            'point03_fem_duffy_coarse_retry_20261008': 'point03_fem_duffy_mid_20261008',
            OLD_K: NEW_K,
            'report_recovered.json': 'report.json',
            'run_point03_d16_time': 'run_point03_d16_mid_time',
            'audit_point03_d16_time': 'audit_point03_d16_mid_time',
            'point03_d16_worker_controls_20261008': 'point03_d16_mid_worker_controls_20261008',
            'POINT-03-D16-COARSE-TIME-CONTRACT.md': 'POINT-03-D16-MID-TIME-CONTRACT.md',
            "mesh='coarse'": "mesh='mid'",
            '4.5*1024**3': '6*1024**3',
        }
        counts = {old: text.count(old) for old in substitutions}
        for old, new in substitutions.items():
            text = text.replace(old, new)
        if old_name == 'run_point03_d16_time.py':
            anchor = '    try:\n        for folder, report in'
            assert text.count(anchor) == 1
            text = text.replace(anchor, "    try:\n        prerequisite = read(ROOT/"+repr(PRIOR)+")\n        assert prerequisite['integrity_pass'] and prerequisite['temporal_precision_pass']\n        for folder, report in")
            anchor = "        source_files = [f'{G}/mass.npz'"
            assert text.count(anchor) == 1
            text = text.replace(anchor, '        source_files = ['+repr(PRIOR)+", f'{G}/mass.npz'")
        ast.parse(text)
        target = ROOT/'scripts'/new_name
        with target.open('x', encoding='utf-8', newline='\n') as f:
            f.write(text)
        rows.append(dict(original=old_name, original_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                         generated=new_name, generated_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                         substitution_counts=counts, syntax_pass=True))
    target = ROOT/'resultados/codex/point03_d16_mid_generation_20261008.json'
    with target.open('x', encoding='utf-8') as f:
        json.dump(dict(generation_pass=True, no_optical_propagation=True, prerequisite=PRIOR, files=rows), f, indent=2)
    print({'generation_pass': True, 'generated_files': 3, 'no_optical_propagation': True})


if __name__ == '__main__':
    main()
