"""Reuse fixed controls on registered coarse geometries, without propagation."""
import argparse
import ast
import inspect
from pathlib import Path
from run_point03_exponential import ROOT,sha,write


def run(kind,mesh_folder,out):
    import check_point03_p4f as detector
    import check_point03_p4g as damping
    assert mesh_folder.name in ('point03_p5a_mesh_coarse_20261008','point03_p5a_mesh_mid_20261008') and not out.exists()
    base=detector if kind=='detector' else damping
    function=ast.parse(inspect.getsource(base.run)).body[0]
    replacement=mesh_folder.relative_to(ROOT).as_posix()
    class Change(ast.NodeTransformer):
        def visit_Call(self,node):
            for keyword in node.keywords:
                if keyword.arg=='old_unsplit_difference_bound_m_inverse':
                    keyword.value=ast.IfExp(test=ast.Compare(left=ast.Attribute(value=ast.Name(id='D',ctx=ast.Load()),attr='shape',ctx=ast.Load()),ops=[ast.Eq()],comparators=[ast.Attribute(value=ast.Name(id='old',ctx=ast.Load()),attr='shape',ctx=ast.Load())]),body=keyword.value,orelse=ast.Constant(None))
            return self.generic_visit(node)
        def visit_Constant(self,node):
            table={'resultados/codex/point03_p4c_mesh_20261008':replacement,'report_recovered.json':'report.json','integrity_pass':'controls_pass','artifact_sha256':'hashes'}
            if isinstance(node.value,str) and node.value in table:return ast.copy_location(ast.Constant(table[node.value]),node)
            return node
    function=Change().visit(function)
    folder=ROOT/'resultados/codex/point03_fem_control_sources_20261008';folder.mkdir(exist_ok=True)
    path=folder/(mesh_folder.name+'_'+kind+'.txt');assert not path.exists()
    path.write_text(ast.unparse(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])))+'\n',encoding='utf-8')
    namespace=base.__dict__.copy();namespace['__file__']=str(path)
    exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),namespace)
    digest=sha(path);namespace['run'](out)
    write(out/'adaptation_record.json',dict(kind=kind,geometry_folder=str(mesh_folder),source_path=str(path),source_sha256=digest,contract_sha256=sha(ROOT/'Docs/POINT-03-P5B-CONTROLS-CONTRACT.md'),original_control_sha256=sha(Path(base.__file__)),no_propagation=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--kind',choices=('detector','damping'),required=True);parser.add_argument('--mesh',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();run(args.kind,args.mesh.resolve(),args.out.resolve())
