"""Generate pre-registered coarse conforming geometry, with no propagation."""
import argparse
import ast
import inspect
import json
from pathlib import Path
import check_point03_p4c as base
from run_point03_exponential import ROOT,sha,write


def run(h,out):
    assert h in (.546875,.4375) and not out.exists()
    function=ast.parse(inspect.getsource(base.check)).body[0]
    expression=f'{h:.9f} + {3*h:.9f} * Min(1, Max(0, (Sqrt(x*x+y*y)-15)/10))'
    class Change(ast.NodeTransformer):
        def visit_Constant(self,node):
            if node.value=='0.35 + 1.05 * Min(1, Max(0, (Sqrt(x*x+y*y)-15)/10))':return ast.copy_location(ast.Constant(expression),node)
            return node
        def visit_Compare(self,node):
            if 'area_clad / area' in ast.unparse(node):node.comparators=[ast.Constant(5e-5)]
            return self.generic_visit(node)
        def visit_Call(self,node):
            for keyword in node.keywords:
                if keyword.arg in ('dofs','elements'):keyword.value=ast.Call(func=ast.Name(id='int',ctx=ast.Load()),args=[keyword.value],keywords=[])
            return self.generic_visit(node)
    changed=Change().visit(function)
    folder=ROOT/'resultados/codex/point03_mesh_sources_20261008';folder.mkdir(exist_ok=True)
    path=folder/('h'+str(h).replace('.','_')+'.txt');assert not path.exists()
    path.write_text(ast.unparse(ast.fix_missing_locations(ast.Module(body=[changed],type_ignores=[])))+'\n',encoding='utf-8')
    namespace=base.__dict__.copy();exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),namespace)
    code_hash=sha(path);status=namespace['check'](out)
    write(out/'generation_record.json',dict(h_local_um=h,h_background_um=4*h,source_path=str(path),source_sha256=code_hash,original_generator_sha256=sha(ROOT/'scripts/check_point03_p4c.py'),contract_sha256=sha(ROOT/'Docs/POINT-03-P5A-GEOMETRY-CONTRACT.md'),status_code=status,no_propagation=True))
    return status


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--h',type=float,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();raise SystemExit(run(args.h,args.out.resolve()))
