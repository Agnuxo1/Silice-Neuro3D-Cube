"""Demonstrate false M2 approval blocks F1 before any optical worker."""
from pathlib import Path
from unittest.mock import patch
import run_point03_d16_fine_time as target


if __name__ == '__main__':
    out = target.ROOT/'resultados/codex/point03_d16_fine_false_gate_controls_20261009'
    prerequisite = target.ROOT/'resultados/codex/point03_d16_mid_recovery_20261009/local_integrity_audit.json'
    real_read = target.read

    def false_gate(path):
        if Path(path) == prerequisite:
            return dict(integrity_pass=True, temporal_precision_pass=False,
                        purpose='Manufactured prerequisite software control only')
        return real_read(path)

    with patch.object(target, 'read', side_effect=false_gate), \
         patch.object(target.subprocess, 'run', side_effect=AssertionError('Optical worker must never launch')) as launches:
        code = target.run(out)
    e = target.read(out/'execution.json')
    assert code == 1 and e['status'] == 'failed' and e['children'] == []
    assert e['error_type'] == 'AssertionError' and launches.call_count == 0
    assert not (out/'manifest.json').exists() and not list(out.rglob('*.npz'))
    record = dict(controls_pass=True, false_temporal_prerequisite_rejected=True,
                  optical_workers_launched=0, optical_fields_created=0,
                  prerequisite_mocked_for_software_control_only=True,
                  source_sha256=target.sha(Path(target.__file__)),
                  execution_sha256=target.sha(out/'execution.json'), point03_closed=False)
    target.write(target.ROOT/'resultados/codex/point03_d16_fine_gate_controls_20261009.json', record)
    print(record)
