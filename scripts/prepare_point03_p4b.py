"""Generate a registered aligned hierarchy without running numerical cases."""
import ast
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scripts/diagnose_point03_p4a.py'
tree=ast.parse(source.read_text(encoding='utf-8'))
replacements={400:127,500:255,640:511,767:1023,401:128,501:256,641:512,768:1024}


class Change(ast.NodeTransformer):
    def visit_For(self,node):
        if isinstance(node.target,ast.Name) and node.target.id=='n' and isinstance(node.iter,ast.Tuple):
            node.iter=ast.Tuple(elts=[ast.Constant(value) for value in (127,255,511,1023)],ctx=ast.Load())
        return self.generic_visit(node)

    def visit_Constant(self,node):
        if isinstance(node.value,int) and node.value in replacements:
            return ast.copy_location(ast.Constant(replacements[node.value]),node)
        if node.value=='Docs/POINT-03-P4A-CONTRACT.md':
            return ast.copy_location(ast.Constant('Docs/POINT-03-P4B-CONTRACT.md'),node)
        return node


changed=Change().visit(tree)
marker=next(node for node in ast.walk(changed) if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and isinstance(node.value.func.value,ast.Name) and node.value.func.value.id=='rows' and node.value.func.attr=='append')
extra=ast.parse('''
rawfolder=out.parent/(out.stem+'_raw')
rawfolder.mkdir(exist_ok=True)
rawpath=rawfolder/f'n{n}_{name}.npz'
assert not rawpath.exists()
np.savez(rawpath,axis=x,initial=initial,field=final,diagonal=diagonal,off=off,eigenvalues=values[[0,n//2,n-1]],eigenvectors=vectors[:,[0,n//2,n-1]],mass_diagonal=md,mass_off=mo,generalized=generalized)
rows[-1]['raw_path']=str(rawpath)
rows[-1]['raw_sha256']=hashlib.sha256(rawpath.read_bytes()).hexdigest()
''').body
loop=next(node for node in ast.walk(changed) if isinstance(node,ast.For) and marker in node.body)
position=loop.body.index(marker)+1
loop.body[position:position]=extra
target=ROOT/'scripts/diagnose_point03_p4b_generated.py'
assert not target.exists()
target.write_text(ast.unparse(ast.fix_missing_locations(changed))+'\n',encoding='utf-8')
print('Aligned hierarchy source generated; no numerical experiment run.')
