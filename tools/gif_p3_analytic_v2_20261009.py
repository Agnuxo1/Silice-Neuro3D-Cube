"""Animate existing audited P2 frames with fixed scales; no GPU or propagation."""
from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR'] = str(ROOT/'resultados/codex/plot_cache_p3_20261009')
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import hashlib
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from PIL import Image
sys.path.insert(0, str(ROOT/'scripts'))
from point03_render_reference import evaluate_prepared, prepare, nodal_for_repeat


def main():
    target = ROOT/'assets/13_gpu_p2_analytic_fields_v2.gif'
    manifest = ROOT/'resultados/codex/point03_p3_gif_manifest_v2_20261009.json'
    if target.exists() or manifest.exists():
        raise FileExistsError('exclusive animation')
    source = ROOT/'resultados/codex/point03_render_p3_summary_20261009.json'
    summary = json.loads(source.read_text(encoding='utf-8'))
    inputs = {source.relative_to(ROOT).as_posix(): hashlib.sha256(source.read_bytes()).hexdigest()}
    frames = []
    names = dict(single='Una fuente', constructive='Suma constructiva',
                 destructive='Suma destructiva', quarter='Desfase de 90°')
    cache = prepare(256)
    for backend in ('opengl', 'vulkan'):
        b = summary['backends'][backend]
        assert b['integrity_pass'] and b['accuracy_pass'] and b['fields'] == 84
        inputs.update(b['inputs_sha256'])
        out = ROOT/f'resultados/codex/point03_render_p3_{backend}_run01_20261009'
        for case, name in names.items():
            with np.load(out/f'{case}_256_0.npz', allow_pickle=False) as z:
                raw = z['rgba'].copy()
            field = raw[..., 0].astype(np.float64) + 1j*raw[..., 1].astype(np.float64)
            cpu, inside, compare = evaluate_prepared(case, cache, nodal_for_repeat(0))
            err = abs(field-cpu)
            err[~compare] = np.nan
            fig, axes = plt.subplots(2, 2, figsize=(12, 7.6), dpi=100)
            fig.patch.set_facecolor('#0e1b2a')
            for ax in axes.flat:
                ax.set_facecolor('#0e1b2a')
                ax.tick_params(colors='#ddeaf7')
                ax.spines[:].set_color('#566575')
            for ax, data, title in [(axes[0, 0], field.real, 'Parte real GPU'),
                                    (axes[0, 1], field.imag, 'Parte imaginaria GPU')]:
                h = ax.imshow(data, origin='lower', extent=(-1, 1, -1, 1),
                              vmin=-2.2, vmax=2.2, cmap='RdBu_r')
                ax.set_title(title+' · campo adimensional', color='#ddeaf7', fontsize=12)
                cb = fig.colorbar(h, ax=ax, fraction=.047, pad=.025)
                cb.ax.tick_params(colors='#ddeaf7')
            ax = axes[1, 0]
            h = ax.imshow(err, origin='lower', extent=(-1, 1, -1, 1),
                          vmin=0, vmax=5e-6, cmap='magma')
            ax.set_title('Error complejo frente a la referencia CPU', color='#ddeaf7', fontsize=12)
            cb = fig.colorbar(h, ax=ax, fraction=.047, pad=.025)
            cb.ax.tick_params(colors='#ddeaf7')
            cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f'{value/1e-6:.0f}'))
            cb.set_label('Error absoluto ×10⁻⁶ · umbral 5', color='#ddeaf7', fontsize=10)
            ax = axes[1, 1]
            errors = [b['cases'][c]['max_complex_error'] for c in names]
            ax.barh(range(4), [max(e, 1e-12) for e in errors],
                    color=['#ffbd69' if c == case else '#5dd6c0' for c in names])
            ax.set_yticks(range(4), list(names.values()), fontsize=10)
            ax.invert_yaxis()
            ax.set_xscale('log')
            ax.set_xlim(1e-12, 1e-5)
            ax.axvline(5e-6, color='#ff748c', linestyle='--')
            ax.set_title('Máximo de las 21 muestras por caso', color='#ddeaf7', fontsize=12)
            ax.set_xlabel('Error complejo · cero dibujado en 10⁻¹²', color='#ddeaf7', fontsize=10)
            for ax in (axes[0, 0], axes[0, 1], axes[1, 0]):
                ax.set_xlabel('x normalizada', color='#ddeaf7', fontsize=10)
                ax.set_ylabel('y normalizada', color='#ddeaf7', fontsize=10)
            fig.suptitle(f'R3 · {backend.upper()} · {name} · 256×256', color='white', fontsize=18, y=.985)
            fig.text(.5, .03, 'RTX 3090 / Blender 4.5.14 · 84/84 campos aprobados por backend · No es propagación ni una red funcional',
                     ha='center', color='#ddeaf7', fontsize=10)
            fig.text(.5, .007, 'Píxeles existentes: repetición 0 fija · Auditoría: todas las muestras · Escalas constantes · GIF generado en CPU',
                     ha='center', color='#ddeaf7', fontsize=9)
            fig.subplots_adjust(left=.06, right=.94, top=.9, bottom=.13, hspace=.38, wspace=.48)
            fig.canvas.draw()
            frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGB'))
            plt.close(fig)
    frames[0].save(target, save_all=True, append_images=frames[1:], duration=1400,
                   loop=0, optimize=False)
    with Image.open(target) as g:
        assert g.n_frames == 8
        size = g.size
        for i in range(g.n_frames):
            g.seek(i)
            g.load()
    result = dict(kind='audited manufactured P2 complex fields; not neural network or propagation',
                  displayed_rule='repeat 0, resolution 256, all four cases, both backends',
                  aggregate_rule='all 21 observations of each case', inputs_sha256=inputs,
                  generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  frames=8, size=list(size), duration_ms=1400,
                  sha256=hashlib.sha256(target.read_bytes()).hexdigest(), bytes=target.stat().st_size,
                  numpy=np.__version__, matplotlib=matplotlib.__version__,
                  gpu_executed_by_generator=False, fixed_complex_scale=[-2.2, 2.2],
                  fixed_error_scale=[0, 5e-6], graph_zero_floor=1e-12)
    with manifest.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=2)
    print(json.dumps({k: v for k, v in result.items() if k != 'inputs_sha256'}))


if __name__ == '__main__':
    main()
