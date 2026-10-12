"""Decision statistics for preregistered claims (kit v2).

Implements a complete three-zone decision rule, equivalence (TOST) and
one-sided tests, sample-size planning for between-chip studies, exact
binomial intervals for yields, distribution-free tolerance bounds for tail
percentiles and Holm multiplicity control. Each function states its
assumptions; none of them turns a model result into a measurement.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import beta, binom, nct, t

from agentkit.evidence import write_new_json


def _finite(*values: float) -> None:
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in values):
        raise ValueError("Inputs must be finite numbers")


def three_zone_decision(ci_low: float, ci_high: float, threshold: float,
                        model_floor: float | None = None) -> dict:
    """Classify a confidence interval for a loss-like quantity (smaller is better).

    CONFIRMED: ci_high <= threshold and (no floor or ci_low >= floor).
    FALSIFIED: ci_low > threshold.
    MODEL_CONTROL_FAIL: ci_high < floor (the measurement beats an ideal limit,
    which signals a model or measurement error, never a success).
    INCONCLUSIVE: every other case, including an interval containing the
    threshold or the floor. Every zone is defined before any data are seen.
    """
    _finite(ci_low, ci_high, threshold)
    if ci_low > ci_high:
        raise ValueError("Interval bounds are reversed")
    if model_floor is not None:
        _finite(model_floor)
        if not model_floor < threshold:
            raise ValueError("The model floor must lie below the threshold")
    threshold_zone = ("below" if ci_high <= threshold else
                      "above" if ci_low > threshold else "straddles")
    floor_zone = None
    if model_floor is not None:
        floor_zone = ("above" if ci_low >= model_floor else
                      "below" if ci_high < model_floor else "straddles")
    if floor_zone == "below":
        verdict = "MODEL_CONTROL_FAIL"
    elif threshold_zone == "above":
        verdict = "FALSIFIED"
    elif threshold_zone == "below" and floor_zone in (None, "above"):
        verdict = "CONFIRMED"
    else:
        verdict = "INCONCLUSIVE"
    return {"verdict": verdict, "threshold_zone": threshold_zone,
            "floor_zone": floor_zone, "interval": [ci_low, ci_high],
            "threshold": threshold, "model_floor": model_floor}


def _mean_se(values) -> tuple[float, float, int]:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.all(np.isfinite(x)):
        raise ValueError("At least two finite independent values are required")
    return float(x.mean()), float(x.std(ddof=1) / math.sqrt(len(x))), len(x)


def one_sided_upper(values, threshold: float, alpha: float = 0.05) -> dict:
    """Test H0: mean >= threshold against H1: mean < threshold (t, independent units)."""
    _finite(threshold, alpha)
    if not 0 < alpha < 0.5:
        raise ValueError("alpha must lie in (0, 0.5)")
    mean, se, n = _mean_se(values)
    if se == 0:
        raise ValueError("Zero spread: the t model is not identifiable")
    statistic = (mean - threshold) / se
    return {"mean": mean, "standard_error": se, "n": n,
            "p_value": float(t.cdf(statistic, n - 1)),
            "upper_confidence_bound": mean + float(t.ppf(1 - alpha, n - 1)) * se,
            "reject_h0": bool(t.cdf(statistic, n - 1) < alpha), "alpha": alpha}


def tost(values, low: float, high: float, alpha: float = 0.05) -> dict:
    """Two one-sided tests (Schuirmann 1987) for equivalence within [low, high]."""
    _finite(low, high, alpha)
    if not low < high or not 0 < alpha < 0.5:
        raise ValueError("Require low < high and alpha in (0, 0.5)")
    mean, se, n = _mean_se(values)
    if se == 0:
        raise ValueError("Zero spread: the t model is not identifiable")
    p_low = float(t.sf((mean - low) / se, n - 1))
    p_high = float(t.cdf((mean - high) / se, n - 1))
    margin = float(t.ppf(1 - alpha, n - 1)) * se
    return {"mean": mean, "n": n, "p_low": p_low, "p_high": p_high,
            "equivalent": bool(max(p_low, p_high) < alpha),
            "ci_1_minus_2alpha": [mean - margin, mean + margin], "alpha": alpha}


def one_sided_power(n: int, effect: float, sigma: float, alpha: float = 0.05) -> float:
    """Power of the one-sided t test for a true margin `effect` below the threshold."""
    if type(n) is not int or n < 2:
        raise ValueError("n must be an integer of at least two")
    _finite(effect, sigma, alpha)
    if effect <= 0 or sigma <= 0:
        raise ValueError("effect and sigma must be positive")
    critical = t.ppf(1 - alpha, n - 1)
    return float(nct.sf(critical, n - 1, effect / sigma * math.sqrt(n)))


def sample_size_one_sided(effect: float, sigma: float, alpha: float = 0.025,
                          power: float = 0.8, max_n: int = 10000) -> int:
    """Smallest number of independent units (e.g. chips) reaching the target power.

    alpha = 0.025 matches a decision taken from one bound of a two-sided 95 %
    interval, as in three_zone_decision. The plan assumes the decision uses
    the between-unit standard error; metrology.fit_cutback uses the larger of
    the between-chip and measurement errors, so treat the result as a minimum.
    """
    _finite(power)
    if not 0 < power < 1:
        raise ValueError("power must lie in (0, 1)")
    for n in range(2, max_n + 1):
        if one_sided_power(n, effect, sigma, alpha) >= power:
            return n
    raise ValueError("Target power is not reachable within max_n")


def clopper_pearson(k: int, n: int, confidence: float = 0.95) -> list[float]:
    """Exact two-sided binomial interval (Clopper and Pearson 1934)."""
    if type(k) is not int or type(n) is not int or not 0 <= k <= n or n < 1:
        raise ValueError("Require integers 0 <= k <= n, n >= 1")
    alpha = 1 - confidence
    low = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    high = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [low, high]


def wilks_sample_size(coverage: float = 0.95, confidence: float = 0.95, order: int = 1) -> int:
    """Runs needed so the `order`-th largest value bounds the coverage quantile."""
    _finite(coverage, confidence)
    if not (0 < coverage < 1 and 0 < confidence < 1) or type(order) is not int or order < 1:
        raise ValueError("Invalid coverage, confidence or order")
    n = order
    while binom.sf(order - 1, n, 1 - coverage) < confidence:
        n += 1
        if n > 10_000_000:
            raise ValueError("Sample size beyond supported range")
    return n


def upper_tolerance_bound(values, coverage: float = 0.95, confidence: float = 0.95) -> dict:
    """Distribution-free one-sided upper bound for the coverage quantile.

    Valid for independent, identically distributed realizations. Correlated
    Monte Carlo draws or reused seeds violate this premise.
    """
    x = np.sort(np.asarray(values, dtype=float))
    if x.ndim != 1 or not np.all(np.isfinite(x)):
        raise ValueError("Values must be finite")
    n = len(x)
    best = None
    for r in range(1, n + 1):
        if binom.sf(r - 1, n, 1 - coverage) >= confidence:
            best = r
        else:
            break
    if best is None:
        return {"bound": None, "n": n, "required_n": wilks_sample_size(coverage, confidence),
                "coverage": coverage, "confidence": confidence}
    return {"bound": float(x[n - best]), "order_from_top": best, "n": n,
            "achieved_confidence": float(binom.sf(best - 1, n, 1 - coverage)),
            "coverage": coverage, "confidence": confidence}


def holm(p_values, alpha: float = 0.05) -> list[bool]:
    """Holm step-down rejection decisions in the original order."""
    p = np.asarray(p_values, dtype=float)
    if p.ndim != 1 or len(p) < 1 or np.any((p < 0) | (p > 1)):
        raise ValueError("p-values must lie in [0, 1]")
    order = np.argsort(p)
    reject = np.zeros(len(p), dtype=bool)
    for rank, index in enumerate(order):
        if p[index] <= alpha / (len(p) - rank):
            reject[index] = True
        else:
            break
    return reject.tolist()


def main() -> None:
    """Compute a preregistered decision from a JSON request and keep the result."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    zone = commands.add_parser("decide")
    zone.add_argument("--ci-low", type=float, required=True)
    zone.add_argument("--ci-high", type=float, required=True)
    zone.add_argument("--threshold", type=float, required=True)
    zone.add_argument("--model-floor", type=float)
    size = commands.add_parser("sample-size")
    size.add_argument("--effect", type=float, required=True)
    size.add_argument("--sigma", type=float, required=True)
    size.add_argument("--alpha", type=float, default=0.025)
    size.add_argument("--power", type=float, default=0.8)
    yields = commands.add_parser("yield")
    yields.add_argument("--k", type=int, required=True)
    yields.add_argument("--n", type=int, required=True)
    for sub in (zone, size, yields):
        sub.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "decide":
        result = three_zone_decision(args.ci_low, args.ci_high, args.threshold, args.model_floor)
    elif args.command == "sample-size":
        n = sample_size_one_sided(args.effect, args.sigma, args.alpha, args.power)
        result = {"n_independent_units": n, "effect": args.effect, "sigma": args.sigma,
                  "alpha": args.alpha, "power_target": args.power,
                  "achieved_power": one_sided_power(n, args.effect, args.sigma, args.alpha),
                  "assumption": "independent, approximately normal unit means; sigma is a planning value"}
    else:
        result = {"k": args.k, "n": args.n, "fraction": args.k / args.n,
                  "clopper_pearson_95": clopper_pearson(args.k, args.n)}
    write_new_json(args.out, result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
