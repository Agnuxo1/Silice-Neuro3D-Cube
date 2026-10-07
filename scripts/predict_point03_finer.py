"""Prospective finer-grid diagnostic; never prepares or propagates geometry."""
from datetime import datetime,timezone
import json
from pathlib import Path
from run_point03_exponential import ROOT,sha,write
from point03_scatter_uncertainty import evaluate,predict

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

kp=ROOT/'resultados/codex/point03_linear_prediction_20261007.json'
k640=ROOT/'resultados/codex/point03_linear_K640_20261007.json'
k626=ROOT/'resultados/codex/point03_linear_probe_20261007_K626'
assert read(k626/'execution.json')['status']=='completed' and read(k626/'integrity_audit.json')['integrity_pass']
assert read(ROOT/'resultados/codex/point03_exponential_20261007_H2/integrity_audit.json')['integrity_pass']
initial=read(kp)['rows'];last=read(k640);probe=read(k626/'assessment.json')
rows=[dict(N=row['N'],powers={method:row['methods'][method]['P_core'] for method in ('field','intensity')}) for row in initial]
rows.append(dict(N=640,powers={method:last['gates'][method]['actual'] for method in ('field','intensity')}))
extra=dict(N=626,powers={method:probe['gates'][method]['actual'] for method in ('field','intensity')})
models={};forecasts={}
for method in ('field','intensity'):
    five=evaluate([128/row['N'] for row in rows],[row['powers'][method] for row in rows])
    six=evaluate([128/row['N'] for row in rows+[extra]],[row['powers'][method] for row in rows+[extra]])
    models[method]=dict(five=five,six=six)
    forecasts[method]={}
    for n in (767,959,1199):
        base=predict(five,640/n);included=predict(six,640/n)
        envelope=max(base['envelope_band'],abs(included['prediction']-base['prediction'])+included['envelope_band'])
        forecasts[method][str(n)]=dict(center=base['prediction'],envelope_radius=envelope,five=base,six=included,low=base['prediction']-envelope,high=base['prediction']+envelope)
sources=[Path(__file__).resolve(),ROOT/'Docs/POINT-03-FINER-PREDICTION-CONTRACT.md',ROOT/'scripts/point03_scatter_uncertainty.py',kp,k640,k626/'execution.json',k626/'assessment.json',k626/'integrity_audit.json']
result=dict(created_utc=datetime.now(timezone.utc).isoformat(),no_new_geometry_or_propagation=True,point03_closed=False,rows=rows,negative_probe_in_sensitivity=extra,K626_still_negative=not probe['scientific_pass'],K626_reference_power_differences={method:probe['gates'][method]['reference_power_difference'] for method in ('field','intensity')},models=models,forecasts=forecasts,source_sha256={str(p):sha(p) for p in sources},scope='Conditional prospective diagnostic only; no acceptance criterion or continuum guarantee.')
write(ROOT/'resultados/codex/point03_finer_prediction_20261007_M0.json',result)
print(json.dumps(dict(point03_closed=False,forecasts={m:{n:{key:v[key] for key in ('center','envelope_radius')} for n,v in values.items()} for m,values in forecasts.items()})))
