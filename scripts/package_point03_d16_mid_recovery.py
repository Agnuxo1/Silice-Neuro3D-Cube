"""Package reviewed M2 sources and retained fields; do not launch workers."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile
import run_point03_d16_mid_recovery as recovery

ROOT = recovery.ROOT


if __name__ == '__main__':
    old, manifest, partial = recovery.prerequisites()
    controls = recovery.base.read(ROOT/'resultados/codex/point03_d16_mid_recovery_controls_20261009.json')
    assert controls['controls_pass']
    files = {ROOT/path for path in manifest['source_sha256']}
    for record in partial['cases'].values():
        for cp in record['checkpoints']:
            files.update((recovery.ORIGINAL/cp['path'], recovery.ORIGINAL/cp['field_path']))
    files.update(recovery.ORIGINAL/name for name in ('manifest.json', 'execution.json', recovery.PARTIAL))
    files.update(ROOT/path for path in (
        'scripts/run_point03_d16_mid_recovery.py', 'scripts/audit_point03_d16_mid_recovery.py',
        'scripts/check_point03_d16_mid_recovery.py', 'scripts/prepare_point03_d16_mid_recovery_audit.py',
        'scripts/package_point03_d16_mid_recovery.py', 'Docs/POINT-03-D16-M2-RECOVERY-CONTRACT.md',
        'resultados/codex/point03_d16_mid_recovery_controls_20261009.json',
        'resultados/codex/point03_d16_mid_recovery_audit_generation_20261009.json'))
    out = ROOT/'resultados/codex/point03_d16_mid_recovery_package_20261009'
    out.mkdir()
    archive = out/'Silice_M2_R1_20261009.zip'
    hashes = {p.relative_to(ROOT).as_posix(): recovery.base.sha(p) for p in sorted(files)}
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(hashes):
            z.write(ROOT/path, path)
    assert archive.stat().st_size < 95*1024**2
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(hashes)
        for path, digest in hashes.items():
            assert hashlib.sha256(z.read(path)).hexdigest() == digest
    record = dict(created_utc=datetime.now(timezone.utc).isoformat(), package_integrity_pass=True,
                  package_sha256=recovery.base.sha(archive), bytes=archive.stat().st_size,
                  members=len(hashes), source_sha256=hashes, optical_propagation_executed=False,
                  retained_checkpoints=83, new_Radau_chunks_planned=list(range(52, 65)),
                  original_started_utc=old['started_utc'], original_global_budget_s=22000,
                  additional_resource_wait_budget_s=0, point03_closed=False)
    recovery.base.write(out/'manifest.json', record)
    print(json.dumps({k: v for k, v in record.items() if k != 'source_sha256'}))
