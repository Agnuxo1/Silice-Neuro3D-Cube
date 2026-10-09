"""Apply registered J diagnostic only to completed, audited H references."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from point03_scatter_uncertainty import evaluate

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(h):
    audit=json.loads((h/'integrity_audit.json').read_text(encoding='utf-8'));assert audit['integrity_pass']
    report=json.loads((h/'assessment.json').read_text(encoding='utf-8'))
    assert report['integrity_pass'] and report['reference_consistency_pass']
    assert [r['N'] for r in report['rows']]==[256,320,400,500,640]
    execution=json.loads((h/'execution.json').read_text(encoding='utf-8'));assert execution['status']=='completed'
    assert sha(execution['assessment_path'])==execution['assessment_sha256']
    manifest=json.loads(Path(execution['manifest_path']).read_text(encoding='utf-8'))
    for p,d in manifest['source_sha256'].items():assert sha(p)==d
    models={}
    for method in ('field','intensity'):
        powers=[]
        for r in report['rows']:
            fine=str(r['fine_segments']);sol=r['solutions'][fine];assert sha(sol['field_path'])==sol['field_sha256']
            powers.append(r['methods'][fine][method]['P_core'])
        models[method]=evaluate([128e-6/r['N'] for r in report['rows']],powers)
    controls=ROOT/'resultados/codex/point03_scatter_uncertainty_preflight_20261007_run2.json'
    preflight=json.loads(controls.read_text(encoding='utf-8'));assert preflight['pass_']
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),source_sha256={str(p):sha(p) for p in (h/'assessment.json',h/'integrity_audit.json',Path(__file__),ROOT/'scripts/point03_scatter_uncertainty.py',ROOT/'Docs/POINT-03-SCATTER-DIAGNOSTIC-CONTRACT.md',controls)},models=models,diagnostic_only=True,H_scientific_pass=report['scientific_pass'],point03_closed=False,selected_indicator_manufactured_controls_pass=preflight['selected_indicator_controls_pass'],envelope_manufactured_controls_pass=preflight['envelope_controls_pass'],scope='Conditional engineering indicators from five H references. No replacement of E/G/H gates, new propagation, confidence level, rigorous bound or independent validation.')

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--h',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();report=run(args.h)
    with args.output.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({m:dict(selected=vals['intervals'][-1],envelope=vals['envelope_intervals'][-1]) for m,vals in report['models'].items()}));return 0
if __name__=='__main__':raise SystemExit(main())
