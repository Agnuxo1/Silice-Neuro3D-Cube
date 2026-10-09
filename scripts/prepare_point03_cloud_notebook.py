"""Create a validated companion; no remote execution or upload."""
import ast
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,'D:/PROJECTS/.cognition/point03_notebook_authoring_20261008')
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'resultados/codex/point03_cloud_quadrature_package_20261008'


def main():
    path=OUT/'Silice_T96_Q4_cuadratura_20261008.ipynb';assert not path.exists()
    cells=[
        nbf.v4.new_markdown_cell('# Control de cuadratura T96/Q4\n\nCuaderno diagnóstico reproducible. Estado: preparado y validado estructuralmente, sin ejecutar con los datos del proyecto. La transferencia a Colab requiere autorización específica. La tarea 1 sigue abierta.'),
        nbf.v4.new_markdown_cell('## Método y límites\n\nTres mallas existentes, sin generar h0,28 ni propagar campos. Reglas Gauss–Duffy de 12/16/24 puntos por eje, bloques de 256 triángulos. Controles analíticos de momentos y energías lineales; cotas de discrepancia entre matrices, no de error absoluto frente al continuo. Fuente: contrato incluido en el paquete. Un hilo; versiones fijadas.'),
        nbf.v4.new_code_cell("import json, sys, platform, psutil\nfrom datetime import datetime, timezone\nprint(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'platform':platform.system(),'available_ram_GiB':psutil.virtual_memory().available/2**30},indent=2))"),
        nbf.v4.new_markdown_cell('## Preparar las dependencias\n\nInstalación aislada dentro del almacenamiento temporal de Colab. No montar Google Drive ni cambiar recursos de pago. Python observado en Colab: 3.13.16; entorno local: 3.13.7. Se declara esta diferencia y se exige reproducir la matriz histórica antes de adoptar resultados.'),
        nbf.v4.new_code_cell("import subprocess\nsubprocess.run([sys.executable,'-m','pip','install','--target','/content/silice_deps','numpy==2.2.6','scipy==1.15.1','psutil==6.1.1','meshio==5.3.5','scikit-fem==12.0.2'],check=True)"),
        nbf.v4.new_markdown_cell('## Cargar el paquete autorizado\n\nSeleccionar únicamente Silice_FEM_Cuadratura_20261008.zip. Verificar su SHA256 y todos los archivos de origen. No cargar credenciales, otros proyectos ni entornos locales.'),
        nbf.v4.new_code_cell("from google.colab import files\nfrom pathlib import Path\nimport hashlib, zipfile\nuploaded=files.upload()\nassert set(uploaded)=={'Silice_FEM_Cuadratura_20261008.zip'}\narchive=Path('Silice_FEM_Cuadratura_20261008.zip')\nassert hashlib.sha256(archive.read_bytes()).hexdigest()=='4ae9aa8e48b3176225fb004bee307985220d479c18f29462bacbd41dc427df22'\nfolder=Path('/content/silice_quadrature_20261008')\nassert not folder.exists()\nfolder.mkdir()\nwith zipfile.ZipFile(archive) as z:\n    assert z.testzip() is None\n    assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in z.namelist())\n    z.extractall(folder)\nmanifest=json.loads((folder/'transfer_manifest.json').read_text())\nproject=folder/'project'\nfor row in manifest['scientific_data']:\n    file=project/row['path']\n    assert file.stat().st_size==row['bytes'] and hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256']\nprint({'input_integrity_pass':True,'files_checked':len(manifest['scientific_data'])})"),
        nbf.v4.new_markdown_cell('## Ejecutar los tres controles en orden\n\nLas salidas nuevas se conservan. Un fallo detiene el cuaderno; no se sustituye por éxito ni se repite una salida existente. Estos controles no cierran por sí solos la convergencia espacial o longitudinal.'),
        nbf.v4.new_code_cell("import os\nenvironment=os.environ.copy()\nenvironment['PYTHONPATH']='/content/silice_deps'\nfor key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:\n    environment[key]='1'\nreports={}\nfor mesh in ['prototype','coarse','mid']:\n    out=project/'resultados/codex'/('cloud_duffy_'+mesh+'_20261008')\n    subprocess.run([sys.executable,str(project/'scripts/check_point03_fem_duffy.py'),'--mesh',mesh,'--out',str(out)],env=environment,check=True,timeout=1820)\n    reports[mesh]=json.loads((out/'report.json').read_text())"),
        nbf.v4.new_markdown_cell('## Revisar los resultados\n\nLos valores son cotas conservadoras de discrepancia entre las matrices calculadas, a 2 mm. La potencia se expresa como fracción de la entrada normalizada. Mantener visibles los fallos y las diferencias de entorno; no afirmar validación experimental.'),
        nbf.v4.new_code_cell("rows=[]\nfor mesh,report in reports.items():\n    for pair,values in report['pairs'].items():\n        rows.append({'mesh':mesh,'pair':pair,'field_mass_bound':values['field_mass_norm_bound'],'power_field_bound':values['observable_power_bounds']['field'],'power_intensity_bound':values['observable_power_bounds']['intensity'],'pass':values['conservative_consistency_pass']})\nprint(json.dumps(rows,indent=2))"),
        nbf.v4.new_markdown_cell('## Conservar la evidencia\n\nDescargar matrices, informes y fuentes. Verificar los hashes nuevamente al recuperar los resultados localmente y realizar auditoría independiente antes de incorporarlos al estado del proyecto.'),
        nbf.v4.new_code_cell("results=Path('/content/Silice_cuadratura_resultados_20261008.zip')\nassert not results.exists()\nwith zipfile.ZipFile(results,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:\n    z.writestr('environment.json',json.dumps({'python':sys.version,'platform':platform.system(),'utc':datetime.now(timezone.utc).isoformat()},indent=2))\n    for file in project.rglob('*'):\n        if file.is_file() and 'cloud_duffy_' in str(file):\n            z.write(file,file.relative_to(project).as_posix())\nprint({'result_archive_sha256':hashlib.sha256(results.read_bytes()).hexdigest()})\nfiles.download(str(results))")
    ]
    notebook=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})
    nbf.validate(notebook)
    for cell in cells:
        if cell.cell_type=='code':ast.parse(cell.source)
    nbf.write(notebook,path)
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),notebook=str(path),notebook_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                 nbformat_validation_pass=True,code_syntax_pass=True,executed=False,reason_not_executed='Project data upload awaiting specific authorization.')
    (OUT/'notebook_validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(receipt)


if __name__=='__main__':main()
