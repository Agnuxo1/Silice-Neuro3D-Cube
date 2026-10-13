"""Serialization repair of the preserved prospective compile.py v1.

Geometry, numerical model and thresholds are unchanged. NumPy scalars are
converted to their corresponding Python scalars before writing JSON.
"""
import argparse
import json
import os
for n in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[n]='1'
from pathlib import Path
import numpy as np
from common import write_json,sha
from geometry import compile_geometry,drc

def native(value):
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,dict):return {k:native(v) for k,v in value.items()}
    if isinstance(value,list):return [native(v) for v in value]
    return value

def main():
    p=argparse.ArgumentParser();p.add_argument('--models',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    w=np.load(a.models/'W_main.npy',allow_pickle=False)
    proto=np.load(a.models/'W_proto.npy',allow_pickle=False)
    weights={'N1':w,'N2':w.copy(),'N3':proto,'N4':np.full((4,16),.25)}
    geo=native(compile_geometry(weights))
    write_json(a.out,geo)
    result=native(drc(geo,weights))
    result['geometry_sha256']=sha(a.out);result['geometry_path']=str(a.out.resolve())
    result['weight_input_hashes']={n:sha(a.models/n) for n in ['W_main.npy','W_proto.npy']}
    write_json(a.report,result)
    print(json.dumps({k:result[k] for k in ['passed','error_count','guide_count','network_couplers','weight_max_abs_errors']}))

if __name__=='__main__':main()
