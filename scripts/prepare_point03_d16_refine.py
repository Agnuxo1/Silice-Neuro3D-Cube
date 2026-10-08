"""Freeze a differentiated worker by explicit changes before new fields."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    old = ROOT/'scripts/run_point03_d16_time.py'
    original = old.read_text(encoding='utf-8')
    control = json.loads((ROOT/'resultados/codex/point03_d16_worker_controls_20261008/report.json').read_text())
    assert hashlib.sha256(old.read_bytes()).hexdigest() == control['tested_worker_sha256']
    tree = ast.parse(original)
    definition = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'worker')
    source = ast.get_source_segment(original, definition)
    dispatcher = "(Pade6 if args.case == 'P6_32768' else Radau5)(M, B, .002/32768)"
    assert source.count(dispatcher) == 1
    source = source.replace(dispatcher, 'Radau5(M, B, .002/65536)')
    assert source.count('dt_m=.002/32768') == 1
    source = source.replace('dt_m=.002/32768', 'dt_m=.002/65536')
    template = ROOT/'scripts/point03_d16_refine_driver.py'
    body = template.read_text(encoding='utf-8')
    assert body.count('# WORKER_INSERTION') == 1
    body = body.replace('# WORKER_INSERTION', source)
    ast.parse(body)
    target = ROOT/'scripts/run_point03_d16_refine.py'
    with target.open('x', encoding='utf-8', newline='\n') as f:
        f.write(body)
    record = dict(generation_pass=True, original_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),
                  template_sha256=hashlib.sha256(template.read_bytes()).hexdigest(),
                  generated_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  changes=['Select only Radau5', 'step2mm/65536', 'new driver and retained-reference provenance'],
                  optical_propagation_executed=False)
    with (ROOT/'resultados/codex/point03_d16_refine_generation_20261008.json').open('x', encoding='utf-8') as f:
        json.dump(record, f, indent=2)
    print(record)


if __name__ == '__main__':
    main()
