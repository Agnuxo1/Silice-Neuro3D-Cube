"""Replay 89 retained fields and a resource-race correction without reruns."""
import ast
from datetime import datetime,timezone
import inspect
from pathlib import Path
import numpy as np
from scipy.sparse import load_npz
import audit_point03_p4i3 as original
from audit_point03_p4i3_recovery import partial as first_partial,PRIOR
from audit_point03_p4i import read
from run_point03_exponential import ROOT,sha,write


PREVIOUS=ROOT/'resultados/codex/point03_p4i3_recovery_20261008'


def partial():
    proof=first_partial();assert proof['partial_integrity_pass']
    e=read(PREVIOUS/'execution.json');m=read(PREVIOUS/'manifest.json')
    assert e['status']=='failed' and e['sources_unchanged'] and e['error_type']=='AssertionError'
    assert "resource['available_ram_bytes']>=6*1024**3" in e['diagnostic']
    assert len(e['checkpoints'])==len(e['children'])==89 and not (PREVIOUS/'R5_65536/part090.json').exists()
    assert sha(PREVIOUS/'manifest.json')==e['manifest_sha256']
    for p,v in m['source_sha256'].items():assert sha(p)==v
    assert e['checkpoints'][:74]==read(PRIOR/'execution.json')['checkpoints']
    with np.load(Path(m['detector_folder'])/'gaussian_q16.npz',allow_pickle=False) as data:free=data['free_dofs'].copy()
    M=load_npz(Path(m['geometry_folder'])/'mass.npz')[free,:][:,free]
    previous=e['checkpoints'][73]['path'];digest=e['checkpoints'][73]['sha256'];power=proof['last_accepted_power'];residual=0.
    for index,link in enumerate(e['checkpoints'][74:],75):
        cp=read(link['path']);event=e['children'][index-1]
        assert sha(link['path'])==link['sha256'] and cp['status']=='completed' and cp['case']=='R5_65536' and cp['index']==index
        assert event['index']==index and event['returncode']==0 and event['elapsed_s']<=370 and cp['elapsed_s']<=360
        assert event['parent_resource_start']['available_ram_bytes']>=6*1024**3
        assert cp['previous_report_path']==previous and cp['previous_report_sha256']==digest
        assert cp['steps_done']==256*index and cp['steps_total']==65536 and cp['dt_m']==.002/65536 and cp['started_utc']>m['created_utc']
        for sample in ('resource_start','resource_end'):
            assert cp[sample]['available_ram_bytes']>3*1024**3 and cp[sample]['free_disk_bytes']>2*1024**3
        assert sha(cp['field_path'])==cp['field_sha256']
        with np.load(cp['field_path'],allow_pickle=False) as data:field=data['field'].copy()
        assert field.shape==(len(free),) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
        actual=float(np.vdot(field,M@field).real);residual=max(residual,abs(actual-cp['physical_power']))
        assert abs(actual-cp['physical_power'])<=1e-12 and abs(power-cp['previous_power'])<=1e-12 and 0<actual<=power+1e-9
        previous,digest,power=link['path'],link['sha256'],actual
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),partial_integrity_pass=True,accepted_checkpoints=89,
                last_accepted_power=power,max_power_residual=residual,first_partial_audit=proof,
                previous_execution_sha256=sha(PREVIOUS/'execution.json'),previous_manifest_sha256=sha(PREVIOUS/'manifest.json'),
                no_checkpoint90_computed=True,point03_closed=False,temporal_precision_pass=None)


def prepare_source(out):
    f=ast.parse(inspect.getsource(original.audit)).body[0]
    class Change(ast.NodeTransformer):
        def visit_Compare(self,node):
            if ast.unparse(node)=="cp['started_utc'] > m['created_utc']":
                node.comparators=[ast.parse("m['original_manifest_created_utc'] if index <= 74 else (m['first_recovery_manifest_created_utc'] if index <= 89 else m['created_utc'])",mode='eval').body]
            return self.generic_visit(node)
        def visit_Call(self,node):
            for k in node.keywords:
                if k.arg=='new_checkpoints_checked':k.value=ast.Constant(167)
                if k.arg=='retained_checkpoints_rechecked':k.value=ast.Constant(441)
            return self.generic_visit(node)
    f=Change().visit(f);source=out/'independent_auditor_source.txt';assert not source.exists()
    source.write_text(ast.unparse(ast.fix_missing_locations(ast.Module(body=[f],type_ignores=[])))+'\n',encoding='utf-8')
    return source


def audit(out):
    proof=partial();assert proof['partial_integrity_pass']
    m=read(out/'manifest.json');e=read(out/'execution.json');old=read(PREVIOUS/'execution.json')
    assert m['retained_checkpoint_count']==89 and e['checkpoints'][:89]==old['checkpoints'] and e['children'][:89]==old['children']
    assert m['original_manifest_created_utc']==read(PRIOR/'manifest.json')['created_utc']
    assert m['first_recovery_manifest_created_utc']==read(PREVIOUS/'manifest.json')['created_utc']
    assert e['elapsed_s']<=22000 and e['resource_wait_s']<=1800
    for event in e['children'][74:]:
        assert event['parent_resource_start']['available_ram_bytes']>=6*1024**3 and event['parent_resource_start']['free_disk_bytes']>2*1024**3
    source=Path(m['independent_auditor_source_path']);assert sha(source)==m['source_sha256'][str(source)]
    ns=original.__dict__.copy();exec(compile(source.read_text(encoding='utf-8'),str(source),'exec'),ns)
    result=ns['audit'](out);result.update(retained_P4I3_checkpoints_checked=89,new_recovery_checkpoints_checked=167,
                                       partial_audit_rechecked=proof,interruptions_preserved=True)
    return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result=audit(a.out.resolve());write(a.out/'integrity_audit.json',result);print(result)
