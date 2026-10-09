"""Analytic row/column/channel markers; no optics, GPU import or prior frames."""
import numpy as np

SIZES = ((8, 5), (13, 7), (32, 16))  # width, height; deliberately non-square
CASES = ('constant', 'coordinates')
TOLERANCE = 1e-6


def expected(case, width, height):
    if case not in CASES or (width, height) not in SIZES:
        raise ValueError('unregistered marker')
    if case == 'constant':
        return np.broadcast_to(np.array([.125, .375, .625, .875]),
                               (height, width, 4)).copy()
    x, y = np.meshgrid((np.arange(width)+.5)/width,
                       (np.arange(height)+.5)/height)
    return np.stack((x, y, .125+.25*x+.5*y, np.ones_like(x)), axis=-1)


def old_export_prediction(rgba):
    """C pixel storage presented with the F strides exported by Blender 4.5.14."""
    a = np.asarray(rgba)
    if a.ndim != 3 or a.shape[-1] != 4:
        raise ValueError('RGBA shape')
    return a.ravel(order='C').reshape(a.shape, order='F')


def check_marker(actual, reference):
    a = np.asarray(actual)
    if a.dtype != np.float32 or a.shape != reference.shape or not np.isfinite(a).all():
        raise ValueError('invalid readback')
    error = float(np.max(np.abs(a.astype(np.float64)-reference)))
    return {'max_channel_error': error, 'pass': error <= TOLERANCE}
