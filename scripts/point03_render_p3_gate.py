"""Require complete audited calibration, including retained negative routes."""
import hashlib,json
from point03_render_pipeline_reference import MODES
from point03_render_reference import RESOLUTIONS
USED=('uniform_none','uniform_add1','uniform_add2','attribute_none',
      'bary_analytic_none','bary_analytic_add1','quadratic_analytic_none')

def validate_pipeline(a,backend):
    if a.get('integrity_pass') is not True or a.get('strict_metric_agreement_pass') is not True or a.get('backend')!=backend:
        raise ValueError('P1 integrity/backend mismatch')
    if a.get('marker_frames')!=30 or a.get('accuracy_pass') is not False:
        raise ValueError('P1 full retained result mismatch')
    for name in ('physical_validation','network_validated','p2_field_validated','point03_closed','general_speedup_claim'):
        if a.get(name) is not False:raise ValueError('P1 scope mismatch')
    expected={(m,n) for m in MODES for n in RESOLUTIONS};seen=set()
    rows=a.get('rows',[])
    if len(rows)!=30:raise ValueError('incomplete P1 rows')
    for row in rows:
        key=(row.get('marker'),row.get('resolution'))
        if key not in expected or key in seen:raise ValueError('P1 duplicate/unknown mark')
        seen.add(key)
        if key[0] in USED:
            if row.get('accuracy_pass') is not True or not 0<=row.get('max_channel_error',float('inf'))<=1e-6 or not 0<=row.get('outside_max',float('inf'))<=1e-7:
                raise ValueError('analytic path did not pass')

def require_pipeline(root,profile):
    hashes={}
    if set(profile['pipeline_audits'])!={'OPENGL','VULKAN'}:raise ValueError('both registered calibrations required')
    for backend,item in profile['pipeline_audits'].items():
        path=(root/item['path']).resolve();path.relative_to(root/'resultados/codex')
        b=path.read_bytes();digest=hashlib.sha256(b).hexdigest()
        if digest!=item['sha256']:raise ValueError('P1 audit changed')
        validate_pipeline(json.loads(b),backend);hashes[backend]=digest
    return hashes
