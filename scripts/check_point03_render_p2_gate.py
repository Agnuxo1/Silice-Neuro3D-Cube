"""New controls of false calibration/zero timing gates; no prior raw field read."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from point03_render_p2_gate import validate_p0, ns_seconds


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    good={k:True for k in ('integrity_pass','accuracy_pass','layout_prediction_pass','old_export_rejected')}
    good.update(marker_frames=6,physical_validation=False,p2_field_validated=False,network_validated=False,point03_closed=False)
    validate_p0(good)
    rejected=0
    for key in ('integrity_pass','accuracy_pass','layout_prediction_pass','old_export_rejected'):
        for value in (False,1,None):
            a=dict(good);a[key]=value
            try:validate_p0(a)
            except ValueError:rejected+=1
            else:raise AssertionError('invalid prerequisite accepted')
    for key,value in [('marker_frames',5),('marker_frames',6.0),('network_validated',True),('physical_validation',True)]:
        a=dict(good);a[key]=value
        try:validate_p0(a)
        except ValueError:rejected+=1
        else:raise AssertionError('invalid scope accepted')
    for x in (1,221000,765300,119999999999):assert ns_seconds(x)==x/1e9
    duration_rejects=0
    for x in (0,-1,True,False,1.0,float('inf'),120000000001):
        try:ns_seconds(x)
        except ValueError:duration_rejects+=1
        else:raise AssertionError('invalid duration accepted')
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'pass':True,
            'accepted_calibration_cases':1,'rejected_calibration_cases':rejected,
            'accepted_ns_cases':4,'rejected_ns_cases':duration_rejects,
            'gpu_execution':False,'reads_prior_raw_frames':False,'new_t96_field':False,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with args.output.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:result[k] for k in ['pass','rejected_calibration_cases','rejected_ns_cases','gpu_execution']}))


if __name__=='__main__':main()
