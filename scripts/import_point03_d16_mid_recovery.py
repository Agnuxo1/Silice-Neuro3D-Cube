"""Verify M2-R1 download, safely retain it, then adopt only audited new files."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = 'resultados/codex/point03_d16_mid_refined_time_20261008/R5_65536/'
REC = 'resultados/codex/point03_d16_mid_recovery_20261009/'
RECORDS = {'manifest.json', 'execution.json', 'assessment.json', 'integrity_audit.json', 'progress.json'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def valid_name(name):
    pure = PurePosixPath(name)
    assert name == pure.as_posix() and not pure.is_absolute() and '\\' not in name
    assert all(p not in ('..', '.', '') for p in pure.parts)
    assert ((name.startswith(REC) and name[len(REC):] in RECORDS) or
            (name.startswith(BASE) and re.fullmatch(r'part0(?:5[2-9]|6[0-4])\.(?:json|npz|log)', name[len(BASE):])))
    return pure


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main(archive, expected, out):
    assert re.fullmatch('[0-9a-f]{64}', expected) and sha(archive) == expected
    assert out.is_relative_to(ROOT/'resultados/codex') and not out.exists()
    out.mkdir()
    retained = out/'download.zip'
    shutil.copyfile(archive, retained)
    assert sha(retained) == expected
    unpacked = out/'unpacked'
    unpacked.mkdir()
    with zipfile.ZipFile(retained) as z:
        assert z.testzip() is None and len(z.namelist()) == len(set(z.namelist()))
        for member in z.infolist():
            valid_name(member.filename)
            assert (unpacked/member.filename).resolve().is_relative_to(unpacked.resolve())
            assert (member.external_attr >> 16) & 0o170000 != 0o120000
        z.extractall(unpacked)
    e = read(unpacked/REC/'execution.json')
    m = read(unpacked/REC/'manifest.json')
    assert m['retained_checkpoints'] == e['retained_checkpoints'] == 83
    assert sha(unpacked/REC/'manifest.json') == e['manifest_sha256']
    assert m['original_execution_sha256'] == sha(ROOT/'resultados/codex/point03_d16_mid_refined_time_20261008/execution.json')
    for name, digest in m['source_sha256'].items():
        assert sha(ROOT/name) == digest
    adoption = []
    if e['status'] == 'completed':
        independent = read(unpacked/REC/'integrity_audit.json')
        assert independent['integrity_pass'] and independent['checkpoints_checked'] == 96
        assert e['elapsed_s'] <= 22000 and e['recovery_wait_s'] == 0
        assert sha(unpacked/REC/'assessment.json') == e['assessment_sha256']
        for index in range(52, 65):
            cp = read(unpacked/BASE/f'part{index:03d}.json')
            assert cp['status'] == 'completed' and cp['case'] == 'R5_65536' and cp['index'] == index
            assert cp['dt_m'] == .002/65536 and cp['steps_done'] == index*1024 and cp['elapsed_s'] <= 360
            assert sha(unpacked/'resultados/codex/point03_d16_mid_refined_time_20261008'/cp['field_path']) == cp['field_sha256']
        for source in sorted(unpacked.rglob('*')):
            if source.is_file():
                destination = ROOT/source.relative_to(unpacked)
                if destination.exists():
                    assert sha(destination) == sha(source)
                else:
                    adoption.append((source, destination))
        for source, destination in adoption:
            destination.parent.mkdir(parents=True, exist_ok=True)
            assert not destination.exists()
            with source.open('rb') as input_stream, destination.open('xb') as output_stream:
                shutil.copyfileobj(input_stream, output_stream)
            assert sha(source) == sha(destination)
    record = dict(created_utc=datetime.now(timezone.utc).isoformat(), sha_and_crc_pass=True,
                  download_sha256=expected, download_bytes=retained.stat().st_size,
                  original_failure_preserved=True, remote_status=e['status'],
                  adopted_files=len(adoption), local_independent_audit_pending=True,
                  point03_closed=False)
    with (out/'receipt.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(record))
    return 0 if e['status'] == 'completed' else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    raise SystemExit(main(a.archive.resolve(), a.expected_sha256, a.out.resolve()))
