"""Ideal two-core geometry and explicitly nonmodal Gaussian port reduction."""
from dataclasses import dataclass
import math
import time

import numpy as np

from silice.bpm import power
from silice.coverage import circle_coverage


@dataclass(frozen=True)
class ShiftedGrid:
    grid: object
    cx: float

    @property
    def points(self):
        return self.grid.points

    @property
    def width_m(self):
        return self.grid.width_m

    @property
    def dx_m(self):
        return self.grid.dx_m

    def coordinates(self):
        x, y = self.grid.coordinates()
        return x-self.cx, y


def geometry(grid, *, separation_m=14e-6, radius_m=6e-6,
             thickness_m=6e-6, delta_n=-.005, samples=16, deadline=None):
    """Union of depressed annuli EXCLUDING both intact cores, not added indices.

    Close annuli overlap and are carved where they meet either core. This
    is an explicit coupling-region hypothesis, not two isolated fibre profiles.
    """
    if not all(math.isfinite(v) for v in (separation_m, radius_m, thickness_m, delta_n)):
        raise ValueError("finite geometry required")
    if radius_m <= 0 or thickness_m <= 0 or separation_m <= 2*radius_m:
        raise ValueError("positive dimensions and nonoverlapping cores required")
    if not -.01 <= delta_n < 0 or samples not in (16, 32):
        raise ValueError("weak depressed index and16/32subpixels required")
    outer = radius_m+thickness_m
    if separation_m/2+outer >= .35*grid.width_m-grid.dx_m:
        raise ValueError("geometry must fit before the unchanged70percent sponge")
    x, y = grid.coordinates()
    offsets = ((np.arange(samples)+.5)/samples-.5)*grid.dx_m
    coverage = np.zeros_like(x)
    for oy in offsets:
        for ox in offsets:
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError("two-core construction deadline")
            yl = (y+oy)**2
            rl = (x+ox+separation_m/2)**2+yl
            rr = (x+ox-separation_m/2)**2+yl
            modified = (((rl < outer**2) | (rr < outer**2))
                        & (rl >= radius_m**2) & (rr >= radius_m**2))
            coverage += modified
    coverage /= samples*samples
    weights = np.stack([circle_coverage(ShiftedGrid(grid, cx), radius_m)
                        for cx in (-separation_m/2, separation_m/2)])
    dn = delta_n*coverage
    h = grid.dx_m/2
    fully_core = np.zeros_like(x, dtype=bool)
    for cx in (-separation_m/2, separation_m/2):
        fully_core |= (np.abs(x-cx)+h)**2+(np.abs(y)+h)**2 <= radius_m**2
    meta = dict(separation_m=separation_m, radius_m=radius_m,
                thickness_m=thickness_m, delta_n=delta_n, samples=samples,
                topology="union_outer_disks_minus_both_intact_cores",
                modified_area_m2=float(coverage.sum()*grid.dx_m**2),
                detector_area_errors=[float(abs(w.sum()*grid.dx_m**2/(math.pi*radius_m**2)-1))
                                      for w in weights],
                fully_core_untouched=bool(np.all(dn[fully_core] == 0)),
                no_double_index=bool(np.min(dn) >= delta_n))
    return dn, weights, meta


def gaussian_ports(grid, separation_m=14e-6, waist_m=6e-6):
    """Symmetric inverse-square-root Gram orthogonalization; NOT guided modes."""
    if not all(math.isfinite(v) and v > 0 for v in (separation_m, waist_m)):
        raise ValueError("positive finite port dimensions required")
    x, y = grid.coordinates()
    raw = np.stack([np.exp(-((x-cx)**2+y*y)/waist_m**2).astype(complex)
                    for cx in (-separation_m/2, separation_m/2)])
    raw /= np.sqrt([power(v, grid) for v in raw])[:, None, None]
    gram = raw.reshape(2, -1).conj() @ raw.reshape(2, -1).T * grid.dx_m**2
    ev, vec = np.linalg.eigh(gram)
    if np.min(ev) <= 1e-8:
        raise ValueError("unresolved nearly dependent ports")
    inverse_root = (vec*ev**-.5) @ vec.conj().T
    basis = np.einsum("ab,bij->aij", inverse_root.T, raw)
    actual = basis.reshape(2, -1).conj() @ basis.reshape(2, -1).T * grid.dx_m**2
    return basis, dict(raw_overlap_abs=float(abs(gram[0, 1])),
                       orthogonality_error=float(np.max(np.abs(actual-np.eye(2)))),
                       basis_kind="orthonormalized_Gaussians_NOT_guided_eigenmodes")


def project(field, basis, grid):
    return np.einsum("aij,ij->a", basis.conj(), field)*grid.dx_m**2


def galerkin_generator(basis, dn, grid, wavelength_m=1550e-9, n_reference=1.444):
    """Project the SAME scalar generator; no fit or hidden loss correction."""
    k0 = 2*math.pi/wavelength_m
    beta0 = k0*n_reference
    f = 2*math.pi*np.fft.fftfreq(grid.points, d=grid.dx_m)
    kx, ky = np.meshgrid(f, f, indexing="xy")
    action = np.fft.ifft2(np.fft.fft2(basis)*(-(kx*kx+ky*ky)/(2*beta0)))+k0*dn*basis
    h = np.stack([project(v, basis, grid) for v in action], axis=1)
    error = float(np.max(np.abs(h-h.conj().T)))
    reconstructed = np.einsum("ab,aij->bij", h, basis)
    residual = [math.sqrt(power(v-r, grid)) for v, r in zip(action, reconstructed)]
    return h, dict(hermiticity_error_per_m=error,
                   out_of_basis_generator_norm_per_m=residual,
                   reduction="two_Gaussian_Galerkin_no_sponge_no_fit_NOT_modal_CMT")


def reduced_prediction(h, length_m, amplitudes):
    if not math.isfinite(length_m) or length_m < 0:
        raise ValueError("finite nonnegative length required")
    if np.max(np.abs(h-h.conj().T)) > 1e-8:
        raise ValueError("non-Hermitian generator rejected, not silently repaired")
    ev, vec = np.linalg.eigh(h)
    return (vec*np.exp(1j*ev*length_m)) @ vec.conj().T @ np.asarray(amplitudes)
