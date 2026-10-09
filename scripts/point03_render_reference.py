"""Independent float64 pixel reference for the preregistered P2 shader pilot."""
import numpy as np

TRIANGLE = np.array([[-.8, -.7], [.8, -.7], [0., .8]], dtype=np.float64)
NODAL = np.array([1.+.2j, .3-.4j, -.2+.7j, .6+.1j, -.1+.3j, .5-.2j])
CASES = {'single': (0.,), 'constructive': (0., 0.),
         'destructive': (0., np.pi), 'quarter': (0., np.pi/2)}
RESOLUTIONS = (64, 128, 256)
EDGE_MARGIN = 2e-6


def validate(triangle, nodal, resolution):
    t, a = np.asarray(triangle), np.asarray(nodal)
    if t.shape != (3, 2) or a.shape != (6,):
        raise ValueError('triangle/nodal shape')
    if not np.isfinite(t).all() or not np.isfinite(a).all():
        raise ValueError('nonfinite input')
    if not isinstance(resolution, int) or resolution not in RESOLUTIONS:
        raise ValueError('resolution outside fixed set')
    if abs(np.linalg.det(np.c_[t, np.ones(3)])) <= 1e-12:
        raise ValueError('degenerate triangle')


def shapes(bary):
    b = np.asarray(bary, dtype=np.float64)
    return np.stack([b[..., 0]*(2*b[..., 0]-1),
                     b[..., 1]*(2*b[..., 1]-1),
                     b[..., 2]*(2*b[..., 2]-1),
                     4*b[..., 0]*b[..., 1],
                     4*b[..., 1]*b[..., 2],
                     4*b[..., 2]*b[..., 0]], axis=-1)


def prepare(resolution, triangle=TRIANGLE):
    validate(triangle, NODAL, resolution)
    q = (np.arange(resolution, dtype=np.float64)+.5)*2/resolution-1
    x, y = np.meshgrid(q, q)
    rhs = np.stack([x, y, np.ones_like(x)], axis=-1)
    bary = rhs @ np.linalg.inv(np.vstack([np.asarray(triangle).T, np.ones(3)])).T
    ambiguous = np.any(np.abs(bary) <= EDGE_MARGIN, axis=-1)
    inside = np.all(bary > EDGE_MARGIN, axis=-1)
    return shapes(bary), inside, ~ambiguous


def nodal_for_repeat(repeat):
    if not isinstance(repeat, int) or not 0 <= repeat < 7:
        raise ValueError('repeat outside fixed set')
    perturb = np.array([.1j, .3+.1j, -.2j, .4-.1j, -.3+.2j, .2j])
    return NODAL*(1+.01*repeat)+.001*repeat*perturb


def evaluate_prepared(case, cache, nodal=NODAL):
    if case not in CASES or np.asarray(nodal).shape != (6,) or not np.isfinite(nodal).all():
        raise ValueError('invalid field/case')
    basis, inside, compare = cache
    field = np.einsum('...k,k->...', basis, nodal)
    field = np.where(inside, field, 0.)
    coherent = field*sum(np.exp(1j*p) for p in CASES[case])
    return coherent, inside, compare


def evaluate(case, resolution, triangle=TRIANGLE, nodal=NODAL):
    validate(triangle, nodal, resolution)
    return evaluate_prepared(case, prepare(resolution, triangle), nodal)


def metrics(gpu, cpu, inside, compare, single_power, pixel_area):
    if gpu.shape != cpu.shape or not np.isfinite(gpu).all():
        raise ValueError('invalid GPU output')
    delta = gpu[compare]-cpu[compare]
    maximum = float(np.max(np.abs(delta)))
    norm = float(np.linalg.norm(cpu[compare]))
    relative = float(np.linalg.norm(delta)/norm) if norm > 1e-12 else None
    gpu_power = float(np.sum(np.abs(gpu[compare])**2)*pixel_area)
    cpu_power = float(np.sum(np.abs(cpu[compare])**2)*pixel_area)
    outside = float(np.max(np.abs(gpu[compare & ~inside])))
    dark = gpu_power/single_power if norm <= 1e-12 else None
    gates = [maximum <= 5e-6, relative is None or relative <= 5e-6,
             abs(gpu_power-cpu_power) <= 5e-6, outside <= 1e-7,
             dark is None or dark <= 1e-10]
    return dict(max_complex_error=maximum, relative_l2=relative,
                gpu_power=gpu_power, cpu_power=cpu_power,
                outside_max=outside, dark_power_ratio=dark,
                included_pixels=int(compare.sum()),
                excluded_pixels=int((~compare).sum()), accuracy_pass=all(gates))
