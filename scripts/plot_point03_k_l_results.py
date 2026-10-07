"""Scientific figure from completed, audited K626 and FDST evidence only."""
import argparse
import json
import os
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR']=str(ROOT/'resultados/codex/plot_cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def plot(pilot,out,visible):
    assert not out.exists();out.mkdir(parents=True)
    l=read(pilot/'assessment.json');li=read(pilot/'integrity_audit.json');assert li['integrity_pass'] and li['acceptance_recomputed'] and not l['point03_closed']
    k640=read(ROOT/'resultados/codex/point03_linear_K640_20261007.json');k626=read(ROOT/'resultados/codex/point03_linear_probe_20261007_K626/assessment.json')
    fig,axes=plt.subplots(1,2,figsize=(12,5.8));ax=axes[0]
    ratios=[];labels=[]
    for n,r in ((640,k640),(626,k626)):
        for method,label in (('field','campo'),('intensity','intensidad')):
            v=r['gates'][method];ratios.append(v['residual']/v['limit']);labels.append(f'N{n}\n{label}')
    bars=ax.bar(np.arange(4),ratios,color=['#31794e' if x<=1 else '#a53b38' for x in ratios])
    for bar,value in zip(bars,ratios):ax.text(bar.get_x()+bar.get_width()/2,value+.035,f'{value:.3f}',ha='center',fontsize=10)
    ax.axhline(1,color='black',linestyle='--',label='Límite de aceptación');ax.set_xticks(np.arange(4),labels);ax.set_ylim(0,max(ratios)*1.18)
    ax.set_ylabel('Residuo de predicción / límite registrado');ax.set_title('Predicciones espaciales K');ax.legend(fontsize=8);ax.grid(axis='y',alpha=.2)
    ax=axes[1];x=np.array([r['dz_m']*1e6 for r in l['rows']])
    for quantity,label,color in (('field','Campo: error relativo','#275f9c'),('power_field','Potencia: campo bilineal','#a53b38'),('power_intensity','Potencia: intensidad bilineal','#a7731c')):
        y=np.array([r['errors'][quantity] for r in l['rows']]);ax.loglog(x,y,'o-',label=label,color=color)
    y=np.array([r['errors']['field'] for r in l['rows']]);ax.loglog(x,y[-1]*(x/x[-1])**4,':',color='#666666',label='Pendiente 4 (guía, anclada al fino)')
    ax.axhline(1e-4,color='#275f9c',linestyle='--',alpha=.6,label='Límite de campo fino')
    ax.axhline(1e-6,color='#a53b38',linestyle='--',alpha=.6,label='Límite de ambas potencias finas')
    ax.set_xlabel('Paso longitudinal dz (µm)');ax.set_ylabel('Errores adimensionales frente Taylor R17');ax.set_title(f'Contraste temporal FDST: {"PASS" if l["pilot_pass"] else "FAIL"}');ax.grid(which='both',alpha=.2);ax.legend(fontsize=7)
    fig.suptitle('T96/Q4: punto 3 abierto — 7 de octubre de 2026',fontsize=14)
    fig.text(.02,.02,'K640 reutiliza una trayectoria; K626 es una prueba nueva. FDST contrasta el tiempo: no cierra convergencia espacial.\nLa referencia Taylor conserva su discrepancia R11/R17 de potencia; todos los FAIL anteriores permanecen.',fontsize=8)
    fig.tight_layout(rect=(0,.08,1,.94))
    paths=[]
    for ext in ('png','svg'):
        p=out/f'contraste_K626_FDST.{ext}';fig.savefig(p,dpi=180);paths.append(p)
    plt.close(fig);visible.mkdir(parents=True,exist_ok=True)
    for p in paths:
        target=visible/p.name;assert not target.exists();shutil.copyfile(p,target);assert target.read_bytes()==p.read_bytes()
    print(json.dumps(dict(pilot_pass=l['pilot_pass'],point03_closed=False,files=[str(visible/p.name) for p in paths])))

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--pilot',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--visible',type=Path,required=True);a=p.parse_args();plot(a.pilot,a.out,a.visible)
if __name__=='__main__':main()
