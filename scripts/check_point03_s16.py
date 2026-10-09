"""Known-law and simultaneous-observable S16 controls; no optical reports read."""
from datetime import datetime,timezone
import argparse
import json
from pathlib import Path
from forecast_point03_s16 import ROOT,AUDITS,make_forecasts,sha
from audit_point03_s16_forecast import recompute,valid_header


def fixture(values):
    return [dict(integrity_pass=True,temporal_precision_pass=True,
                 powers={'P6_32768':{key:series[i] for key,series in values.items()}},
                 power_differences={'field':1e-15,'intensity':1e-15},
                 purpose='Manufactured scalar-law software control only') for i in range(3)]


if __name__=='__main__':
    h=[.546875,.4375,.35,.28]
    values={'field':[.32+1e-4*x**2 for x in h],
            'intensity':[.31+2e-4*x**3 for x in h]}
    inputs=fixture(values)
    positive=make_forecasts(inputs)
    assert positive['forecast_eligible'] and positive['reserved_mesh_generation_allowed']
    for key in values:
        result=positive['observables'][key]
        assert abs(result['prediction']-values[key][3])<=1e-12
        independent=recompute(values[key][:3],[1e-15]*3)
        assert independent['prediction']==result['prediction'] and independent['eligible']
    invalid_values=dict(values,intensity=[.31,.33,.32])
    negative=make_forecasts(fixture(invalid_values))
    assert negative['observables']['field']['eligible']
    assert not negative['forecast_eligible'] and not negative['reserved_mesh_generation_allowed']
    noisy=fixture(values)
    for item in noisy:
        item['power_differences']['intensity']=1e-3
    unresolved=make_forecasts(noisy)
    assert unresolved['observables']['field']==positive['observables']['field']
    assert not unresolved['forecast_eligible']
    false_gate=fixture(values)
    false_gate[-1]['temporal_precision_pass']=False
    try:
        make_forecasts(false_gate)
    except AssertionError:
        false_prerequisite_rejected=True
    else:
        raise AssertionError('Failed temporal prerequisite accepted')
    flat=make_forecasts(fixture({'field':[.32]*3,'intensity':[.31]*3}))
    assert not flat['forecast_eligible']
    header=dict(primary='P6_32768',h_um=[.546875,.4375,.35],point03_closed=False,
                reserved_mesh_generated=False,optical_fields_generated=False,
                nominal_refinement_ratio=1.25,observables=positive['observables'],audit_paths=AUDITS)
    valid_header(header)
    for invalid in (dict(header,nominal_refinement_ratio=1.5),
                    dict(header,audit_paths=list(reversed(AUDITS)))):
        try:
            valid_header(invalid)
        except AssertionError:
            pass
        else:
            raise AssertionError('Altered spatial series metadata accepted')
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),controls_pass=True,
                known_laws=[2,3],both_observables_mandatory=True,
                temporal_discrepancy_is_observable_specific=True,
                false_temporal_prerequisite_rejected=false_prerequisite_rejected,
                zero_increments_rejected=True,altered_series_metadata_rejected=True,
                no_T96_results_read=True,optical_fields_created=0,
                sources={name:sha(ROOT/'scripts'/name) for name in (
                    'forecast_point03_s16.py','audit_point03_s16_forecast.py','check_point03_s16.py',
                    'point03_fem_spatial.py')},point03_closed=False)
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'resultados/codex/point03_s16_controls_20261009.json')
    with parser.parse_args().out.open('x',encoding='utf-8') as stream:
        json.dump(record,stream,indent=2)
        stream.write('\n')
    print(json.dumps(record))
