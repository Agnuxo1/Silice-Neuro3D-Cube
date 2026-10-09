"""New CPU analytic controls only; no GPU imports and no historical fields."""
import argparse,json
from pathlib import Path
import numpy as np
from point03_render_pipeline_reference import barycentric,reference,metrics,MODES
from point03_render_reference import TRIANGLE

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    np.testing.assert_allclose(barycentric(TRIANGLE[:,0],TRIANGLE[:,1]),np.eye(3),atol=2e-16)
    c=TRIANGLE.mean(axis=0)
    np.testing.assert_allclose(barycentric(*c),[1/3]*3,atol=2e-16)
    b=barycentric(np.array([-.2,.1]),np.array([.0,.2]))
    np.testing.assert_allclose(b.sum(axis=-1),1,atol=2e-16)
    groups=[]
    for mode in MODES:
        e,i,m=reference(mode,64);r=e.astype(np.float32)
        assert metrics(r,e,i,m)['accuracy_pass']
        assert not metrics(r[::-1].copy(),e,i,m)['accuracy_pass']
        changed=r.copy();changed[i,0]+=.002
        assert not metrics(changed,e,i,m)['accuracy_pass']
        groups.append(mode)
    bad=[('missing',64),(MODES[0],63),(MODES[0],64.),(MODES[0],True)]
    for mode,n in bad:
        try:reference(mode,n)
        except ValueError:pass
        else:raise AssertionError('invalid input accepted')
    e,i,m=reference(MODES[0],64)
    for r in (e,e.astype(np.float32)[:,:-1],np.full(e.shape,np.nan,dtype=np.float32)):
        try:metrics(r,e,i,m)
        except ValueError:pass
        else:raise AssertionError('invalid pixels accepted')
    result=dict(pass_all=True,analytic_controls=3,mark_groups=groups,
                invalid_input_groups=4,invalid_pixel_groups=3,gpu_execution=False,new_t96_field=False)
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps(result))
if __name__=='__main__':main()
