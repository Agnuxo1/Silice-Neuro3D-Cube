"""One (dn, t, family) job for CONTRATO-VECTORIAL-GEOMETRIA: writes trinchera_jobs/<key>.json."""
import json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import trinchera_vectorial as T  # noqa: E402

dn, t, name = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
res = T.solve(dn, t, name)
d = HERE / "trinchera_jobs"
d.mkdir(exist_ok=True)
(d / f"dn{dn:g}_t{t:g}_{name}.json").write_text(json.dumps({"dn": dn, "t_um": t, "family": name, "result": res},
                                                           ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"dn": dn, "t": t, "family": name, "result": res}, ensure_ascii=False))
