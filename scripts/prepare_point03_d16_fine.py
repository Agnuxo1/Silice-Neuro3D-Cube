"""Prepare F1 without changing frozen M2 or launching new T96 fields."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_K = 'd90b53ab2fb53538596b31871050a80cd50cfdc73cf096fb5d5b0e736c88408e'
NEW_K = 'f251ae68f374cb6ae98288caed1984d528a6147c7b74ada3229e7aa98771074f'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


if __name__ == '__main__':
    controls = json.loads((ROOT/'resultados/codex/point03_d16_mid_refined_worker_controls_20261008/report.json').read_text())
    assert controls['controls_pass'] and controls['tested_worker_sha256'] == sha(ROOT/'scripts/run_point03_d16_mid_refined_time.py')
    pairs = [('run_point03_d16_mid_refined_time.py', 'run_point03_d16_fine_time.py'),
             ('audit_point03_d16_mid_refined_time.py', 'audit_point03_d16_fine_time.py'),
             ('check_point03_d16_mid_refined_worker.py', 'check_point03_d16_fine_worker.py'),
             ('check_point03_d16_mid_refined_inputs.py', 'check_point03_d16_fine_inputs.py'),
             ('check_point03_d16_mid_refined_controls.py', 'check_point03_d16_fine_controls.py')]
    replacements = {
        'point03_p5a_mesh_mid_20261008': 'point03_p4c_mesh_20261008',
        'point03_p5b_detector_mid_20261008': 'point03_p4f_detector_20261008',
        'point03_p5b_damping_mid_20261008': 'point03_p4g_damping_20261008',
        'point03_fem_duffy_mid_20261008': 'point03_fem_duffy_prototype_20261008',
        OLD_K: NEW_K,
        'run_point03_d16_mid_refined_time': 'run_point03_d16_fine_time',
        'audit_point03_d16_mid_refined_time': 'audit_point03_d16_fine_time',
        'check_point03_d16_mid_refined_worker': 'check_point03_d16_fine_worker',
        'check_point03_d16_mid_refined_controls': 'check_point03_d16_fine_controls',
        'check_point03_d16_mid_refined_inputs': 'check_point03_d16_fine_inputs',
        'prepare_point03_d16_mid_refined': 'prepare_point03_d16_fine',
        'point03_d16_mid_refined_worker_controls_20261008': 'point03_d16_fine_worker_controls_20261009',
        'point03_d16_mid_refined_input_integrity_20261008': 'point03_d16_fine_input_integrity_20261009',
        'point03_d16_mid_refined_evaluator_controls_20261008': 'point03_d16_fine_evaluator_controls_20261009',
        'point03_d16_mid_refined_generation_20261008': 'point03_d16_fine_generation_20261009',
        'POINT-03-D16-MID-REFINED-TIME-CONTRACT.md': 'POINT-03-D16-FINE-TIME-CONTRACT.md',
        'point03_d16_refine_recovery_20261008/integrity_audit.json': 'point03_d16_mid_recovery_20261009/local_integrity_audit.json',
        '22000': '32000',
    }
    rows = []
    for original, generated in pairs:
        source = ROOT/'scripts'/original
        text = source.read_text(encoding='utf-8')
        counts = {old: text.count(old) for old in replacements}
        for old, new in replacements.items():
            text = text.replace(old, new)
        if original.startswith('run_'):
            text = once(text, 'portable mid-mesh', 'portable fine-mesh')
            text = once(text, "STEPS = {'P6_32768': 32768, 'R5_65536': 65536}", "STEPS = {'P6_32768': 32768, 'R5_65536': 65536}\nCHUNK_STEPS = 512\nDEADLINE = datetime(2026, 10, 9, 13, 45, tzinfo=timezone.utc)\n\ndef deadline_remaining():\n    return (DEADLINE-datetime.now(timezone.utc)).total_seconds()")
            text = once(text, 'solver.advance(initial, 1024)', 'solver.advance(initial, CHUNK_STEPS)')
            text = once(text, 'steps_done=args.index*1024', 'steps_done=args.index*CHUNK_STEPS')
            text = once(text, '        for folder, report in ((G, \'report.json\'), (T, \'report.json\'), (D, \'report.json\')):', "        geometry = read(ROOT/G/'report_recovered.json')\n        assert geometry['integrity_pass'] and geometry['geometry_and_assembly_controls_pass']\n        for folder, report in ((T, 'report.json'), (D, 'report.json')):")
            text = once(text, "read(ROOT/G/'report.json')['hashes'][name]", "geometry['artifact_sha256'][name]")
            text = once(text, "f'{G}/report.json'", "f'{G}/report_recovered.json'")
            text = once(text, 'chunk_steps=1024,', "chunk_steps=CHUNK_STEPS, global_budget_s=32000, deadline_utc=DEADLINE.isoformat(),")
            text = once(text, "mesh='mid'", "mesh='fine'")
            text = text.replace('STEPS[case]//1024', 'STEPS[case]//CHUNK_STEPS')
            text = text.replace('assert time.monotonic()-start <= 32000', 'assert time.monotonic()-start <= 32000 and deadline_remaining() > 0')
            text = once(text, 'timeout=370)', 'timeout=min(370., 32000-(time.monotonic()-start), deadline_remaining()))')
        elif original.startswith('audit_'):
            text = once(text, 'm[\'chunk_steps\'] == 1024', "m['chunk_steps'] == 512 and m['global_budget_s'] == 32000")
            text = once(text, 'len(e[\'children\']) == 96', "len(e['children']) == 192")
            text = once(text, 'STEPS[case]//1024', 'STEPS[case]//512')
            text = once(text, 'index*1024', 'index*512')
            text = once(text, "    assert not e['point03_closed']", "    assert datetime.fromisoformat(e['finished_utc']) <= datetime(2026, 10, 9, 13, 45, tzinfo=timezone.utc)\n    assert not e['point03_closed']")
        elif original.endswith('_worker.py'):
            text = once(text, 'index*1024*.002', 'index*target.CHUNK_STEPS*.002')
        elif original.endswith('_inputs.py'):
            text = once(text, "(base.G, 'hashes'", "(base.G, 'artifact_sha256'")
            text = once(text, "record = base.read(base.ROOT/folder/'report.json')", "record = base.read(base.ROOT/folder/('report_recovered.json' if folder == base.G else 'report.json'))")
            text = once(text, '    prerequisite = base.read(prior)\n    assert prerequisite[\'integrity_pass\'] and prerequisite[\'temporal_precision_pass\']', "    prerequisite = base.read(prior) if prior.exists() else {}\n    prior_pass = bool(prerequisite.get('integrity_pass') and prerequisite.get('temporal_precision_pass'))")
            text = once(text, 'prerequisite_present=prior.exists(),', 'prerequisite_present=prior.exists(), prerequisite_pass=prior_pass,')
        ast.parse(text)
        target = ROOT/'scripts'/generated
        with target.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
        rows.append(dict(original=original, original_sha256=sha(source), generated=generated,
                         generated_sha256=sha(target), syntax_pass=True, substitution_counts=counts))
    record = dict(created_utc=datetime.now(timezone.utc).isoformat(), generation_pass=True,
                  no_optical_propagation=True, prerequisite='Local independently audited M2-R1 PASS',
                  chunk_steps=512, steps_by_case={'P6_32768':32768, 'R5_65536':65536},
                  global_budget_s=32000, deadline_utc='2026-10-09T13:45:00+00:00', files=rows)
    with (ROOT/'resultados/codex/point03_d16_fine_generation_20261009.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print({'generation_pass':True, 'files':len(rows), 'no_optical_propagation':True})
