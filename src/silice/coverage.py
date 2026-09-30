"""Cell averages for ideal glass profiles; original solver stays immutable."""
from dataclasses import dataclass
import math
import time

import numpy as np

from silice.tracks import track_centres


@dataclass(frozen=True)
class CellGrid:
    points: int = 256
    width_m: float = 128e-6

    def __post_init__(self):
        if isinstance(self.points, bool) or not isinstance(self.points, int) or not 16 <= self.points <= 320:
            raise ValueError("opt-in cell grid requires integer points in [16,320]")
        if not math.isfinite(self.width_m) or self.width_m <= 0:
            raise ValueError("finite positive grid width required")

    @property
    def dx_m(self):
        return self.width_m / self.points

    def coordinates(self):
        ax = (np.arange(self.points) - self.points // 2) * self.dx_m
        return np.meshgrid(ax, ax, indexing="xy")


def circle_coverage(grid, radius_m):
    """Analytic circle/rectangle area; exact geometry, not exact field integral."""
    if not math.isfinite(radius_m) or not 0 < radius_m < grid.width_m / 2 - grid.dx_m:
        raise ValueError("circle must fit safely in grid")
    x, y = grid.coordinates()
    r = radius_m

    def primitive(a, b):
        u = np.minimum(np.abs(a), r) / r
        v = np.minimum(np.abs(b), r) / r
        stop = np.minimum(u, np.sqrt(np.maximum(1 - v*v, 0)))

        def arc(t):
            return .5 * (t*np.sqrt(np.maximum(1 - t*t, 0)) + np.arcsin(t))

        # Dimensionless primitive over [0,u]x[0,v], extended with signs.
        return np.sign(a)*np.sign(b)*(v*stop + arc(u) - arc(stop))

    h = grid.dx_m / 2
    area = (primitive(x+h, y+h) - primitive(x-h, y+h)
            - primitive(x+h, y-h) + primitive(x-h, y-h))
    weights = area * (r / grid.dx_m)**2
    # Cancelled primitives outside the circle should be exactly empty.
    near_x = np.maximum(np.abs(x)-h, 0)
    near_y = np.maximum(np.abs(y)-h, 0)
    outside = near_x**2 + near_y**2 >= r*r
    inside = (np.abs(x)+h)**2 + (np.abs(y)+h)**2 <= r*r
    weights[outside] = 0
    weights[inside] = 1
    return np.clip(weights, 0, 1)


def union_coverage(grid, centres, track_radius_m=1.25e-6,
                   core_radius_m=6e-6, thickness_m=6e-6, samples=16, deadline=None):
    """Midpoint raster of union, only local support and per-disk bounding boxes."""
    if samples not in (16, 32, 64):
        raise ValueError("coverage sampling must be16/32/64")
    if not math.isfinite(track_radius_m) or track_radius_m <= 0 or not centres:
        raise ValueError("positive radius and nonempty centers required")
    if any(not all(math.isfinite(v) for v in c) for c in centres):
        raise ValueError("finite centers required")
    if not math.isfinite(core_radius_m) or core_radius_m <= 0 or not math.isfinite(thickness_m) or thickness_m <= 0:
        raise ValueError("finite positive ring dimensions required")
    bound = core_radius_m + thickness_m
    if bound >= grid.width_m / 2 - grid.dx_m:
        raise ValueError("ring must fit in grid")
    ax = (np.arange(grid.points) - grid.points // 2) * grid.dx_m
    indices = np.flatnonzero(np.abs(ax) <= bound + grid.dx_m)
    offsets = (np.arange(samples) + .5) / samples - .5
    fine = (ax[indices, None] + offsets*grid.dx_m).reshape(-1)
    occupied = np.zeros((fine.size, fine.size), dtype=bool)
    for cx, cy in centres:
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("profile construction deadline")
        i0, i1 = np.searchsorted(fine, [cx-track_radius_m, cx+track_radius_m], side="left")
        j0, j1 = np.searchsorted(fine, [cy-track_radius_m, cy+track_radius_m], side="left")
        dx = fine[i0:i1] - cx
        dy = fine[j0:j1] - cy
        occupied[j0:j1, i0:i1] |= dy[:, None]**2 + dx[None, :]**2 <= track_radius_m**2
    # Do not allocate a float64 full fine-grid radius array (up to130MiB).
    for row in range(0, fine.size, 128):
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("profile clipping deadline")
        r2 = fine[row:row+128, None]**2 + fine[None, :]**2
        occupied[row:row+128] &= (r2 >= core_radius_m**2) & (r2 < bound**2)
    small = occupied.reshape(len(indices), samples, len(indices), samples).mean(axis=(1, 3))
    full = np.zeros((grid.points, grid.points))
    full[np.ix_(indices, indices)] = small
    return full


def averaged_profile(grid, *, per_ring=None, missing_wedge_rad=0,
                     match_integral=False, delta_n=-.003, samples=16, deadline=None):
    if not math.isfinite(delta_n) or not -.01 <= delta_n < 0:
        raise ValueError("passive weak index required")
    core = circle_coverage(grid, 6e-6)
    outer = circle_coverage(grid, 12e-6)
    continuous = np.maximum(outer-core, 0)
    if per_ring is None:
        coverage = continuous
        centres = ()
        reference_area = 108*math.pi*1e-12
        raster_reference = "analytic_ring"
    else:
        centres = track_centres(per_ring=per_ring, missing_wedge_rad=missing_wedge_rad)
        coverage = union_coverage(grid, centres, samples=samples, deadline=deadline)
        fine = union_coverage(grid, centres, samples=64, deadline=deadline)
        reference_area = float(fine.sum()*grid.dx_m**2)
        raster_reference = "midpoint64_not_exact_area"
    area = float(coverage.sum()*grid.dx_m**2)
    if area <= 0 or reference_area <= 0:
        raise ValueError("unresolved profile")
    scale = float(continuous.sum()/coverage.sum()) if match_integral else 1.0
    if abs(delta_n*scale) > .01:
        raise ValueError("equal integral exceeds weak-index budget")
    dn = delta_n*scale*coverage
    x, y = grid.coordinates()
    h = grid.dx_m/2
    entirely_core = (np.abs(x)+h)**2 + (np.abs(y)+h)**2 <= (6e-6)**2
    entirely_outside = np.maximum(np.abs(x)-h, 0)**2 + np.maximum(np.abs(y)-h, 0)**2 >= (12e-6)**2
    return dn, core, dict(
        tracks_count=len(centres) if centres else None,
        centres_m=centres, samples=samples, integral_scale=scale,
        modified_area_m2=area, reference_area_m2=reference_area,
        reference_area_method=raster_reference,
        coverage_area_relative_error=abs(area/reference_area-1),
        ring_fill_fraction=area/(108*math.pi*1e-12),
        detector_area_relative_error=abs(core.sum()*grid.dx_m**2/(36*math.pi*1e-12)-1),
        integral_abs_delta_n_m2=float(abs(dn).sum()*grid.dx_m**2),
        integral_match_relative_error=abs(abs(dn).sum()/continuous.sum()/abs(delta_n)-1) if match_integral else None,
        peak_delta_n=float(dn.min()),
        fully_core_cells_untouched=bool(np.all(dn[entirely_core] == 0)),
        fully_outside_cells_untouched=bool(np.all(dn[entirely_outside] == 0)),
    )


def weighted_core_power(field, weights, grid, input_power):
    a = np.asarray(field)
    w = np.asarray(weights)
    if (a.shape != (grid.points, grid.points) or w.shape != a.shape
            or not np.all(np.isfinite(a)) or not np.all(np.isfinite(w))
            or np.any(w < 0) or np.any(w > 1) or not math.isfinite(input_power) or input_power <= 0):
        raise ValueError("finite bounded detector and positive input power required")
    return float((w*np.abs(a)**2).sum()*grid.dx_m**2/input_power)
