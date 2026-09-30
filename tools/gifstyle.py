"""Estilo comun de los GIF del repositorio. Todos los datos numericos vienen de los experimentos; lo esquematico se rotula 'ilustracion'."""
import os,sys; sys.dont_write_bytecode=True
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LinearSegmentedColormap
BG="#0b1220"; PANEL="#111a2e"; GRID="#22304d"; TXT="#e6edf7"; MUTED="#8ea0bd"
CY="#22d3ee"; AM="#fbbf24"; MG="#f472b6"; GR="#34d399"; RD="#f87171"; VI="#a78bfa"
LIGHT=LinearSegmentedColormap.from_list("light",[BG,"#0e3a5c","#22d3ee","#e0fbff","#ffffff"])
plt.rcParams.update({"figure.facecolor":BG,"axes.facecolor":PANEL,"axes.edgecolor":GRID,"text.color":TXT,"axes.labelcolor":MUTED,
    "xtick.color":MUTED,"ytick.color":MUTED,"font.family":"DejaVu Sans","font.size":10,"axes.titleweight":"bold","axes.titlesize":12,
    "grid.color":GRID,"savefig.facecolor":BG})
ASSETS=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","assets")
def save(fig,update,frames,name,fps=15):
    an=FuncAnimation(fig,update,frames=frames,blit=False)
    out=os.path.join(ASSETS,name); an.save(out,writer=PillowWriter(fps=fps),dpi=72); plt.close(fig)
    print(name,round(os.path.getsize(out)/1e6,2),"MB"); return out
def caption(fig,text,y=0.02): fig.text(0.5,y,text,ha="center",va="bottom",color=MUTED,fontsize=8.5)
