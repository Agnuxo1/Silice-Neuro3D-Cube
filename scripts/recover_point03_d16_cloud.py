"""Verify and recover the completed ZIP, then audit it independently on Windows."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
import numpy as np
from scipy.sparse import load_npz
from audit_point03_d16_time import audit
from run_point03_d16_time import ROOT, read, sha, write


def main():
    folder = ROOT/'resultados/codex/point03_d16_cloud_recovery_20261008'
    archive = folder/'Silice_D16_C1_resultados_20261008.zip'
    digest = sha(archive)
    assert digest == '154c97d008acb69c766cd4e802e932e42317f4b7a42e1b6cf985b0374e83064e'
    assert archive.stat().st_size == 30429527
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for info in z.infolist():
            name = info.filename
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            assert name == 'runtime.json' or name.startswith('resultados/codex/cloud_d16_c1_20261008/')
            assert (info.external_attr >> 16) & 0o170000 != 0o120000
            target = (folder/name).resolve()
            assert target.is_relative_to(folder.resolve()) and not target.exists()
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as source, target.open('xb') as out:
                shutil.copyfileobj(source, out)
        files = len(z.infolist())
    out = folder/'resultados/codex/cloud_d16_c1_20261008'
    independent = audit(out)
    write(out/'local_integrity_audit.json', independent)
    with np.load(ROOT/'resultados/codex/point03_p5b_detector_coarse_20261008/gaussian_q16.npz', allow_pickle=False) as data:
        free = data['free_dofs'].copy()
    M = load_npz(ROOT/'resultados/codex/point03_p5a_mesh_coarse_20261008/mass.npz')[free, :][:, free]
    cross = {}
    for case in ('P6_32768', 'R5_32768'):
        local = ROOT/'resultados/codex/point03_d16_cross_platform_20261008'
        a_report = read(local/case/'part001.json')
        b_report = read(out/case/'part001.json')
        assert a_report['status'] == b_report['status'] == 'completed'
        assert sha(local/a_report['field_path']) == a_report['field_sha256']
        assert sha(out/b_report['field_path']) == b_report['field_sha256']
        with np.load(local/a_report['field_path'], allow_pickle=False) as data:
            a = data['field'].copy()
        with np.load(out/b_report['field_path'], allow_pickle=False) as data:
            b = data['field'].copy()
        difference = a-b
        relative = float(np.sqrt(np.vdot(difference, M@difference).real/np.vdot(b, M@b).real))
        power_difference = float(abs(np.vdot(a, M@a).real-np.vdot(b, M@b).real))
        cross[case] = dict(relative_field_difference=relative, physical_power_difference=power_difference,
                           cross_platform_pass=relative <= 1e-10 and power_difference <= 1e-12)
    write(folder/'cross_platform_assessment.json', dict(cases=cross, cross_platform_pass=all(v['cross_platform_pass'] for v in cross.values()),
             distance_m=6.25e-5, full_device_validation=False, point03_closed=False))
    write(folder/'recovery_receipt.json', dict(archive_sha256=digest, bytes=archive.stat().st_size,
             CRC_pass=True, files_recovered=files, local_integrity_pass=independent['integrity_pass'],
             temporal_precision_pass=independent['temporal_precision_pass'], point03_closed=False,
             transport='Visible HTTPS notebook output, bounded base64 ranges; exact archive hash preserved'))
    print({'recovery_pass': True, 'files_recovered': files, 'local_integrity_pass': independent['integrity_pass'],
           'temporal_precision_pass': independent['temporal_precision_pass'], 'cross_platform': cross})


if __name__ == '__main__':
    main()
