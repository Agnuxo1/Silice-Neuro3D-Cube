"""Synthetic rejection controls; no real fields or GPU imports."""
import argparse,copy,json
from pathlib import Path
from point03_render_p3_gate import validate_pipeline,USED
from point03_render_pipeline_reference import MODES
from point03_render_reference import RESOLUTIONS

def fixture():
    return dict(integrity_pass=True,strict_metric_agreement_pass=True,backend='OPENGL',marker_frames=30,
                accuracy_pass=False,physical_validation=False,network_validated=False,p2_field_validated=False,
                point03_closed=False,general_speedup_claim=False,
                rows=[dict(marker=m,resolution=n,accuracy_pass=m in USED,max_channel_error=1e-8 if m in USED else 1e-4,outside_max=0.) for m in MODES for n in RESOLUTIONS])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    good=fixture();validate_pipeline(good,'OPENGL');bad=[]
    for k,v in [('integrity_pass',False),('strict_metric_agreement_pass',False),('backend','VULKAN'),('marker_frames',29),('accuracy_pass',True)]+[(k,True) for k in ('physical_validation','network_validated','p2_field_validated','point03_closed','general_speedup_claim')]:
        b=copy.deepcopy(good);b[k]=v;bad.append(b)
    for modify in ('missing','duplicate','unknown','precision','outside','false','nan'):
        b=copy.deepcopy(good)
        if modify=='missing':b['rows'].pop()
        if modify=='duplicate':b['rows'][1]=copy.deepcopy(b['rows'][0])
        if modify=='unknown':b['rows'][0]['marker']='other'
        if modify=='precision':b['rows'][0]['max_channel_error']=2e-6
        if modify=='outside':b['rows'][0]['outside_max']=2e-7
        if modify=='false':b['rows'][0]['accuracy_pass']=False
        if modify=='nan':b['rows'][0]['max_channel_error']=float('nan')
        bad.append(b)
    for b in bad:
        try:validate_pipeline(b,'OPENGL')
        except ValueError:pass
        else:raise AssertionError('invalid calibration accepted')
    with a.output.open('x',encoding='utf-8') as f:json.dump(dict(pass_all=True,rejections=len(bad),full_negative_retained=True,gpu_execution=False,new_t96_field=False),f,indent=2)
    print(json.dumps(dict(pass_all=True,rejections=len(bad))))
if __name__=='__main__':main()
