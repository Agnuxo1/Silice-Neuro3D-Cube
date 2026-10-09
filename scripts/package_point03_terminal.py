"""Package and verify portable terminal fields; does not replace the 90-field audit."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

from point03_linear_detector import Detector
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'resultados/codex/point03_terminal_20261007'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build():
    assert not FOLDER.exists()
    FOLDER.mkdir()
    m1 = ROOT/'resultados/codex/point03_finer_20261007_M1'
    e, a = read(m1/'execution.json'), read(m1/'assessment.json')
    assert read(m1/'integrity_audit.json')['integrity_pass'] and e['status']=='completed'
    items = []
    for label, solution in e['solutions'].items():
        cp = read(solution['checkpoints'][-1]['path'])
        items.append(dict(N=767,label=label,source=cp['field_path'],sha256=cp['field_sha256'],P_in=a['P_in'],expected={method:a['methods'][label][method]['P_core'] for method in ('field','intensity')}))
    h = read(ROOT/'resultados/codex/point03_exponential_20261007_H2/assessment.json')
    pred = read(ROOT/'resultados/codex/point03_m1_prediction_20261007.json')
    for index,n in enumerate((320,400,500,640)):
        row = next(row for row in h['rows'] if row['N']==n)
        solution = row['solutions'][str(row['fine_segments'])]
        items.append(dict(N=n,label='primary',source=solution['field_path'],sha256=solution['field_sha256'],P_in=row['P_in'],expected={method:pred['prediction'][method]['powers'][index] for method in ('field','intensity')}))
    for item in items:
        source = Path(item.pop('source'))
        assert source.is_relative_to(ROOT) and digest(source)==item['sha256']
        item['source_relative_path'] = source.relative_to(ROOT).as_posix()
        item['file'] = f"n{item['N']}_{item['label']}.npz"
        shutil.copyfile(source,FOLDER/item['file'])
        assert digest(FOLDER/item['file'])==item['sha256']
    (FOLDER/'index.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),items=items,scope='Seven terminal arrays only; intermediate fields for the full 90-field chain audit remain local.'),indent=2)+'\n',encoding='utf-8')


def check(output):
    index = read(FOLDER/'index.json')
    detector = Detector()
    rows = []
    assert len(index['items'])==7
    for item in index['items']:
        path = FOLDER/item['file']
        assert path.is_relative_to(FOLDER) and digest(path)==item['sha256']
        with np.load(path,allow_pickle=False) as archive:
            field = archive['field'].copy()
        assert field.shape==(item['N'],item['N']) and field.dtype==np.dtype('complex128') and np.all(np.isfinite(field))
        measurements = detector.measure(field,item['N'],item['P_in'])
        errors = {method:abs(measurements[method]['P_core']-item['expected'][method]) for method in ('field','intensity')}
        assert max(errors.values())<=1e-12
        rows.append(dict(N=item['N'],label=item['label'],errors=errors))
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(),terminal_verification_pass=True,arrays_checked=7,rows=rows,point03_closed=False,scope='Portable numerical observable verification only, not full chain audit or independent physical replication.')
    assert not output.exists()
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:report[key] for key in ('terminal_verification_pass','arrays_checked','point03_closed')}))


if __name__=='__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--build',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    if args.build:
        build()
    check(args.output)
