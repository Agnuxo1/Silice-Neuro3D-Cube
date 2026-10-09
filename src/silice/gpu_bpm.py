"""Opt-in CUDA scalar SSFM. No import-time torch/CUDA or geometry changes.

The NumPy operator preparation is explicit CPU work. Propagation, FFT,
phase application and removed-power reductions run on CUDA; export and
independent validation stay on CPU. NOT physical optical computation.
"""
import math
import time
import numpy as np


def operators(points, width_m, length_m, steps, delta_n,
              wavelength_m=1550e-9, n_reference=1.444):
    if isinstance(points, bool) or not isinstance(points, int) or not 16 <= points <= 320:
        raise ValueError('pilot grid must be integer 16..320')
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 1000:
        raise ValueError('steps must be integer 1..1000')
    if not all(math.isfinite(v) and v > 0 for v in
               (width_m, length_m, wavelength_m, n_reference)):
        raise ValueError('positive finite SI parameters required')
    dn = np.asarray(delta_n)
    if dn.shape != (points, points) or np.iscomplexobj(dn) or not np.isfinite(dn).all():
        raise ValueError('finite real index on declared grid required')
    if np.max(abs(dn)) > .01 or np.min(n_reference + dn) <= 0:
        raise ValueError('outside weak-index domain')
    dx, dz = width_m / points, length_m / steps
    k0 = 2 * math.pi / wavelength_m
    f = 2 * math.pi * np.fft.fftfreq(points, d=dx)
    kx, ky = np.meshgrid(f, f, indexing='xy')
    axis = (np.arange(points) - points // 2) * dx
    x, y = np.meshgrid(axis, axis, indexing='xy')
    edge = np.maximum(abs(x), abs(y)) / (width_m / 2)
    return (np.exp(.5j * k0 * dn * dz),
            np.exp(-1j * (kx*kx + ky*ky) * dz / (2*k0*n_reference)),
            np.exp(-np.maximum((edge-.7)/.3, 0)**4 * dz/50e-6))


def validate_field(field, points):
    a = np.asarray(field)
    if a.shape != (points, points) or not np.isfinite(a).all() or not np.any(a):
        raise ValueError('finite nonzero input field required')
    return a


def cuda_propagate(torch, a, half_phase, diffraction, damping, *, steps, dx_m,
                   deadline):
    """Resident tensors; no intermediate field readback or phase alignment.

    Per-step boundary power is accumulated on GPU, not inferred from the
    final energy difference. Only final scalar budget is read back.
    """
    if any(t.device.type != 'cuda' for t in (a, half_phase, diffraction, damping)):
        raise ValueError('all tensors must be CUDA resident')
    b = a.clone()
    removed = torch.zeros((), device=a.device, dtype=torch.float64)
    initial = (b.abs().square().to(torch.float64).sum()) * dx_m**2
    for step in range(steps):
        if step % 16 == 0 and time.monotonic() >= deadline:
            raise TimeoutError('GPU SSFM deadline')
        b *= half_phase
        b = torch.fft.ifft2(torch.fft.fft2(b) * diffraction)
        b *= half_phase
        before = b.abs().square().to(torch.float64).sum()
        b *= damping
        after = b.abs().square().to(torch.float64).sum()
        removed += (before - after) * dx_m**2
    final = b.abs().square().to(torch.float64).sum() * dx_m**2
    budget = torch.stack((initial, final, removed)).cpu().numpy()
    return b, dict(input_power=float(budget[0]), output_power=float(budget[1]),
                   boundary_removed=float(budget[2]), material_removed=0.0,
                   balance_relative=float(abs(budget[0]-budget[1]-budget[2])/budget[0]))
