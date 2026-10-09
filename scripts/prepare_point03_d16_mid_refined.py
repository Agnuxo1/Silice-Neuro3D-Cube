"""Generate M2 separately from unstarted M1 after independently audited C2."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIOR_OLD = 'resultados/codex/point03_d16_cloud_recovery_20261008/resultados/codex/cloud_d16_c1_20261008/local_integrity_audit.json'
PRIOR_NEW = 'resultados/codex/point03_d16_refine_recovery_20261008/integrity_audit.json'
STEPS_TEXT = "{'P6_32768': 32768, 'R5_65536': 65536}"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


def main():
    prior = json.loads((ROOT/PRIOR_NEW).read_text())
    assert prior['integrity_pass'] and prior['temporal_precision_pass']
    generation = json.loads((ROOT/'resultados/codex/point03_d16_mid_generation_20261008.json').read_text())
    for row in generation['files']:
        assert sha(ROOT/'scripts'/row['generated']) == row['generated_sha256']
    pairs = [
        ('run_point03_d16_mid_time.py', 'run_point03_d16_mid_refined_time.py'),
        ('audit_point03_d16_mid_time.py', 'audit_point03_d16_mid_refined_time.py'),
        ('check_point03_d16_mid_worker.py', 'check_point03_d16_mid_refined_worker.py'),
        ('check_point03_d16_mid_inputs.py', 'check_point03_d16_mid_refined_inputs.py'),
        ('check_point03_d16_controls.py', 'check_point03_d16_mid_refined_controls.py'),
    ]
    rows = []
    for old_name, new_name in pairs:
        source = ROOT/'scripts'/old_name
        text = source.read_text(encoding='utf-8')
        for old, new in {
            'run_point03_d16_mid_time': 'run_point03_d16_mid_refined_time',
            'audit_point03_d16_mid_time': 'audit_point03_d16_mid_refined_time',
            'point03_d16_mid_worker_controls_20261008': 'point03_d16_mid_refined_worker_controls_20261008',
            'point03_d16_mid_input_integrity_20261008': 'point03_d16_mid_refined_input_integrity_20261008',
            'point03_d16_evaluator_controls_20261008': 'point03_d16_mid_refined_evaluator_controls_20261008',
            'POINT-03-D16-MID-TIME-CONTRACT.md': 'POINT-03-D16-MID-REFINED-TIME-CONTRACT.md',
            PRIOR_OLD: PRIOR_NEW,
            'R5_32768': 'R5_65536',
        }.items():
            text = text.replace(old, new)
        if old_name == 'run_point03_d16_mid_time.py':
            text = replace_once(text, 'portable coarse-mesh', 'portable mid-mesh')
            text = replace_once(text, '\n\ndef read(path):', '\nSTEPS = '+STEPS_TEXT+'\n\ndef read(path):')
            assert text.count('.002/32768') == 2
            text = text.replace('.002/32768', '.002/STEPS[args.case]')
            text = replace_once(text, 'steps=32768, chunk_steps=1024,', 'steps_by_case=STEPS, chunk_steps=1024,')
            text = replace_once(text, 'range(1, 33)', 'range(1, STEPS[case]//1024+1)')
            text = replace_once(text, 'total=32, elapsed_s=', 'total=STEPS[case]//1024, elapsed_s=')
            text = replace_once(text, "{index}/32', flush=True)", "{index}/{STEPS[case]//1024}', flush=True)")
            text = replace_once(text, "        for folder, report in", "        controls = read(ROOT/'resultados/codex/point03_d16_mid_refined_worker_controls_20261008/report.json')\n        assert controls['controls_pass'] and controls['tested_worker_sha256'] == sha(Path(__file__))\n        assert read(ROOT/'resultados/codex/point03_d16_mid_refined_input_integrity_20261008.json')['input_integrity_pass']\n        for folder, report in")
            text = replace_once(text, "                        'scripts/point03_fem_time.py'", "                        'scripts/check_point03_d16_mid_refined_worker.py',\n                        'scripts/check_point03_d16_mid_refined_controls.py',\n                        'scripts/check_point03_d16_mid_refined_inputs.py',\n                        'scripts/prepare_point03_d16_mid_refined.py',\n                        'resultados/codex/point03_d16_mid_refined_worker_controls_20261008/report.json',\n                        'resultados/codex/point03_d16_mid_refined_input_integrity_20261008.json',\n                        'resultados/codex/point03_d16_mid_refined_generation_20261008.json',\n                        'scripts/point03_fem_time.py'")
        elif old_name == 'audit_point03_d16_mid_time.py':
            text = replace_once(text, '\n\ndef read(path):', '\nSTEPS = '+STEPS_TEXT+'\n\ndef read(path):')
            text = replace_once(text, "m['steps'] == 32768", "m['steps_by_case'] == STEPS")
            text = replace_once(text, "len(e['children']) == 64", "len(e['children']) == 96")
            text = replace_once(text, 'len(links) == 32', 'len(links) == STEPS[case]//1024')
            text = replace_once(text, 'cp[\'dt_m\'] == .002/32768', "cp['dt_m'] == .002/STEPS[case]")
        elif old_name == 'check_point03_d16_mid_worker.py':
            text = replace_once(text, '.002/32768', '.002/target.STEPS[case]')
        elif old_name == 'check_point03_d16_mid_inputs.py':
            text = replace_once(text, '    report = dict(', "    prerequisite = base.read(prior)\n    assert prerequisite['integrity_pass'] and prerequisite['temporal_precision_pass']\n    report = dict(")
        else:
            text = replace_once(text, 'from run_point03_d16_time import evaluate', 'from run_point03_d16_mid_refined_time import evaluate')
        ast.parse(text)
        target = ROOT/'scripts'/new_name
        with target.open('x', encoding='utf-8', newline='\n') as f:
            f.write(text)
        rows.append(dict(original=old_name, original_sha256=sha(source),
                         generated=new_name, generated_sha256=sha(target), syntax_pass=True))
    destination = ROOT/'resultados/codex/point03_d16_mid_refined_generation_20261008.json'
    with destination.open('x', encoding='utf-8') as f:
        json.dump(dict(generation_pass=True, no_optical_propagation=True, prerequisite=PRIOR_NEW,
                       prerequisite_sha256=sha(ROOT/PRIOR_NEW), steps_by_case=json.loads(STEPS_TEXT.replace("'", '"')),
                       files=rows), f, indent=2)
    print({'generation_pass': True, 'files': len(rows), 'no_optical_propagation': True})


if __name__ == '__main__':
    main()
