"""Prospective Green-boundary candidate for a disk union clipped by an annulus.

All coordinates and radii are in micrometres. This module performs no geometry
on import and contains no grid loops. Numerical acceptance belongs to the
separate, prospectively frozen audit and its independent reference.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
from functools import lru_cache, wraps
import math
import sys


_ANGLE_PRECISION = 128
_ANGLE_WORK_PRECISION = _ANGLE_PRECISION+16


def _topology_context(function):
    @wraps(function)
    def contextual(*args, **kwargs):
        with localcontext() as context:
            context.prec = _ANGLE_PRECISION
            return function(*args, **kwargs)
    return contextual


def _atan_unit(value):
    """atan for 0<=value<=1, with half-angle reduction and a local series."""
    multiplier = 1
    while value > Decimal(1)/8:
        value /= 1+(1+value*value).sqrt()
        multiplier *= 2
    square = value*value
    power, total, denominator = value, value, 1
    while power:
        power *= -square
        denominator += 2
        updated = total+power/denominator
        if updated == total:
            break
        total = updated
    return multiplier*total


@lru_cache(maxsize=1)
def _angle_constants():
    # Lazy: importing the module evaluates no geometry or angular series.
    with localcontext() as context:
        context.prec = _ANGLE_WORK_PRECISION
        pi = 16*_atan_unit(Decimal(1)/5)-4*_atan_unit(Decimal(1)/239)
        context.prec = _ANGLE_PRECISION
        pi = +pi
        return pi, 2*pi


def _decimal_angle(x, y):
    """atan2 without rounding an event vector or its angle to binary64."""
    x = x if isinstance(x,Decimal) else Decimal.from_float(float(x))
    y = y if isinstance(y,Decimal) else Decimal.from_float(float(y))
    if not x and not y:
        raise ArithmeticError("An angular event has a zero direction vector.")
    pi,_ = _angle_constants()
    with localcontext() as context:
        context.prec = _ANGLE_WORK_PRECISION
        ax,ay = abs(x),abs(y)
        if not ay:
            angle = pi if x < 0 else Decimal(0)
        elif not ax:
            angle = pi/2
        elif ay <= ax:
            angle = _atan_unit(ay/ax)
        else:
            angle = pi/2-_atan_unit(ax/ay)
        if x < 0 and ay:
            angle = pi-angle
        if y < 0:
            angle = -angle
        context.prec = _ANGLE_PRECISION
        return +angle


def _json_diagnostic(value):
    if isinstance(value,Decimal):
        return str(value)
    if isinstance(value,dict):
        return {key:_json_diagnostic(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):
        return [_json_diagnostic(item) for item in value]
    return value


class GeometryResolutionError(ArithmeticError):
    """An event or an open interval cannot be represented without losing it."""
    def __init__(self, message, diagnostic):
        super().__init__(message)
        self.diagnostic = diagnostic


class _Circle:
    __slots__ = ("cx", "cy", "r", "roles", "bounds")
    def __init__(self, key, roles):
        self.cx, self.cy, self.r = key
        self.roles = frozenset(roles)
        self.bounds = (self.cx-self.r, self.cx+self.r, self.cy-self.r, self.cy+self.r)
        if not all(math.isfinite(v) for v in self.bounds):
            raise ValueError("Circle bounds must remain finite.")


def _finite(value):
    if isinstance(value, bool):
        raise ValueError("Boolean geometry coordinates are not accepted.")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Geometry values must be finite.")
    return result


def _decimal_values(values):
    converted = tuple(Decimal.from_float(float(v)) for v in values)
    nonzero = [v for v in converted if v]
    if nonzero:
        span = max(v.adjusted() for v in nonzero)-min(v.as_tuple().exponent for v in nonzero)+2
    else:
        span = 1
    # Four-degree discriminants in exact binary-float input values. The extra
    # digits also reserve precision for division and square roots of roots.
    return converted, max(96, 4*span+64)


def _trig(angle):
    if angle == 0:
        return 1.0, 0.0
    if angle == math.pi or angle == -math.pi:
        return -1.0, 0.0
    if angle == math.pi/2:
        return 0.0, 1.0
    if angle == -math.pi/2:
        return 0.0, -1.0
    return math.cos(angle), math.sin(angle)


def _segment_angle(delta):
    """Evaluate delta-sin(delta), retaining short segments with a series."""
    if delta >= .125:
        return delta-math.sin(delta)
    term = delta*delta*delta/6
    terms = [term]
    degree = 3
    while term:
        term *= -delta*delta/((degree+1)*(degree+2))
        terms.append(term)
        degree += 2
        if abs(term) <= sys.float_info.epsilon*abs(terms[0]):
            break
    return math.fsum(terms)


class UnionRegion:
    """Boolean region: any track disk AND outer disk AND NOT inner disk.

    Annulus constraints are absent when spec['annulus'] is None. Coincident
    circles are represented once with all their roles, not summed twice.
    """
    def __init__(self, spec):
        if not isinstance(spec, dict) or not isinstance(spec.get("disks"), list):
            raise ValueError("spec must contain a disks list and optional annulus.")
        geometries = {}
        for row in spec["disks"]:
            if len(row) != 3:
                raise ValueError("Each disk must contain cx, cy, radius.")
            key = tuple(_finite(v) for v in row)
            if key[2] <= 0:
                raise ValueError("Disk radii must be positive.")
            geometries.setdefault(key, set()).add("track")
        annulus = spec.get("annulus")
        outer_key = inner_key = None
        if annulus is not None:
            cx, cy = (_finite(v) for v in annulus["center"])
            inner, outer = _finite(annulus["inner"]), _finite(annulus["outer"])
            if not 0 <= inner < outer:
                raise ValueError("Annulus radii must satisfy 0 <= inner < outer.")
            outer_key = (cx,cy,outer)
            geometries.setdefault(outer_key,set()).add("outer")
            if inner:
                inner_key = (cx,cy,inner)
                geometries.setdefault(inner_key,set()).add("inner")
        keys = list(geometries)
        self._circles = [_Circle(key,geometries[key]) for key in keys]
        self._outer = keys.index(outer_key) if outer_key is not None else None
        self._inner = keys.index(inner_key) if inner_key is not None else None
        self._tracks = [i for i,c in enumerate(self._circles) if "track" in c.roles]
        self._events = None
        self._memberships = None
        self._exposed_arcs = None
        self._line_cache = {}
        self._halfplane_cache = {}
        self.diagnostics = {"schema":"silice.point03-union.predicates.v1",
                            "input_disk_count":len(spec["disks"]),"unique_circle_count":len(keys),
                            "coincident_roles":[{"circle":[c.cx,c.cy,c.r],"roles":sorted(c.roles)}
                                                for c in self._circles if len(c.roles)>1],
                            "float_predicates":0,"decimal_predicates":0,"exact_zero_predicates":0,
                            "unrepresentable_events":0,"classification_boundary_hits":0,
                            "line_cache_hits":0,"predicate_categories":{},
                            "angular_membership_queries":0,
                            "halfplane_cache_hits":0,
                            "angular_merging":"Exact Decimal equality only; no angular epsilon.",
                            "angular_representation":{"decimal_digits":_ANGLE_PRECISION,
                                "working_digits":_ANGLE_WORK_PRECISION,
                                "atan":"Half-angle reduction to abs(z)<=1/8, then alternating series.",
                                "pi":"Cached Machin formula; constants and events share precision.",
                                "integration":"Convert only the preserved Decimal span and trig angles to float."},
                            "cancel_ratio_definition":"abs(raw area)/sum(abs(contributions)); 1 for empty sum.",
                            "validation_status":"requires_independent_geometry_audit"}

    def _sign(self, label, value, scale, values, expression):
        self.diagnostics["float_predicates"] += 1
        categories = self.diagnostics["predicate_categories"]
        categories[label] = categories.get(label,0)+1
        if math.isfinite(value) and abs(value) > 64*sys.float_info.epsilon*scale:
            return (value>0)-(value<0)
        converted, precision = _decimal_values(values)
        with localcontext() as context:
            context.prec = precision
            exact = expression(*converted)
        self.diagnostics["decimal_predicates"] += 1
        if not exact:
            self.diagnostics["exact_zero_predicates"] += 1
        return (exact>0)-(exact<0)

    def _unresolved(self, label, detail):
        self.diagnostics["unrepresentable_events"] += 1
        self.diagnostics["last_unrepresentable_event"] = _json_diagnostic({"label":label,**detail})
        raise GeometryResolutionError("Distinct geometry event or interval is not representable: "+label,
                                      dict(self.diagnostics["last_unrepresentable_event"]))

    def _circle_sign(self, point, circle):
        x,y = point
        dx,dy = x-circle.cx,y-circle.cy
        terms = (dx*dx,dy*dy,circle.r*circle.r)
        return self._sign("point_circle",math.fsum((terms[0],terms[1],-terms[2])),sum(terms),
                          (x,y,circle.cx,circle.cy,circle.r),
                          lambda x,y,cx,cy,r:(x-cx)**2+(y-cy)**2-r*r)

    def _inside(self, point, index, direction):
        circle = self._circles[index]
        sign = self._circle_sign(point,circle)
        if sign:
            return sign < 0
        self.diagnostics["classification_boundary_hits"] += 1
        x,y = point
        vx,vy = direction
        dx,dy = x-circle.cx,y-circle.cy
        derivative = self._sign("infinitesimal_normal",math.fsum((dx*vx,dy*vy)),
                                abs(dx*vx)+abs(dy*vy),(x,y,circle.cx,circle.cy,vx,vy),
                                lambda x,y,cx,cy,vx,vy:(x-cx)*vx+(y-cy)*vy)
        # The second-order squared-distance term is positive if derivative=0.
        return derivative < 0

    def _region_at(self, point, relevant, direction, own=None, own_inside=None):
        flags = {i:(own_inside if i == own else self._inside(point,i,direction)) for i in relevant}
        tracks = any(flags.get(i,False) for i in self._tracks)
        outer = self._outer is None or flags.get(self._outer,False)
        inner = self._inner is not None and flags.get(self._inner,False)
        return tracks and outer and not inner

    def _pair_angles(self, first, second):
        dx,dy = second.cx-first.cx,second.cy-first.cy
        d2 = math.fsum((dx*dx,dy*dy))
        if d2 == 0 and first.cx == second.cx and first.cy == second.cy:
            return []  # Concentric unequal circles have no isolated crossings.
        k = math.fsum((d2,first.r*first.r,-second.r*second.r))
        discriminant = math.fsum((4*d2*first.r*first.r,-k*k))
        values = (first.cx,first.cy,first.r,second.cx,second.cy,second.r)
        def polynomial(x1,y1,r1,x2,y2,r2):
            distance2 = (x2-x1)**2+(y2-y1)**2
            return 4*distance2*r1*r1-(distance2+r1*r1-r2*r2)**2
        sign = self._sign("circle_intersection",discriminant,abs(4*d2*first.r*first.r)+abs(k*k),values,polynomial)
        if sign < 0:
            return []
        converted,precision = _decimal_values(values)
        # Preserve vectors until angular construction, including separations
        # smaller than one binary64 ULP around a nonzero global angle.
        with localcontext() as context:
            context.prec = max(precision,_ANGLE_WORK_PRECISION)
            x1,y1,r1,x2,y2,r2 = converted
            ddx,ddy = x2-x1,y2-y1
            dd2 = ddx*ddx+ddy*ddy
            kk = dd2+r1*r1-r2*r2
            q = polynomial(*converted)
            if (q > 0)-(q < 0) != sign:
                self._unresolved("circle_pair_predicate_mismatch",{"circles":[[first.cx,first.cy,first.r],[second.cx,second.cy,second.r]]})
            hh = q.sqrt()/(2*dd2) if sign else Decimal(0)
            foot = kk/(2*dd2)
            vectors = [(foot*ddx-s*hh*ddy,foot*ddy+s*hh*ddx,
                        (foot-1)*ddx-s*hh*ddy,(foot-1)*ddy+s*hh*ddx)
                       for s in ((-1,1) if sign else (1,))]
            result = [(_decimal_angle(vx,vy),_decimal_angle(wx,wy)) for vx,vy,wx,wy in vectors]
        if sign and (result[0][0] == result[1][0] or result[0][1] == result[1][1]):
            self._unresolved("circle_pair_angles",{"circles":[[first.cx,first.cy,first.r],[second.cx,second.cy,second.r]]})
        return result

    def _base_events(self):
        if self._events is None:
            pi,_ = _angle_constants()
            events = [[-pi,pi] for _ in self._circles]
            memberships = [[False for _ in self._circles] for _ in self._circles]
            for i,first in enumerate(self._circles):
                for j in range(i+1,len(self._circles)):
                    second = self._circles[j]
                    if (first.bounds[1] < second.bounds[0] or second.bounds[1] < first.bounds[0]
                            or first.bounds[3] < second.bounds[2] or second.bounds[3] < first.bounds[2]):
                        continue
                    crossings = self._pair_angles(first,second)
                    for a,b in crossings:
                        events[i].append(a)
                        events[j].append(b)
                    memberships[i][j] = self._angular_relation(first,second,[a for a,b in crossings])
                    memberships[j][i] = self._angular_relation(second,first,[b for a,b in crossings])
            self._events = events
            self._memberships = memberships
        return self._events

    def _angular_relation(self, circle, other, crossings):
        """Membership of this circle's boundary in another disk, without a
        reconstructed Cartesian point. Crossings were obtained with atan2 of
        height/projection vectors, including the near-tangency Decimal path.
        """
        dx,dy = other.cx-circle.cx,other.cy-circle.cy
        if len(crossings) < 2:
            if other.r <= circle.r:
                return False
            difference = other.r-circle.r
            value = math.fsum((dx*dx,dy*dy,-difference*difference))
            sign = self._sign("circle_containment",value,dx*dx+dy*dy+difference*difference,
                              (circle.cx,circle.cy,circle.r,other.cx,other.cy,other.r),
                              lambda x1,y1,r1,x2,y2,r2:(x2-x1)**2+(y2-y1)**2-(r2-r1)**2)
            # Isolated tangency points have zero measure and are event cuts.
            return sign <= 0
        low,high = sorted(crossings)
        if low == high or high-low == _angle_constants()[1]:
            self._unresolved("angular_membership_endpoints",{"angles":[low,high]})
        center_direction = _decimal_angle(Decimal.from_float(other.cx)-Decimal.from_float(circle.cx),
                                          Decimal.from_float(other.cy)-Decimal.from_float(circle.cy))
        if center_direction == low or center_direction == high:
            self._unresolved("angular_membership_center",{"angles":[low,high],"center_direction":center_direction})
        middle_inside = low < center_direction < high
        return (low,high,middle_inside)

    def _interval_membership(self, low, high, relation, label):
        """Classify an entire open interval; adjacent float endpoints are valid.

        Every relevant crossing is a partition cut. A remaining straddling
        interval is unresolved, not an invitation to sample a rounded point.
        """
        if isinstance(relation,bool):
            return relation
        left,right,middle_inside = relation
        if left <= low and high <= right:
            return middle_inside
        if high <= left or low >= right:
            return not middle_inside
        self._unresolved(label,{"interval":[low,high],"membership_interval":[left,right],
                                "middle_inside":middle_inside})

    def _region_from_flags(self, flags):
        return (any(flags[i] for i in self._tracks)
                and (self._outer is None or flags[self._outer])
                and not (self._inner is not None and flags[self._inner]))

    def _region_on_circle(self, index, low, high, own_inside):
        flags = []
        for other,relation in enumerate(self._memberships[index]):
            if other == index:
                flags.append(own_inside)
            elif isinstance(relation,bool):
                flags.append(relation)
            else:
                self.diagnostics["angular_membership_queries"] += 1
                flags.append(self._interval_membership(low,high,relation,"circle_boundary_partition"))
        return self._region_from_flags(flags)

    def _halfplane_relation(self, circle, coordinate, axis, greater):
        key = (circle.cx,circle.cy,circle.r,coordinate,axis,greater)
        if key in self._halfplane_cache:
            self.diagnostics["halfplane_cache_hits"] += 1
            return self._halfplane_cache[key]
        crossing = self._line_height(circle,coordinate,axis)
        center = circle.cx if axis == "x" else circle.cy
        if crossing is None or crossing[1] == 0:
            # Tangency leaves either all or none of the open circumference in
            # the halfplane. The single point of contact has zero area.
            result = (coordinate < center) if greater else (coordinate > center)
            self._halfplane_cache[key] = result
            return result
        converted,precision = _decimal_values((circle.r,coordinate,center))
        with localcontext() as context:
            context.prec = max(precision,_ANGLE_WORK_PRECISION)
            radius,value,center_decimal = converted
            offset = value-center_decimal
            height = (radius*radius-offset*offset).sqrt()
        vectors = ((offset,height),(offset,-height)) if axis == "x" else ((height,offset),(-height,offset))
        low,high = sorted(_decimal_angle(x,y) for x,y in vectors)
        pi,tau = _angle_constants()
        if low == high or high-low == tau:
            self._unresolved("halfplane_events",{"circle":[circle.cx,circle.cy,circle.r],
                                                  "coordinate":coordinate,"axis":axis,"angles":[low,high]})
        direction = (Decimal(0) if greater else pi) if axis == "x" else (pi/2 if greater else -pi/2)
        if direction == low or direction == high:
            self._unresolved("halfplane_sector_direction",{"angles":[low,high],"direction":direction})
        result = (low,high,low < direction < high)
        self._halfplane_cache[key] = result
        return result

    def _line_height(self, circle, coordinate, axis):
        key = (circle.cx,circle.cy,circle.r,coordinate,axis)
        if key in self._line_cache:
            self.diagnostics["line_cache_hits"] += 1
            return self._line_cache[key]
        center = circle.cx if axis == "x" else circle.cy
        offset = coordinate-center
        q = circle.r*circle.r-offset*offset
        scale = circle.r*circle.r+offset*offset
        sign = self._sign("circle_line",q,scale,(circle.r,coordinate,center),
                          lambda r,v,c:r*r-(v-c)**2)
        if sign < 0:
            self._line_cache[key] = None
            return None
        if abs(q) <= 64*sys.float_info.epsilon*scale:
            converted,precision = _decimal_values((circle.r,coordinate,center))
            with localcontext() as context:
                context.prec = precision
                r,v,c = converted
                height = float((r*r-(v-c)**2).sqrt()) if sign else 0.0
        else:
            height = math.sqrt(q)
        if sign and height == 0:
            self._unresolved("circle_line_height",{"circle":[circle.cx,circle.cy,circle.r],"coordinate":coordinate,"axis":axis})
        self._line_cache[key] = (offset,height)
        return self._line_cache[key]

    def support_bounds(self):
        if not self._tracks:
            return None
        bounds = (min(self._circles[i].bounds[0] for i in self._tracks),max(self._circles[i].bounds[1] for i in self._tracks),
                  min(self._circles[i].bounds[2] for i in self._tracks),max(self._circles[i].bounds[3] for i in self._tracks))
        if self._outer is not None:
            outer = self._circles[self._outer].bounds
            bounds = (max(bounds[0],outer[0]),min(bounds[1],outer[1]),max(bounds[2],outer[2]),min(bounds[3],outer[3]))
        return bounds if bounds[0] < bounds[1] and bounds[2] < bounds[3] else None

    def _arc(self, circle, start, end, direction, origin, contributions, closure):
        decimal_span = end-start
        delta = float(decimal_span)
        if decimal_span > 0 and not delta:
            self._unresolved("integration_arc_span",{"angles":[start,end],"span":decimal_span})
        pi,tau = _angle_constants()
        if decimal_span == tau:
            chord,dx,dy = 0.0,0.0,0.0
            segment_terms = [float(pi)*circle.r*circle.r]
        else:
            cos0,sin0 = _trig(float(start))
            cosm,sinm = _trig(float(start+decimal_span/2))
            if decimal_span > pi:
                complement = float(tau-decimal_span)
                if not complement:
                    self._unresolved("integration_arc_complement",{"angles":[start,end],"span":decimal_span})
                sine = math.sin(complement/2)
                # Keep the full-disk and tiny complementary-segment terms
                # separate rather than rounding a nearly full turn to TAU.
                segment_terms = [float(pi)*circle.r*circle.r,
                                 -.5*circle.r*circle.r*_segment_angle(complement)]
            else:
                sine = math.sin(delta/2)
                segment_terms = [.5*circle.r*circle.r*_segment_angle(delta)]
            dx,dy = -2*circle.r*sinm*sine,2*circle.r*cosm*sine
            x = math.fsum((circle.cx,-origin[0],circle.r*cos0))
            y = math.fsum((circle.cy,-origin[1],circle.r*sin0))
            chord = .5*math.fsum((x*dy,-y*dx))
        contributions.append(direction*chord)
        contributions.extend(direction*term for term in segment_terms)
        closure.append((direction*dx,direction*dy))

    def _boundary_arcs(self):
        """Classify each complete Boolean-boundary arc once, before cell cuts."""
        if self._exposed_arcs is not None:
            return self._exposed_arcs
        events = self._base_events()
        relevant = list(range(len(self._circles)))
        result = [[] for _ in self._circles]
        for index in relevant:
            circle = self._circles[index]
            angles = sorted(set(events[index]))
            for start,end in zip(angles,angles[1:]):
                inside = self._region_on_circle(index,start,end,True)
                outside = self._region_on_circle(index,start,end,False)
                if inside != outside:
                    result[index].append((start,end,1 if inside else -1))
        self._exposed_arcs = result
        self.diagnostics["cached_exposed_arc_count"] = sum(len(rows) for rows in result)
        return result

    def _arcs(self, rect, origin, relevant, contributions, closure):
        count = 0
        exposed = self._boundary_arcs()
        for index in relevant:
            circle = self._circles[index]
            cuts = []
            halfplanes = []
            if rect is not None:
                for axis,coordinates in (("x",rect[:2]),("y",rect[2:])):
                    for side,coordinate in enumerate(coordinates):
                        relation = self._halfplane_relation(circle,coordinate,axis,side == 0)
                        halfplanes.append(relation)
                        if not isinstance(relation,bool):
                            cuts.extend(relation[:2])
            if any(relation is False for relation in halfplanes):
                continue
            for start,end,direction in exposed[index]:
                angles = sorted(set([start,end]+[v for v in cuts if start < v < end]))
                for low,high in zip(angles,angles[1:]):
                    if not all(self._interval_membership(low,high,relation,"cell_arc_partition") for relation in halfplanes):
                        continue
                    self._arc(circle,low,high,direction,origin,contributions,closure)
                    count += 1
        return count

    def _edges(self, rect, origin, relevant, contributions, closure):
        xmin,xmax,ymin,ymax = rect
        edges = [((xmin,ymin),(1.,0.),xmax-xmin,(0.,1.)),((xmax,ymin),(0.,1.),ymax-ymin,(-1.,0.)),
                 ((xmax,ymax),(-1.,0.),xmax-xmin,(0.,-1.)),((xmin,ymax),(0.,-1.),ymax-ymin,(1.,0.))]
        count = 0
        for start,direction,length,inward in edges:
            ux,uy = direction
            events = [0.0,length]
            relations = {}
            for index in relevant:
                circle = self._circles[index]
                crossing = self._line_height(circle,start[1] if ux else start[0],"y" if ux else "x")
                if crossing is None:
                    relations[index] = False
                    continue
                _,height = crossing
                projection = (circle.cx-start[0])*ux+(circle.cy-start[1])*uy
                left,right = projection-height,projection+height
                if height and left == right and 0 <= projection <= length:
                    self._unresolved("edge_root_events",{"circle":[circle.cx,circle.cy,circle.r],
                                                          "edge_start":list(start),"position":projection})
                relations[index] = (left,right,True) if left < right else False
                for position in (left,right):
                    if 0 < position < length:
                        events.append(position)
            events = sorted(set(events))
            for low,high in zip(events,events[1:]):
                flags = [False for _ in self._circles]
                for index,relation in relations.items():
                    flags[index] = self._interval_membership(low,high,relation,"cell_edge_partition")
                if not self._region_from_flags(flags):
                    continue
                dx,dy = ux*(high-low),uy*(high-low)
                x = math.fsum((start[0],-origin[0],ux*low))
                y = math.fsum((start[1],-origin[1],uy*low))
                contributions.append(.5*math.fsum((x*dy,-y*dx)))
                closure.append((dx,dy))
                count += 1
        return count

    def _integrate(self, rect, origin):
        contributions,closure = [],[]
        relevant = list(range(len(self._circles)))
        if rect is not None:
            relevant = [i for i,c in enumerate(self._circles) if c.bounds[0] <= rect[1] and c.bounds[1] >= rect[0]
                        and c.bounds[2] <= rect[3] and c.bounds[3] >= rect[2]]
        if not any(i in self._tracks for i in relevant):
            relevant = []
        arcs = self._arcs(rect,origin,relevant,contributions,closure) if relevant else 0
        segments = self._edges(rect,origin,relevant,contributions,closure) if rect is not None and relevant else 0
        area = math.fsum(contributions)
        absolute = math.fsum(abs(v) for v in contributions)
        closed = [math.fsum(v[axis] for v in closure) for axis in (0,1)]
        if not all(math.isfinite(v) for v in (area,absolute,*closed)):
            self._unresolved("nonfinite_boundary_sum",{"contribution_count":len(contributions)})
        return {"area_raw_um2":area,"boundary_closure_um":closed,"absolute_contribution_sum_um2":absolute,
                "cancel_ratio":abs(area)/absolute if absolute else 1.0,"arc_count":arcs,"segment_count":segments}

    @_topology_context
    def cell(self, rect, origin=None):
        rect = tuple(_finite(v) for v in rect)
        if len(rect) != 4 or not rect[0] < rect[1] or not rect[2] < rect[3]:
            raise ValueError("rect must be xmin,xmax,ymin,ymax with positive width and height.")
        if origin is None:
            origin = (rect[0]+(rect[1]-rect[0])/2,rect[2]+(rect[3]-rect[2])/2)
        else:
            origin = tuple(_finite(v) for v in origin)
            if len(origin) != 2:
                raise ValueError("origin must contain two finite coordinates.")
        result = self._integrate(rect,origin)
        area = (rect[1]-rect[0])*(rect[3]-rect[2])
        raw = result["area_raw_um2"]/area
        guarded = -1e-12 <= raw <= 1+1e-12
        fraction = min(1.0,max(0.0,raw)) if guarded else raw
        result.update(raw_fraction=raw,fraction=fraction,correction=fraction-raw,within_guard=guarded,
                      cell_area_um2=area,origin_um=list(origin),
                      boundary_closure_limit_um=1e-11*min(rect[1]-rect[0],rect[3]-rect[2]),
                      boundary_closed=max(abs(v) for v in result["boundary_closure_um"]) <= 1e-11*min(rect[1]-rect[0],rect[3]-rect[2]))
        return result

    @_topology_context
    def global_area(self):
        bounds = self.support_bounds()
        origin = ((bounds[0]+(bounds[1]-bounds[0])/2,bounds[2]+(bounds[3]-bounds[2])/2)
                  if bounds is not None else (0.0,0.0))
        result = self._integrate(None,origin) if bounds is not None else {
            "area_raw_um2":0.0,"boundary_closure_um":[0.0,0.0],"absolute_contribution_sum_um2":0.0,
            "cancel_ratio":1.0,"arc_count":0,"segment_count":0}
        result.update(area_um2=result["area_raw_um2"],closure=result["boundary_closure_um"],cancel=result["cancel_ratio"],origin_um=list(origin))
        return result
