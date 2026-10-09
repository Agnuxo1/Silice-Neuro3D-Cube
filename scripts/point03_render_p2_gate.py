"""Fixed prerequisite and positive ns checks; does not import GPU or read fields."""
import hashlib
import json


def validate_p0(audit):
    required = ('integrity_pass', 'accuracy_pass', 'layout_prediction_pass', 'old_export_rejected')
    if any(audit.get(k) is not True for k in required):
        raise ValueError('P0 calibration did not pass all gates')
    if type(audit.get('marker_frames')) is not int or audit['marker_frames'] != 6:
        raise ValueError('P0 marker set differs')
    if any(audit.get(k) is not False for k in
           ('physical_validation', 'p2_field_validated', 'network_validated', 'point03_closed')):
        raise ValueError('P0 scope differs')


def require_p0(root, profile):
    path=(root/profile['p0_local_audit_path']).resolve()
    path.relative_to(root/'resultados/codex')
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=profile['p0_local_audit_sha256']:
        raise ValueError('frozen P0 audit changed')
    validate_p0(json.loads(data))
    return profile['p0_local_audit_sha256']


def ns_seconds(value):
    if type(value) is not int or not 0 < value <= 120_000_000_000:
        raise ValueError('invalid or nonpositive pair duration')
    return value/1e9
