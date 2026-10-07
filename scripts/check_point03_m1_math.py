"""Analytical scalar controls only; no optical input or geometry read."""
from datetime import datetime,timezone
import json
from pathlib import Path
from run_point03_exponential import ROOT,sha,write
from run_point03_m1 import order
from audit_point03_m1 import observed

cases=[]
for ns in ([320,400,500],[400,500,640],[500,640,767]):
    for p in (.5,1.,2.,3.,6.):
        for coefficient in (-1e-4,1e-4):
            powers=[.334+coefficient*(640/n)**p for n in ns]
            a=order(ns,powers);b=observed(ns,powers)
            assert b is not None and abs(a-p)<=1e-8 and abs(b-p)<=1e-8
            cases.append(dict(N=ns,truth_order=p,coefficient=coefficient,controller_order=a,auditor_order=b))
forecasts=[]
for p in (.5,1.,2.,3.,6.):
    for coefficient in (-1e-4,1e-4):
        powers=[.334+coefficient*(640/n)**p for n in (400,500,640)]
        estimated=order([400,500,640],powers)
        forecast=powers[-1]+(powers[-1]-powers[-2])*(1-(640/767)**estimated)/((640/500)**estimated-1)
        truth=.334+coefficient*(640/767)**p
        assert abs(forecast-truth)<=1e-12
        forecasts.append(dict(truth_order=p,coefficient=coefficient,truth=truth,prediction=forecast,error=abs(forecast-truth)))
rejections=[]
for name,powers in [('constant',[.334]*3),('nonmonotonic',[.333,.335,.334]),('negative_order',[.334+1e-4*(640/n)**-1 for n in (400,500,640)])]:
    rejected=False
    try:order([400,500,640],powers)
    except (AssertionError,ValueError):rejected=True
    assert rejected and observed([400,500,640],powers) is None
    rejections.append(dict(case=name,controller_rejected=True,auditor_rejected=True))
paths=[Path(__file__).resolve(),ROOT/'scripts/run_point03_m1.py',ROOT/'scripts/audit_point03_m1.py',ROOT/'Docs/POINT-03-M1-MATH-CONTROL-CONTRACT.md']
result=dict(created_utc=datetime.now(timezone.utc).isoformat(),pass_=True,no_optical_data_read=True,no_propagation=True,order_cases=cases,forecasts=forecasts,rejections=rejections,source_sha256={str(path):sha(path) for path in paths},scope='Scalar analytical formula verification only; not validation of the optical convergence hypothesis.')
write(ROOT/'resultados/codex/point03_m1_math_control_20261007.json',result)
print(json.dumps(dict(pass_=True,order_cases=len(cases),forecasts=len(forecasts),negative_controls=len(rejections))))
