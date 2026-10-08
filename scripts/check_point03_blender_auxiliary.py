"""Pinned external scalar controls and a regional visualization exchange."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
COMMITS = {'BlenderPhotonics': '732799f9e3ebe10e013e316b8a21d88452755dc8',
           'blender-optics-simulator': '2b488e2e99dff4f56d67f57f9674bd00f812dda1'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(a, b):
    return float(np.linalg.norm(a-b)/np.linalg.norm(b))


def run(source, output):
    assert not output.exists() and output.is_relative_to(ROOT/'resultados/codex')
    output.mkdir()
    provenance = {}
    for name, expected in COMMITS.items():
        path = source/name
        actual = subprocess.check_output(['git', '-c', f'safe.directory={path.as_posix()}',
                                          'rev-parse', 'HEAD'], cwd=path, text=True).strip()
        assert actual == expected
        files = ('field.py',) if name == 'blender-optics-simulator' else ('utils.py', 'runmmc.py', 'obj2surf.py')
        provenance[name] = {'commit': actual, 'source_sha256': {
            f: sha(path/('optical_alignment_sim' if name == 'blender-optics-simulator' else '')/f) for f in files}}
    path = source/'blender-optics-simulator/optical_alignment_sim/field.py'
    spec = importlib.util.spec_from_file_location('silice_external_field', path)
    field = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(field)
    lam_nm = 1550/1.444
    lam_mm = lam_nm*1e-6
    z = .2
    k = 2*np.pi/lam_mm
    metrics = {}
    gaussians = {}
    for n in (256, 512):
        dx = .256/n
        rows, cols = np.indices((n, n))
        plane = np.ones((n, n), complex)
        wave = np.exp(2j*np.pi*(3*cols+2*rows)/n)
        for label, u, frequency2 in (('constant', plane, 0.), ('fourier32', wave, (3/.256)**2+(2/.256)**2)):
            expected = u*np.exp(1j*k*z*np.sqrt(1-lam_mm**2*frequency2))
            actual = field.angular_spectrum(u, dx, z, lam_nm, band_limit=True)
            error = relative(actual, expected)
            assert error <= 1e-10
            metrics[f'{label}_{n}'] = error
        u = field.gaussian_field(n, dx, .030)
        assert np.isfinite(u).all()
        propagated = field.angular_spectrum(u, dx, z, lam_nm, band_limit=False)
        back = field.angular_spectrum(propagated, dx, -z, lam_nm, band_limit=False)
        roundtrip = relative(back, u)
        power = float(abs(np.sum(abs(propagated)**2)/np.sum(abs(u)**2)-1))
        x = (np.arange(n)-n//2)*dx
        X, Y = np.meshgrid(x, x)
        q = 1+1j*z/(np.pi*.030**2/lam_mm)
        analytic = np.exp(1j*k*z)/q*np.exp(-(X*X+Y*Y)/(.030**2*q))
        paraxial = relative(propagated, analytic)
        assert roundtrip <= 1e-10 and power <= 1e-10 and paraxial <= 2e-4
        metrics[f'gaussian_{n}'] = dict(roundtrip=roundtrip, relative_power_change=power,
                                      complex_error_vs_paraxial=paraxial)
        gaussians[n] = propagated
    discrepancy = relative(gaussians[512][::2, ::2], gaussians[256])
    assert discrepancy <= 1e-8
    metrics['gaussian_grid_discrepancy'] = discrepancy
    rejected = 0
    for invalid in (np.ones((3, 4)), np.array([])):
        try:
            field.angular_spectrum(invalid, .001, z, lam_nm)
        except ValueError:
            rejected += 1
    assert rejected == 2
    geom = ROOT/'resultados/codex/point03_p4c_mesh_20261008/mesh_arrays.npz'
    with np.load(geom, allow_pickle=False) as data:
        coords = data['doflocs'].T.copy()
        ed = data['element_dofs'].copy()
        cladding = data['cladding_cells'].copy()
    # ElementTriP2: vertices 0,1,2; edge nodes 01,12,02.
    local = np.array([[0, 3, 5], [3, 1, 4], [5, 4, 2], [3, 4, 5]])
    faces = ed[local].transpose(2, 0, 1).reshape(-1, 3)
    p = coords[faces]
    area2 = (p[:, 1, 0]-p[:, 0, 0])*(p[:, 2, 1]-p[:, 0, 1])-(p[:, 1, 1]-p[:, 0, 1])*(p[:, 2, 0]-p[:, 0, 0])
    assert np.all(abs(area2)>0)
    faces[area2 < 0] = faces[area2 < 0][:, [0, 2, 1]]
    mask = np.zeros(ed.shape[1], bool)
    mask[cladding] = True
    mask = np.repeat(mask, 4)
    assert faces.shape[0] == 4*ed.shape[1]
    vertices = np.column_stack((coords*1e3, np.zeros(len(coords))))
    mesh = {'_DataInfo_': {'JMeshVersion': '0.5'}, 'MeshVertex3': vertices.tolist(),
            'MeshTri3(1)': (faces[~mask]+1).tolist(), 'MeshTri3(2)': (faces[mask]+1).tolist()}
    exchange = output/'T96_section_visualization_mm.jmsh'
    exchange.write_text(json.dumps(mesh, separators=(',', ':')), encoding='utf-8')
    loaded = json.loads(exchange.read_text(encoding='utf-8'))
    recovered = np.asarray(loaded['MeshVertex3'])[:, :2]*1e-3
    coordinate_error = float(np.max(abs(recovered-coords)))
    recovered_faces = np.vstack([loaded['MeshTri3(1)'], loaded['MeshTri3(2)']])-1
    assert coordinate_error <= 1e-18 and recovered_faces.min() >= 0 and recovered_faces.max() < len(coords)
    assert len(recovered_faces) == len(faces)
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(), status='passed',
                  point03_closed=False, t96_propagated=False, blender_import_executed=False,
                  python=sys.version, numpy=np.__version__, provenance=provenance, metrics=metrics,
                  invalid_shapes_rejected=rejected,
                  visualization=dict(vertices=len(vertices), triangles=len(faces),
                                     region_triangles=[int((~mask).sum()), int(mask.sum())],
                                     maximum_coordinate_error_m=coordinate_error,
                                     source_mesh_sha256=sha(geom), exchange_sha256=sha(exchange), units='mm',
                                     limitations='Planar piecewise-linear visualization only; not tetrahedral production geometry'),
                  script_sha256=sha(Path(__file__)))
    (output/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.source.resolve(), args.output.resolve())
