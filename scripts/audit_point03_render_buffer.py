"""Independent fixed-marker audit; no optical or speedup claim."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import numpy as np
from point03_render_buffer_reference import expected, old_export_prediction, check_marker, SIZES, CASES

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True)
    args=ap.parse_args(); out=args.out.resolve(); out.relative_to(ROOT/'resultados/codex')
    r=json.loads((out/'render_result.json').read_text()); g=json.loads((out/'guard.json').read_text())
    assert r['status']=='completed' and g['status']=='completed' and g['child_finished']
    assert r['gpu_execution'] and r['marker_only'] and not r['new_t96_field']
    profile=ROOT/g['profile_relative']; p=json.loads(profile.read_text())
    assert hashlib.sha256(profile.read_bytes()).hexdigest()==g['profile_sha256']==r['profile_sha256']
    assert p['sources_sha256']==g['sources_sha256']==r['sources_sha256']
    assert p['blender_sha256']==g['blender_sha256']
    assert hashlib.sha256(Path(p['guard_python']).read_bytes()).hexdigest()==p['guard_python_sha256']
    assert hashlib.sha256(Path(p['blender_executable']).read_bytes()).hexdigest()==p['blender_sha256']
    for name,digest in p['sources_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    assert r['engine']['version'].startswith('4.5.14') and '3090' in r['engine']['renderer']
    assert 'NVIDIA' in r['engine']['renderer'].upper() and r['engine']['backend']=='OPENGL'
    assert g['elapsed_child_with_startup_s']<=120
    assert datetime.fromisoformat(g['finished_utc'])<=datetime(2026,10,9,13,45,tzinfo=timezone.utc)
    assert g['samples'][0]['available_ram_gib']>=8
    assert all(s['available_ram_gib']>=6 and s['vram_used_gib']<=4 and s['temperature_c']<=80
               and s.get('owned_rss_gib',0)<=1.5 for s in g['samples'])
    assert all(v=='1' for v in r['runtime']['thread_caps'].values())
    expected_keys={(case,w,h) for w,h in SIZES for case in CASES}; seen=set(); rows=[]
    for row in r['rows']:
        key=(row['case'],row['width'],row['height']); assert key in expected_keys and key not in seen
        seen.add(key); case,w,h=key; name=f'{case}_{w}x{h}.npz'; assert row['raw']==name
        path=out/name; assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        with np.load(path,allow_pickle=False) as a:
            old=a['old_export'].copy(); corrected=a['corrected'].copy()
        ref=expected(case,w,h); cm=check_marker(corrected,ref); om=check_marker(old,ref)
        pred_error=float(np.max(np.abs(old-old_export_prediction(corrected))))
        assert cm==row['corrected'] and om==row['old']
        assert pred_error==row['old_stride_prediction_max_error']
        assert row['draw_both_readbacks_ns']>0
        assert row['buffer_metadata']['dimensions']==[h,w,4]
        assert row['buffer_metadata']['numpy_strides']==[4,4*h,4*h*w]
        rows.append(dict(case=case,width=w,height=h,corrected=cm,old=om,prediction_error=pred_error))
    assert seen==expected_keys
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'integrity_pass':True,
            'accuracy_pass':all(x['corrected']['pass'] for x in rows),
            'layout_prediction_pass':all(x['prediction_error']<=1e-6 for x in rows),
            'old_export_rejected':all(not x['old']['pass'] for x in rows),
            'marker_frames':len(rows),'rows':rows,'physical_validation':False,
            'p2_field_validated':False,'network_validated':False,'general_speedup_claim':False,
            'point03_closed':False,'report_sha256':hashlib.sha256((out/'render_result.json').read_bytes()).hexdigest()}
    with (out/'local_integrity_audit.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:result[k] for k in ['integrity_pass','accuracy_pass','layout_prediction_pass','marker_frames','point03_closed']}))


if __name__=='__main__':main()
