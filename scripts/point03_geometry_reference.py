"""Independent vertical-integration reference for the Point 03 Stage D audit.

All input lengths are micrometres.  No candidate geometry code is imported.
The reference integrates a union of vertical disk intervals, intersects the
outer annulus disk, subtracts the inner disk and clips to the rectangle.
QUADPACK estimates and a two-tolerance comparison are diagnostics, not a
certified mathematical bound on transcendental floating-point calculations.

Importing this module does not evaluate geometry or invoke quadrature.
"""

from __future__ import annotations

import math
import time
import warnings
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from numbers import Real
from typing import Any, Callable


COARSE_TAU = 1e-13
FINE_TAU = 2.5e-14
QUALITY_LIMIT = 1e-13
OMISSION_LIMIT = 1e-14
FRACTION_RANGE_TOLERANCE = 1e-12
DECIMAL_PRECISION = 80
QUAD_LIMIT = 100
INTERNAL_SECONDS = 35.0
_EPS = math.ulp(1.0)


class ReferenceDeadlineExceeded(TimeoutError):
    """A caller/child deadline was reached; partial diagnostics are attached."""

    def __init__(self, message: str, diagnostics: dict[str, Any] | None = None):
        super().__init__(message)
        self.diagnostics = diagnostics or {}


class ReferenceEvaluationError(RuntimeError):
    """Reference execution failed; available partial diagnostics are attached."""

    def __init__(self, message: str, diagnostics: dict[str, Any] | None = None):
        super().__init__(message)
        self.diagnostics = diagnostics or {}


class _Clock:
    def __init__(self, deadline: float | None):
        self.started = time.monotonic()
        own = self.started + INTERNAL_SECONDS
        if deadline is None:
            self.deadline = own
        else:
            supplied = _number(deadline, "deadline")
            self.deadline = min(own, supplied)

    def check(self) -> None:
        if time.monotonic() >= self.deadline:
            raise ReferenceDeadlineExceeded("Independent geometry reference deadline reached")


def _number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _dec(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


@dataclass(frozen=True)
class _Circle:
    cx: float
    cy: float
    r: float
    xq: Fraction
    yq: Fraction
    rq: Fraction

    @classmethod
    def parse(cls, triple: Any, name: str) -> "_Circle":
        if not isinstance(triple, (list, tuple)) or len(triple) != 3:
            raise ValueError(f"{name} must be [cx, cy, radius]")
        cx, cy, radius = (_number(v, name) for v in triple)
        if radius < 0:
            raise ValueError(f"{name} radius must be nonnegative")
        return cls(cx, cy, radius, Fraction(cx), Fraction(cy), Fraction(radius))

    @property
    def key(self) -> tuple[float, float, float]:
        return self.cx, self.cy, self.r


@dataclass(frozen=True)
class _Rect:
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    x0q: Fraction
    x1q: Fraction
    y0q: Fraction
    y1q: Fraction
    wq: Fraction
    hq: Fraction
    width: float
    height: float
    area: float

    @classmethod
    def parse(cls, raw: Any) -> "_Rect":
        if not isinstance(raw, (list, tuple)) or len(raw) != 4:
            raise ValueError("rect must be (xmin, xmax, ymin, ymax)")
        xmin, xmax, ymin, ymax = (_number(v, "rect") for v in raw)
        if not xmin < xmax or not ymin < ymax:
            raise ValueError("rect must have positive width and height")
        x0q, x1q, y0q, y1q = map(Fraction, (xmin, xmax, ymin, ymax))
        wq, hq = x1q - x0q, y1q - y0q
        width, height, area = float(wq), float(hq), float(wq * hq)
        if not all(math.isfinite(v) and v > 0 for v in (width, height, area)):
            raise ValueError("rect dimensions/area are not representable positive floats")
        return cls(xmin, xmax, ymin, ymax, x0q, x1q, y0q, y1q,
                   wq, hq, width, height, area)

    @property
    def serialized(self) -> list[float]:
        return [self.xmin, self.xmax, self.ymin, self.ymax]


def _parse_spec(spec: Any) -> tuple[list[_Circle], _Circle | None, _Circle | None]:
    if not isinstance(spec, dict) or not isinstance(spec.get("disks"), (list, tuple)):
        raise ValueError("spec must contain a list of disks")
    disks = [_Circle.parse(disk, f"disks[{i}]") for i, disk in enumerate(spec["disks"])]
    ring = spec.get("annulus")
    if ring is None:
        return disks, None, None
    if not isinstance(ring, dict):
        raise ValueError("annulus must be null or a dictionary")
    center = ring.get("center")
    if not isinstance(center, (list, tuple)) or len(center) != 2:
        raise ValueError("annulus center must contain two coordinates")
    inner = _Circle.parse([*center, ring.get("inner")], "annulus inner")
    outer = _Circle.parse([*center, ring.get("outer")], "annulus outer")
    if not 0 <= inner.r < outer.r:
        raise ValueError("annulus radii must satisfy 0 <= inner < outer")
    return disks, outer, inner if inner.r > 0 else None


def _bbox_meets(circle: _Circle, rect: _Rect) -> bool:
    # Strict bbox overlap suffices: tangency alone has zero area.
    return (circle.rq > 0 and circle.xq + circle.rq > rect.x0q
            and circle.xq - circle.rq < rect.x1q
            and circle.yq + circle.rq > rect.y0q
            and circle.yq - circle.rq < rect.y1q)


def _pair_points(first: _Circle, second: _Circle) -> list[tuple[Decimal, Decimal]]:
    """Exact rational incidence predicates, then 80-digit point construction.

    The inputs are the exact values of their serialized binary floats.  This
    independent construction uses a rational line-of-centres projection and
    a perpendicular offset; no angular boundary or Green integration is used.
    """
    dx, dy = second.xq - first.xq, second.yq - first.yq
    distance2 = dx * dx + dy * dy
    if distance2 == 0:
        return []  # Concentric/coincident circles have no isolated crossings.
    if (distance2 > (first.rq + second.rq) ** 2
            or distance2 < (first.rq - second.rq) ** 2):
        return []
    projection = (distance2 + first.rq ** 2 - second.rq ** 2) / (2 * distance2)
    offset2 = first.rq ** 2 / distance2 - projection ** 2
    if offset2 < 0:
        raise ArithmeticError("Exact circle-incidence predicates disagree")
    footx = first.xq + projection * dx
    footy = first.yq + projection * dy
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        fx, fy = _dec(footx), _dec(footy)
        if offset2 == 0:
            return [(fx, fy)]
        scale = _dec(offset2).sqrt()
        ox, oy = -_dec(dy) * scale, _dec(dx) * scale
        return [(fx + ox, fy + oy), (fx - ox, fy - oy)]


def circle_intersections(disks: Any, with_provenance: bool = False,
                         deadline: float | None = None) -> list[Any]:
    """Return deterministic isolated track/track crossings, including tangency.

    Default: exact-duplicate float points removed, lexicographic [x,y] order.
    Provenance mode: one record per pair/crossing, ordered by (i,j,angle_rad),
    where the angle is measured about the first circle.  Coincident circles
    have no isolated intersection points.  This function performs no area
    integration and imports no candidate or SciPy module.
    """
    clock = _Clock(deadline)
    if not isinstance(disks, (list, tuple)):
        raise ValueError("disks must be a list")
    circles = [_Circle.parse(disk, f"disks[{i}]") for i, disk in enumerate(disks)]
    records: list[dict[str, Any]] = []
    points: set[tuple[float, float]] = set()
    for i, first in enumerate(circles):
        for j in range(i + 1, len(circles)):
            clock.check()
            for xdecimal, ydecimal in _pair_points(first, circles[j]):
                point = (float(xdecimal), float(ydecimal))
                if not all(math.isfinite(v) for v in point):
                    raise ValueError("Circle intersection is not representable")
                points.add(point)
                records.append({"pair": [i, j], "point": list(point),
                                "angle_rad": math.atan2(point[1] - first.cy,
                                                        point[0] - first.cx)})
    if with_provenance:
        return sorted(records, key=lambda item: (*item["pair"], item["angle_rad"]))
    return [list(point) for point in sorted(points)]


def _upward_float(value: Decimal) -> float:
    if value <= 0:
        return 0.0
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError("A geometric width is not representable")
    if Decimal.from_float(converted) < value:
        converted = math.nextafter(converted, math.inf)
    return converted


def _partition(circles: list[_Circle], rect: _Rect, clock: _Clock) -> dict[str, Any]:
    """Collect all incidence events before any quadrature result is available."""
    counts = {"x_extrema": 0, "circle_pair_points": 0, "horizontal_wall_points": 0}
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION
        xmin, xmax = _dec(rect.x0q), _dec(rect.x1q)
        width = _dec(rect.wq)
        physical: set[Decimal] = {xmin, xmax}

        def add(x: Decimal, kind: str) -> None:
            counts[kind] += 1
            if xmin <= x <= xmax:
                physical.add(x)

        for circle in circles:
            clock.check()
            add(_dec(circle.xq - circle.rq), "x_extrema")
            add(_dec(circle.xq + circle.rq), "x_extrema")
            for wall in (rect.y0q, rect.y1q):
                discriminant = circle.rq ** 2 - (wall - circle.yq) ** 2
                if discriminant >= 0:
                    offset = _dec(discriminant).sqrt()
                    center = _dec(circle.xq)
                    add(center - offset, "horizontal_wall_points")
                    add(center + offset, "horizontal_wall_points")
        for i, first in enumerate(circles):
            for second in circles[i + 1:]:
                clock.check()
                for x, _ in _pair_points(first, second):
                    add(x, "circle_pair_points")

        groups: dict[float, list[Decimal]] = {}
        for x in sorted(physical):
            normalized = (x - xmin) / width
            rounded = float(normalized)
            if not 0 <= rounded <= 1:
                raise ArithmeticError("Critical point normalized outside its rectangle")
            groups.setdefault(rounded, []).append(normalized)
        breaks = sorted(groups)
        omissions: list[dict[str, Any]] = []
        for rounded, exactish in groups.items():
            lower, upper = min(exactish), max(exactish)
            if upper > lower:
                omissions.append({"kind": "critical_points_share_one_float",
                                  "u_representable": rounded,
                                  "u_lower_decimal": str(lower),
                                  "u_upper_decimal": str(upper),
                                  "width_bound": _upward_float(upper - lower)})

    collapsed_bound = math.fsum(item["width_bound"] for item in omissions)
    omission_total = collapsed_bound
    intervals = [(a, b) for a, b in zip(breaks[:-1], breaks[1:]) if b > a]
    omitted_indices: set[int] = set()
    # The omission decision uses only geometry and the fixed global budget.
    for index in sorted(range(len(intervals)), key=lambda i: (intervals[i][1] - intervals[i][0], i)):
        a, b = intervals[index]
        width = b - a
        if width > OMISSION_LIMIT:
            break
        proposed = math.fsum([omission_total, width])
        if proposed <= OMISSION_LIMIT:
            omitted_indices.add(index)
            omissions.append({"kind": "narrow_partition_interval", "u_lower": a,
                              "u_upper": b, "width_bound": width})
            omission_total = proposed
    retained = [(a, b) for i, (a, b) in enumerate(intervals) if i not in omitted_indices]
    return {"critical_breaks": breaks,
            "critical_breaks_um": [math.fsum([rect.xmin, u * rect.width]) for u in breaks],
            "intervals": retained, "omissions": omissions,
            "omitted_width_bound": math.fsum(item["width_bound"] for item in omissions),
            "collapsed_critical_width_bound": collapsed_bound,
            "event_counts": counts, "distinct_high_precision_points": len(physical)}


def _measure(intervals: list[tuple[Any, Any]], outer: tuple[Any, Any] | None,
             inner: tuple[Any, Any] | None, ring_active: bool, zero: Any, one: Any) -> Any:
    """Merge a vertical union; intersect outer, subtract inner, clip the cell."""
    if not intervals or (ring_active and outer is None):
        return zero
    clipped = []
    for low, high in intervals:
        low, high = max(zero, low), min(one, high)
        if outer is not None:
            low, high = max(low, outer[0]), min(high, outer[1])
        if high > low:
            clipped.append((low, high))
    clipped.sort()
    merged: list[tuple[Any, Any]] = []
    for low, high in clipped:
        if merged and low <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(high, merged[-1][1]))
        else:
            merged.append((low, high))
    lengths = []
    for low, high in merged:
        if inner is None:
            lengths.append(high - low)
        else:
            overlap = max(zero, min(high, inner[1]) - max(low, inner[0]))
            lengths.append((high - low) - overlap)
    if isinstance(zero, Decimal):
        return sum(lengths, zero)
    return math.fsum(lengths)


class _CrossSection:
    def __init__(self, tracks: list[_Circle], outer: _Circle | None,
                 inner: _Circle | None, rect: _Rect, clock: _Clock):
        self.tracks, self.outer, self.inner = tracks, outer, inner
        self.rect, self.clock = rect, clock
        unique = {circle.key: circle for circle in [*tracks, outer, inner] if circle is not None}
        self.circles = list(unique.values())
        self.float_calls = 0
        self.decimal_calls = 0
        self.affine_gap_fallbacks = 0
        self.active: list[_Circle] = self.circles
        self.track_keys = {circle.key for circle in tracks}
        self.xa_q = rect.x0q
        self.delta_x_q = rect.wq
        self.gaps: dict[tuple[float, float, float], tuple[float, float, float, float]] = {}
        self.exact_gap_required: set[tuple[float, float, float]] = set()

    def set_interval(self, a: float, b: float) -> None:
        # Every circle x-extremum is already a partition boundary; selecting
        # by overlap (rather than a rounded midpoint) preserves tiny slivers.
        xlo = self.rect.x0q + Fraction(a) * self.rect.wq
        xhi = self.rect.x0q + Fraction(b) * self.rect.wq
        self.xa_q, self.delta_x_q = xlo, xhi - xlo
        self.active = [circle for circle in self.circles
                       if circle.xq + circle.rq >= xlo and circle.xq - circle.rq <= xhi]
        self.gaps = {}
        self.exact_gap_required = set()
        for circle in self.active:
            # Form each small distance before conversion to binary64.  Forming
            # a displacement near +/-radius and then subtracting the radius
            # would discard precisely the lens depth needed on tiny intervals.
            left, right = circle.xq - circle.rq, circle.xq + circle.rq
            exact = (xlo - left, xhi - left, right - xlo, right - xhi)
            try:
                converted = tuple(float(value) for value in exact)
            except OverflowError:
                self.exact_gap_required.add(circle.key)
                continue
            if any(not math.isfinite(value) or (value == 0 and original != 0)
                   for value, original in zip(converted, exact)):
                self.exact_gap_required.add(circle.key)
            self.gaps[circle.key] = converted

    def _decimal(self, t: float) -> float:
        self.decimal_calls += 1
        rect = self.rect
        # Preserve the local affine position through the exact discriminant;
        # Decimal(Fraction(a + (b-a)*t)) would be too late to recover lost bits.
        xq = self.xa_q + Fraction(t) * self.delta_x_q
        with localcontext() as context:
            context.prec = DECIMAL_PRECISION
            height = _dec(rect.hq)
            intervals: dict[tuple[float, float, float], tuple[Decimal, Decimal]] = {}
            for circle in self.active:
                discriminant = circle.rq ** 2 - (xq - circle.xq) ** 2
                if discriminant <= 0:
                    continue
                root = _dec(discriminant).sqrt()
                center = _dec(circle.yq - rect.y0q)
                intervals[circle.key] = ((center - root) / height, (center + root) / height)
            track_intervals = [intervals[key] for key in self.track_keys if key in intervals]
            outer = intervals.get(self.outer.key) if self.outer is not None else None
            inner = intervals.get(self.inner.key) if self.inner is not None else None
            value = _measure(track_intervals, outer, inner, self.outer is not None,
                             Decimal(0), Decimal(1))
            if not Decimal(0) <= value <= Decimal(1):
                raise ArithmeticError("Decimal cross section is outside [0,1]")
            return float(value)

    def __call__(self, t: float) -> float:
        self.clock.check()
        self.float_calls += 1
        if not math.isfinite(t) or not 0 <= t <= 1:
            raise ArithmeticError("Local quadrature coordinate is outside [0,1]")
        rect = self.rect
        one_minus_t = 1.0 - t
        intervals: dict[tuple[float, float, float], tuple[float, float]] = {}
        endpoint_values: list[tuple[float, tuple[float, float, float]]] = []
        for circle in self.active:
            if circle.key in self.exact_gap_required:
                self.affine_gap_fallbacks += 1
                return self._decimal(t)
            left_a, left_b, right_a, right_b = self.gaps[circle.key]
            left_terms = (one_minus_t * left_a, t * left_b)
            right_terms = (one_minus_t * right_a, t * right_b)
            left_gap, right_gap = math.fsum(left_terms), math.fsum(right_terms)
            left_guard = 64 * _EPS * math.fsum(abs(value) for value in left_terms)
            right_guard = 64 * _EPS * math.fsum(abs(value) for value in right_terms)
            if (not all(math.isfinite(value) for value in (left_gap, right_gap, left_guard, right_guard))
                    or abs(left_gap) <= left_guard or abs(right_gap) <= right_guard):
                self.affine_gap_fallbacks += 1
                return self._decimal(t)
            if left_gap < 0 or right_gap < 0:
                continue
            radicand = left_gap * right_gap
            if not math.isfinite(radicand) or radicand <= 0:
                self.affine_gap_fallbacks += 1
                return self._decimal(t)
            root = math.sqrt(radicand)
            low = math.fsum([circle.cy, -rect.ymin, -root]) / rect.height
            high = math.fsum([circle.cy, -rect.ymin, root]) / rect.height
            if not math.isfinite(low) or not math.isfinite(high):
                return self._decimal(t)
            if any(abs(endpoint - wall) <= 64 * _EPS * max(1.0, abs(endpoint))
                   for endpoint in (low, high) for wall in (0.0, 1.0)):
                return self._decimal(t)
            intervals[circle.key] = (low, high)
            endpoint_values.extend((endpoint, circle.key) for endpoint in (low, high)
                                   if 0 < endpoint < 1)
        endpoint_values.sort()
        for (left, left_key), (right, right_key) in zip(endpoint_values[:-1], endpoint_values[1:]):
            if left_key != right_key and right - left <= 64 * _EPS:
                return self._decimal(t)
        track_intervals = [intervals[key] for key in self.track_keys if key in intervals]
        outer = intervals.get(self.outer.key) if self.outer is not None else None
        inner = intervals.get(self.inner.key) if self.inner is not None else None
        value = _measure(track_intervals, outer, inner, self.outer is not None, 0.0, 1.0)
        if not math.isfinite(value) or not 0 <= value <= 1:
            return self._decimal(t)
        return value


def _quad_information(info: dict[str, Any]) -> dict[str, Any]:
    last = int(info.get("last", 0))
    retained = {"neval": int(info.get("neval", 0)), "last": last}
    for key in ("alist", "blist", "rlist", "elist"):
        retained[key] = [float(value) for value in info.get(key, [])[:last]]
    # QUADPACK defines only this many entries of its error-ordering vector.
    count = last if last <= QUAD_LIMIT // 2 + 2 else QUAD_LIMIT + 1 - last
    retained["iord_fortran"] = [int(value) for value in info.get("iord", [])[:max(0, count)]]
    return retained


def _integrate(quad: Callable[..., Any], section: _CrossSection,
               intervals: list[tuple[float, float]], tau: float,
               report: dict[str, Any], clock: _Clock) -> tuple[float, float, list[str]]:
    messages: list[str] = []
    values, errors = [], []
    report.update({"tau": tau, "quad_limit": QUAD_LIMIT, "intervals": [], "completed": False,
                   "quadrature_coordinate": "local t in [0,1] for each retained u interval",
                   "normalization": "I_u=delta_u*I_t; error_u=delta_u*error_t"})
    for index, (a, b) in enumerate(intervals):
        clock.check()
        section.set_interval(a, b)
        delta_u = float(Fraction(b) - Fraction(a))
        epsabs = tau * delta_u
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            returned = quad(section, 0.0, 1.0, epsabs=tau, epsrel=tau,
                            limit=QUAD_LIMIT, full_output=1)
        value_local, error_local, info = float(returned[0]), float(returned[1]), returned[2]
        value, error = delta_u * value_local, delta_u * error_local
        diagnostic_messages = [str(item) for item in returned[3:] if item]
        diagnostic_messages.extend(f"{item.category.__name__}: {item.message}" for item in caught)
        record = {"index": index, "u_lower": a, "u_upper": b,
                  "delta_u": delta_u, "quad_lower_t": 0.0, "quad_upper_t": 1.0,
                  "quad_epsabs_t": tau, "quad_epsrel_t": tau,
                  "value_local_t": value_local, "estimated_error_local_t": error_local,
                  "affine_x_exact_um": {"left_fraction": str(section.xa_q),
                                        "span_fraction": str(section.delta_x_q)},
                  "epsabs": epsabs, "epsrel": tau, "value": value,
                  "estimated_error": error, "messages": diagnostic_messages,
                  "quadpack_t": _quad_information(info)}
        report["intervals"].append(record)
        if (not all(math.isfinite(number) for number in (delta_u, value_local, error_local, value, error))
                or delta_u <= 0 or error_local < 0 or error < 0):
            raise ArithmeticError("QUADPACK returned a nonfinite value or invalid error estimate")
        values.append(value)
        errors.append(error)
        messages.extend(f"tau={tau:g}, interval={index}: {message}" for message in diagnostic_messages)
    total, total_error = math.fsum(values), math.fsum(errors)
    report.update({"completed": True, "fraction": total, "estimated_error": total_error,
                   "evaluation_count": sum(item["quadpack_t"]["neval"] for item in report["intervals"])})
    return total, total_error, messages


def cell_reference(spec: Any, rect: Any, deadline: float | None = None) -> dict[str, Any]:
    """Evaluate a cell with both prospective tolerances and full diagnostics.

    ``deadline`` is an absolute ``time.monotonic()`` value; a caller can give
    all calls in a child the same deadline.  A call never grants itself more
    than 35 seconds.  Every error/quality quantity is normalized by rectangle
    area.  ``quality_pass`` requires both the fixed quality formula and no
    unresolved QUADPACK/partition diagnostic.  No failed result is substituted.
    """
    clock = _Clock(deadline)
    rectangle = _Rect.parse(rect)
    original, outer, inner = _parse_spec(spec)
    tracks = list({circle.key: circle for circle in original if _bbox_meets(circle, rectangle)}.values())
    unique = {circle.key: circle for circle in [*tracks, outer, inner]
              if circle is not None and _bbox_meets(circle, rectangle)}
    diagnostics: dict[str, Any] = {
        "algorithm": "vertical interval union / outer intersection / inner subtraction",
        "normalization": "integral L(xmin+u*width)/height du, u in [0,1]",
        "predicate_arithmetic": "Fraction of the serialized binary floats",
        "intersection_construction": f"Decimal precision {DECIMAL_PRECISION}",
        "cross_section_arithmetic": "exact endpoint gaps, local affine interpolation, filtered float with independent Decimal fallback",
        "affine_gap_filter": "64*eps*sum(abs(weighted endpoint gaps)); exact fallback for uncertain signs",
        "input_disk_count": len(original), "bbox_filtered_unique_disk_count": len(tracks),
        "critical_circle_count": len(unique), "coarse": {}, "fine": {},
        "error_estimates_are_certified_bounds": False,
    }
    try:
        clock.check()
        import scipy
        from scipy.integrate import quad
        if scipy.__version__ != "1.15.1":
            raise RuntimeError(f"Stage D requires SciPy 1.15.1, observed {scipy.__version__}")
        diagnostics["scipy_version"] = scipy.__version__
        partition = _partition(list(unique.values()), rectangle, clock)
        diagnostics["partition"] = {key: value for key, value in partition.items()
                                    if key not in ("critical_breaks", "critical_breaks_um", "intervals")}
        diagnostics["retained_partition_intervals"] = [list(item) for item in partition["intervals"]]
        section = _CrossSection(tracks, outer, inner, rectangle, clock)
        coarse, coarse_error, coarse_messages = _integrate(
            quad, section, partition["intervals"], COARSE_TAU, diagnostics["coarse"], clock)
        fine, fine_error, fine_messages = _integrate(
            quad, section, partition["intervals"], FINE_TAU, diagnostics["fine"], clock)
        stability = abs(fine - coarse)
        omitted = partition["omitted_width_bound"]
        quality = math.fsum([fine_error, omitted, stability])
        messages = coarse_messages + fine_messages
        if omitted > OMISSION_LIMIT:
            messages.append("Unrepresentable critical intervals exceed the fixed omission-width budget")
        if not all(math.isfinite(value) for value in (coarse, fine, coarse_error, fine_error, stability, quality)):
            messages.append("A reference result is nonfinite")
        if not (-FRACTION_RANGE_TOLERANCE <= coarse <= 1 + FRACTION_RANGE_TOLERANCE
                and -FRACTION_RANGE_TOLERANCE <= fine <= 1 + FRACTION_RANGE_TOLERANCE):
            messages.append("An integrated fraction is outside the prospective fractional range tolerance")
        diagnostics.update({"float_cross_section_calls": section.float_calls,
                            "decimal_cross_section_calls": section.decimal_calls,
                            "affine_gap_fallback_calls": section.affine_gap_fallbacks,
                            "elapsed_seconds": time.monotonic() - clock.started})
        clock.check()
        return {"schema": "silice.point03-geometry.reference.v1",
                "fraction_coarse": coarse, "fraction_fine": fine,
                "estimated_error_coarse": coarse_error, "estimated_error_fine": fine_error,
                "stability": stability, "omitted_width_bound": omitted,
                "quality_total": quality,
                "quality_pass": bool(quality <= QUALITY_LIMIT and not messages),
                "area_coarse_um2": coarse * rectangle.area,
                "area_fine_um2": fine * rectangle.area,
                "rect_um": rectangle.serialized, "rect_area_um2": rectangle.area,
                "critical_breaks": partition["critical_breaks"],
                "critical_breaks_um": partition["critical_breaks_um"],
                "messages": messages, "diagnostics": diagnostics}
    except ReferenceDeadlineExceeded as exc:
        exc.diagnostics = diagnostics
        raise
    except (Exception, KeyboardInterrupt) as exc:
        raise ReferenceEvaluationError(f"{type(exc).__name__}: {exc}", diagnostics) from exc


def global_reference(spec: Any, rect: Any, deadline: float | None = None) -> dict[str, Any]:
    """The same independent integral over the caller's retained global rectangle."""
    return cell_reference(spec, rect, deadline=deadline)
