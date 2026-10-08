"""Registered scalar-observable forecast and conditional spatial indicators."""
import math


def forecast(powers, temporal_differences, r=1.25):
    assert len(powers) == len(temporal_differences) == 3 and r == 1.25
    assert all(math.isfinite(v) and v > 0 for v in powers)
    assert all(math.isfinite(v) and v >= 0 for v in temporal_differences)
    a, b = powers[1]-powers[0], powers[2]-powers[1]
    monotone = a*b > 0
    p = math.log(a/b)/math.log(r) if monotone else None
    resolved = min(abs(a), abs(b)) > 20*max(temporal_differences)
    eligible = monotone and p is not None and .5 <= p <= 6 and resolved
    return dict(powers=list(powers), temporal_differences=list(temporal_differences), r=r,
                increments=[a,b], monotone=monotone, resolved_above_time_discrepancy=resolved,
                order=p, eligible=eligible, prediction=powers[2]+b/r**p if eligible else None)


def assess(powers, registered, temporal_differences, temporal_psd, quadrature_indicator, reconstruction_difference):
    assert len(powers) == len(temporal_differences) == 4
    assert powers[:3] == registered['powers'] and registered['r'] == 1.25
    assert all(math.isfinite(v) and v > 0 for v in powers)
    assert all(math.isfinite(v) and v >= 0 for v in temporal_differences)
    assert all(math.isfinite(v) and v >= 0 for v in (temporal_psd,quadrature_indicator,reconstruction_difference))
    d0 = powers[2]-powers[1]
    d1 = powers[3]-powers[2]
    monotone = d0*d1 > 0
    p = math.log(d0/d1)/math.log(1.25) if monotone else None
    valid_order = p is not None and .5 <= p <= 6
    stable = valid_order and registered['eligible'] and abs(p-registered['order'])/max(p,registered['order']) <= .2
    residual = abs(powers[3]-registered['prediction']) if registered['eligible'] else None
    prospective = residual is not None and residual <= .1*abs(d1)
    resolved = abs(d1) > 20*max(temporal_differences)
    U = 1.25*abs(d1)/(1.25**min(p,2)-1) if valid_order else None
    total = U+temporal_psd+quadrature_indicator+reconstruction_difference if U is not None else None
    bounded = total is not None and total <= 1e-3 and total <= .01*powers[3]
    passed = registered['eligible'] and monotone and valid_order and stable and prospective and resolved and bounded
    return dict(spatial_pass=bool(passed), point03_closed=False, powers=list(powers), order=p,
                order_discrepancy=abs(p-registered['order'])/max(p,registered['order']) if valid_order and registered['eligible'] else None,
                prediction=registered['prediction'], prediction_residual=residual, prediction_limit=.1*abs(d1),
                gates=dict(coarse_eligible=registered['eligible'], monotone=monotone, order_range=valid_order,
                           order_stability=bool(stable), prospective_prediction=prospective, temporal_resolution=resolved, total_indicator=bounded),
                indicators=dict(spatial=U,temporal_PSD=temporal_psd,quadrature=quadrature_indicator,
                                reconstruction=reconstruction_difference,total=total),
                scope='Conditional consistency indicators, not an absolute continuum error bound or statistical interval.')
