"""Explicit opt-in fine grid; frozen CPU/first CUDA limits stay unchanged."""
from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class FineGrid:
    points: int
    width_m: float = 128e-6

    def __post_init__(self):
        if isinstance(self.points,bool) or not isinstance(self.points,int) or not 64<=self.points<=640:
            raise ValueError('fine pilot integer points64..640 required')
        if not math.isfinite(self.width_m) or self.width_m<=0:
            raise ValueError('finite positive width required')

    @property
    def dx_m(self):
        return self.width_m/self.points

    def coordinates(self):
        ax=(np.arange(self.points)-self.points//2)*self.dx_m
        return np.meshgrid(ax,ax,indexing='xy')


def fine_operators(grid,dn,steps,length_m=1e-3):
    if isinstance(steps,bool) or not isinstance(steps,int) or not 1<=steps<=1000:
        raise ValueError('integer steps1..1000 required')
    if not math.isfinite(length_m) or length_m<=0:
        raise ValueError('positive finite length required')
    if dn.shape!=(grid.points,grid.points) or np.iscomplexobj(dn) or not np.isfinite(dn).all() or np.max(abs(dn))>.01:
        raise ValueError('real weak-index profile required')
    dz=length_m/steps; k0=2*math.pi/1550e-9
    f=2*math.pi*np.fft.fftfreq(grid.points,d=grid.dx_m)
    kx,ky=np.meshgrid(f,f,indexing='xy')
    x,y=grid.coordinates(); edge=np.maximum(abs(x),abs(y))/(grid.width_m/2)
    return (np.exp(.5j*k0*dn*dz),np.exp(-1j*(kx*kx+ky*ky)*dz/(2*k0*1.444)),
            np.exp(-np.maximum((edge-.7)/.3,0)**4*dz/50e-6))
