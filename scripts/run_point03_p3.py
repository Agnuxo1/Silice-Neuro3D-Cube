"""Confirm fine-regime hypothesis with a new blind field; retain P2 rejection."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
import run_point03_p2 as p2
from run_point03_exponential import ROOT,sha,write,guard


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def predict():
    old=ROOT/'resultados/codex/point03_fixed_domain_20261007_P2'
    audit=read(old/'integrity_audit.json');assert audit['integrity_pass'] and not audit['scientific_pass'] and audit['stage']=='prerequisites_failed'
    coarse=read(old/'coarse_assessment.json');old_prediction=read(old/'prediction.json');methods={}
    assert all(row['eligible'] for row in coarse.values())
    for method in ('field','intensity'):
        values=old_prediction['methods'][method];powers=values['powers'][1:];order=values['orders'][-1]
        assert 1.8<=order<=2.2
        forecast=powers[-1]+(powers[-1]-powers[-2])*(1-(640/800)**order)/((640/500)**order-1)
        methods[method]=dict(powers=powers,orders=[order],prediction=forecast)
    sources=[Path(__file__).resolve(),ROOT/'scripts/audit_point03_p3.py',ROOT/'Docs/POINT-03-P3-CONTRACT.md',old/'prediction.json',old/'coarse_assessment.json',old/'integrity_audit.json',old/'execution.json']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),methods=methods,primary_M=[400,500,640],holdout_M=800,diagnostic_M320_retained=True,P2_pass=False,point03_closed=False,source_sha256={str(path):sha(path) for path in sources})


def run(out):
    start=time.monotonic();assert not out.exists() and out.is_relative_to(ROOT/'resultados/codex');out.mkdir()
    e=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),children=[],solutions={},point03_closed=False)
    manifest={}
    try:
        prediction=read(ROOT/'resultados/codex/point03_p3_prediction_20261008.json')
        for path,digest in prediction['source_sha256'].items():assert sha(path)==digest
        assert prediction['created_utc']<e['started_utc']
        assert read(ROOT/'resultados/codex/point03_p2_cost_20261007.json')['pass_']
        old=ROOT/'resultados/codex/point03_fixed_domain_20261007_P2';coarse=read(old/'coarse_assessment.json')
        e['reused_P2_execution_path']=str(old/'execution.json');e['reused_P2_execution_sha256']=sha(old/'execution.json')
        control=p2.gaussian_control();write(out/'gaussian_control.json',control);assert control['pass_']
        fine=p2.prepare800(out,start)
        parent_manifest=read(old/'coarse_manifest.json')
        area=parent_manifest['plan'][0]['cladding_area_m2'];assert abs(fine['cladding_area_m2']/area-1)<=1e-12
        sources=[Path(__file__).resolve(),ROOT/'scripts/audit_point03_p3.py',ROOT/'Docs/POINT-03-P3-CONTRACT.md',ROOT/'scripts/run_point03_p2.py',ROOT/'scripts/audit_point03_p2.py',ROOT/'resultados/codex/point03_p3_prediction_20261008.json',old/'coarse_manifest.json',old/'coarse_assessment.json',old/'integrity_audit.json',old/'prediction.json',old/'execution.json',out/'geometry_source.txt',out/'geometry_report.json',out/'geometry_selection.json',out/'gaussian_control.json']
        manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),plan=[fine],source_sha256={**parent_manifest['source_sha256'],**{str(path):sha(path) for path in sources}},ghost_bounds_m=[-64e-6,64e-6],numerical_threads=1)
        path=out/'manifest.json';write(path,manifest)
        e.update(manifest_sha256=sha(path),prediction_sha256=sha(ROOT/'resultados/codex/point03_p3_prediction_20261008.json'))
        e['solutions']={f'E{total}':p2.trajectory(out,path,e,800,total,'E',start) for total in (29,41)}
        e['solutions']['F64']=p2.trajectory(out,path,e,800,64,'F',start)
        assessment=p2.final_assessment(coarse,prediction,fine,e['solutions']);write(out/'assessment.json',assessment)
        e.update(status='completed',scientific_pass=assessment['scientific_pass'],assessment_sha256=sha(out/'assessment.json'))
    except Exception as error:e.update(status='failed',error=str(error),error_type=type(error).__name__,diagnostic=traceback.format_exc())
    e.update(finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_s=time.monotonic()-start,sources_unchanged=all(sha(path)==digest for path,digest in manifest.get('source_sha256',{}).items()))
    write(out/'execution.json',e);print(json.dumps({key:e.get(key) for key in ('status','scientific_pass','elapsed_s','error')}),flush=True)
    return 0 if e.get('scientific_pass') else 2 if e['status']=='completed' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--prediction',action='store_true');parser.add_argument('--out',type=Path);args=parser.parse_args()
    if args.prediction:
        result=predict();write(ROOT/'resultados/codex/point03_p3_prediction_20261008.json',result);print(json.dumps(result));raise SystemExit(0)
    raise SystemExit(run(args.out.resolve()))
