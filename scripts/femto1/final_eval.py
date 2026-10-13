"""Prepared one-shot F4 prediction inside Blender. Not runnable on current gates."""
import argparse
import json
import sys
from pathlib import Path
import numpy as np
import bpy
from common import save_npz,write_json,sha
from geometry import network_matrix
from blender_twin import export
from release_guard import validate_gates,canonical_sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--release-evidence',type=Path,required=True)
    p.add_argument('--data-manifest',type=Path,required=True)
    p.add_argument('--test-features',type=Path,required=True);p.add_argument('--readout',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    release=validate_gates(a.release_evidence) # before accessing any test data
    manifest=json.loads(a.data_manifest.read_text(encoding='utf-8'))
    if sha(a.test_features)!=manifest['files']['test_X.npz']:
        raise RuntimeError('Test features differ from sealed partition manifest')
    geometry,curve_error=export(bpy.context.scene)
    if canonical_sha(geometry)!=release['geometry_canonical_sha256']:
        raise RuntimeError('Opened Blender objects differ from release geometry')
    if a.out.exists():raise RuntimeError('Final prediction attempt already recorded')
    a.out.mkdir(parents=True)
    write_json(a.out/'prediction_started.json',release)
    w=network_matrix(geometry,'N1')
    with np.load(a.test_features,allow_pickle=False) as d:x,ids=d['X'],d['raw_indices']
    with np.load(a.readout,allow_pickle=False) as d:g,b=d['gain'],d['offset']
    if g.shape!=(4,) or b.shape!=(4,) or not np.all(np.isfinite(g)) or not np.all(np.isfinite(b)) or np.any(g<=0):
        raise RuntimeError('Readout must contain exactly four positive gains and four finite offsets')
    # Blender route reads object properties. Independent CPU route uses explicit
    # powers through each coupler, without multiplying by the reconstructed W.
    power=x@w.T;cpu=np.zeros_like(power)
    for j in range(16):
        ratios=[]
        for q in range(3):
            c=next(c for c in geometry['couplers'] if c['zone']=='N1' and c['input']==j and c['tree_index']==q)
            ratios.append(np.sin(c['kappa_per_m']*c['length_m']+c['access_angle_rad'])**2)
        a0,b0,c0=ratios;leaves=[a0*b0,a0*(1-b0),(1-a0)*c0]
        for klass,fraction in zip(geometry['networks']['N1']['leaf_classes'][j],leaves):cpu[:,klass]+=x[:,j]*fraction
    difference=float(abs(power-cpu).max())
    pred=(power*g+b).argmax(1);cpred=(cpu*g+b).argmax(1)
    if difference>1e-12 or not np.array_equal(pred,cpred):raise RuntimeError('CPU equivalence failed')
    file=a.out/'predictions.npz'
    save_npz(file,power=power,predictions=pred,raw_indices=ids)
    write_json(a.out/'frozen_receipt.json',{'backend':'Blender objects / intensity model',
                'predictions_sha256':sha(file),'geometry_canonical_sha256':canonical_sha(geometry),
                'release_manifest_sha256':release['release_manifest_sha256'],
                'cpu_max_abs_power_difference':difference,'cpu_predictions_identical':True,
                'visible_curve_error_m':curve_error,'readout_sha256':sha(a.readout)})
    print('FEMTO1 '+json.dumps({'final_predictions_frozen':True,'n':len(pred)}))

if __name__=='__main__':main()
