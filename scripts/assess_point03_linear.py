"""K640 gates. No new propagation and no closure without a new N626 probe."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from point03_linear_detector import Detector
import numpy as np
from predict_point03_linear import sha, ROOT

def assess(prediction_path,h_path):
    prediction=json.loads(prediction_path.read_text(encoding='utf-8'))
    for p,d in prediction['source_sha256_map'].items():assert sha(p)==d
    h=json.loads((h_path/'assessment.json').read_text(encoding='utf-8'))
    assert h['integrity_pass'] and [r['N'] for r in h['rows']]==[256,320,400,500,640]
    r=h['rows'][-1];coarse=r['coarse_segments'];fine=r['fine_segments'];det=Detector();methods={}
    assert prediction['created_utc']<h['created_utc']
    for segments in (coarse,fine):
        sol=r['solutions'][str(segments)];assert sha(sol['field_path'])==sol['field_sha256']
        with np.load(sol['field_path'],allow_pickle=False) as data:field=data['field']
        methods[str(segments)]=det.measure(field,640,r['P_in'])
    g=json.loads((ROOT/'resultados/codex/point03_reconstructed_20261007_G2/assessment.json').read_text(encoding='utf-8'))
    c=next(c for c in g['rows'] if c['N']==640 and c['dz_m']==.3125e-6)
    assert sha(c['field_path'])==c['field_sha256']
    with np.load(c['field_path'],allow_pickle=False) as data:adi=det.measure(data['field'],640,r['P_in'])
    gates={};agreement=abs(methods[str(fine)]['field']['P_core']-methods[str(fine)]['intensity']['P_core'])
    for m in ('field','intensity'):
        actual=methods[str(fine)][m]['P_core'];last=prediction['rows'][-1]['methods'][m]['P_core'];frozen=prediction['predictions'][m]['640']
        residual=abs(actual-frozen['prediction']) if frozen else None;limit=.1*abs(actual-last)
        temporal=abs(adi[m]['P_core']-actual);reference=abs(methods[str(coarse)][m]['P_core']-actual)
        order=prediction['spatial'][m].get('orders',[None,None])[-1]
        space=1.25*abs(actual-last)/(1.28**min(order,2)-1) if order is not None and order>0 else None
        terms=dict(space=space,temporal=temporal,detector=agreement,quadrature=methods[str(fine)][m]['change'],reference=reference)
        combined=sum(terms.values()) if space is not None else None
        gates[m]=dict(actual=actual,prediction=frozen,residual=residual,limit=limit,holdout_pass=residual is not None and abs(actual-last)>1e-12 and residual<=limit,terms=terms,combined=combined,uncertainty_pass=combined is not None and combined<=1e-3 and combined<=.01*actual,temporal_pass=temporal<=1e-6,reference_pass=reference<=1e-10,quadrature_pass=terms['quadrature']<=1e-10)
    passed=prediction['primary_pass'] and r['reference_field_difference']<=1e-9 and all(all(v[k] for k in ('holdout_pass','uncertainty_pass','temporal_pass','reference_pass','quadrature_pass')) for v in gates.values())
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),prediction_path=str(prediction_path),prediction_sha256=sha(prediction_path),h_assessment_sha256=sha(h_path/'assessment.json'),integrity_pass=True,rows=[dict(N=640,methods=methods)],gates=gates,K640_pass=passed,H2_closed=h['point03_closed'],N626_permitted=passed and not h['point03_closed'],point03_closed=False,scope='K640 screening only; new N626 prospectively predicted probe mandatory for K acceptance.')

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--prediction',type=Path,required=True);p.add_argument('--h',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    report=assess(args.prediction,args.h)
    with args.output.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(report['gates']));return 0
if __name__=='__main__':raise SystemExit(main())
