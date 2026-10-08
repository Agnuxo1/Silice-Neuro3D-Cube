"""Notebook input transport recovery only; numerical sources remain unchanged."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import zipfile

archive = Path('/content/Silice_D16_C1_20261008.zip')
assert hashlib.sha256(archive.read_bytes()).hexdigest() == 'cebaeac0f2952360f319acd9081f0f6149e0fbda7112258ac738aafc6d0a3ea1'
folder = Path('/content/silice_d16_c1_20261008')
assert not folder.exists()
folder.mkdir()
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in z.namelist())
    z.extractall(folder)
project = folder/'project'
manifest = json.loads((folder/'transfer_manifest.json').read_text())
for row in manifest['files']:
    p = project/row['path']
    assert p.stat().st_size == row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256']
print({'input_integrity_pass': True, 'files': len(manifest['files']),
       'utc': datetime.now(timezone.utc).isoformat(), 'transport': 'Colab file sidebar'})
