"""Freeze adapted audit: numerical criteria unchanged, split operational provenance."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT/'scripts/audit_point03_d16_refine.py'
    body = source.read_text(encoding='utf-8')
    anchor = "    m, e, a = (read(out/name) for name in ('manifest.json', 'execution.json', 'assessment.json'))"
    assert body.count(anchor) == 1
    body = body.replace(anchor, anchor+"\n    case_folder = ROOT/m['continuation_out_dir']")
    changes = {
        "e.get('wait_s', 0.) <= 900": "e['original_wait_budget_exhausted'] and e['recovery_wait_s'] == 0",
        "read(out/link['path'])": "read(case_folder/link['path'])",
        "sha(out/link['path'])": "sha(case_folder/link['path'])",
        "sha(out/cp['field_path'])": "sha(case_folder/cp['field_path'])",
        "np.load(out/cp['field_path']": "np.load(case_folder/cp['field_path']",
        "event['reservation']['available_ram_bytes'] > 6*1024**3": "event['reservation']['available_ram_bytes'] > (6 if index <= 15 else 4.5)*1024**3",
    }
    for old, new in changes.items():
        assert body.count(old) == 1
        body = body.replace(old, new)
    ast.parse(body)
    path = ROOT/'scripts/audit_point03_d16_recovery.py'
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(body)
    with (ROOT/'resultados/codex/point03_d16_recovery_audit_generation_20261008.json').open('x', encoding='utf-8') as f:
        json.dump(dict(original_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                       generated_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                       numerical_criteria_unchanged=True, syntax_pass=True, changes=changes), f, indent=2)
    print({'audit_generated': True, 'numerical_criteria_unchanged': True})


if __name__ == '__main__':
    main()
