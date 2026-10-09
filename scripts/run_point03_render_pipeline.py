"""Frozen analytic marks for registered OpenGL/Vulkan comparison."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
sys.path.insert(0,str(Path(__file__).resolve().parent))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--profile',type=Path,required=True)
    a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);out=a.out.resolve();out.relative_to(ROOT/'resultados/codex')
    if (out/'render_result.json').exists():raise FileExistsError('existing result')
    p=json.loads(a.profile.read_text(encoding='utf-8'));start=time.perf_counter_ns()
    from point03_render_p2_gate import require_p0,ns_seconds
    prerequisite=require_p0(ROOT,p)
    for name,digest in p['sources_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('source mismatch')
    h=json.loads(Path('D:/PROJECTS/.cognition/gpu_queue/holder.json').read_text(encoding='utf-8'))
    if os.environ.get('GPUQ_HOLDER')!='1' or h.get('child_pid')!=os.getppid():raise RuntimeError('own FIFO guard missing')
    r=dict(status='failure_retained',rows=[],gpu_execution=False,new_t96_field=False,physical_validation=False,
           profile_sha256=hashlib.sha256(a.profile.read_bytes()).hexdigest(),sources_sha256=p['sources_sha256'],p0_local_audit_sha256=prerequisite)
    try:
        import bpy,gpu,numpy as np
        from gpu_extras.batch import batch_for_shader
        from point03_render_pipeline_reference import MODES,CONSTANT,reference,metrics
        from point03_render_reference import TRIANGLE,RESOLUTIONS
        r['runtime']=dict(python=sys.version.split()[0],numpy=np.__version__,thread_caps={k:os.environ[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')})
        r['engine']=dict(version=bpy.app.version_string,backend=gpu.platform.backend_type_get(),renderer=gpu.platform.renderer_get())
        if bpy.app.version[:3]!=(4,5,14) or r['engine']['backend']!=p['backend'] or '3090' not in r['engine']['renderer']:raise RuntimeError('unregistered engine/backend')
        t=time.perf_counter_ns();stage=gpu.types.GPUStageInterfaceInfo('silice_pipeline_marker');stage.smooth('VEC3','varying_value')
        info=gpu.types.GPUShaderCreateInfo();info.vertex_in(0,'VEC3','position');info.vertex_in(1,'VEC3','attribute_value');info.vertex_out(stage);info.fragment_out(0,'VEC4','color')
        info.push_constant('INT','mode');info.push_constant('FLOAT','resolution');info.push_constant('VEC3','constant_value')
        info.vertex_source('void main(){varying_value=attribute_value;gl_Position=vec4(position,1.0);}')
        info.fragment_source('''void main(){
        vec2 xy=2.0*gl_FragCoord.xy/resolution-1.0;
        float l2=(xy.y+0.7)/1.5;float l1=(1.0-l2)*0.5+xy.x/1.6;
        vec3 analytic=vec3(1.0-l1-l2,l1,l2);
        vec3 v=constant_value;
        if(mode==1)v=varying_value;
        if(mode==2)v=analytic;
        if(mode==3)v=varying_value*varying_value;
        if(mode==4)v=analytic*analytic;
        color=vec4(v,1.0);
        }''')
        shader=gpu.shader.create_from_info(info)
        batches={}
        for attribute in ('constant','bary'):
            values=[CONSTANT]*3 if attribute=='constant' else [(1.,0.,0.),(0.,1.,0.),(0.,0.,1.)]
            batches[attribute]=[batch_for_shader(shader,'TRIS',{'position':[(float(x),float(y),z) for x,y in TRIANGLE],'attribute_value':values}) for z in (0.,.25)]
        r['shader_batch_preparation_ns']=time.perf_counter_ns()-t;r['gpu_execution']=True
        for n in RESOLUTIONS:
            off=gpu.types.GPUOffScreen(n,n,format='RGBA32F')
            try:
                with off.bind():
                    fb=gpu.state.active_framebuffer_get();gpu.state.viewport_set(0,0,n,n);gpu.state.depth_test_set('NONE');gpu.state.face_culling_set('NONE')
                    for marker in MODES:
                        if time.perf_counter_ns()-start>=110_000_000_000 or datetime.now(timezone.utc)>=datetime(2026,10,9,13,45,tzinfo=timezone.utc):raise RuntimeError('time limit')
                        t=time.perf_counter_ns();e,i,m=reference(marker,n);cpu_ns=time.perf_counter_ns()-t
                        gpu.state.blend_set('ADDITIVE' if 'add' in marker else 'NONE')
                        attribute='constant' if marker=='attribute_none' else 'bary'
                        mode=1 if marker=='attribute_none' or 'bary_smooth' in marker else 2 if 'bary_analytic' in marker else 3 if 'quadratic_smooth' in marker else 4 if 'quadratic_analytic' in marker else 0
                        t=time.perf_counter_ns();fb.clear(color=(0.,0.,0.,0.));shader.bind();shader.uniform_int('mode',mode);shader.uniform_float('resolution',n);shader.uniform_float('constant_value',CONSTANT)
                        for k in range(2 if 'add2' in marker else 1):batches[attribute][k].draw(shader)
                        buffer=fb.read_color(0,0,n,n,4,0,'FLOAT');buffer.dimensions=n*n*4;raw=np.array(buffer,dtype=np.float32).reshape(n,n,4);gpu_ns=time.perf_counter_ns()-t
                        name=f'{marker}_{n}.npz';path=out/name
                        with path.open('xb') as f:np.savez_compressed(f,rgba=raw)
                        r['rows'].append(dict(marker=marker,resolution=n,raw=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),cpu_ns=cpu_ns,gpu_ns=gpu_ns,cpu_s=ns_seconds(cpu_ns),gpu_s=ns_seconds(gpu_ns),**metrics(raw,e,i,m)))
            finally:gpu.state.blend_set('NONE');off.free()
        r['status']='completed';r['accuracy_pass']=all(row['accuracy_pass'] for row in r['rows'])
    except Exception as ex:r.update(error_type=type(ex).__name__,error_message=str(ex)[:500],accuracy_pass=False)
    finally:
        r['elapsed_worker_ns']=time.perf_counter_ns()-start;r['finished_utc']=datetime.now(timezone.utc).isoformat()
        with (out/'render_result.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.flush();os.fsync(f.fileno())
    os._exit(0 if r['status']=='completed' else 2)
if __name__=='__main__':main()
