"""K preregistered detector predictions: only four H1 fine references."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from point03_linear_detector import Detector
import numpy as np
from assess_point03_exponential import spatial

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def predict(powers,n):
    a,b,c=powers[-3:];d1=b-a;d2=c-b
    if abs(d1)<=1e-12 or abs(d2)<=1e-12 or d1*d2<=0:return None
    p=math.log(abs(d1/d2))/math.log(1.25)
    if p<=0:return None
    infinity=c+d2/(1.25**p-1)
    return dict(N=n,order=p,infinity=infinity,prediction=infinity+(c-infinity)*(500/n)**p)

def run(preflight):
    assert preflight['pass_']
    source=ROOT/'resultados/codex/point03_exponential_20261007_H1/prediction.json'
    old=json.loads(source.read_text(encoding='utf-8'))
    assert [r['N'] for r in old['rows']]==[256,320,400,500]
    det=Detector();rows=[]
    for r in old['rows']:
        sol=r['solutions']['8'];p=Path(sol['field_path'])
        assert sha(p)==sol['field_sha256']
        with np.load(p,allow_pickle=False) as data:field=data['field']
        methods=det.measure(field,r['N'],r['P_in'])
        assert all(0<=v['P_core']<=r['P_total']+1e-8 and v['change']<=1e-10 for v in methods.values())
        rows.append(dict(N=r['N'],field_path=str(p),field_sha256=sha(p),P_in=r['P_in'],methods=methods))
    powers={m:[r['methods'][m]['P_core'] for r in rows] for m in ('field','intensity')}
    screens={m:spatial(ps) for m,ps in powers.items()}
    predictions={m:{str(n):predict(ps,n) for n in (640,626)} for m,ps in powers.items()}
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),source_path=str(source),source_sha256=sha(source),source_sha256_map={str(p):sha(p) for p in (Path(__file__),ROOT/'scripts/point03_linear_detector.py',ROOT/'scripts/assess_point03_linear.py',ROOT/'scripts/assess_point03_exponential.py',ROOT/'Docs/POINT-03-LINEAR-DETECTOR-CONTRACT.md',ROOT/'resultados/codex/point03_linear_detector_preflight_20261007.json')},rows=rows,spatial=screens,predictions=predictions,primary_pass=all(s['pass_'] for s in screens.values()),point03_closed=False,N640_new_functionals_not_measured=True,N626_not_prepared_or_propagated=True,scope='Bilinear core-power convergence; same local scalar model, no full field/phase/Maxwell claim.')

def selfcheck():
    h=[1/n for n in (256,320,400,500)]
    for p in (.5,2.,4.):
        values=[.3-.2*x**p for x in h]
        for n in (626,640):
            result=predict(values,n);assert result is not None
            assert abs(result['prediction']-(.3-.2/n**p))<1e-12
    assert predict([1,1,1,1],640) is None
    assert predict([.2,.3,.2,.3],640) is None
    return dict(pass_=True,manufactured_orders=[.5,2,4],targets=[626,640],constant_and_oscillation_rejected=True)

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--selfcheck-only',action='store_true');args=p.parse_args()
    controls=selfcheck()
    report=controls if args.selfcheck_only else run(json.loads((ROOT/'resultados/codex/point03_linear_detector_preflight_20261007.json').read_text(encoding='utf-8')))
    report['predictor_selfcheck']=controls.copy()
    with args.output.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({k:report[k] for k in ('primary_pass','spatial','predictions') if k in report}))
    return 0
if __name__=='__main__':raise SystemExit(main())
