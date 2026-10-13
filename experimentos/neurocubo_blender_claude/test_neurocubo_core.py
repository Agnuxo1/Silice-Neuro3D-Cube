"""Software checks of the neuro-cube core (no data, no training).

Run from the repository root:  python -B -m pytest experimentos/neurocubo_blender_claude -q
or directly:                   python -B experimentos/neurocubo_blender_claude/test_neurocubo_core.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for path in (str(ROOT), str(HERE)):
    if path not in sys.path:
        sys.path.insert(0, path)

import neurocubo_core as nc  # noqa: E402
from agentkit import learning as akl  # noqa: E402
from agentkit import learning_v2 as akl2  # noqa: E402
from agentkit import mzi as akm  # noqa: E402


def _gradient_check(cfg, seed, samples=12):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((samples, cfg.n))
    y = rng.integers(0, len(cfg.ports), samples)
    p = nc.init_params(cfg, seed)
    _, grad = nc.objective(p, x, y, cfg)
    h = 1e-6
    numeric = np.zeros_like(p)
    for i in range(len(p)):
        e = np.zeros_like(p)
        e[i] = h
        numeric[i] = (nc.objective(p + e, x, y, cfg)[0] - nc.objective(p - e, x, y, cfg)[0]) / (2 * h)
    return float(np.max(abs(grad - numeric)) / max(1e-12, np.max(abs(numeric))))


def gradient_relative_errors() -> dict:
    """Analytic gradient vs central differences for every model family used."""
    out = {}
    for n, ports in ((4, (0, 1, 2, 3)), (8, (0, 1, 2, 3))):
        cfg = nc.optical_config(n, 4.0, ports)
        rng = np.random.default_rng(7)
        cfg = nc.with_errors(cfg, nc.draw_splitter_errors(cfg, 0.02, 0.8, rng))
        out["optical_N%d" % n] = _gradient_check(cfg, 11 + n)
        out["real_matched_N%d" % n] = _gradient_check(nc.real_matched_config(n, 4.0, ports), 21 + n)
    return out


def test_gradients():
    errors = gradient_relative_errors()
    assert max(errors.values()) <= 1e-6, errors


def test_mesh_matches_agentkit_reconstruct():
    """mesh_transfer (with coupler errors) equals agentkit.mzi.clements_reconstruct."""
    for n in (4, 8):
        spec = nc.ideal_mesh_spec(n)
        rng = np.random.default_rng(n)
        spec.eps = rng.normal(0, 0.03, (spec.n_mzi, 2))
        p = rng.uniform(0, 2 * math.pi, spec.n_params)
        t, _ = nc.mesh_transfer(p, spec)
        ref = spec.eta * akm.clements_reconstruct(nc.decomposition_from_params(p, spec), spec.eps)
        assert np.max(abs(t - ref)) < 1e-13


def _hermitian_params(u):
    """Coefficients p with expm(i sum p_k B_k) = u in the agentkit.learning basis."""
    values, vectors = np.linalg.eig(u)
    h = vectors @ np.diag(np.angle(values)) @ np.linalg.inv(vectors)
    h = 0.5 * (h + h.conj().T)
    n = len(u)
    p = [h[i, i].real for i in range(n)]
    p += [h[i, j].real for i in range(n) for j in range(i + 1, n)]
    p += [h[i, j].imag for i in range(n) for j in range(i + 1, n)]
    return np.asarray(p)


def test_forward_matches_learning_v2():
    """Lossless, G = 1, all ports: identical scores to learning_v2.unitary_mzm_signed."""
    n = 4
    spec = nc.ideal_mesh_spec(n, loss_db_per_stage=0.0)
    cfg = nc.optical_config(n, 1.0, range(n), (spec, spec))
    rng = np.random.default_rng(3)
    p = rng.uniform(0, 2 * math.pi, cfg.n_params)
    t1, _ = nc.mesh_transfer(p[:n * n], spec)
    t2, _ = nc.mesh_transfer(p[n * n:], spec)
    h = np.concatenate([_hermitian_params(t1), _hermitian_params(t2)])
    assert np.max(abs(akl.transfer(h[:n * n], n, True, False)[0] - t1)) < 1e-10
    x = rng.standard_normal((20, n))
    ours = nc.forward(p, x, cfg)[0]
    theirs = akl2.scores_and_directions_v2(h, x, "unitary_mzm_signed", 1.0, 0.0)[0]
    assert np.max(abs(ours - theirs)) < 1e-9


def geometry_reconstruction_errors() -> dict:
    """Design with Clements phases of Haar targets -> transfer from geometry -> compare."""
    out = {}
    for n in (4, 8):
        rng = np.random.default_rng(100 + n)
        targets = [nc.haar_unitary(n, rng) for _ in range(2)]
        decs = [akm.clements_decompose(u) for u in targets]
        layer_params = [nc.params_from_decomposition(d) for d in decs]
        geometry = nc.design_layout(n, 1.0, range(min(n, 4)), layer_params=layer_params)
        errors = []
        for li, layer in enumerate(geometry["layers"]):
            spec, p = nc.spec_from_geometry_layer(layer)
            t, _ = nc.mesh_transfer(p, spec)
            expected = spec.eta * np.exp(1j * spec.common_phase) * targets[li]
            errors.append(float(np.linalg.norm(t - expected, 2)))
            assert np.max(abs(spec.eps)) < 1e-14
        out["N%d" % n] = max(errors)
    return out


def test_geometry_reconstruction():
    errors = geometry_reconstruction_errors()
    assert max(errors.values()) < 1e-10, errors


def test_real_matched_gain_bound():
    rng = np.random.default_rng(5)
    for n in (4, 8):
        w, _ = nc.real_matched_transfer(rng.standard_normal(n * n) * 3, n, 0.8)
        assert np.linalg.norm(w, 2) <= 0.8 + 1e-12


def test_quantize_and_kappa():
    q = nc.quantize_phases(np.array([0.0, 2 * math.pi - 1e-9, 1.0]), 8)
    assert q[0] == 0.0 and q[1] == 0.0 and abs(q[2] - 1.0) <= math.pi / 256
    assert nc.kappa_of_gap(14e-6) == 471.6394183216887
    assert abs(nc.coupler_angle(14e-6, nc.balanced_coupler_length()) - math.pi / 4) < 1e-15
    try:
        nc.kappa_of_gap(10e-6)
    except ValueError:
        pass
    else:
        raise AssertionError("kappa extrapolated outside the validated range")


if __name__ == "__main__":
    import json
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
    summary = {"tests_passed": True, "gradient_relative_errors": gradient_relative_errors(),
               "geometry_reconstruction_errors_core": geometry_reconstruction_errors(),
               "numpy": np.__version__}
    print(json.dumps(summary, indent=1))
    if len(sys.argv) > 1:
        out = Path(sys.argv[1])
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("x", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=1)
