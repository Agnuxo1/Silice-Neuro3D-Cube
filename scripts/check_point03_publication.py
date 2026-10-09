"""Record bounded checks of committed research artifacts before GitHub publication."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(
        ['git', '-c', f'safe.directory={ROOT.as_posix()}', *args], cwd=ROOT
    )


def main(destination):
    destination = destination.resolve()
    assert destination.is_relative_to(ROOT / 'resultados/codex')
    assert not destination.exists()
    head = git('rev-parse', 'HEAD').decode().strip()
    base = git('rev-parse', 'origin/main').decode().strip()
    changed = git('diff', '--name-only', '-z', 'origin/main...HEAD').decode().split('\0')
    changed = {path for path in changed if path}
    patterns = {
        'github_token': re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{60,})'),
        'aws_access_key': re.compile(rb'(?:AKIA|ASIA)[A-Z0-9]{16}'),
        'private_key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    }
    findings = []
    rows = []
    for record in git('ls-tree', '-r', '-l', '-z', 'HEAD').decode().split('\0'):
        if not record:
            continue
        metadata, path = record.split('\t', 1)
        mode, kind, oid, size = metadata.split()
        if path not in changed or kind != 'blob':
            continue
        size = int(size)
        rows.append({'path': path, 'git_blob': oid, 'size_bytes': size})
        if size > 100 * 1024 ** 2:
            findings.append({'path': path, 'reason': 'GitHub file size exceeds 100 MiB'})
        if mode == '120000':
            findings.append({'path': path, 'reason': 'symlink requires explicit review'})
        if Path(path).suffix.lower() in {'.py', '.md', '.json', '.toml', '.txt', '.yml', '.yaml', '.ps1', '.sh', '.bat', '.lock'}:
            data = git('cat-file', 'blob', oid)
            for label, pattern in patterns.items():
                if pattern.search(data):
                    findings.append({'path': path, 'reason': label})
    report = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'head': head, 'base': base,
        'commits_ahead': int(git('rev-list', '--count', 'origin/main..HEAD')),
        'changed_files': len(changed), 'present_changed_blobs': len(rows),
        'changed_blob_bytes': sum(row['size_bytes'] for row in rows),
        'largest_changed_blobs': sorted(rows, key=lambda row: row['size_bytes'], reverse=True)[:10],
        'findings': findings, 'publication_preflight_pass': not findings,
        'scope': 'Committed changes: file size, symlinks, selected credential signatures. Not a proof of absence of every secret. No raw values disclosed.',
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('head', 'commits_ahead', 'changed_files', 'changed_blob_bytes', 'findings', 'publication_preflight_pass')}))
    return 0 if not findings else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--output', type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output))
