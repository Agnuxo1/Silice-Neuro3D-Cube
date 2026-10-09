"""Audit the accepted partial chain, resource failure, and final recovery."""
import argparse
import ast
from datetime import datetime,timezone
import inspect
import os
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from scipy.sparse import load_npz
import audit_point03_p4i3 as original
from audit_point03_p4i import read
from run_point03_exponential import ROOT,sha,write


PRIOR=ROOT/'resultados/codex/point03_p4i3_gaussian_time_20261008'


def partial():
    e=read(PRIOR/'execution.json');m=read(PRIOR/'manifest.json')
    assert e['status']=='failed' and e['sources_unchanged'] and e['error_type']=='AssertionError'
    assert len(e['children'])==75 and len(e['checkpoints'])==74
    assert sha(PRIOR/'manifest.json')==e['manifest_sha256']
    for p,v in m['source_sha256'].items():assert sha(p)==v
    with np.load(Path(m['detector_folder'])/'gaussian_q16.npz',allow_pickle=False) as data:free=data['free_dofs'].copy()
    M=load_npz(Path(m['geometry_folder'])/'mass.npz')[free,:][:,free]
    previous=digest=None;power=m['P_in'];residual=0.
    for index,link in enumerate(e['checkpoints'],1):
        cp=read(link['path']);event=e['children'][index-1]
        assert sha(link['path'])==link['sha256'] and cp['status']=='completed' and cp['case']=='R5_65536' and cp['index']==index
        assert event['index']==index and event['returncode']==0 and event['elapsed_s']<=370 and cp['elapsed_s']<=360
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
    failure_path=PRIOR/'R5_65536/part075.json';failure=read(failure_path)
    assert failure['status']=='failed' and failure['index']==75 and failure['case']=='R5_65536'
    assert failure['error_type']=='AssertionError' and 'in guard' in failure['diagnostic'] and 'resource_end=guard' in failure['diagnostic']
    assert 'resource_end' not in failure and failure['previous_report_sha256']==digest and failure['previous_report_path']==previous
    assert e['children'][-1]['returncode']!=0 and sha(failure['field_path'])==failure['field_sha256']
    with np.load(failure['field_path'],allow_pickle=False) as data:failed=data['field'].copy()
    assert failed.shape==(len(free),) and failed.dtype==np.dtype('complex128') and np.all(np.isfinite(failed))
    failed_power=float(np.vdot(failed,M@failed).real)
    assert 0<failed_power<=power+1e-9
    return dict(created_utc=datetime.now(timezone.utc).isoformat(),partial_integrity_pass=True,accepted_checkpoints=74,
                rejected_checkpoint=75,failed_field_not_adopted=True,failed_field_recomputed_mass_power=failed_power,
                last_accepted_power=power,max_power_residual=residual,original_execution_sha256=sha(PRIOR/'execution.json'),
                original_manifest_sha256=sha(PRIOR/'manifest.json'),failed_report_sha256=sha(failure_path),
                failed_field_sha256=failure['field_sha256'],point03_closed=False,temporal_precision_pass=None)


def prepare_source(out):
    f=ast.parse(inspect.getsource(original.audit)).body[0]
    class Change(ast.NodeTransformer):
        def visit_Compare(self,node):
            if ast.unparse(node)=="cp['started_utc'] > m['created_utc']":
                node.comparators=[ast.parse("m['retained_manifest_created_utc'] if index <= 74 else m['created_utc']",mode='eval').body]
            return self.generic_visit(node)
        def visit_Call(self,node):
            for k in node.keywords:
                if k.arg=='new_checkpoints_checked':k.value=ast.Constant(182)
                if k.arg=='retained_checkpoints_rechecked':k.value=ast.Constant(426)
            return self.generic_visit(node)
    f=Change().visit(f)
    source=out/'independent_auditor_source.txt'
    assert not source.exists()
    source.write_text(ast.unparse(ast.fix_missing_locations(ast.Module(body=[f],type_ignores=[])))+'\n',encoding='utf-8')
    return source


def audit(out):
    initial=partial();assert initial['partial_integrity_pass']
    m=read(out/'manifest.json');e=read(out/'execution.json');old=read(PRIOR/'execution.json')
    assert m['retained_checkpoint_count']==74 and m['retained_manifest_created_utc']==read(PRIOR/'manifest.json')['created_utc']
    assert e['checkpoints'][:74]==old['checkpoints'] and e['children'][:74]==old['children'][:74]
    assert e['elapsed_s']<=22000 and e['resource_wait_s']<=1800
    for event in e['children'][74:]:
        assert event['parent_resource_start']['available_ram_bytes']>=6*1024**3
        assert event['parent_resource_start']['free_disk_bytes']>2*1024**3
    source=Path(m['independent_auditor_source_path']);assert sha(source)==m['source_sha256'][str(source)]
    namespace=original.__dict__.copy();exec(compile(source.read_text(encoding='utf-8'),str(source),'exec'),namespace)
    result=namespace['audit'](out)
    result.update(reused_P4I3_checkpoints_checked=74,new_recovery_checkpoints_checked=182,
                  original_failed_checkpoint_preserved=True,partial_audit_rechecked=initial,
                  original_deadline_budget_s=22000,elapsed_including_interruption_s=e['elapsed_s'])
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    result=audit(args.out.resolve());write(args.out/'integrity_audit.json',result);print(result)
