"""Generate a separately hashed independent recovery auditor from frozen M2."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


if __name__ == '__main__':
    source = ROOT/'scripts/audit_point03_d16_mid_refined_time.py'
    text = source.read_text(encoding='utf-8')
    text = replace_once(text, "    assert e['status'] == 'completed'", "    case_folder = ROOT/m['continuation_out_dir']\n    original = read(case_folder/'execution.json')\n    assert original['status'] == 'failed' and sha(case_folder/'execution.json') == m['original_execution_sha256']\n    assert e['retained_checkpoints'] == m['retained_checkpoints'] == 83\n    assert e['original_wait_budget_exhausted'] and e['recovery_wait_s'] == 0\n    assert e['started_utc'] == m['original_started_utc'] == original['started_utc']\n    assert m['recovery_reservation_GiB'] == 6 and m['recovery_wait_budget_s'] == 0\n    assert e['status'] == 'completed'")
    for old, new in (("out/link['path']", "case_folder/link['path']"),
                     ("out/cp['field_path']", "case_folder/cp['field_path']")):
        assert text.count(old) > 0
        text = text.replace(old, new)
    text = replace_once(text, "            assert cp['started_utc'] > m['created_utc']", "            assert cp['started_utc'] > m['created_utc']\n            if case == 'R5_65536' and index >= 52:\n                assert cp['started_utc'] > m['recovery_created_utc']")
    text = replace_once(text, '                max_power_residual=residual,', "                retained_checkpoints=83, new_checkpoints_checked=13,\n                original_execution_sha256=m['original_execution_sha256'],\n                original_wait_budget_exhausted=True, recovery_wait_s=0.,\n                max_power_residual=residual,")
    ast.parse(text)
    target = ROOT/'scripts/audit_point03_d16_mid_recovery.py'
    with target.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)
    record = dict(generation_pass=True, original_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  generated_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  no_optical_propagation=True, evaluator_imported=False)
    with (ROOT/'resultados/codex/point03_d16_mid_recovery_audit_generation_20261009.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(record)
