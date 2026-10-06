from pathlib import Path
import json
OUT=Path("D:\\PROJECTS\\Silice-Neuro3D-Cube-work-20261006\\resultados\\codex\\point03_sparse_20261006T223947Z")
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
data=read(OUT/'execution.json')
small=[read(row['path']) for row in data.get('small_reports',[])]
groups=[]
for row in data.get('case_reports',[]):
    reports=[read(p) for p in (OUT/row['case_id']).glob('chunk_*.json')]
    groups.append(dict(case_id=row['case_id'],comparison=row['comparison'],checkpoints=len(reports),
       propagation_s=sum(r['propagation_s'] for r in reports),
       solve_s=sum(f['solve_elapsed_s'] for r in reports for f in r['factor_metadata']['factors']),
       setup_s=sum(f['setup_elapsed_s'] for r in reports for f in r['factor_metadata']['factors']),
       peak_wset_bytes=max(r['memory']['peak_wset_bytes'] for r in reports)))
result={k:data.get(k) for k in ('status','equivalence_pass','operational_pass','elapsed_s','tracked_inputs_unchanged','frozen_unchanged','produced_unchanged','environment','scope')}
result.update(audit_manifest_sha256=data['audit_manifest_sha256'],tracked_file_count=len(data['tracked_sha256_before']),child_count=len(data['children']),max_child_s=max(r['elapsed_s'] for r in data['children']),case_results=groups,
small_results=[{'profile':r['small_profile'],'checks':r['checks'],'matrix_checks':r['matrix_checks'],'elapsed_s':r['elapsed_s'],'peak_wset_bytes':r['memory']['peak_wset_bytes']} for r in small])
with (OUT/'compact_result.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
(OUT/'summarize_orchestrator.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(result))
