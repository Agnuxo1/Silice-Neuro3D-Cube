"""Manufactured controls only; imports neither Blender nor a GPU backend."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import numpy as np
from point03_render_reference import TRIANGLE, NODAL, shapes, evaluate, validate, metrics


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', type=Path, required=True)
    a = p.parse_args(); checks = []
    b = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1],
                  [.5, .5, 0], [0, .5, .5], [.5, 0, .5]])
    assert np.max(abs(shapes(b)-np.eye(6))) < 1e-14
    checks.append('six nodal identities')
    rng = np.random.default_rng(901); bary = rng.dirichlet(np.ones(3), 37)
    assert np.max(abs(shapes(bary).sum(-1)-1)) < 1e-14
    checks.append('partition of unity')
    def polynomial(x, y): return 1+2*x-3*y+4*x*y+5*x*x-2*y*y+1j*(x+y*y)
    nodes = np.r_[TRIANGLE, [(TRIANGLE[0]+TRIANGLE[1])/2,
                           (TRIANGLE[1]+TRIANGLE[2])/2,
                           (TRIANGLE[2]+TRIANGLE[0])/2]]
    values = polynomial(nodes[:, 0], nodes[:, 1]); xy = bary @ TRIANGLE
    assert np.max(abs(shapes(bary) @ values-polynomial(xy[:, 0], xy[:, 1]))) < 1e-14
    checks.append('complex quadratic reproduction')
    single, inside, mask = evaluate('single', 64)
    base = float(np.sum(abs(single[mask])**2)*(2/64)**2)
    for case, factor in [('constructive', 4), ('destructive', 0), ('quarter', 2)]:
        field, _, m = evaluate(case, 64)
        assert abs(float(np.sum(abs(field[m])**2)*(2/64)**2)-factor*base) < 1e-14
        assert metrics(field, field, inside, m, base, (2/64)**2)['accuracy_pass']
        checks.append('coherent '+case)
    bad = [('shape', TRIANGLE[:2], NODAL, 64),
           ('nan', TRIANGLE, np.r_[np.nan, NODAL[1:]], 64),
           ('inf', TRIANGLE*np.inf, NODAL, 64),
           ('resolution', TRIANGLE, NODAL, 63),
           ('degenerate', np.zeros((3, 2)), NODAL, 64)]
    for name, t, v, n in bad:
        try: validate(t, v, n)
        except ValueError: checks.append('reject '+name)
        else: raise AssertionError('accepted '+name)
    altered = single.copy(); altered[inside] *= np.exp(.1j)
    assert not metrics(altered, single, inside, mask, base, (2/64)**2)['accuracy_pass']
    checks.append('reject phase alteration')
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                  control_pass=True, checks=checks, new_gpu_execution=False,
                  new_t96_field=False, physical_validation=False,
                  sources_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in [Path(__file__), Path(__file__).with_name('point03_render_reference.py')]})
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open('x', encoding='utf-8') as f: json.dump(report, f, indent=2)
    print(json.dumps({'controls':len(checks), 'pass':True, 'new_gpu_execution':False}))


if __name__ == '__main__': main()
