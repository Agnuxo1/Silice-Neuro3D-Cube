"""Retain and verify every F1 export group; adopt only complete audited data."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = 'resultados/codex/point03_d16_fine_time_20261009/'
RECORDS = {'manifest.json', 'execution.json', 'assessment.json', 'integrity_audit.json', 'progress.json'}
STEPS = {'P6_32768':32768, 'R5_65536':65536}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def source_path(name):
    path = (ROOT/name).resolve()
    assert name.startswith(('scripts/','Docs/','resultados/codex/'))
    assert path.is_relative_to(ROOT.resolve())
    return path


def valid_name(name):
    pure = PurePosixPath(name)
    assert name == pure.as_posix() and not pure.is_absolute() and '\\' not in name
    assert all(part not in ('..', '.', '') for part in pure.parts) and name.startswith(BASE)
    relative = name[len(BASE):]
    if relative in RECORDS:
        return pure
    match = re.fullmatch(r'(P6_32768|R5_65536)/part(\d{3})\.(json|npz|log)', relative)
    assert match and 1 <= int(match[2]) <= STEPS[match[1]]//512
    return pure


def import_exports(export_manifest, archives, out):
    record = read(export_manifest)
    assert record['execution_status'] in ('completed', 'failed') and record['point03_closed'] is False
    assert record['bundles'] and out.is_relative_to(ROOT/'resultados/codex') and not out.exists()
    expected_names = []
    for index, item in enumerate(record['bundles'], 1):
        name = f'Silice_D16_F1_results_20261009_part{index:02d}.zip'
        assert PurePosixPath(item['path']).name == name and item['path'] == '/content/'+name
        assert re.fullmatch('[0-9a-f]{64}', item['sha256'])
        assert (archives/name).stat().st_size == item['bytes'] and sha(archives/name) == item['sha256']
        expected_names.append(name)
    out.mkdir()
    shutil.copyfile(export_manifest, out/'export_manifest.json')
    unpacked = out/'unpacked'
    unpacked.mkdir()
    seen = set()
    for name, item in zip(expected_names, record['bundles']):
        retained = out/name
        shutil.copyfile(archives/name, retained)
        assert sha(retained) == item['sha256']
        with zipfile.ZipFile(retained) as z:
            assert z.testzip() is None and len(z.namelist()) == item['members']
            for member in z.infolist():
                valid_name(member.filename)
                assert member.filename not in seen
                assert (unpacked/member.filename).resolve().is_relative_to(unpacked.resolve())
                assert (member.external_attr >> 16) & 0o170000 != 0o120000
                seen.add(member.filename)
            z.extractall(unpacked)
    case = unpacked/BASE
    execution = read(case/'execution.json')
    manifest = read(case/'manifest.json')
    assert execution['status'] == record['execution_status']
    assert manifest['steps_by_case'] == STEPS and manifest['chunk_steps'] == 512
    assert manifest['global_budget_s'] == 32000 and manifest['numerical_threads'] == 1
    assert manifest['stiffness_sha256'] == 'f251ae68f374cb6ae98288caed1984d528a6147c7b74ada3229e7aa98771074f'
    assert sha(case/'manifest.json') == execution['manifest_sha256']
    for name, digest in manifest['source_sha256'].items():
        assert sha(source_path(name)) == digest
    adoption = []
    if execution['status'] == 'completed':
        independent = read(case/'integrity_audit.json')
        assert independent['integrity_pass'] and independent['checkpoints_checked'] == 192
        assert independent['temporal_precision_pass'] == record['temporal_precision_pass'] == execution['temporal_precision_pass']
        assert execution['elapsed_s'] <= 32000 and execution.get('wait_s', 0.) <= 900
        assert datetime.fromisoformat(execution['finished_utc']) <= datetime(2026,10,9,13,45,tzinfo=timezone.utc)
        assert sha(case/'assessment.json') == execution['assessment_sha256']
        expected = {BASE+name for name in RECORDS}
        for family in STEPS:
            previous, previous_sha = None, None
            links = execution['solutions'][family]['checkpoints']
            assert len(links) == STEPS[family]//512
            for index, link in enumerate(links, 1):
                cp_path = case/family/f'part{index:03d}.json'
                cp = read(cp_path)
                assert link['path'] == f'{family}/part{index:03d}.json' and sha(cp_path) == link['sha256']
                assert cp['status'] == 'completed' and cp['case'] == family and cp['index'] == index
                assert cp['previous_report_path'] == previous and cp['previous_report_sha256'] == previous_sha
                assert cp['dt_m'] == .002/STEPS[family] and cp['steps_done'] == index*512 and cp['elapsed_s'] <= 360
                assert cp['field_path'] == f'{family}/part{index:03d}.npz'
                assert sha(case/cp['field_path']) == cp['field_sha256']
                previous, previous_sha = link['path'], link['sha256']
                expected.update(BASE+f'{family}/part{index:03d}.'+suffix for suffix in ('json','npz','log'))
        assert expected == seen
        for name in sorted(seen):
            source, destination = unpacked/name, ROOT/name
            if destination.exists():
                assert sha(source) == sha(destination)
            else:
                adoption.append((source,destination))
        for source, destination in adoption:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with source.open('rb') as input_stream, destination.open('xb') as output_stream:
                shutil.copyfileobj(input_stream, output_stream)
            assert sha(source) == sha(destination)
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(), SHA_CRC_pass=True,
                   groups_checked=len(expected_names), members_checked=len(seen),
                   export_manifest_sha256=sha(export_manifest), adopted_files=len(adoption),
                   remote_status=execution['status'], local_audit_pending=True, point03_closed=False)
    with (out/'receipt.json').open('x', encoding='utf-8') as stream:
        json.dump(receipt,stream,indent=2)
        stream.write('\n')
    print(json.dumps(receipt))
    return 0 if execution['status'] == 'completed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--export-manifest',type=Path,required=True)
    parser.add_argument('--archives',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    raise SystemExit(import_exports(args.export_manifest.resolve(),args.archives.resolve(),args.out.resolve()))
