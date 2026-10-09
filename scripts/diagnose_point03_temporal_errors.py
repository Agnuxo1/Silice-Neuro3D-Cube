"""Post-hoc arithmetic diagnosis of retained temporal powers, no new gate."""
import argparse
from datetime import datetime,timezone
import json
import math
from pathlib import Path
from run_point03_exponential import ROOT,sha,write

def run():
    gp=ROOT/'resultados/codex/point03_reconstructed_20261007_G2/assessment.json';hp=ROOT/'resultados/codex/point03_exponential_20261007_H2/assessment.json'
    g=json.loads(gp.read_text(encoding='utf-8'));h=json.loads(hp.read_text(encoding='utf-8'));rows=[]
    assert g['integrity_pass'] and h['integrity_pass'] and h['reference_consistency_pass']
    for n in (400,500):
        reference=next(r for r in h['rows'] if r['N']==n)
        cases=sorted([r for r in g['rows'] if r['N']==n],key=lambda r:r['dz_m'],reverse=True)
        assert [r['dz_m'] for r in cases]==[.625e-6,.3125e-6,.15625e-6]
        assert len({c['input_sha256'] for c in cases})==1
        for c in cases:assert sha(c['input_path'])==c['input_sha256'] and sha(c['field_path'])==c['field_sha256']
        for method in ('field','intensity'):
            exact=reference['methods'][str(reference['fine_segments'])][method]['P_core'];powers=[c['methods'][method]['P_core'] for c in cases];errors=[p-exact for p in powers]
            differences=[powers[i]-powers[i+1] for i in (0,1)]
            error_orders=[math.log2(abs(errors[i]/errors[i+1])) if abs(errors[i+1])>1e-12 and errors[i]*errors[i+1]>0 else None for i in (0,1)]
            richardson_order=math.log2(abs(differences[0]/differences[1])) if abs(differences[1])>1e-12 and differences[0]*differences[1]>0 else None
            rows.append(dict(N=n,method=method,reference=exact,dz_um=[c['dz_m']*1e6 for c in cases],powers=powers,signed_reference_errors=errors,absolute_reference_errors=list(map(abs,errors)),error_ratios_observed_orders=error_orders,successive_differences_order=richardson_order,original_order_gate_pass=richardson_order is not None and 1.8<=richardson_order<=2.2,fine_direct_error_pass=abs(errors[-1])<=2.5e-7,mid_direct_error_pass=abs(errors[1])<=1e-6))
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),source_sha256={str(p):sha(p) for p in (gp,hp,Path(__file__))},rows=rows,diagnostic_only=True,post_hoc_known_results=True,point03_closed=False,scope='Dimensionless core power error at fixed N, relative to the H semidiscrete reference. Not a continuum error bound, causal attribution, phase validation or replacement of old gates.')

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=run();write(a.output,r);print(json.dumps(r['rows']));return 0
if __name__=='__main__':raise SystemExit(main())
