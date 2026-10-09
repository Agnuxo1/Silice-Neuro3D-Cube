"""Summarize already audited R3 fields; never launch a renderer or solver."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]


def main():
    target = ROOT / 'resultados/codex/point03_render_p3_summary_20261009.json'
    doc = ROOT / 'Docs/POINT-03-RENDER-P3-ANALYTIC-RESULTS.md'
    if target.exists() or doc.exists():
        raise FileExistsError('exclusive summary')
    summary = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                   preparation_commit='ce183e71df79371f3b3f66d4a8fc82dc2a88abf1',
                   physical_validation=False, network_validated=False,
                   t96_closed=False, general_speedup_claim=False, backends={})
    for backend in ('opengl', 'vulkan'):
        out = ROOT / f'resultados/codex/point03_render_p3_{backend}_run01_20261009'
        audit = json.loads((out / 'local_integrity_audit.json').read_text(encoding='utf-8'))
        report = json.loads((out / 'render_result.json').read_text(encoding='utf-8'))
        guard = json.loads((out / 'guard.json').read_text(encoding='utf-8'))
        assert audit['integrity_pass'] and audit['accuracy_pass'] and audit['raw_frames'] == 84
        assert audit['strict_metric_agreement_pass'] and guard['status'] == 'completed'
        rows = audit['rows']
        grouped = {}
        for case in ('single', 'constructive', 'destructive', 'quarter'):
            group = [r for r in rows if r['case'] == case]
            assert len(group) == 21 and all(r['accuracy_pass'] for r in group)
            grouped[case] = dict(fields=len(group), max_complex_error=max(r['max_complex_error'] for r in group),
                                max_relative_l2=max((r['relative_l2'] for r in group if r['relative_l2'] is not None), default=None),
                                max_abs_power_difference=max(abs(r['gpu_power']-r['cpu_power']) for r in group))
        hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in out.iterdir() if p.is_file()}
        costs = dict(child_with_startup_s=guard['elapsed_child_with_startup_s'],
                     guard_s=guard['elapsed_guard_s'], worker_s=report['elapsed_worker_s'],
                     shader_batch_preparation_s=report['shader_batch_preparation_s'],
                     cpu_geometry_preparation_s=sum(report['cpu_geometry_preparation_s'].values()),
                     cpu_evaluation_sum_s=sum(r['cpu_s'] for r in report['rows']),
                     gpu_uniform_draw_readback_sum_s=sum(r['gpu_draw_uniform_readback_s'] for r in report['rows']))
        paired = []
        for n in (64, 128, 256):
            for case in grouped:
                g = [r for r in report['rows'] if r['resolution'] == n and r['case'] == case]
                paired.append(dict(resolution=n, case=case, observations=7,
                                   cpu_median_s=statistics.median(r['cpu_s'] for r in g),
                                   gpu_median_s=statistics.median(r['gpu_draw_uniform_readback_s'] for r in g),
                                   paired_ratios=[r['cpu_s']/r['gpu_draw_uniform_readback_s'] for r in g]))
        summary['backends'][backend] = dict(integrity_pass=True, accuracy_pass=True, fields=84,
            max_complex_error=max(r['max_complex_error'] for r in rows),
            max_relative_l2=max(r['relative_l2'] for r in rows if r['relative_l2'] is not None),
            max_abs_power_difference=max(abs(r['gpu_power']-r['cpu_power']) for r in rows),
            outside_max=max(r['outside_max'] for r in rows),
            dark_power_ratio_max=max(r['dark_power_ratio'] for r in rows if r['dark_power_ratio'] is not None),
            cases=grouped, costs=costs, paired_observations=paired, inputs_sha256=hashes)
    with target.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(summary, f, indent=2)
    b = summary['backends']
    lines = ['# R3: representación compleja P2 aprobada en OpenGL y Vulkan', '',
        'Los dos ensayos nuevos ejecutaron 84 campos por backend en Blender 4.5.14 LTS / RTX 3090. '
        'Las fuentes y perfiles publicados en ce183e71 preceden a los 168 campos. '
        'Los dos auditores locales aprueban integridad, precisión, fuentes, recursos, duraciones positivas, '
        'cierre normal y acuerdo de métricas a 1e-14 entre NumPy 1.26.4 del motor y 2.2.6 en Windows.', '',
        'Se mantienen los cuatro casos, siete perturbaciones, tres resoluciones, nodos, fases, máscaras y '
        'umbrales originales. El cambio prospectivo calcula baricéntricas analíticas desde gl_FragCoord '
        'para el triángulo fijo w=1. R1, R2 y la ruta smooth negativa de P1 permanecen intactos; '
        'este aprobado no los transforma ni adopta retroactivamente.', '',
        '| Criterio | OpenGL | Vulkan | Umbral registrado |', '|---|---:|---:|---:|']
    for label, key, gate in [('Error complejo máximo', 'max_complex_error', '5e-6'),
                             ('L2 relativo máximo', 'max_relative_l2', '5e-6'),
                             ('Diferencia absoluta de potencia', 'max_abs_power_difference', '5e-6'),
                             ('Exterior máximo', 'outside_max', '1e-7'),
                             ('Razón de potencia oscura', 'dark_power_ratio_max', '1e-10')]:
        lines.append(f'| {label} | {b["opengl"][key]:.10e} | {b["vulkan"][key]:.10e} | {gate} |')
    lines += ['', 'Cada backend aprueba 84/84 campos: 21 por caso (una fuente, suma constructiva, '
              'suma destructiva y desfase de un cuarto de vuelta). Los 168 NPZ completos se conservan '
              'con sus informes y hashes. El L2 relativo no es aplicable al campo oscuro de referencia nula; '
              'se conserva como null y se exige la razón de potencia oscura original. '
              'No se alinearon fases ni eligieron píxeles después del resultado.', '',
              '| Coste medido, segundos | OpenGL | Vulkan |', '|---|---:|---:|---:|']
    for label, key in [('Hijo con arranque', 'child_with_startup_s'), ('Supervisor', 'guard_s'),
                       ('Trabajador', 'worker_s'), ('Shader y batches', 'shader_batch_preparation_s'),
                       ('Preparación de geometría CPU', 'cpu_geometry_preparation_s'),
                       ('Suma de las 84 evaluaciones CPU', 'cpu_evaluation_sum_s'),
                       ('Suma de 84 uniforms/dibujos/readback', 'gpu_uniform_draw_readback_sum_s')]:
        lines.append(f'| {label} | {b["opengl"]["costs"][key]:.9f} | {b["vulkan"]["costs"][key]:.9f} |')
    lines += ['', 'Las filas representan alcances distintos y algunos costes están incluidos en otros: '
              'no deben sumarse todos como costes independientes. El ensayo alterna CPU/GPU y GPU/CPU; '
              'todos los pares y siete observaciones por caso/resolución se publican. Son dos ensayos '
              'individuales en una máquina compartida, con compilación, arranque y lectura explícitos. '
              'No establecen ventaja general ni eficiencia energética del sistema completo.', '',
              '![Campos P2 complejos auditados](../assets/13_gpu_p2_analytic_fields_v2.gif)', '',
              'El GIF se genera en CPU desde los campos existentes y auditorías. Muestra, por regla fija, '
              'la repetición cero a resolución 256 de cada caso/backend, y el máximo error de todas las '
              '21 muestras de cada caso. Escalas fijas, sin interpolar datos ni presentar actividad neuronal.', '',
              '**Alcance:** representación y superposición coherente manufacturada P2 en un framebuffer FP32 '
              'rasterizado. No comprueba propagación guiada, T96/Q4, modos, entrenamiento, una red funcional, '
              'RT, un dispositivo ni validación física. F1 sigue sin copia final recuperada; S16, '
              'malla reservada y dominio permanecen bloqueados. Tarea 1 abierta. JEV: fallback local explícito.', '']
    with doc.open('x', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print(json.dumps({k: {n: v for n, v in value.items() if n not in ('inputs_sha256', 'paired_observations', 'cases')}
                      for k, value in b.items()}))


if __name__ == '__main__':
    main()
