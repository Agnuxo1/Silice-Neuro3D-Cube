"""FEMTO-1 fork of NEUROCUBO custody: MNIST intensities, no PCA or centering.

Only this module accesses source labels. This is procedural custody on the
same machine, not an independently controlled vault. MNIST has prior exploratory
use; the new split does not make the dataset historically unseen.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import secrets
import struct
import urllib.request
from pathlib import Path
import numpy as np
from common import sha, now, write_json, save_npz

TASKS={'mnist03':([0,1,2,3],'MNIST prior exploratory use; new procedural holdout')}
RESOURCES={'train-images-idx3-ubyte.gz':'f68b3c2dcbeaaa9fbdd348bbdeb94873',
           'train-labels-idx1-ubyte.gz':'d53e105ee54ea40749a09fcbcd1e9432'}
SOURCE='https://ossci-datasets.s3.amazonaws.com/mnist/'

def download(raw):
    raw.mkdir(parents=True,exist_ok=True)
    files={}
    for name,md5 in RESOURCES.items():
        path=raw/name
        if not path.exists():
            with urllib.request.urlopen(SOURCE+name,timeout=45) as r:
                content=r.read()
            with path.open('xb') as f:
                f.write(content)
        if hashlib.md5(path.read_bytes()).hexdigest()!=md5:
            raise ValueError('MNIST source checksum mismatch: '+name)
        files[name]={'md5':md5,'sha256':sha(path),'url':SOURCE+name}
    return files

def labels_hash(salt,y,ids):
    return hashlib.sha256(salt.encode()+np.asarray(y,dtype='<i8').tobytes()
                          +np.asarray(ids,dtype='<i8').tobytes()).hexdigest()

def seal(args):
    out=args.public_dir/args.task
    vault=args.sealed_dir/args.task
    if out.exists() or vault.exists():
        raise FileExistsError('Never overwrite a sealed partition')
    if args.sealed_dir.resolve().is_relative_to(args.root.resolve()):
        raise ValueError('Vault must be outside git repository')
    sources=download(args.raw_dir)
    b=gzip.decompress((args.raw_dir/'train-images-idx3-ubyte.gz').read_bytes())
    magic,n,h,w=struct.unpack('>IIII',b[:16])
    if (magic,n,h,w)!=(2051,60000,28,28) or len(b)!=16+n*h*w:
        raise ValueError('Invalid MNIST image IDX')
    images=np.frombuffer(b,dtype=np.uint8,offset=16).reshape(n,28,28)
    b=gzip.decompress((args.raw_dir/'train-labels-idx1-ubyte.gz').read_bytes())
    magic,nlabels=struct.unpack('>II',b[:8])
    if (magic,nlabels)!=(2049,n) or len(b)!=8+n:
        raise ValueError('Invalid MNIST label IDX')
    y=np.frombuffer(b,dtype=np.uint8,offset=8)
    ids=np.flatnonzero(np.isin(y,TASKS[args.task][0]))
    y=y[ids].astype(np.int64)
    x=images[ids].reshape(-1,4,7,4,7).mean(axis=(2,4)).reshape(-1,16)/255
    rng=np.random.default_rng(args.seed)
    # 60/20/20 by class. Training includes a separate calibration subset.
    parts={k:[] for k in ['fit','calibration','validation','test']}
    for label in range(4):
        p=rng.permutation(np.flatnonzero(y==label))
        nt,nv=int(.6*len(p)),int(.2*len(p))
        nc=int(.2*nt)
        parts['fit'].extend(p[:nt-nc]); parts['calibration'].extend(p[nt-nc:nt])
        parts['validation'].extend(p[nt:nt+nv]); parts['test'].extend(p[nt+nv:])
    parts={k:np.sort(v) for k,v in parts.items()}
    assert sum(map(len,parts.values()))==len(ids)
    assert len(np.unique(np.concatenate(list(parts.values()))))==len(ids)
    assert len(parts['test'])>=2000
    out.mkdir(parents=True); vault.mkdir(parents=True)
    manifest={'task':args.task,'seed':args.seed,'sealed_at_utc':now(),
              'source_files':sources,'classes':[0,1,2,3],
              'preprocessing':'28x28 -> mean of each disjoint 7x7 block /255; 16 intensities [0,1]; no learned transform',
              'history_limit':'MNIST used in prior exploratory model fitting/evaluation. New seeded split, not a historically unseen dataset.',
              'custody_limit':'Procedural same-host seal; source labels public and recoverable; no independent custodian claim.',
              'counts':{k:len(v) for k,v in parts.items()},'files':{}}
    for name in ['fit','calibration','validation']:
        p=parts[name]
        file=out/(name+'.npz')
        save_npz(file,X=x[p],y=y[p],raw_indices=ids[p])
        manifest['files'][file.name]=sha(file)
    p=parts['test']
    file=out/'test_X.npz'
    save_npz(file,X=x[p],raw_indices=ids[p])
    manifest['files'][file.name]=sha(file)
    salt=secrets.token_hex(32)
    save_npz(vault/'test_labels.npz',y=y[p],raw_indices=ids[p])
    write_json(vault/'salt.json',{'salt':salt})
    manifest['test_label_commitment_sha256']=labels_hash(salt,y[p],ids[p])
    manifest['commitment_rule']='sha256(salt_utf8 || little-endian int64 labels || little-endian int64 raw indices)'
    write_json(out/'manifest.json',manifest)
    return {'counts':manifest['counts'],'manifest_sha256':sha(out/'manifest.json')}

def reveal(args):
    vault=args.sealed_dir/args.task
    receipt=vault/'reveal_receipt.json'
    if receipt.exists():
        raise RuntimeError('Second reveal forbidden')
    # Final predictions must be from Blender and satisfy all upstream gates.
    frozen=json.loads(args.frozen_receipt.read_text(encoding='utf-8'))
    gates=json.loads(args.release_gates.read_text(encoding='utf-8'))
    if frozen.get('backend')!='Blender objects / intensity model' or not gates.get('sealed_test_ready'):
        raise RuntimeError('Physical/layout/release gates pending; preserve sealed test')
    if sha(args.predictions)!=frozen['predictions_sha256']:
        raise RuntimeError('Frozen predictions hash mismatch')
    m=json.loads((args.public_dir/args.task/'manifest.json').read_text(encoding='utf-8'))
    salt=json.loads((vault/'salt.json').read_text(encoding='utf-8'))['salt']
    with np.load(vault/'test_labels.npz',allow_pickle=False) as d:
        y,ids=d['y'],d['raw_indices']
    if labels_hash(salt,y,ids)!=m['test_label_commitment_sha256']:
        raise RuntimeError('Vault differs from commitment')
    with np.load(args.predictions,allow_pickle=False) as d:
        if not np.array_equal(d['raw_indices'],ids) or len(d['predictions'])!=len(y):
            raise RuntimeError('Prediction order mismatch')
    args.out_dir.mkdir(parents=True,exist_ok=True)
    save_npz(args.out_dir/'revealed_labels.npz',y=y,raw_indices=ids)
    record={'revealed_at_utc':now(),'predictions_sha256':sha(args.predictions),
            'labels_sha256':sha(args.out_dir/'revealed_labels.npz'),'salt':salt,
            'commitment_verified':True,'commitment':m['test_label_commitment_sha256']}
    write_json(receipt,record); write_json(args.out_dir/'reveal_receipt.json',record)
    return {'commitment_verified':True,'n':len(y)}

def main():
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['seal','reveal'])
    p.add_argument('--task',choices=TASKS,default='mnist03'); p.add_argument('--seed',type=int,default=20261013)
    p.add_argument('--root',type=Path,default=Path.cwd())
    p.add_argument('--public-dir',type=Path,required=True);p.add_argument('--sealed-dir',type=Path,required=True)
    p.add_argument('--raw-dir',type=Path);p.add_argument('--predictions',type=Path)
    p.add_argument('--frozen-receipt',type=Path);p.add_argument('--release-gates',type=Path);p.add_argument('--out-dir',type=Path)
    args=p.parse_args();print(json.dumps(seal(args) if args.command=='seal' else reveal(args)))

if __name__=='__main__': main()
