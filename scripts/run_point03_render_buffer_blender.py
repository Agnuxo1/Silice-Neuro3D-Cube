"""P0 marker-only GPU calibration; fixed gates, owned process and bounded exit."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
             'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[name] = '1'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--profile', type=Path, required=True)
    args = ap.parse_args(sys.argv[sys.argv.index('--')+1:])
    out = args.out.resolve(); out.relative_to(ROOT/'resultados/codex')
    p = json.loads(args.profile.read_text(encoding='utf-8'))
    for name, digest in p['sources_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('frozen source changed')
    holder = json.loads(Path('D:/PROJECTS/.cognition/gpu_queue/holder.json').read_text())
    if os.environ.get('GPUQ_HOLDER') != '1' or holder['child_pid'] != os.getppid():
        raise RuntimeError('own direct supervisor reservation required')
    result = {'status': 'failure_retained', 'rows': [], 'gpu_execution': False,
              'new_t96_field': False, 'physical_validation': False,
              'profile_sha256': hashlib.sha256(args.profile.read_bytes()).hexdigest(),
              'sources_sha256': p['sources_sha256'], 'marker_only': True,
              'exit_method': 'os._exit after offscreen free and closed/fsynced report'}
    start = time.perf_counter_ns()
    try:
        import bpy
        import gpu
        import numpy as np
        from gpu_extras.batch import batch_for_shader
        from point03_render_buffer_reference import expected, old_export_prediction, check_marker, SIZES, CASES
        result['engine'] = {'version': bpy.app.version_string,
                            'renderer': gpu.platform.renderer_get(),
                            'vendor': gpu.platform.vendor_get(),
                            'backend': gpu.platform.backend_type_get()}
        result['runtime'] = {'python': sys.version.split()[0], 'numpy': np.__version__,
                             'perf_counter_resolution_s': time.get_clock_info('perf_counter').resolution,
                             'monotonic_resolution_s': time.get_clock_info('monotonic').resolution,
                             'thread_caps': {n: os.environ[n] for n in
                                            ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')}}
        if bpy.app.version[:3] != (4, 5, 14) or '3090' not in result['engine']['renderer']:
            raise RuntimeError('unregistered engine/device')
        prep = time.perf_counter_ns()
        info = gpu.types.GPUShaderCreateInfo()
        info.vertex_in(0, 'VEC3', 'position'); info.fragment_out(0, 'VEC4', 'marker')
        info.push_constant('VEC2', 'size'); info.push_constant('INT', 'kind')
        info.vertex_source('void main(){gl_Position=vec4(position,1.0);}')
        info.fragment_source('''void main(){
          vec2 q=gl_FragCoord.xy/size;
          marker=(kind==0)?vec4(0.125,0.375,0.625,0.875)
                         :vec4(q.x,q.y,0.125+0.25*q.x+0.5*q.y,1.0);
        }''')
        shader = gpu.shader.create_from_info(info)
        batch = batch_for_shader(shader, 'TRIS', {'position':
            [(-1.,-1.,0.),(1.,-1.,0.),(1.,1.,0.),(-1.,-1.,0.),(1.,1.,0.),(-1.,1.,0.)]})
        result['shader_batch_preparation_ns'] = time.perf_counter_ns()-prep
        result['gpu_execution'] = True
        for width, height in SIZES:
            off = gpu.types.GPUOffScreen(width, height, format='RGBA32F')
            try:
                with off.bind():
                    fb = gpu.state.active_framebuffer_get()
                    gpu.state.viewport_set(0, 0, width, height)
                    gpu.state.depth_test_set('NONE'); gpu.state.face_culling_set('NONE')
                    gpu.state.blend_set('NONE')
                    for kind, case in enumerate(CASES):
                        if (time.perf_counter_ns()-start)/1e9 >= 110 or datetime.now(timezone.utc) >= datetime(2026,10,9,13,45,tzinfo=timezone.utc):
                            raise RuntimeError('worker deadline')
                        t = time.perf_counter_ns()
                        fb.clear(color=(0.,0.,0.,0.)); shader.bind()
                        shader.uniform_float('size', (width, height)); shader.uniform_int('kind', kind)
                        batch.draw(shader)
                        buffer = fb.read_color(0, 0, width, height, 4, 0, 'FLOAT')
                        metadata = {'dimensions': list(buffer.dimensions),
                                    'numpy_strides': list(np.asarray(buffer).strides)}
                        old = np.array(buffer, dtype=np.float32).reshape(height, width, 4)
                        # Explicit one-dimensional export has only item-size stride.
                        # This defines pixel/channel storage; no image alignment is fitted.
                        buffer.dimensions = width*height*4
                        flat = np.array(buffer, dtype=np.float32)
                        corrected = flat.reshape(height, width, 4)
                        elapsed = time.perf_counter_ns()-t
                        reference = expected(case, width, height)
                        m = check_marker(corrected, reference)
                        old_m = check_marker(old, reference)
                        pred = old_export_prediction(corrected)
                        prediction_error = float(np.max(np.abs(old-pred)))
                        name = f'{case}_{width}x{height}.npz'
                        with (out/name).open('xb') as f:
                            np.savez_compressed(f, old_export=old, corrected=corrected)
                        result['rows'].append({'case': case, 'width': width, 'height': height,
                            'raw': name, 'sha256': hashlib.sha256((out/name).read_bytes()).hexdigest(),
                            'buffer_metadata': metadata, 'draw_both_readbacks_ns': elapsed,
                            'corrected': m, 'old': old_m,
                            'old_stride_prediction_max_error': prediction_error})
            finally:
                off.free()
        result['status'] = 'completed'
        result['accuracy_pass'] = all(r['corrected']['pass'] for r in result['rows'])
        result['layout_prediction_pass'] = all(r['old_stride_prediction_max_error'] <= 1e-6 for r in result['rows'])
        result['timing_positive'] = all(r['draw_both_readbacks_ns'] > 0 for r in result['rows'])
    except Exception as error:
        result['error_type'] = type(error).__name__; result['error_message'] = str(error)[:500]
        result['accuracy_pass'] = False
    finally:
        result['elapsed_worker_ns'] = time.perf_counter_ns()-start
        result['finished_utc'] = datetime.now(timezone.utc).isoformat()
        with (out/'render_result.json').open('x', encoding='utf-8') as f:
            json.dump(result, f, indent=2); f.flush(); os.fsync(f.fileno())
    # Only this factory-startup process is closed; no user scene or sibling process.
    os._exit(0 if result['status'] == 'completed' else 2)


if __name__ == '__main__': main()
