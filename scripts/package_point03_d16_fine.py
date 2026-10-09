"""Package F1 after local M2 PASS, without launching fields or altering inputs."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile
import run_point03_d16_fine_time as target

ROOT = target.ROOT


def string_value(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and node.id in ('G', 'T', 'D', 'Q'):
        return getattr(target, node.id)
    if isinstance(node, ast.JoinedStr):
        return ''.join(string_value(part) for part in node.values)
    if isinstance(node, ast.FormattedValue) and node.conversion == -1 and node.format_spec is None:
        return string_value(node.value)
    raise ValueError('Unsupported expression in reviewed source-file list')


def source_names():
    tree = ast.parse((ROOT/'scripts/run_point03_d16_fine_time.py').read_text(encoding='utf-8'))
    nodes = [n.value for n in ast.walk(tree) if isinstance(n, ast.Assign) and
             any(isinstance(t, ast.Name) and t.id == 'source_files' for t in n.targets)]
    assert len(nodes) == 1 and isinstance(nodes[0], ast.List)
    names = [string_value(n) for n in nodes[0].elts]
    assert len(names) == len(set(names))
    for name in names:
        path = (ROOT/name).resolve()
        assert path.is_relative_to(ROOT.resolve()) and name.startswith(('scripts/', 'Docs/', 'resultados/codex/'))
    return names


if __name__ == '__main__':
    prior_path = ROOT/'resultados/codex/point03_d16_mid_recovery_20261009/local_integrity_audit.json'
    prior = target.read(prior_path)
    assert prior['integrity_pass'] and prior['temporal_precision_pass'] and prior['local_recalculation']
    controls = target.read(ROOT/'resultados/codex/point03_d16_fine_worker_controls_20261009/report.json')
    assert controls['controls_pass'] and controls['tested_worker_sha256'] == target.sha(ROOT/'scripts/run_point03_d16_fine_time.py')
    assert target.read(ROOT/'resultados/codex/point03_d16_fine_gate_controls_20261009.json')['controls_pass']
    names = source_names()+['scripts/package_point03_d16_fine.py',
                            'scripts/check_point03_d16_fine_gate.py',
                            'resultados/codex/point03_d16_fine_gate_controls_20261009.json']
    hashes = {name:target.sha(ROOT/name) for name in names}
    out = ROOT/'resultados/codex/point03_d16_fine_package_20261009'
    out.mkdir()
    archive = out/'Silice_D16_F1_20261009.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in sorted(hashes):
            z.write(ROOT/name, name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and set(z.namelist()) == set(hashes)
        for name, digest in hashes.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == digest
    record = dict(created_utc=datetime.now(timezone.utc).isoformat(), package_integrity_pass=True,
                  package_sha256=target.sha(archive), bytes=archive.stat().st_size,
                  members=len(hashes), source_sha256=hashes,
                  local_M2_audit_sha256=target.sha(prior_path), optical_propagation_executed=False,
                  point03_closed=False)
    target.write(out/'manifest.json', record)
    print(json.dumps({k:v for k,v in record.items() if k != 'source_sha256'}))
