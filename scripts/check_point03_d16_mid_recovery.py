"""Recovery orchestration negative controls; never launch an optical worker."""
import ast
import json
from pathlib import Path
from unittest.mock import patch
import run_point03_d16_mid_recovery as target


def rejects(function, *args):
    try:
        function(*args)
    except AssertionError:
        return True
    raise AssertionError('Invalid recovery request was accepted')


if __name__ == '__main__':
    out = target.ROOT/'resultados/codex/point03_d16_mid_recovery_controls_20261009'
    out.mkdir()
    prefix = out/'never_launched'
    GiB = 1024**3
    target.allowed(11000, 7*GiB, 10*GiB, prefix)
    checks = {'budget_expired_rejected': rejects(target.allowed, 22001, 7*GiB, 10*GiB, prefix),
              'negative_elapsed_rejected': rejects(target.allowed, -1, 7*GiB, 10*GiB, prefix),
              'insufficient_RAM_rejected': rejects(target.allowed, 11000, 6*GiB, 10*GiB, prefix),
              'insufficient_disk_rejected': rejects(target.allowed, 11000, 7*GiB, 2*GiB, prefix)}
    with Path(str(prefix)+'.npz').open('xb') as stream:
        stream.write(b'Guard control marker; not an optical field')
    checks['existing_output_rejected'] = rejects(target.allowed, 11000, 7*GiB, 10*GiB, prefix)
    old, manifest, partial = target.prerequisites()
    real_read = target.base.read

    def wrong_status(path):
        data = real_read(path)
        return dict(data, status='running') if Path(path) == target.ORIGINAL/'execution.json' else data

    with patch.object(target.base, 'read', side_effect=wrong_status):
        checks['unfinished_original_rejected'] = rejects(target.prerequisites)
    checks['real_retained_prerequisites_verified'] = True
    auditor_path = target.ROOT/'scripts/audit_point03_d16_mid_recovery.py'
    tree = ast.parse(auditor_path.read_text(encoding='utf-8'))
    imported = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    checks['independent_auditor_no_evaluator_import'] = not any(n and n.startswith('run_point03') for n in imported)
    assert all(checks.values())
    record = dict(controls_pass=True, checks=checks,
                  worker_sha256=target.base.sha(Path(target.__file__)),
                  auditor_sha256=target.base.sha(auditor_path),
                  resources_synthetic_in_controls_only=True, optical_worker_launched=False,
                  original_failure_sha256=target.base.sha(target.ORIGINAL/'execution.json'),
                  partial_audit_sha256=target.base.sha(target.ORIGINAL/target.PARTIAL), point03_closed=False)
    target.base.write(target.ROOT/'resultados/codex/point03_d16_mid_recovery_controls_20261009.json', record)
    print(json.dumps(record))
