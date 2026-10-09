"""Reconstruct expm_multiply selection, without applying an exponential."""
import argparse
from datetime import datetime,timezone
import hashlib
import inspect
import json
from pathlib import Path
import time
from run_point03_exponential import ROOT,operator,sha,guard,write
import numpy as np
import scipy
from scipy.sparse.linalg import _expm_multiply as internal

def run():
    assert scipy.__version__=='1.15.1';start=time.monotonic();guard(ROOT/'resultados/codex')
    manifest=ROOT/'resultados/codex/point03_exponential_20261007_H2/manifest.json'
    m=json.loads(manifest.read_text(encoding='utf-8'));rows=[]
    for n,partitions in ((500,(4,8)),(640,(11,17))):
        c=next(c for c in m['plan'] if c['N']==n);assert sha(c['input_path'])==c['input_sha256']
        with np.load(c['input_path'],allow_pickle=False) as inp:base,trace=operator(inp['dn'],inp['sigma'],128e-6/n)
        selections=[]
        for segments in partitions:
            np.random.seed(0);length=.002/segments;a=length*base;trace_scaled=length*trace
            mu=trace_scaled/float(a.shape[0]);a=a-mu*internal._ident_like(a)
            norm=internal._exact_1_norm(a);info=internal.LazyOperatorNormInfo(a,A_1_norm=norm,ell=2)
            degree,scales=internal._fragment_3_1(info,1,2**-53,ell=2)
            selections.append(dict(segments=segments,m_star=int(degree),s=int(scales),nominal_internal_length_m=length/scales,scaled_1_norm=float(norm)))
        a,b=(s['nominal_internal_length_m'] for s in selections)
        rows.append(dict(N=n,input_path=c['input_path'],input_sha256=c['input_sha256'],selections=selections,exact_same_increment=a==b,relative_increment_difference=abs(a-b)/max(a,b)))
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),manifest_sha256=sha(manifest),scipy_version=scipy.__version__,selection_source_sha256=hashlib.sha256(inspect.getsource(internal._expm_multiply_simple).encode()).hexdigest(),rows=rows,elapsed_s=time.monotonic()-start,no_exponential_action_performed=True,scope='Reconstructed maximum degree/scales, not instrumented term counts or independent algorithms; no new acceptance gate.')

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=run();write(a.output,r);print(json.dumps(r));return 0
if __name__=='__main__':raise SystemExit(main())
