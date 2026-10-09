"""Blender GPU vertex/fragment raster pilot. Run only under the pinned guard."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
for cap in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[cap]='1'
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    out = args.out.resolve(); out.relative_to(ROOT/'resultados/codex')
    report_path = out/'render_result.json'
    if report_path.exists(): raise FileExistsError(report_path)
    started_ns = time.perf_counter_ns(); started = started_ns/1e9; deadline = datetime(2026, 10, 9, 13, 45, tzinfo=timezone.utc)
    profile = json.loads(args.profile.read_text(encoding='utf-8'))
    from point03_render_p2_gate import require_p0, ns_seconds
    p0_sha = require_p0(ROOT, profile)
    for name, digest in profile['sources_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('frozen source mismatch')
    holder = json.loads(Path(r'D:/PROJECTS/.cognition/gpu_queue/holder.json').read_text(encoding='utf-8'))
    if os.environ.get('GPUQ_HOLDER') != '1' or holder.get('child_pid') != os.getppid():
        raise RuntimeError('live own supervisor reservation missing')
    if datetime.now(timezone.utc) >= deadline: raise RuntimeError('absolute deadline')
    result = dict(status='failure_retained', rows=[], gpu_execution=False,
                  new_t96_field=False, physical_validation=False,
                  profile_sha256=hashlib.sha256(args.profile.read_bytes()).hexdigest(),
                  sources_sha256=profile['sources_sha256'], p0_local_audit_sha256=p0_sha,
                  readback_method='Buffer 1D then C reshape',
                  exit_method='os._exit after freeing offscreens and closed/fsynced report')
    try:
        import bpy
        import gpu
        import numpy as np
        from gpu_extras.batch import batch_for_shader
        from point03_render_reference import (TRIANGLE, CASES, RESOLUTIONS, prepare,
             evaluate_prepared, nodal_for_repeat, metrics)
        result['runtime'] = dict(python=sys.version.split()[0], numpy=np.__version__,
            perf_counter_resolution_s=time.get_clock_info('perf_counter').resolution,
            thread_caps={k:os.environ[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')})
        renderer = gpu.platform.renderer_get()
        result['engine'] = dict(version=bpy.app.version_string, renderer=renderer,
                               vendor=gpu.platform.vendor_get(), backend=gpu.platform.backend_type_get())
        if bpy.app.version[:3] != (4, 5, 14) or '3090' not in renderer or 'NVIDIA' not in renderer.upper():
            raise RuntimeError('unregistered engine/device')
        compile_start = (time.perf_counter_ns()/1e9)
        stage = gpu.types.GPUStageInterfaceInfo('silice_p2_interface')
        stage.smooth('VEC3', 'bary')
        info = gpu.types.GPUShaderCreateInfo()
        info.vertex_in(0, 'VEC3', 'position'); info.vertex_in(1, 'VEC3', 'bary_in')
        info.vertex_out(stage); info.fragment_out(0, 'VEC4', 'output_field')
        info.push_constant('FLOAT', 'phase')
        for i in range(6): info.push_constant('VEC2', 'c'+str(i))
        info.vertex_source('void main(){bary=bary_in;gl_Position=vec4(position,1.0);}')
        info.fragment_source('''void main(){
          vec2 e=bary.x*(2.0*bary.x-1.0)*c0+bary.y*(2.0*bary.y-1.0)*c1
                +bary.z*(2.0*bary.z-1.0)*c2+4.0*bary.x*bary.y*c3
                +4.0*bary.y*bary.z*c4+4.0*bary.z*bary.x*c5;
          float cp=cos(phase),sp=sin(phase);
          output_field=vec4(cp*e.x-sp*e.y,sp*e.x+cp*e.y,0.0,1.0);
        }''')
        shader = gpu.shader.create_from_info(info)
        batches = [batch_for_shader(shader, 'TRIS',
                    {'position':[(float(x),float(y),z) for x,y in TRIANGLE],
                     'bary_in':[(1.,0.,0.),(0.,1.,0.),(0.,0.,1.)]}) for z in (0., .25)]
        result['shader_batch_preparation_s'] = (time.perf_counter_ns()/1e9)-compile_start
        result['gpu_execution'] = True
        for n in RESOLUTIONS:
            prep_start = (time.perf_counter_ns()/1e9); cache = prepare(n)
            result.setdefault('cpu_geometry_preparation_s', {})[str(n)] = (time.perf_counter_ns()/1e9)-prep_start
            off = gpu.types.GPUOffScreen(n, n, format='RGBA32F')
            try:
                with off.bind():
                    fb = gpu.state.active_framebuffer_get()
                    gpu.state.viewport_set(0, 0, n, n)
                    gpu.state.depth_test_set('NONE'); gpu.state.face_culling_set('NONE')
                    gpu.state.blend_set('ADDITIVE')
                    for case, phases in CASES.items():
                        for repeat in range(7):
                            if (time.perf_counter_ns()/1e9)-started >= 110 or datetime.now(timezone.utc) >= deadline:
                                raise RuntimeError('worker time/deadline')
                            nodal = nodal_for_repeat(repeat)
                            def cpu_call():
                                t=time.perf_counter_ns(); val=evaluate_prepared(case, cache, nodal)
                                return val, time.perf_counter_ns()-t
                            def gpu_call():
                                t=time.perf_counter_ns(); fb.clear(color=(0.,0.,0.,0.)); shader.bind()
                                for k,p in enumerate(phases):
                                    shader.uniform_float('phase', p)
                                    for j,value in enumerate(nodal):
                                        shader.uniform_float('c'+str(j), (float(value.real),float(value.imag)))
                                    batches[k].draw(shader)
                                buffer=fb.read_color(0,0,n,n,4,0,'FLOAT')
                                buffer.dimensions=n*n*4
                                raw=np.array(buffer,dtype=np.float32).reshape(n,n,4)
                                return raw, time.perf_counter_ns()-t
                            if repeat%2 == 0:
                                (cpu,inside,compare), cpu_ns=cpu_call(); raw,gpu_ns=gpu_call(); order='CPU/GPU'
                            else:
                                raw,gpu_ns=gpu_call(); (cpu,inside,compare),cpu_ns=cpu_call(); order='GPU/CPU'
                            cpu_s=ns_seconds(cpu_ns); gpu_s=ns_seconds(gpu_ns)
                            field=raw[...,0].astype(np.float64)+1j*raw[...,1].astype(np.float64)
                            base,_,_=evaluate_prepared('single',cache,nodal)
                            base_power=float(np.sum(abs(base[compare])**2)*(2/n)**2)
                            m=metrics(field,cpu,inside,compare,base_power,(2/n)**2)
                            name=f'{case}_{n}_{repeat}.npz'; path=out/name
                            with path.open('xb') as f: np.savez_compressed(f, rgba=raw)
                            result['rows'].append(dict(case=case, resolution=n, repeat=repeat,
                                order=order, cpu_s=cpu_s, gpu_draw_uniform_readback_s=gpu_s,
                                cpu_ns=cpu_ns, gpu_draw_uniform_readback_ns=gpu_ns,
                                raw=name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), **m))
            finally:
                gpu.state.blend_set('NONE'); off.free()
        result['status']='completed'
        result['accuracy_pass']=all(row['accuracy_pass'] for row in result['rows'])
        result['general_speedup_claim']=False
    except Exception as error:
        result['error_type']=type(error).__name__
        result['error_message']=str(error)[:500]
        result['accuracy_pass']=False
    finally:
        result['elapsed_worker_ns']=time.perf_counter_ns()-started_ns
        result['elapsed_worker_s']=result['elapsed_worker_ns']/1e9
        result['finished_utc']=datetime.now(timezone.utc).isoformat()
        with report_path.open('x',encoding='utf-8') as f:
            json.dump(result,f,indent=2); f.flush(); os.fsync(f.fileno())
    os._exit(0 if result['status']=='completed' else 2)


if __name__ == '__main__': main()
