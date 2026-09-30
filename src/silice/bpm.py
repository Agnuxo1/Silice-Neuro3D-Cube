"""Bounded CPU scalar weak-index paraxial SSFM; all lengths in metres.

Forward, monochromatic, no polarization/reflection. Fourier boundaries are
periodic; optional sponge removes numerical radiation, not material loss.
"""
from dataclasses import dataclass
import math
import time

import numpy as np


@dataclass(frozen=True)
class Grid:
    points: int = 128
    width_m: float = 96e-6

    def __post_init__(self):
        if isinstance(self.points, bool) or not isinstance(self.points, int):
            raise ValueError("points must be an integer")
        if not 16 <= self.points <= 256:
            raise ValueError("bounded research grid: 16 <= points <= 256")
        if not math.isfinite(self.width_m) or self.width_m <= 0:
            raise ValueError("width_m must be finite and positive")

    @property
    def dx_m(self):
        return self.width_m / self.points

    def coordinates(self):
        axis = (np.arange(self.points) - self.points // 2) * self.dx_m
        return np.meshgrid(axis, axis, indexing="xy")


def gaussian(grid, waist_m):
    if not math.isfinite(waist_m) or waist_m <= 0:
        raise ValueError("waist_m must be positive")
    x, y = grid.coordinates()
    field = np.exp(-(x*x + y*y) / waist_m**2).astype(np.complex128)
    return field / math.sqrt(power(field, grid))


def power(field, grid):
    return float(np.sum(np.abs(field)**2) * grid.dx_m**2)


def index_profile(grid, core_radius_m, thickness_m, delta_n, kind="ring"):
    values = (core_radius_m, thickness_m, delta_n)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("profile parameters must be finite")
    if core_radius_m <= 0 or thickness_m <= 0:
        raise ValueError("radii/thickness must be positive")
    if core_radius_m + thickness_m >= grid.width_m / 2:
        raise ValueError("profile must fit inside transverse domain")
    x, y = grid.coordinates()
    radius = np.hypot(x, y)
    if kind == "ring":
        mask = (radius >= core_radius_m) & (radius < core_radius_m+thickness_m)
    elif kind == "core":
        mask = radius < core_radius_m
    else:
        raise ValueError("kind must be ring or core")
    return np.where(mask, delta_n, 0.0)


def propagate(field, delta_n, grid, *, wavelength_m=1550e-9,
              n_reference=1.444, length_m=2e-3, steps=200,
              sponge=True, material_loss_db_per_m=0.0, deadline=None):
    """Strang step. No renormalization; retain each removed-power budget."""
    if isinstance(steps, bool) or not isinstance(steps, int) or not 1 <= steps <= 1000:
        raise ValueError("steps must be an integer in [1,1000]")
    scalars = (wavelength_m, n_reference, length_m, material_loss_db_per_m)
    if not all(math.isfinite(v) for v in scalars):
        raise ValueError("parameters must be finite")
    if wavelength_m <= 0 or n_reference <= 0 or length_m <= 0:
        raise ValueError("wavelength, index and length must be positive")
    if material_loss_db_per_m < 0:
        raise ValueError("passive model cannot have negative loss")
    array = np.array(field, dtype=np.complex128, copy=True)
    dn = np.asarray(delta_n)
    shape = (grid.points, grid.points)
    if array.shape != shape or dn.shape != shape:
        raise ValueError("field/profile shape must match grid")
    if np.iscomplexobj(dn) or not np.all(np.isfinite(dn)):
        raise ValueError("delta_n must be finite and real")
    if not np.all(np.isfinite(array)) or power(array, grid) <= 0:
        raise ValueError("input field must be finite and nonzero")
    if np.max(np.abs(dn)) > 0.01 or np.min(n_reference+dn) <= 0:
        raise ValueError("outside declared weak-index domain")
    dz = length_m / steps
    k0 = 2*math.pi / wavelength_m
    beta0 = k0*n_reference
    f = 2*math.pi*np.fft.fftfreq(grid.points, d=grid.dx_m)
    kx, ky = np.meshgrid(f, f, indexing="xy")
    diffraction = np.exp(-1j*(kx*kx+ky*ky)*dz/(2*beta0))
    half_phase = np.exp(0.5j*k0*dn*dz)
    x, y = grid.coordinates()
    edge = np.maximum(np.abs(x), np.abs(y)) / (grid.width_m/2)
    # Fixed 50 um damping length, zero damping in central 70% of domain.
    damping = np.exp(-np.maximum((edge-0.7)/0.3, 0)**4 * dz/50e-6)
    attenuation = 10**(-material_loss_db_per_m*dz/20)
    p_initial = power(array, grid)
    material_removed = boundary_removed = 0.0
    for _ in range(steps):
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("CPU experiment deadline reached")
        array *= half_phase
        array = np.fft.ifft2(np.fft.fft2(array)*diffraction)
        array *= half_phase
        before = power(array, grid)
        array *= attenuation
        after = power(array, grid)
        material_removed += before-after
        if sponge:
            array *= damping
            boundary_removed += after-power(array, grid)
    p_final = power(array, grid)
    balance = abs(p_initial-p_final-material_removed-boundary_removed)/p_initial
    return array, {
        "input_power": p_initial, "output_power": p_final,
        "material_removed": material_removed, "boundary_removed": boundary_removed,
        "balance_relative": balance, "backend": "scalar_paraxial_cpu_ssfm",
        "steps": steps, "dx_m": grid.dx_m, "dz_m": dz,
    }


def metrics(field, grid, core_radius_m):
    x, y = grid.coordinates()
    intensity = np.abs(field)**2
    total = float(intensity.sum())
    if total <= 0 or not np.isfinite(total):
        raise ValueError("metrics require finite nonzero power")
    r2 = x*x+y*y
    return {
        "core_fraction_remaining": float(intensity[r2<core_radius_m**2].sum()/total),
        "rms_radius_m": math.sqrt(float((intensity*r2).sum()/total)),
        "edge_fraction_remaining": float(intensity[
            np.maximum(np.abs(x), np.abs(y))>0.4*grid.width_m].sum()/total),
    }
