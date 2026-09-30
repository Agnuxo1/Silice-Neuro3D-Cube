"""Hypothetical union-of-disks index jacket, NOT a laser writing recipe."""
import math
import numpy as np
from silice.bpm import index_profile


def track_centres(core_radius_m=6e-6, thickness_m=6e-6,
                  track_radius_m=1.25e-6, per_ring=32, missing_wedge_rad=0.0):
    values=(core_radius_m,thickness_m,track_radius_m,missing_wedge_rad)
    if not all(math.isfinite(v) for v in values): raise ValueError("finite dimensions required")
    if core_radius_m<=0 or track_radius_m<=0 or thickness_m<2*track_radius_m:
        raise ValueError("disks must fit in the jacket without touching core interior")
    if isinstance(per_ring,bool) or not isinstance(per_ring,int) or not 3<=per_ring<=128:
        raise ValueError("per_ring integer in [3,128]")
    if not 0<=missing_wedge_rad<2*math.pi:raise ValueError("wedge in [0,2pi)")
    centres=[]
    for ring,radius in enumerate(np.linspace(core_radius_m+track_radius_m,
                                             core_radius_m+thickness_m-track_radius_m,3)):
        offset=math.pi/per_ring if ring%2 else 0
        for j in range(per_ring):
            angle=2*math.pi*j/per_ring+offset
            signed=(angle+math.pi)%(2*math.pi)-math.pi
            if missing_wedge_rad and abs(signed)<missing_wedge_rad/2:continue
            centres.append((float(radius*math.cos(angle)),float(radius*math.sin(angle))))
    return tuple(centres)


def discrete_profile(grid, *, delta_n=-0.003, core_radius_m=6e-6,
                     thickness_m=6e-6, track_radius_m=1.25e-6,
                     per_ring=32, missing_wedge_rad=0.0, match_integral=False):
    if not math.isfinite(delta_n) or not -0.01<=delta_n<0:
        raise ValueError("negative weak-index delta_n in [-0.01,0)")
    # Also validates domain/radii before allocating or generating tracks.
    reference=index_profile(grid,core_radius_m,thickness_m,delta_n)
    centres=track_centres(core_radius_m,thickness_m,track_radius_m,per_ring,missing_wedge_rad)
    x,y=grid.coordinates();mask=np.zeros_like(x,dtype=bool)
    for cx,cy in centres:
        mask|=(x-cx)**2+(y-cy)**2<=track_radius_m**2
    r=np.hypot(x,y)
    # Bound only floating point tangency error; domain is the untouched core.
    mask&=(r>=core_radius_m)&(r<core_radius_m+thickness_m)
    profile=np.where(mask,delta_n,0.0)
    if not np.any(mask):raise ValueError("grid does not resolve any track")
    scale=1.0
    if match_integral:
        scale=float(np.abs(reference).sum()/np.abs(profile).sum())
        if abs(delta_n*scale)>0.01:raise ValueError("equal-dose exceeds weak-index bound")
        profile*=scale
    return profile,dict(centres_m=centres,track_radius_m=track_radius_m,
        per_ring=per_ring,tracks_count=len(centres),missing_wedge_rad=missing_wedge_rad,
        integral_scale=scale,peak_delta_n=float(profile.min()),
        modified_area_m2=float(mask.sum()*grid.dx_m**2),
        integral_abs_delta_n_m2=float(np.abs(profile).sum()*grid.dx_m**2),
        core_untouched=bool(np.all(profile[r<core_radius_m]==0)),
        outside_untouched=bool(np.all(profile[r>=core_radius_m+thickness_m]==0)))
