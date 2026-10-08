"""Build an explicit, inspectable transfer bundle; never upload it."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'resultados/codex/point03_cloud_quadrature_package_20261008'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def main():
    assert not OUT.exists();OUT.mkdir()
    files=[ROOT/p for p in ('scripts/check_point03_fem_duffy.py','scripts/check_point03_p4f.py','scripts/point03_fem_detector.py',
                             'scripts/run_point03_exponential.py','scripts/audit_point03_p4i.py',
                             'Docs/POINT-03-FEM-DUFFY-CONTRACT.md','Docs/POINT-03-FEM-STIFFNESS-QUADRATURE-CONTRACT.md',
                             'resultados/codex/point03_p4i3_recovery2_20261008/execution.json')]
    pairs=[('point03_p4c_mesh_20261008','point03_p4f_detector_20261008','report_recovered.json'),
           ('point03_p5a_mesh_coarse_20261008','point03_p5b_detector_coarse_20261008','report.json'),
           ('point03_p5a_mesh_mid_20261008','point03_p5b_detector_mid_20261008','report.json')]
    for geom_name,det_name,report_name in pairs:
        geom=ROOT/'resultados/codex'/geom_name;det=ROOT/'resultados/codex'/det_name
        report=json.loads((geom/report_name).read_text(encoding='utf-8'))
        entries=report['artifact_sha256'] if report_name=='report_recovered.json' else report['hashes']
        for name,digest in entries.items():
            assert sha(geom/name)==digest;files.append(geom/name)
        files.append(geom/report_name)
        for name in ('core_q32.npz','intensity_q32.npy','gaussian_q16.npz'):files.append(det/name)
    files=sorted(set(files))
    assert all(p.is_relative_to(ROOT) and p.is_file() for p in files)
    manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),purpose='Three-mesh stiffness quadrature audit only; no optical propagation or physical claim.',
                  destination_proposed='Private CPU Google Colab notebook, only after specific upload authorization.',
                  scientific_data=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files],
                  dependencies=dict(numpy='2.2.6',scipy='1.15.1',psutil='6.1.1',meshio='5.3.5',**{'scikit-fem':'12.0.2'}),
                  upload_performed=False,point03_closed=False)
    (OUT/'transfer_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    readme='''# Paquete de control de cuadratura T96

Estado: preparado localmente; no enviado a Colab. Contiene sólo tres
mallas ideales T96 guardadas, matrices, detectores, entrada gaussiana,
informes de procedencia y los cinco módulos necesarios para el control.
El informe de ejecución parcial se incluye como marcador del ensayo
local terminado; no autoriza adoptar sus campos ni reconstruye resultados.

Verificar todos los SHA256 del manifiesto después de extraer. Fijar las
cinco dependencias indicadas en un entorno separado. Python del CPU
Colab observado: 3.13.16, Linux; el entorno local usa 3.13.7, Windows.
La diferencia se declara y obliga a comprobar reproducción de la matriz
histórica y los controles analíticos antes de adoptar resultados remotos.

Ejecutar secuencialmente prototype, coarse y mid con salidas nuevas.
La malla reservada h0,28 no está incluida y no debe generarse. No se
incluyen credenciales, .git, entornos virtuales, archivos personales ni
datos de otros proyectos. El paquete no publica ni comparte el repositorio.
'''
    (OUT/'LEEME.md').write_text(readme,encoding='utf-8')
    archive=OUT/'Silice_FEM_Cuadratura_20261008.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,'project/'+p.relative_to(ROOT).as_posix())
        z.write(OUT/'transfer_manifest.json','transfer_manifest.json');z.write(OUT/'LEEME.md','LEEME.md')
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),archive=str(archive),archive_sha256=sha(archive),
                 archive_bytes=archive.stat().st_size,source_files=len(files),uncompressed_source_bytes=sum(p.stat().st_size for p in files),
                 CRC_pass=True,upload_performed=False)
    (OUT/'package_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(receipt)


if __name__=='__main__':main()
