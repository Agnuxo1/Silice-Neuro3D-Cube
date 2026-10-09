"""Independent local audit of every raw instrument mark; preserve negatives."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from point03_render_pipeline_reference import MODES,reference,metrics
from point03_render_reference import RESOLUTIONS
from point03_render_p2_gate import require_p0,ns_seconds

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    out=a.out.resolve();root=Path(__file__).resolve().parents[1];out.relative_to(root/'resultados/codex')
    target=out/'local_integrity_audit.json'
    if target.exists():raise FileExistsError(target)
    r=json.loads((out/'render_result.json').read_text(encoding='utf-8'));g=json.loads((out/'guard.json').read_text(encoding='utf-8'))
    assert r['status']==g['status']=='completed' and g['child_finished'] and r['gpu_execution'] and not r['new_t96_field']
    pp=(root/g['profile_relative']).resolve();pp.relative_to(root/'resultados/codex');p=json.loads(pp.read_text(encoding='utf-8'))
    assert hashlib.sha256(pp.read_bytes()).hexdigest()==g['profile_sha256']==r['profile_sha256']
    assert p['sources_sha256']==g['sources_sha256']==r['sources_sha256']
    assert require_p0(root,p)==r['p0_local_audit_sha256']
    assert np.__version__=='2.2.6' and r['runtime']['numpy']=='1.26.4' and r['runtime']['python']=='3.11.15'
    assert all(v=='1' for v in r['runtime']['thread_caps'].values())
    assert r['engine']['version'].startswith('4.5.14') and r['engine']['backend']==p['backend'] and '3090' in r['engine']['renderer']
    for name,digest in p['sources_sha256'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
        q=subprocess.run(['git','-c','safe.directory='+str(root),'show',g['published_commit']+':'+name],cwd=root,capture_output=True,timeout=10)
        assert q.returncode==0 and hashlib.sha256(q.stdout).hexdigest()==digest
    assert g['blender_sha256']==p['blender_sha256'] and g['elapsed_child_with_startup_s']<=120
    assert datetime.fromisoformat(g['finished_utc'])<=datetime(2026,10,9,13,45,tzinfo=timezone.utc)
    assert g['samples'][0]['available_ram_gib']>=8
    assert all(s['available_ram_gib']>=6 and s['vram_used_gib']<=4 and s['temperature_c']<=80 and s.get('owned_rss_gib',0)<=1.5 for s in g['samples'])
    expected={(m,n) for m in MODES for n in RESOLUTIONS};seen=set();rows=[]
    assert len(r['rows'])==len(expected)
    for row in r['rows']:
        key=(row['marker'],row['resolution']);assert key in expected and key not in seen;seen.add(key)
        marker,n=key;name=f'{marker}_{n}.npz';assert row['raw']==name
        path=out/name;assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        with np.load(path,allow_pickle=False) as z:
            assert z.files==['rgba'];raw=z['rgba'].copy()
        e,i,m=reference(marker,n);v=metrics(raw,e,i,m)
        for k,value in v.items():
            if isinstance(value,(bool,int)):assert row[k]==value
            else:assert abs(row[k]-value)<=1e-14*max(1,abs(value))
        assert ns_seconds(row['cpu_ns'])==row['cpu_s'] and ns_seconds(row['gpu_ns'])==row['gpu_s']
        rows.append(dict(marker=marker,resolution=n,**v))
    result=dict(integrity_pass=True,accuracy_pass=all(row['accuracy_pass'] for row in rows),marker_frames=30,rows=rows,
                backend=p['backend'],strict_metric_agreement_pass=True,physical_validation=False,network_validated=False,
                p2_field_validated=False,point03_closed=False,general_speedup_claim=False,
                created_utc=datetime.now(timezone.utc).isoformat(),local_numpy=np.__version__,worker_numpy=r['runtime']['numpy'])
    with target.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:result[k] for k in ('integrity_pass','accuracy_pass','marker_frames','backend')}))
if __name__=='__main__':main()
