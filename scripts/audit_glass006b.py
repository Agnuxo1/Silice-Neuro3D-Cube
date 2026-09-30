"""Read-only retained-array audit. No propagation, peer execution or GPU."""
import os
for variable in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[variable]='1'
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_report(path):
    report=json.loads(path.read_text())
    assert report['status']=='completed'
    assert report['hashes_before']==report['hashes_after']
    rows=[]
    for c in report['cases']:
        raw=ROOT/c['report_path']
        assert digest(raw)==c['report_sha256']
        original=json.loads(raw.read_text())
        assert all(original[k]==v for k,v in c.items() if k not in ('report_path','report_sha256'))
        array_path=ROOT/c['arrays_path']
        assert digest(array_path)==c['arrays_sha256']
        with np.load(array_path,allow_pickle=False) as data:
            field=data['output']; a=data['input']; q=data['basis']; w=data['detectors']
            dx=float(data['dx_m']); h=data['generator']; z=float(data['length_m'])
            p=lambda f:float(np.sum(np.abs(f)**2)*dx**2)
            input_power=p(a)
            ports=np.sum(q.conj()*field,axis=(1,2))*dx**2
            saved=np.array([complex(*v) for v in c['gaussian_port_amplitudes']])
            assert np.max(np.abs(ports-saved))<1e-12
            core=np.sum(w*np.abs(field)**2,axis=(1,2))*dx**2/input_power
            assert np.max(np.abs(core-np.array(c['core_powers_input'])))<1e-12
            remainder=field-np.sum(ports[:,None,None]*q,axis=0)
            residual=p(remainder)/input_power
            assert abs(residual-c['unprojected_power_input'])<1e-12
            assert abs(np.vdot(ports,ports).real+residual-p(field))<1e-10
            assert abs(p(field)-c['output_power'])<1e-12
            assert abs(input_power-c['input_power'])<1e-12
            ev,vec=np.linalg.eigh(h)
            initial=np.sum(q.conj()*a,axis=(1,2))*dx**2
            predicted=(vec*np.exp(1j*ev*z))@vec.conj().T@initial
            error=float(np.max(np.abs(predicted-ports)))
            assert abs(error-c['reduction_max_complex_error'])<1e-12
            assert c['reduction_pass']==(error<.05)
            balance=abs(c['input_power']-c['output_power']-c['boundary_removed']-c['material_removed'])/input_power
            assert abs(balance-c['balance_relative'])<1e-14
        rows.append(dict(name=c['name'],core_powers_input=core.tolist(),port_error=error,
                         reduction_pass=error<.05,balance=balance,arrays_sha256=c['arrays_sha256']))
    assert all(ch['rc']==0 and ch['elapsed_s']<30 for ch in report['children'])
    return dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(path),
                evidence_consistent=True,cases=rows,gates=report['gates'],
                measured_status=report.get('numeric_pass',report.get('fine_pair_stability_pass')),
                reduction_pass=report['reduction_pass'])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('reports',nargs='+',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    start=time.monotonic()
    result=dict(auditor_sha256=digest(Path(__file__).resolve()),gpu_used=False,
                audit_kind='recomputed_retained_array_arithmetic_NOT_independent_wave_solver',
                reports=[check_report(p.resolve()) for p in args.reports],elapsed_s=time.monotonic()-start)
    text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if args.out:
        path=args.out.resolve()
        if not path.is_relative_to(ROOT/'resultados/codex'):
            parser.error('own result path required')
        with path.open('x',encoding='utf-8',newline='\n') as out:
            out.write(text)
    print(json.dumps({'evidence_consistent':True,'counts':[len(r['cases']) for r in result['reports']],
                      'measured_status':[r['measured_status'] for r in result['reports']],
                      'reduction_pass':[r['reduction_pass'] for r in result['reports']]}))
    return 0


if __name__=='__main__':
    sys.exit(main())
