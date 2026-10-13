"""Require concrete hash-linked upstream evidence before a one-shot test.

This is a procedural integrity gate on the same host, not a secure independent
custodian or digital signature. Arbitrary 'sealed_test_ready=true' is ignored.
"""
import hashlib
import json
from pathlib import Path
from common import sha

def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def validate_gates(manifest_path):
    manifest_path=Path(manifest_path).resolve()
    m=json.loads(manifest_path.read_text(encoding='utf-8'))
    if m.get('schema')!='femto1_release_evidence_v1':raise RuntimeError('Missing release evidence schema')
    required=['F0','F3','F4','F5','F6','geometry']
    records={}
    for name in required:
        entry=m.get('evidence',{}).get(name,{})
        if not entry.get('path') or not entry.get('sha256'):
            raise RuntimeError('Missing hashed upstream artifact '+name)
        path=Path(entry['path'])
        if not path.is_absolute() or not path.is_file() or sha(path)!=entry['sha256']:
            raise RuntimeError('Upstream artifact missing/changed '+name)
        records[name]=json.loads(path.read_text(encoding='utf-8'))
    f0,f3,f4,f5,f6=(records[k] for k in required[:5])
    if (f0.get('supplier_domain')!='femtoprint.ch' or not f0.get('reply_message_id')
        or not f0.get('written_rules_confirmed') or not f0.get('accepted_design_formats')):
        raise RuntimeError('Actual written supplier rules missing')
    if (f3.get('passed') is not True or f3.get('supplier_rules_confirmed') is not True
        or f3.get('error_count')!=0 or f3.get('F0_evidence_sha256')!=m['evidence']['F0']['sha256']):
        raise RuntimeError('Supplier-linked DRC has not passed')
    if f3.get('geometry_sha256')!=m['evidence']['geometry']['sha256']:
        raise RuntimeError('DRC checked another geometry')
    canonical=canonical_sha(records['geometry'])
    if (f4.get('roundtrip_identical') is not True or f4.get('geometry_canonical_sha256')!=canonical
        or f4.get('export_canonical_sha256')!=canonical):
        raise RuntimeError('Blender round-trip geometry differs')
    if (f5.get('passed') is not True or f5.get('geometry_canonical_sha256')!=canonical
        or f5.get('supplier_profile_confirmed') is not True or f5.get('polarizations_validated')!=2
        or f5.get('maximum_split_absolute_error',1)>.02
        or f5.get('maximum_integrated_interference_fraction',1)>.01):
        raise RuntimeError('Independent physical/spectral/polarization validation pending')
    if (f6.get('passed') is not True or f6.get('geometry_canonical_sha256')!=canonical
        or f6.get('all_required_error_sources_included') is not True
        or f6.get('minimum_polarization_mean_accuracy',0)<.85
        or f6.get('source_power_required_W',1)>.01
        or f6.get('unresolved_blockers',1)!=0):
        raise RuntimeError('Complete tolerance and power budget pending')
    return {'verified':True,'geometry_canonical_sha256':canonical,
            'release_manifest_sha256':sha(manifest_path),'scope':'procedural integrity; same host'}
