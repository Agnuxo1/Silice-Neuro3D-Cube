"""Imprime las tablas de n_eff y diferencias a partir de resultados_radial2.json (solo lectura)."""
import os
import sys
import json

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "resultados_radial2.json"), encoding="utf-8"))

print("## C1 (fibra de salto 2 capas, a=6 um)")
print("Delta | V | modo | n_eff cerrada | n_eff solver E | n_eff solver P | |E-cer| | |P-cer| | |P-cer|/Delta")
for rec in d.get("C1", []):
    for l in ("l0", "l1"):
        m = rec["modes"][l]
        for i, c in enumerate(m["closed_neff"]):
            e = m["solver_E_neff"][i] if i < len(m["solver_E_neff"]) else None
            p = m["solver_P_neff"][i] if i < len(m["solver_P_neff"]) else None
            ae = m["abs_err_E"][i] if m.get("abs_err_E") else None
            ap = m["abs_err_P"][i] if m.get("abs_err_P") else None
            rp = m["abs_err_P_over_Delta"][i] if m.get("abs_err_P_over_Delta") else None
            fmt = lambda x, f="{:.10f}": "-" if x is None else f.format(x)
            print(f"{rec['Delta']} | {rec['V']:.3f} | LP{l[1]}{i+1} | {fmt(c)} | {fmt(e)} | {fmt(p)} | {fmt(ae,'{:.2e}')} | {fmt(ap,'{:.2e}')} | {fmt(rp,'{:.2e}')}")
print("criterios C1:", json.dumps(d.get("C1_criteria", {}), indent=1))

print("\n## C2 (camisa con trinchera, a=6 y 10 um; comparacion con radial_ecs nominal)")
print("a | t | dn | modo sel (Re g, Im g) | n_eff solver | loss solver | ECS Re g | ECS Im g | ECS loss | dRe rel | dloss | prim | nraices (validas)")
for r in d.get("C2", []):
    s = r.get("selected")
    e = r.get("ecs_nominal") or {}
    c = r.get("compare") or {}
    nvalid = sum(1 for x in r["roots"] if x["valid"])
    selstr = "-" if s is None else f"({s['g_re']:.3f}, {s['g_im']:.4f})"
    neff = "-" if s is None else f"{s['neff']:.9f}"
    lo = "-" if s is None else f"{s['loss_dB_cm']:.5f}"
    eg = e.get("gamma_re", "-")
    ei = e.get("gamma_im", "-")
    el = e.get("loss", "-")
    dre = c.get("dRe_rel", "-")
    dl = c.get("dloss_abs", "-")
    f = lambda x, fm: x if isinstance(x, str) else format(x, fm)
    print(f"{r['a_um']:.0f} | {r['t_um']:.0f} | {r['dn']} | {selstr} | {neff} | {lo} | {f(eg,'.3f')} | {f(ei,'.4f')} | {f(el,'.5f')} | {f(dre,'.2e')} | {f(dl,'.2e')} | {r['primary']} | {len(r['roots'])} ({nvalid})")
print("criterios C2:", json.dumps(d.get("C2_criteria", {}), indent=1))

print("\n## C3")
print(json.dumps(d.get("C3", {}), indent=1))
