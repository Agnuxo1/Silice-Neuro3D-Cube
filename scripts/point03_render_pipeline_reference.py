"""Analytic instrument marks; independent of optical P2 nodal fields."""
import numpy as np
from point03_render_reference import TRIANGLE, RESOLUTIONS, EDGE_MARGIN

MODES = ('uniform_none','uniform_add1','uniform_add2','attribute_none',
         'bary_smooth_none','bary_smooth_add1','bary_analytic_none',
         'bary_analytic_add1','quadratic_smooth_none','quadratic_analytic_none')
CONSTANT = (.137,.271,.419)

def barycentric(x,y):
    l2=(np.asarray(y,dtype=np.float64)+.7)/1.5
    l1=(1-l2)/2+np.asarray(x,dtype=np.float64)/1.6
    return np.stack([1-l1-l2,l1,l2],axis=-1)

def reference(mode,n):
    if mode not in MODES or type(n) is not int or n not in RESOLUTIONS:
        raise ValueError('unregistered mark or resolution')
    q=(np.arange(n,dtype=np.float64)+.5)*2/n-1
    x,y=np.meshgrid(q,q);b=barycentric(x,y)
    inside=np.all(b>EDGE_MARGIN,axis=-1)
    compare=~np.any(np.abs(b)<=EDGE_MARGIN,axis=-1)
    raw=np.zeros((n,n,4),dtype=np.float64)
    if mode.startswith(('uniform','attribute')): raw[...,:3]=CONSTANT
    elif mode.startswith('quadratic'): raw[...,:3]=b*b
    else: raw[...,:3]=b
    if 'add2' in mode: raw[...,:3]*=2
    raw[...,3]=0 if 'add' in mode else 1
    raw[~inside]=0
    return raw,inside,compare

def metrics(raw,expected,inside,compare):
    if raw.dtype!=np.float32 or raw.shape!=expected.shape or not np.isfinite(raw).all():
        raise ValueError('invalid instrument pixels')
    errors=np.max(np.abs(raw.astype(np.float64)-expected),axis=-1)
    maximum=float(errors[compare].max())
    outside=float(np.abs(raw[compare & ~inside]).max())
    return dict(max_channel_error=maximum,outside_max=outside,
                included_pixels=int(compare.sum()),excluded_pixels=int((~compare).sum()),
                accuracy_pass=maximum<=1e-6 and outside<=1e-7)
