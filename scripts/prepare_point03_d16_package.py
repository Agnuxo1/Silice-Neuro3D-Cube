"""Prepare and validate a portable CPU transfer; never send project data."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile
sys.path.insert(0, 'D:/PROJECTS/.cognition/point03_notebook_authoring_20261008')
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'resultados/codex/point03_d16_cloud_package_retry_20261008'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    OUT.mkdir()
    from run_point03_d16_time import G, T, D, Q, K_SHA
    assert sha(ROOT/Q/'stiffness_duffy16.npz') == K_SHA
    files = ['scripts/run_point03_d16_time.py', 'scripts/audit_point03_d16_time.py',
             'scripts/point03_fem_time.py', 'scripts/point03_fem_radau.py',
             'scripts/check_point03_d16_controls.py', 'Docs/POINT-03-D16-COARSE-TIME-CONTRACT.md',
             'scripts/check_point03_d16_worker.py',
             'resultados/codex/point03_d16_worker_controls_20261008/report.json',
             'resultados/codex/point03_d16_evaluator_controls_20261008.json',
             f'{G}/mass.npz', f'{G}/cladding_mass.npz', f'{G}/report.json',
             f'{T}/gaussian_q16.npz', f'{T}/core_q32.npz', f'{T}/intensity_q32.npy', f'{T}/report.json',
             f'{D}/damping_q12.npz', f'{D}/report_recovered.json',
             f'{Q}/stiffness_duffy16.npz', f'{Q}/report.json']
    manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(), files=[
        dict(path=p, bytes=(ROOT/p).stat().st_size, sha256=sha(ROOT/p)) for p in files],
        purpose='D16-C1: one coarse T96 ideal mesh, 2mm, two temporal families; no task closure',
        proposed_destination='Private Google Colab CPU notebook', upload_performed=False,
        dependencies={'numpy': '2.2.6', 'scipy': '1.15.1', 'psutil': '6.1.1'},
        excludes='No credentials, .git, personal files, other projects, fabrication data or virtual environments')
    worker_report = json.loads((ROOT/'resultados/codex/point03_d16_worker_controls_20261008/report.json').read_text())
    assert worker_report['controls_pass'] and worker_report['tested_worker_sha256'] == sha(ROOT/'scripts/run_point03_d16_time.py')
    (OUT/'transfer_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    archive = OUT/'Silice_D16_C1_20261008.zip'
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in files:
            z.write(ROOT/p, 'project/'+p)
        z.write(OUT/'transfer_manifest.json', 'transfer_manifest.json')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
    digest = sha(archive)
    cells = [nbf.v4.new_markdown_cell('# Silice: control longitudinal D16-C1\n\nCPU estándar, un hilo. Protocolo preregistrado, sin resultado óptico todavía. Dos familias a32768pasos, 2mm, matriz Duffy16. Preservar todos los dictámenes. No generar malla fina ni avanzar tareas. La transferencia y ejecución remota requieren aprobación específica.'),
             nbf.v4.new_code_cell("import os, sys, json, platform, subprocess, hashlib, zipfile\nfrom pathlib import Path\nfrom datetime import datetime, timezone\nprint({'utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'platform':platform.system()})"),
             nbf.v4.new_markdown_cell('Preparación aislada: dependencias fijadas en almacenamiento temporal. No montar Drive ni contratar recursos.'),
             nbf.v4.new_code_cell("subprocess.run([sys.executable,'-m','pip','install','--target','/content/silice_d16_deps','numpy==2.2.6','scipy==1.15.1','psutil==6.1.1'],check=True)"),
             nbf.v4.new_code_cell(f"from google.colab import files\nuploaded=files.upload()\nassert set(uploaded)=={{'{archive.name}'}}\narchive=Path('{archive.name}')\nassert hashlib.sha256(archive.read_bytes()).hexdigest()=='{digest}'\nfolder=Path('/content/silice_d16_c1_20261008')\nassert not folder.exists()\nfolder.mkdir()\nwith zipfile.ZipFile(archive) as z:\n    assert z.testzip() is None\n    assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in z.namelist())\n    z.extractall(folder)\nproject=folder/'project'\nmanifest=json.loads((folder/'transfer_manifest.json').read_text())\nfor row in manifest['files']:\n    p=project/row['path']\n    assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']\nprint({{'input_integrity_pass':True,'files':len(manifest['files'])}})"),
             nbf.v4.new_markdown_cell('Ejecutar una vez. Un fallo se conserva y detiene esta etapa. No continuar por un dictamen negativo sin revisarlo. Tiempo máximo22000s, recursos limitados por contrato; mantener el uso interactivo normal de Colab.'),
             nbf.v4.new_code_cell("environment=os.environ.copy()\nenvironment['PYTHONPATH']='/content/silice_d16_deps'\nfor key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:\n    environment[key]='1'\nout=project/'resultados/codex/cloud_d16_c1_20261008'\nchild=subprocess.run([sys.executable,str(project/'scripts/run_point03_d16_time.py'),'--out',str(out)],env=environment,timeout=22030)\nprint({'returncode':child.returncode})\nexecution=json.loads((out/'execution.json').read_text())\nprint(json.dumps(execution,indent=2))\nif execution['status']=='completed':\n    subprocess.run([sys.executable,str(project/'scripts/audit_point03_d16_time.py'),'--out',str(out)],env=environment,check=True,timeout=600)\n    print((out/'integrity_audit.json').read_text())"),
             nbf.v4.new_markdown_cell('Descargar evidencia incluso si el ensayo falla. Verificar hashes localmente antes de adoptar resultados. Un aprobado temporal no cierra T96/Q4.'),
             nbf.v4.new_code_cell("result=Path('/content/Silice_D16_C1_resultados_20261008.zip')\nassert not result.exists()\nwith zipfile.ZipFile(result,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:\n    for p in out.rglob('*'):\n        if p.is_file():\n            z.write(p,p.relative_to(project).as_posix())\n    z.writestr('runtime.json',json.dumps({'python':sys.version,'platform':platform.system(),'utc':datetime.now(timezone.utc).isoformat()},indent=2))\nprint({'result_sha256':hashlib.sha256(result.read_bytes()).hexdigest()})\nfiles.download(str(result))")]
    notebook = nbf.v4.new_notebook(cells=cells, metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}})
    nbf.validate(notebook)
    for cell in cells:
        if cell.cell_type == 'code':
            ast.parse(cell.source)
    path = OUT/'Silice_D16_C1_20261008.ipynb'
    nbf.write(notebook, path)
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(), archive_bytes=archive.stat().st_size,
                   archive_sha256=digest, source_files=len(files), CRC_pass=True,
                   notebook_sha256=sha(path), nbformat_validation_pass=True, syntax_pass=True,
                   upload_performed=False, remote_execution_performed=False)
    (OUT/'package_receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(receipt)


if __name__ == '__main__':
    main()
