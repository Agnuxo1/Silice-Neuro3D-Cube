"""Known power laws and falsification controls; no optical input files."""
import argparse
from datetime import datetime,timezone
from pathlib import Path
from point03_fem_spatial import forecast, assess
from run_point03_exponential import ROOT,sha,write


def run(out):
    assert not out.exists()
    h=[.546875,.4375,.35,.28]
    rows=[]
    for p in (.75,1.,2.,3.,5.):
        values=[.32+1e-4*x**p for x in h]
        pred=forecast(values[:3],[1e-15]*3)
        result=assess(values,pred,[1e-15]*4,1e-12,1e-14,0.)
        assert pred['eligible'] and result['spatial_pass']
        assert abs(pred['order']-p)<1e-7 and abs(result['order']-p)<1e-7
        assert abs(pred['prediction']-values[3])<1e-12
        truth_error=abs(values[3]-.32)
        assert result['indicators']['total']>=truth_error
        rows.append(dict(kind='known_law',known_order=p,values=values,known_continuum=.32,known_error=truth_error,forecast=pred,result=result))
    values=rows[2]['values'];pred=rows[2]['forecast']
    perturbed=values[:3]+[values[3]+.5*abs(values[3]-values[2])]
    rejected=assess(perturbed,pred,[1e-15]*4,1e-12,1e-14,0.)
    assert not rejected['spatial_pass'] and not rejected['gates']['prospective_prediction']
    rows.append(dict(kind='wrong_holdout',values=perturbed,result=rejected))
    osc=forecast([.31,.33,.32],[1e-15]*3)
    assert not osc['eligible'] and not osc['monotone']
    rows.append(dict(kind='oscillation',result=osc))
    for p in (.1,7.):
        vals=[.32+1e-4*x**p for x in h[:3]]
        rejected=forecast(vals,[1e-15]*3)
        assert not rejected['eligible']
        rows.append(dict(kind='order_outside_range',known_order=p,values=vals,result=rejected))
    noisy=forecast(values[:3],[1e-3]*3)
    assert not noisy['eligible'] and not noisy['resolved_above_time_discrepancy']
    rows.append(dict(kind='unresolved_time',result=noisy))
    large=assess(values,pred,[1e-15]*4,1e-12,.002,0.)
    assert not large['spatial_pass'] and not large['gates']['total_indicator']
    rows.append(dict(kind='large_indicator',result=large))
    sources=[Path(__file__).resolve(),ROOT/'scripts/point03_fem_spatial.py',ROOT/'Docs/POINT-03-P5D-SPATIAL-CONTRACT.md',ROOT/'Docs/POINT-03-P5D-EVALUATOR-CONTROL.md']
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),controls_pass=True,no_T96_results_read=True,
                cases_checked=len(rows),rows=rows,source_sha256={str(p):sha(p) for p in sources},point03_closed=False)
    write(out,report)
    print(dict(controls_pass=True,cases_checked=len(rows),no_T96_results_read=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    run(args.out.resolve())
