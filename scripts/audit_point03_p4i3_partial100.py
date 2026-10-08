"""Verify every retained Radau chunk after resource wait exhaustion."""
from datetime import datetime,timezone
import os
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
import numpy as np
from scipy.sparse import load_npz
from audit_point03_p4i3_recovery2 import partial as prior_partial
from audit_point03_p4i import read
from run_point03_exponential import ROOT,sha,write


def main():
    prior=prior_partial();assert prior['partial_integrity_pass']
    folder=ROOT/'resultados/codex/point03_p4i3_recovery2_20261008';e=read(folder/'execution.json');m=read(folder/'manifest.json')
    assert e['status']=='failed' and e['sources_unchanged'] and len(e['checkpoints'])==len(e['children'])==100
    assert not (folder/'R5_65536/part101.json').exists() and 1800<=e['resource_wait_s']<1800.01
    assert sha(folder/'manifest.json')==e['manifest_sha256']
    for p,v in m['source_sha256'].items():assert sha(p)==v
    with np.load(Path(m['detector_folder'])/'gaussian_q16.npz',allow_pickle=False) as data:free=data['free_dofs'].copy()
    M=load_npz(Path(m['geometry_folder'])/'mass.npz')[free,:][:,free]
    previous=e['checkpoints'][88]['path'];digest=e['checkpoints'][88]['sha256'];power=prior['last_accepted_power'];residual=0.
    for index,link in enumerate(e['checkpoints'][89:],90):
        cp=read(link['path']);event=e['children'][index-1]
        assert sha(link['path'])==link['sha256'] and cp['status']=='completed' and cp['case']=='R5_65536' and cp['index']==index
        assert event['index']==index and event['returncode']==0 and event['elapsed_s']<=370 and cp['elapsed_s']<=360
        assert event['parent_resource_start']['available_ram_bytes']>=6*1024**3 and event['parent_resource_start']['free_disk_bytes']>2*1024**3
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
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),partial_integrity_pass=True,accepted_checkpoints=100,
                previous_partial_checkpoints=89,new_checkpoints_checked=11,maximum_power_residual=residual,last_accepted_power=power,
                steps_done=25600,steps_target=65536,distance_m=.002*25600/65536,no_checkpoint101_computed=True,
                temporal_precision_pass=None,point03_closed=False,prior_partial_audit=prior,
                source_sha256={str(Path(__file__).resolve()):sha(__file__),str(folder/'execution.json'):sha(folder/'execution.json')})
    write(folder/'partial100_integrity_audit.json',result);print({k:result[k] for k in ('partial_integrity_pass','accepted_checkpoints','maximum_power_residual','distance_m')})


if __name__=='__main__':main()
