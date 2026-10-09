"""README GIFs from audited data and one explicitly conceptual network diagram."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
import argparse
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import numpy as np
os.environ['MPLCONFIGDIR']=str(Path(__file__).resolve().parents[1]/'resultados/codex/readme_matplotlib_cache_20261009')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import PIL

ROOT=Path(__file__).resolve().parents[1]
BG='#0b1220';PANEL='#111a2e';TXT='#e6edf7';MUTED='#91a4c0';CY='#22d3ee';AM='#fbbf24';GR='#34d399';RD='#f87171'
plt.rcParams.update({'figure.facecolor':BG,'axes.facecolor':PANEL,'axes.edgecolor':MUTED,
    'text.color':TXT,'axes.labelcolor':TXT,'xtick.color':MUTED,'ytick.color':MUTED,
    'font.family':'DejaVu Sans','font.size':10,'savefig.facecolor':BG})


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def frame(fig):
    fig.canvas.draw()
    return Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGB')


def save_gif(path,frames,duration=250):
    if path.exists():raise FileExistsError(path)
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=False)
    with Image.open(path) as im:
        assert im.n_frames>1
        for k in range(im.n_frames):im.seek(k);im.load()
        return dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),
                    bytes=path.stat().st_size,frames=im.n_frames,size=list(im.size))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True)
    args=ap.parse_args();assets=ROOT/'assets';inputs=[];outputs=[]
    mpath=ROOT/'resultados/codex/point03_d16_mid_recovery_20261009/local_integrity_audit.json'
    m=json.loads(mpath.read_text());assert m['integrity_pass'] and m['temporal_precision_pass'] and m['checkpoints_checked']==96
    inputs.append(dict(path=mpath.relative_to(ROOT).as_posix(),sha256=sha(mpath)))
    labels=['Campo relativo','Potencia · campo','Potencia · intensidad','Cota PSD · campo','Cota PSD · intensidad']
    values=np.array([m['relative_field_difference'],m['power_differences']['field'],
        m['power_differences']['intensity'],m['PSD_observable_bounds']['field'],m['PSD_observable_bounds']['intensity']])
    limits=np.array([1e-4,1e-6,1e-6,1e-5,1e-5]);ratios=values/limits
    assert np.all((ratios>0)&(ratios<=1))
    fig,ax=plt.subplots(figsize=(9.6,5.4),dpi=90);fig.subplots_adjust(left=.25,right=.96,top=.8,bottom=.2)
    bars=ax.barh(np.arange(5),ratios,color=CY,height=.55);ax.invert_yaxis()
    ax.set_yticks(np.arange(5),labels);ax.set_xscale('log');ax.set_xlim(1e-5,1.25)
    ax.axvline(1,color=AM,ls='--',lw=1.5);ax.set_xlabel('Valor / umbral registrado · escala logarítmica')
    ax.grid(axis='x',alpha=.15);ax.text(1,.97,'límite',transform=ax.get_xaxis_transform(),ha='right',color=AM)
    for k,(v,lim,ratio) in enumerate(zip(values,limits,ratios)):
        ax.text(.975,k,f'{v:.3e} / {lim:.0e}',va='center',ha='right',fontsize=9,
                transform=ax.get_yaxis_transform(),bbox=dict(facecolor=PANEL,edgecolor='none',alpha=.85,pad=2))
    fig.text(.06,.92,'M2-R1 · auditoría temporal aprobada',fontsize=19,weight='bold')
    fig.text(.06,.85,'96 campos · 83 conservados + 13 nuevos · dos detectores',color=MUTED)
    fig.text(.5,.055,'Valores finales fijos; el resaltado es visual. Modelo escalar ideal, sin validación física.',ha='center',fontsize=8.5,color=MUTED)
    frames=[]
    for k in range(5):
        for j,b in enumerate(bars):b.set_color(GR if j==k else CY);b.set_alpha(1 if j==k else .5)
        frames.extend([frame(fig) for _ in range(3)])
    outputs.append(dict(**save_gif(assets/'09_m2_temporal_audit_v2.gif',frames,420),kind='audited_numerical_results'))
    plt.close(fig)
    pdir=ROOT/'resultados/codex/point03_render_buffer_calibration_run01_20261009'
    apath=pdir/'local_integrity_audit.json';audit=json.loads(apath.read_text())
    assert audit['integrity_pass'] and audit['accuracy_pass'] and audit['marker_frames']==6
    inputs.append(dict(path=apath.relative_to(ROOT).as_posix(),sha256=sha(apath)))
    dataset=[]
    for row in audit['rows']:
        p=pdir/f"{row['case']}_{row['width']}x{row['height']}.npz"
        inputs.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
        with np.load(p,allow_pickle=False) as z:dataset.append((row,z['old_export'].copy(),z['corrected'].copy()))
    fig,axes=plt.subplots(1,2,figsize=(9.6,5.4),dpi=90);fig.subplots_adjust(left=.07,right=.88,bottom=.22,top=.77,wspace=.22)
    ims=[ax.imshow(np.zeros((16,32)),origin='lower',extent=(0,1,0,1),vmin=0,vmax=1,cmap='viridis',interpolation='nearest',aspect='auto') for ax in axes]
    for ax,title in zip(axes,['Lectura anterior · rechazada','Lectura calibrada · aprobada']):
        ax.set_title(title,fontsize=11);ax.set_xlabel('Coordenada normalizada x');ax.set_ylabel('y')
    cbax=fig.add_axes([.91,.26,.018,.43]);fig.colorbar(ims[1],cax=cbax,label='Valor del canal (0–1)')
    fig.text(.06,.91,'GPU · seis marcas auditadas',fontsize=19,weight='bold')
    subtitle=fig.text(.06,.83,'',color=MUTED)
    fig.text(.5,.06,'Datos Blender / RTX 3090. Calibración de lectura; no propagación ni red neuronal validada.',ha='center',fontsize=8.3,color=MUTED)
    frames=[]
    for row,old,new in dataset:
        for channel in range(3):
            ims[0].set_data(old[...,channel]);ims[1].set_data(new[...,channel])
            subtitle.set_text(f"{row['case']} · {row['width']} × {row['height']} · canal {'RGB'[channel]} · error nuevo ≤ 1e−6")
            frames.append(frame(fig))
    outputs.append(dict(**save_gif(assets/'10_gpu_buffer_calibration_v2.gif',frames,450),kind='audited_gpu_calibration'))
    plt.close(fig)
    fig=plt.figure(figsize=(9.6,5.4),dpi=90);ax=fig.add_subplot(111,projection='3d');fig.subplots_adjust(left=0,right=1,bottom=.15,top=.87)
    ax.set_facecolor(BG);ax.set_axis_off();ax.set_xlim(-.1,1.3);ax.set_ylim(0,1);ax.set_zlim(0,1);ax.set_box_aspect((1.4,1,1))
    ax.view_init(elev=19,azim=-66)
    corners=np.array([[x,y,z] for x in (0,1) for y in (0,1) for z in (0,1)])
    for i,a in enumerate(corners):
        for b in corners[i+1:]:
            if np.count_nonzero(a!=b)==1:ax.plot(*np.stack([a,b]).T,color=MUTED,lw=.8,alpha=.35)
    layers=[np.array([[.08,.2,.25],[.08,.8,.75]]),np.array([[.45,.2,.65],[.45,.5,.4],[.45,.8,.65]]),np.array([[.9,.35,.3],[.9,.7,.7]])]
    edges=[]
    for left,right in zip(layers,layers[1:]):
        for a in left:
            for b in right:
                edges.append((a,b));ax.plot(*np.stack([a,b]).T,color=CY,lw=1.3,alpha=.35)
    for layer,color in zip(layers,[CY,AM,GR]):ax.scatter(*layer.T,s=70,c=color,depthshade=False,edgecolors=TXT,lw=.5)
    end=np.array([1.2,.5,.5]);ax.scatter(*end,s=110,c=AM,marker='s',depthshade=False)
    for a in layers[-1]:ax.plot(*np.stack([a,end]).T,color=GR,lw=1.2,alpha=.5)
    moving=ax.scatter([],[],[],s=22,c=TXT,depthshade=False)
    fig.text(.06,.93,'Red óptica 3D · arquitectura propuesta',fontsize=19,weight='bold')
    fig.text(.06,.875,'Entradas → guías / fases / acopladores → detección y control',color=MUTED)
    fig.text(.5,.055,'Ilustración conceptual CPU: el movimiento no es una trayectoria óptica calculada.\nEntrenamiento, fabricación e integración completos pendientes.',ha='center',fontsize=8.4,color=MUTED)
    frames=[]
    for k in range(32):
        t=k/31;points=np.array([a+(b-a)*t for a,b in edges]);moving._offsets3d=(points[:,0],points[:,1],points[:,2])
        frames.append(frame(fig))
    outputs.append(dict(**save_gif(assets/'11_optical_network_proposal_v2.gif',frames,110),kind='conceptual_cpu_illustration_not_simulation'))
    plt.close(fig)
    report={'created_utc':datetime.now(timezone.utc).isoformat(),'inputs':inputs,'outputs':outputs,
        'generator_sha256':sha(Path(__file__)),'runtime':{'python':sys.version.split()[0],'numpy':np.__version__,'matplotlib':matplotlib.__version__,'pillow':PIL.__version__},
        'numerical_gifs_use_audited_data':True,'architecture_proposal_labeled_in_every_frame':True,
        'new_simulation':False,'gpu_execution':False,'physical_validation':False,'network_validated':False}
    with args.manifest.open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2)
    print(json.dumps({'outputs':outputs,'new_simulation':False,'network_validated':False}))


if __name__=='__main__':main()
