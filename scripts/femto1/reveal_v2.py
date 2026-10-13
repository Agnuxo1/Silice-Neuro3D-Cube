"""F4 release wrapper: hash-linked gates and atomic consumption before labels.

Use instead of directly invoking the preserved preregistered custodian v1.
Never execute on the real vault until the required physical/layout gates pass.
"""
import argparse
import json
import os
from pathlib import Path
from common import sha,write_json
from release_guard import validate_gates
from custodian import reveal

def consume_marker(path,record):
    data=(json.dumps(record,sort_keys=True)+'\n').encode('utf8')
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    with os.fdopen(fd,'wb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())

def main():
    p=argparse.ArgumentParser();p.add_argument('--release-evidence',type=Path,required=True)
    p.add_argument('--frozen-receipt',type=Path,required=True);p.add_argument('--predictions',type=Path,required=True)
    p.add_argument('--public-dir',type=Path,required=True);p.add_argument('--sealed-dir',type=Path,required=True)
    p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--task',default='mnist03')
    args=p.parse_args()
    release=validate_gates(args.release_evidence)
    frozen=json.loads(args.frozen_receipt.read_text(encoding='utf-8'))
    if (frozen.get('release_manifest_sha256')!=release['release_manifest_sha256']
        or frozen.get('geometry_canonical_sha256')!=release['geometry_canonical_sha256']
        or frozen.get('predictions_sha256')!=sha(args.predictions)):
        raise RuntimeError('Final Blender receipt does not match current evidence')
    vault=args.sealed_dir/args.task
    if (vault/'reveal_receipt.json').exists():raise RuntimeError('Already revealed')
    consume_marker(vault/'reveal_started.json',{'release':release,'predictions_sha256':sha(args.predictions)})
    args.out_dir.mkdir(parents=True,exist_ok=True)
    verified=args.out_dir/'release_verified.json'
    write_json(verified,{**release,'sealed_test_ready':True})
    args.release_gates=verified
    result=reveal(args)
    print(json.dumps(result))

if __name__=='__main__':main()
