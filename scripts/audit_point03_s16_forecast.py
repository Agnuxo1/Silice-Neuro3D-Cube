"""Independent S16 forecast recomputation; never import the forecast evaluator."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def recompute(powers,differences):
    assert len(powers)==len(differences)==3
    assert all(math.isfinite(v) and v>0 for v in powers)
    assert all(math.isfinite(v) and v>=0 for v in differences)
    delta01=powers[1]-powers[0]
    delta12=powers[2]-powers[1]
    monotone=delta01*delta12>0
    order=math.log(delta01/delta12)/math.log(1.25) if monotone else None
    resolved=min(abs(delta01),abs(delta12))>20*max(differences)
    eligible=bool(monotone and order is not None and .5<=order<=6 and resolved)
    prediction=powers[2]+delta12/1.25**order if eligible else None
    return dict(increments=[delta01,delta12],order=order,eligible=eligible,prediction=prediction)


def valid_header(result):
    assert result['primary']=='P6_32768' and result['h_um']==[.546875,.4375,.35]
    assert not result['point03_closed'] and not result['reserved_mesh_generated'] and not result['optical_fields_generated']
    assert result['nominal_refinement_ratio']==1.25
    assert set(result['observables'])=={'field','intensity'}
    assert result['audit_paths']==[
        'resultados/codex/point03_d16_refine_recovery_20261008/integrity_audit.json',
        'resultados/codex/point03_d16_mid_recovery_20261009/local_integrity_audit.json',
        'resultados/codex/point03_d16_fine_time_20261009/local_integrity_audit.json']


def audit(out):
    result=read(out/'forecast.json')
    valid_header(result)
    for path,digest in result['source_sha256'].items():
        assert sha(ROOT/path)==digest
    inputs=[read(ROOT/path) for path in result['audit_paths']]
    assert all(a['integrity_pass'] and a['temporal_precision_pass'] for a in inputs)
    assert all(a['local_recalculation'] for a in inputs[1:])
    independent={}
    for detector in ('field','intensity'):
        powers=[a['powers']['P6_32768'][detector] for a in inputs]
        differences=[a['power_differences'][detector] for a in inputs]
        computed=recompute(powers,differences)
        stored=result['observables'][detector]
        assert stored['powers']==powers and stored['temporal_differences']==differences
        for key in ('increments','order','eligible','prediction'):
            assert stored[key]==computed[key]
        independent[detector]=computed
    approved=all(v['eligible'] for v in independent.values())
    assert approved==result['forecast_eligible']==result['reserved_mesh_generation_allowed']
    assert result['status']==('eligible' if approved else 'negative')
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,
                 forecast_eligible=approved,reserved_mesh_generation_allowed=approved,
                 independent=independent,forecast_sha256=sha(out/'forecast.json'),
                 auditor_sha256=sha(Path(__file__)),point03_closed=False)
    with (out/'integrity_audit.json').open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,indent=2,allow_nan=False)
        stream.write('\n')
    print(json.dumps(receipt))


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--out',type=Path,required=True)
    audit(parser.parse_args().out.resolve())
