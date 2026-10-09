"""Rebuild every CPU pixel reference and independently adopt no partial result."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import numpy as np
from point03_render_p2_gate import require_p0, ns_seconds
from point03_render_reference import CASES, RESOLUTIONS, prepare, evaluate_prepared, nodal_for_repeat, metrics


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();audit=out/'local_integrity_audit.json'
    if audit.exists():raise FileExistsError(audit)
    report=json.loads((out/'render_result.json').read_text(encoding='utf-8'))
    guard=json.loads((out/'guard.json').read_text(encoding='utf-8'))
    assert report['status']=='completed' and guard['status']=='completed' and guard['child_finished']
    assert report['gpu_execution'] and not report['new_t96_field']
    root=Path(__file__).resolve().parents[1]
    profile_path=(root/guard['profile_relative']).resolve()
    profile_path.relative_to(root/'resultados/codex')
    assert hashlib.sha256(profile_path.read_bytes()).hexdigest()==guard['profile_sha256']==report['profile_sha256']
    profile=json.loads(profile_path.read_text(encoding='utf-8'))
    assert profile['sources_sha256']==guard['sources_sha256']==report['sources_sha256']
    assert profile['blender_sha256']==guard['blender_sha256'] and guard['published_commit']
    assert require_p0(root,profile)==report['p0_local_audit_sha256']
    from point03_render_p3_gate import require_pipeline
    assert require_pipeline(root,profile)==report['pipeline_audit_hashes']
    assert report['runtime']['python']=='3.11.15' and report['runtime']['numpy']=='1.26.4'
    assert np.__version__=='2.2.6'
    assert all(v=='1' for v in report['runtime']['thread_caps'].values())
    assert report['readback_method']=='Buffer 1D then C reshape'
    assert report['engine']['backend']==profile['backend']
    for path,digest in profile['sources_sha256'].items():
        target=(root/path).resolve();target.relative_to(root)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
    assert report['engine']['version'].startswith('4.5.14')
    assert '3090' in report['engine']['renderer'] and 'NVIDIA' in report['engine']['renderer'].upper()
    assert guard['elapsed_child_with_startup_s'] <= 120
    assert datetime.fromisoformat(guard['finished_utc']) <= datetime(2026,10,9,13,45,tzinfo=timezone.utc)
    assert guard['samples'][0]['available_ram_gib']>=8
    assert all(s['available_ram_gib']>=6 and s['vram_used_gib']<=4 and s['temperature_c']<=80
               and s.get('owned_rss_gib',0)<=1.5 for s in guard['samples'])
    expected={(case,n,k) for case in CASES for n in RESOLUTIONS for k in range(7)}
    assert len(report['rows'])==len(expected)
    got=set(); recalculated=[];cache={n:prepare(n) for n in RESOLUTIONS}
    for row in report['rows']:
        key=(row['case'],row['resolution'],row['repeat']);assert key in expected and key not in got;got.add(key)
        case,n,k=key;name=f'{case}_{n}_{k}.npz';assert row['raw']==name
        p=out/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
        with np.load(p,allow_pickle=False) as a:raw=a['rgba'].copy()
        assert raw.dtype==np.float32 and raw.shape==(n,n,4) and np.isfinite(raw).all()
        field=raw[...,0].astype(np.float64)+1j*raw[...,1].astype(np.float64)
        nodal=nodal_for_repeat(k);cpu,inside,compare=evaluate_prepared(case,cache[n],nodal)
        base,_,_=evaluate_prepared('single',cache[n],nodal)
        single=float(np.sum(abs(base[compare])**2)*(2/n)**2)
        m=metrics(field,cpu,inside,compare,single,(2/n)**2)
        for name,value in m.items():
            if value is None or isinstance(value,(bool,int)):assert row[name]==value
            else:assert abs(row[name]-value)<=1e-14*max(1,abs(value))
        assert row['order']==('CPU/GPU' if k%2==0 else 'GPU/CPU')
        assert 0<row['cpu_s']<120 and 0<row['gpu_draw_uniform_readback_s']<120
        assert ns_seconds(row['cpu_ns'])==row['cpu_s']
        assert ns_seconds(row['gpu_draw_uniform_readback_ns'])==row['gpu_draw_uniform_readback_s']
        recalculated.append(dict(case=case,resolution=n,repeat=k,**m))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),integrity_pass=True,
                accuracy_pass=all(r['accuracy_pass'] for r in recalculated),
                raw_frames=len(recalculated),rows=recalculated,
                physical_validation=False,network_validated=False,point03_closed=False,
                general_speedup_claim=False,local_numpy=np.__version__,
                worker_runtime=report['runtime'],strict_metric_agreement_pass=True,backend=profile['backend'],pipeline_audit_hashes=report['pipeline_audit_hashes'],
                p0_local_audit_sha256=profile['p0_local_audit_sha256'],report_sha256=hashlib.sha256((out/'render_result.json').read_bytes()).hexdigest())
    with audit.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:result[k] for k in ['integrity_pass','accuracy_pass','raw_frames','point03_closed']}))


if __name__=='__main__':main()
