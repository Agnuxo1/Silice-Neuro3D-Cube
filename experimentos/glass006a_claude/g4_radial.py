# Artefacto exacto de G4 (GLASS-006a): comando `python g4_radial.py`, config radial_ecs.core_fraction(-0.003, N=700) => defaults a=6um,t=6um,w=6um,z=2mm,R0=60um,Rmax=140um,theta=0.6
import os,sys,json; os.environ["OMP_NUM_THREADS"]="1"; sys.dont_write_bytecode=True; sys.path.insert(0,"../glass005_claude")
from radial_ecs import core_fraction
f=core_fraction(-0.003,N=700)[0]; print(repr(f))
