"""Resumable FEMTO-1 phase dispatcher; never overwrites evidence or opens test early.

Use status/verify for this already-executed run. A full independent replay must
be prepared with a fresh output/custody namespace and stage commitments; this
dispatcher does not disguise existing artifacts as a fresh reproduction.
"""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse
import json
import subprocess
from pathlib import Path
from common import sha
from release_guard import validate_gates

ROOT=Path(__file__).resolve().parents[2]
WORK=Path('D:/PROJECTS/.cognition/femto1')
PY=Path('D:/SiliceAgentkit/.venv-closure/Scripts/python.exe')
BLENDER=Path('D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.exe')
GPUQ=Path('D:/PROJECTS/.cognition/gpu_queue/gpuq.py')

def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def status():
    drc=ROOT/'resultados/codex/femto1_layout_20261013_v2/DRC.json'
    f2=ROOT/'resultados/codex/femto1_20261013/F2_validation.json'
    return {'F0':'SENT; written rules pending','F1':'server commitment and split recorded',
            'F2':load(f2)['gates'] if f2.exists() else 'pending',
            'F3':{'passed':load(drc)['passed'],'errors':load(drc)['error_count']} if drc.exists() else 'pending',
            'F4':'not executed; DRC/physical dependencies pending; no Blender/test claim',
            'F5':'supplier profile/independent propagation pending','F6':'noise sweep completed; physical gate pending',
            'F7':'review files only; STEP/STL/independent CAD reimport pending','F8':'not fabrication-ready; no tag/release',
            'F9':'requires fabricated device','sealed_test_revealed':(WORK/'sealed/mnist03/reveal_receipt.json').exists()}

def verify():
    m=load(WORK/'data/mnist03/manifest.json')
    for name in ['fit.npz','calibration.npz','validation.npz']:
        if sha(WORK/'data/mnist03'/name)!=m['files'][name]:raise RuntimeError('Partition changed '+name)
    run=load(ROOT/'resultados/codex/femto1_20261013/RUN.json')
    for name,digest in run['files'].items():
        if sha(ROOT/'resultados/codex/femto1_20261013'/name)!=digest:raise RuntimeError('F2 artifact changed '+name)
    drc=load(ROOT/'resultados/codex/femto1_layout_20261013_v2/DRC.json')
    if sha(WORK/'geometry_FEMTO1_candidate_v2.json')!=drc['geometry_sha256']:raise RuntimeError('Geometry changed')
    return {'partition_and_F2_artifact_hashes_verified':True,'geometry_hash_verified':True,
            'test_features_or_labels_read':False,'DRC_passed':drc['passed']}

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['femto1'])
    p.add_argument('stage',choices=['status','verify','twin','final-eval'],default='status',nargs='?')
    p.add_argument('--release-evidence',type=Path);a=p.parse_args()
    if a.stage=='status':print(json.dumps(status(),indent=2));return
    if a.stage=='verify':print(json.dumps(verify()));return
    drc=load(ROOT/'resultados/codex/femto1_layout_20261013_v2/DRC.json')
    if not drc['passed']:raise SystemExit('BLOCKED: DRC failed; preserve evidence and sealed test')
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'scripts/femto1')+os.pathsep+str(ROOT)
    if a.stage=='twin':
        command=[str(BLENDER),'-b','--factory-startup','-t','1','--python',str(ROOT/'scripts/femto1/blender_twin.py'),'--',
                 '--geometry',str(WORK/'geometry_FEMTO1_candidate_v2.json'),'--blend',str(WORK/'FEMTO1.blend'),
                 '--export',str(WORK/'geometry_from_blender.json'),'--report',str(WORK/'F4_roundtrip.json')]
    else:
        if not a.release_evidence:raise SystemExit('Hash-linked release evidence required')
        validate_gates(a.release_evidence)
        command=[str(BLENDER),'-b',str(WORK/'FEMTO1.blend'),'-t','1','--python',str(ROOT/'scripts/femto1/final_eval.py'),'--',
                 '--release-evidence',str(a.release_evidence.resolve()),'--data-manifest',str(WORK/'data/mnist03/manifest.json'),
                 '--test-features',str(WORK/'data/mnist03/test_X.npz'),'--readout',str(ROOT/'resultados/codex/femto1_20261013/readout_nominal.npz'),
                 '--out',str(WORK/'final_predictions')]
    # Queue and reserve before any Blender load; all requested jobs are bounded.
    queued=['python',str(GPUQ),'run','--name','femto1:'+a.stage,'--vram','1','--ram','1.5','--cwd',str(ROOT),'--',*command]
    try:result=subprocess.run(queued,cwd=ROOT,env=env,timeout=900,check=False)
    except subprocess.TimeoutExpired:raise SystemExit('Queue/Blender deadline reached; inspect own queue process before resuming')
    raise SystemExit(result.returncode)

if __name__=='__main__':main()
