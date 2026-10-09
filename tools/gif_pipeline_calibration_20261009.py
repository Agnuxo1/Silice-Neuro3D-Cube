"""Plot audited instrument marks only; no optical propagation or GPU execution."""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR']=str(ROOT/'resultados/codex/plot_cache_pipeline_20261009')
os.environ['OPENBLAS_NUM_THREADS']='1'
import hashlib,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
sys.path.insert(0,str(ROOT/'scripts'))
from point03_render_pipeline_reference import reference,MODES

def main():
    target=ROOT/'assets/12_gpu_pipeline_opengl_vulkan.gif'
    manifest=ROOT/'resultados/codex/point03_pipeline_gif_manifest_20261009.json'
    if target.exists() or manifest.exists():raise FileExistsError('exclusive animation')
    frames=[];inputs={};colors=['#ffbd69','#5dd6c0']
    for backend in ('opengl','vulkan'):
        out=ROOT/f'resultados/codex/point03_render_pipeline_{backend}_run01_20261009'
        p=out/'local_integrity_audit.json';a=json.loads(p.read_text(encoding='utf-8'));assert a['integrity_pass']
        inputs[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
        for n in (64,128,256):
            rows={r['marker']:r for r in a['rows'] if r['resolution']==n}
            fig,(ax,im)=plt.subplots(1,2,figsize=(11,6.2),dpi=100,gridspec_kw={'width_ratios':[1.3,1]})
            fig.patch.set_facecolor('#0e1b2a')
            for x in (ax,im):x.set_facecolor('#0e1b2a');x.tick_params(colors='#ddeaf7');x.spines[:].set_color('#566575')
            errors=[rows[m]['max_channel_error'] for m in MODES]
            ax.barh(range(10),errors,color=[colors[0] if e>1e-6 else colors[1] for e in errors])
            ax.set_yticks(range(10),[m.replace('_',' ') for m in MODES],fontsize=9)
            ax.invert_yaxis();ax.set_xscale('log');ax.set_xlim(1e-9,1e-3)
            ax.axvline(1e-6,color='#ff748c',linestyle='--',label='Umbral 1e-6')
            ax.set_xlabel('Error absoluto máximo RGBA',color='#ddeaf7');ax.legend(facecolor='#0e1b2a',labelcolor='#ddeaf7',fontsize=9)
            rawpath=out/f'bary_smooth_none_{n}.npz';inputs[rawpath.relative_to(ROOT).as_posix()]=hashlib.sha256(rawpath.read_bytes()).hexdigest()
            with np.load(rawpath,allow_pickle=False) as z:raw=z['rgba'].copy()
            expected,inside,compare=reference('bary_smooth_none',n)
            err=np.max(abs(raw.astype(np.float64)-expected),axis=-1);err[~compare]=np.nan
            h=im.imshow(err,origin='lower',vmin=0,vmax=5e-5,cmap='magma',extent=(-1,1,-1,1))
            im.set_title('Error de coordenadas smooth',color='#ddeaf7',fontsize=11)
            im.set_xlabel('x normalizada',color='#ddeaf7');im.set_ylabel('y normalizada',color='#ddeaf7')
            cb=fig.colorbar(h,ax=im,fraction=.047,pad=.04);cb.ax.tick_params(colors='#ddeaf7');cb.set_label('Error absoluto',color='#ddeaf7')
            fig.suptitle(f'Calibración GPU real · {backend.upper()} · {n}×{n}',color='white',fontsize=17,y=.975)
            fig.text(.5,.025,'RTX 3090 / Blender 4.5.14 · 21/30 marcas aprueban por backend · No es una red ni propagación',ha='center',color='#ddeaf7',fontsize=9)
            fig.subplots_adjust(left=.2,right=.96,top=.86,bottom=.13,wspace=.32)
            fig.canvas.draw();rgba=np.asarray(fig.canvas.buffer_rgba()).copy();frames.append(Image.fromarray(rgba).convert('RGB'));plt.close(fig)
    frames[0].save(target,save_all=True,append_images=frames[1:],duration=1200,loop=0,optimize=False)
    with Image.open(target) as g:assert g.n_frames==6;size=g.size
    result=dict(kind='audited GPU instrument calibration; no generated optical network',inputs_sha256=inputs,
                generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),frames=6,size=list(size),
                sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size,
                numpy=np.__version__,matplotlib=matplotlib.__version__,gpu_executed_by_generator=False)
    with manifest.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps(result))
if __name__=='__main__':main()
