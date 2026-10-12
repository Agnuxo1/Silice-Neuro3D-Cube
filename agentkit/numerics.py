"""Small independent controls for coherent optics and numerical error.

Dense routines are restricted to reduced systems. Large FEM matrices must
use sparse solvers with a separately reviewed resource and accuracy protocol.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.linalg import eig, eigh, expm, expm_frechet
from scipy.optimize import linprog
from scipy.sparse import csr_matrix


def finite_array(value, *, ndim=None) -> np.ndarray:
    """Convert numerical input and reject NaNs and infinities."""
    array = np.asarray(value)
    if ndim is not None and array.ndim != ndim:
        raise ValueError("Unexpected array dimension")
    if not np.all(np.isfinite(array)):
        raise ValueError("Array must contain only finite values")
    return array


def mass_matrix(mass, n: int) -> np.ndarray:
    """Validate a positive Hermitian mass matrix or positive diagonal weights."""
    if not 1 <= n <= 512:
        raise ValueError("Dense reduced-system limit is 512 degrees of freedom")
    m = finite_array(mass)
    if m.ndim == 1:
        if m.shape != (n,) or np.iscomplexobj(m) or np.min(m) <= 0:
            raise ValueError("Mass weights must be positive and real")
        return np.diag(m)
    if m.shape != (n, n) or not np.allclose(m, m.conj().T, atol=1e-13, rtol=1e-13):
        raise ValueError("Mass matrix must be Hermitian")
    np.linalg.cholesky(m)
    return m


def mass_power(field, mass) -> float:
    """Compute the physical quadratic norm without normalizing the field."""
    u = finite_array(field, ndim=1).astype(complex)
    m = mass_matrix(mass, len(u))
    value = np.vdot(u, m @ u)
    if abs(value.imag) > 1e-11 * max(1.0, abs(value.real)):
        raise ValueError("Mass power has a material imaginary component")
    return float(value.real)


def logarithmic_norm(operator, mass) -> float:
    """Bound growth for M du/dz = A u in the validated mass norm."""
    a = finite_array(operator, ndim=2).astype(complex)
    if a.shape[0] != a.shape[1]:
        raise ValueError("Generator numerator must be square")
    m = mass_matrix(mass, len(a))
    return float(eigh((a+a.conj().T)/2, m, eigvals_only=True)[-1])


def residual_error_bound(times, residual_upper_bounds, initial_error: float,
                         growth_bound: float) -> float:
    """Integrate certified per-interval residual enclosures.

    Each supplied value must upper-bound the residual norm throughout its
    interval. Point samples alone do not satisfy this mathematical premise.
    """
    time = finite_array(times, ndim=1).astype(float)
    upper = finite_array(residual_upper_bounds, ndim=1).astype(float)
    if (len(time) < 2 or upper.shape != (len(time)-1,) or np.min(np.diff(time)) <= 0
            or np.min(upper) < 0 or not math.isfinite(initial_error)
            or initial_error < 0 or not math.isfinite(growth_bound)):
        raise ValueError("Residual enclosure inputs are invalid")
    end = time[-1]
    bound = math.exp(growth_bound*(end-time[0])) * initial_error
    for begin, finish, value in zip(time[:-1], time[1:], upper):
        duration = finish-begin
        weight = (duration if growth_bound == 0 else
                  math.exp(growth_bound*(end-finish)) *
                  math.expm1(growth_bound*duration) / growth_bound)
        bound += value*weight
    if not math.isfinite(bound):
        raise ValueError("Residual bound overflowed")
    return float(bound)


def detector_error_bound(reference_field, mass, detector, field_error: float) -> float:
    """Propagate a valid mass-norm field bound to a PSD detector functional."""
    u = finite_array(reference_field, ndim=1).astype(complex)
    m = mass_matrix(mass, len(u))
    d = finite_array(detector, ndim=2).astype(complex)
    if d.shape != m.shape or not np.allclose(d, d.conj().T, atol=1e-13):
        raise ValueError("Detector must be a matching Hermitian operator")
    spectrum = eigh(d, m, eigvals_only=True)
    if spectrum[0] < -1e-12 or not math.isfinite(field_error) or field_error < 0:
        raise ValueError("Detector must be PSD and field error nonnegative")
    norm = max(0.0, float(spectrum[-1]))
    return norm*(2*math.sqrt(mass_power(u, m))*field_error + field_error**2)


def coherent_decomposition(field, basis, mass, dual=None) -> dict:
    """Return mode, remainder and cross power with an exact coherent balance.

    With no dual, use the mass-orthogonal projection onto the basis span.
    With a dual, require dual.H @ M @ basis = I. Individual nonorthogonal
    modal powers are not additive and coefficients are not efficiencies.
    """
    u = finite_array(field, ndim=1).astype(complex)
    r = finite_array(basis, ndim=2).astype(complex)
    if r.shape[0] != len(u) or not 1 <= r.shape[1] <= len(u):
        raise ValueError("Basis shape is invalid")
    m = mass_matrix(mass, len(u))
    gram = r.conj().T @ m @ r
    if dual is None:
        if np.linalg.cond(gram) > 1e12:
            raise ValueError("Basis Gram matrix is too ill-conditioned")
        coefficients = np.linalg.solve(gram, r.conj().T @ m @ u)
    else:
        l = finite_array(dual, ndim=2).astype(complex)
        if l.shape != r.shape or np.linalg.norm(
                l.conj().T @ m @ r - np.eye(r.shape[1]), 2) > 1e-9:
            raise ValueError("Dual basis is not mass-biorthogonal")
        coefficients = l.conj().T @ m @ u
    mode = r @ coefficients
    remainder = u - mode
    total = mass_power(u, m)
    modal = mass_power(mode, m)
    residual = mass_power(remainder, m)
    cross = float(2 * np.real(np.vdot(mode, m @ remainder)))
    balance = total - modal - residual - cross
    return {"coefficients": coefficients, "mode": mode, "remainder": remainder,
            "total_power": total, "mode_power": modal,
            "remainder_power": residual, "cross_power": cross,
            "balance_error": float(abs(balance)),
            "basis_condition": float(np.linalg.cond(gram))}


def generalized_modes(operator, mass) -> dict:
    """Find left/right generalized modes and quantify nonnormal sensitivity."""
    k = finite_array(operator, ndim=2).astype(complex)
    if k.shape[0] != k.shape[1]:
        raise ValueError("Operator must be square")
    m = mass_matrix(mass, k.shape[0])
    values, left, right = eig(k, m, left=True, right=True)
    conditions, residuals = [], []
    scale = np.linalg.norm(k, 2) + np.linalg.norm(m, 2) * np.max(np.abs(values))
    for i, value in enumerate(values):
        rv = right[:, i]
        rv /= math.sqrt(mass_power(rv, m))
        overlap = np.vdot(left[:, i], m @ rv)
        if abs(overlap) <= 1e-13:
            raise ValueError("Near-defective eigenpair requires Schur/subspace analysis")
        left[:, i] /= np.conj(overlap)
        conditions.append(float(np.linalg.norm(left[:, i]) * np.linalg.norm(rv)))
        residuals.append(float(np.linalg.norm(k @ rv - value * (m @ rv)) /
                               max(np.finfo(float).tiny, scale * np.linalg.norm(rv))))
    gram = left.conj().T @ m @ right
    if np.linalg.norm(gram - np.eye(len(values)), 2) > 1e-8:
        raise ValueError("Eigenbasis is not biorthogonal; use invariant subspaces")
    return {"values": values, "right": right, "left": left,
            "relative_residuals": np.array(residuals),
            "eigenvalue_condition_indicators": np.array(conditions),
            "biorthogonality_error": float(np.linalg.norm(gram - np.eye(len(values)), 2))}


def splitting_control(a, b, initial, length: float, steps: int) -> dict:
    """Compare Strang with a dense exponential of the same discrete operator."""
    a, b = finite_array(a, ndim=2), finite_array(b, ndim=2)
    u = finite_array(initial, ndim=1).astype(complex)
    if a.shape != b.shape or a.shape != (len(u), len(u)) or len(u) > 128:
        raise ValueError("Dense splitting control requires matching matrices up to 128")
    if not math.isfinite(length) or length <= 0 or type(steps) is not int or steps < 1:
        raise ValueError("Length and step count must be positive")
    h = length / steps
    half, full = expm(h * a / 2), expm(h * b)
    approximation = u.copy()
    for _ in range(steps):
        approximation = half @ (full @ (half @ approximation))
    reference = expm(length * (a + b)) @ u
    commutator = a @ b - b @ a
    return {"field": approximation, "reference": reference,
            "relative_field_error": float(np.linalg.norm(approximation - reference) /
                                          max(np.linalg.norm(reference), 1e-300)),
            "commutator_norm": float(np.linalg.norm(commutator, 2)),
            "a_nested_norm": float(np.linalg.norm(a @ commutator - commutator @ a, 2)),
            "b_nested_norm": float(np.linalg.norm(b @ commutator - commutator @ b, 2))}


def transfer_sensitivity(generator, perturbation, length: float) -> dict:
    """Differentiate the complete complex transfer matrix, including phase."""
    h, dh = finite_array(generator, ndim=2), finite_array(perturbation, ndim=2)
    if h.shape != dh.shape or h.shape[0] != h.shape[1] or h.shape[0] > 128:
        raise ValueError("Reduced square matrices up to 128 are required")
    if not math.isfinite(length) or length <= 0:
        raise ValueError("Length must be positive")
    transfer, derivative = expm_frechet(1j * length * h, 1j * length * dh)
    return {"transfer": transfer, "derivative": derivative,
            "derivative_operator_norm": float(np.linalg.norm(derivative, 2))}


def optical_error_budget(index: float, length_m: float, wavelength_m: float,
                         delta_index: float, delta_length_m: float,
                         delta_wavelength_m: float = 0.0) -> dict:
    """Bound scalar optical-path phase perturbation, without claiming PDE closure."""
    inputs = (index, length_m, wavelength_m, delta_index,
              delta_length_m, delta_wavelength_m)
    if not all(math.isfinite(x) for x in inputs):
        raise ValueError("Budget values must be finite")
    if min(index, length_m, wavelength_m) <= 0 or min(inputs[3:]) < 0:
        raise ValueError("Nominal values must be positive and uncertainties nonnegative")
    if delta_wavelength_m >= wavelength_m:
        raise ValueError("Wavelength interval must exclude zero")
    opl_error = index * delta_length_m + length_m * delta_index + delta_index * delta_length_m
    phase_error = 2 * math.pi * (
        opl_error / (wavelength_m - delta_wavelength_m) +
        index * length_m * delta_wavelength_m /
        (wavelength_m * (wavelength_m - delta_wavelength_m)))
    return {"optical_path_error_m": opl_error, "phase_error_rad": phase_error,
            "unit_amplitude_field_error_bound": float(min(2.0, phase_error))}


def phase_metrics(reference, candidate, weights, amplitude_floor: float = 1e-12) -> dict:
    """Compare complex fields without global phase alignment."""
    ref, value, w = (finite_array(x, ndim=1) for x in (reference, candidate, weights))
    if (ref.shape != value.shape or w.shape != ref.shape or np.iscomplexobj(w)
            or np.min(w) < 0 or w.sum() <= 0):
        raise ValueError("Field and nonnegative weight shapes must agree")
    if not math.isfinite(amplitude_floor) or amplitude_floor <= 0:
        raise ValueError("Amplitude floor must be positive")
    error = np.sqrt(np.sum(w * abs(value - ref)**2))
    norm = np.sqrt(np.sum(w * abs(ref)**2))
    mask = (abs(ref) > amplitude_floor) & (abs(value) > amplitude_floor) & (w > 0)
    phase = np.angle(value[mask] * np.conj(ref[mask]))
    return {"absolute_field_error": float(error),
            "relative_field_error": None if norm == 0 else float(error / norm),
            "max_phase_error_rad": None if not mask.any() else float(np.max(abs(phase))),
            "phase_samples": int(mask.sum()),
            "power_difference": float(abs(np.sum(w * abs(value)**2) - np.sum(w * abs(ref)**2)))}


def spatial_forecast(powers, temporal_errors, ratio: float = 1.25) -> dict:
    """Implement the fixed S16 scalar forecast with strict eligibility gates."""
    p = finite_array(powers, ndim=1).astype(float)
    errors = finite_array(temporal_errors, ndim=1).astype(float)
    if p.shape != (3,) or errors.shape != (3,) or np.min(errors) < 0:
        raise ValueError("Three powers and three nonnegative temporal errors are required")
    if not math.isclose(ratio, 1.25, abs_tol=1e-14, rel_tol=0):
        raise ValueError("S16 fixes the refinement ratio to 1.25")
    d0, d1 = np.diff(p)
    same_sign = d0 != 0 and d1 != 0 and d0 * d1 > 0
    order = float(math.log(d0 / d1) / math.log(ratio)) if same_sign else None
    separation = min(abs(d0), abs(d1)) > 20 * max(errors)
    eligible = bool(same_sign and order is not None and 0.5 <= order <= 6 and separation)
    prediction = float(p[-1] + d1 / ratio**order) if eligible else None
    return {"eligible": eligible, "order": order, "prediction": prediction,
            "increments": [float(d0), float(d1)],
            "temporal_separation": bool(separation)}


def spatial_holdout(powers, temporal_errors, reserved_power: float,
                    temporal_psd_bound: float, reconstruction_difference: float,
                    quadrature_indicator: float) -> dict:
    """Evaluate S16's reserved sample; its uncertainty is a numerical indicator."""
    forecast = spatial_forecast(powers, temporal_errors)
    extras = (reserved_power, temporal_psd_bound, reconstruction_difference, quadrature_indicator)
    if not all(math.isfinite(x) for x in extras) or min(extras) < 0:
        raise ValueError("Reserved power and error indicators must be finite/nonnegative")
    if not forecast["eligible"]:
        return {"passed": False, "reason": "Forecast prerequisites failed", "forecast": forecast}
    increment = reserved_power - powers[-1]
    previous = forecast["increments"][-1]
    sign_ok = increment != 0 and increment * previous > 0
    order = math.log(previous / increment) / math.log(1.25) if sign_ok else None
    checks = {"same_sign": sign_ok,
              "order_range": order is not None and 0.5 <= order <= 6,
              "order_consistency": order is not None and
              abs(order - forecast["order"]) / max(order, forecast["order"]) <= 0.2,
              "prediction": abs(reserved_power - forecast["prediction"]) <= 0.1 * abs(increment),
              "temporal_separation": abs(increment) > 20 * max(temporal_errors)}
    uncertainty = None
    if checks["order_range"]:
        gci = 1.25 * abs(increment) / (1.25**min(order, 2.0) - 1.0)
        uncertainty = gci + temporal_psd_bound + reconstruction_difference + quadrature_indicator
    checks["budget"] = uncertainty is not None and uncertainty <= 1e-3 and uncertainty <= 0.01 * reserved_power
    checks = {key: bool(value) for key, value in checks.items()}
    return {"passed": all(checks.values()), "checks": checks,
            "new_order": order,
            "uncertainty_indicator": None if uncertainty is None else float(uncertainty),
            "forecast": forecast}


def exact_discrete_transport(source_points, source_mass, target_points, target_mass) -> dict:
    """Solve a bounded discrete quadratic OT problem with a checked LP.

    This is a calibration diagnostic. A finite barycentric plan is not the
    continuous Brenier map or a numerical implementation of the new theorem.
    """
    x, y = finite_array(source_points, ndim=2), finite_array(target_points, ndim=2)
    a, b = finite_array(source_mass, ndim=1), finite_array(target_mass, ndim=1)
    n, m = len(x), len(y)
    if x.shape[1] != y.shape[1] or a.shape != (n,) or b.shape != (m,):
        raise ValueError("Transport point and mass shapes disagree")
    if min(n, m) < 1 or n * m > 4096 or min(a.min(), b.min()) < 0:
        raise ValueError("Transport requires nonnegative masses and at most 4096 variables")
    if not np.isclose(a.sum(), 1.0) or not np.isclose(b.sum(), 1.0):
        raise ValueError("Transport masses must each sum to one")
    cost = np.sum((x[:, None, :] - y[None, :, :])**2, axis=2)
    rows = np.repeat(np.arange(n), m)
    cols = np.arange(n * m)
    source_constraints = csr_matrix((np.ones(n*m), (rows, cols)), shape=(n, n*m))
    rows = np.tile(np.arange(m), n)
    target_constraints = csr_matrix((np.ones(n*m), (rows, cols)), shape=(m, n*m))
    from scipy.sparse import vstack
    result = linprog(cost.ravel(), A_eq=vstack([source_constraints, target_constraints]),
                     b_eq=np.r_[a, b], bounds=(0, None), method="highs",
                     options={"time_limit": 20.0})
    if not result.success:
        raise RuntimeError("Transport LP failed: " + result.message)
    plan = result.x.reshape(n, m)
    marginal_error = max(np.max(abs(plan.sum(axis=1)-a)), np.max(abs(plan.sum(axis=0)-b)))
    if marginal_error > 1e-8 or plan.min() < -1e-10:
        raise RuntimeError("Transport solution failed the feasibility audit")
    positive = a > 0
    barycentres = np.full_like(x, np.nan, dtype=float)
    barycentres[positive] = (plan[positive] @ y) / a[positive, None]
    return {"plan": plan, "barycentres": barycentres,
            "wasserstein2": float(np.sqrt(max(0.0, result.fun))),
            "marginal_error": float(marginal_error)}
