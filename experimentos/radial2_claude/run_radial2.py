"""Driver de la Tarea C: C1 (cerradas LP, 2 capas), C2 (trinchera vs radial_ecs de GLASS-006a), C3 (convergencia).
Ejecutar: python -B run_radial2.py  (OMP_NUM_THREADS=1). Escribe resultados_radial2.json en esta carpeta.
Todo es modelo numerico. No se toca codigo de otras carpetas: solo se LEE el JSON de GLASS-006a y se registra su SHA-256."""
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
import sys
import json
import time
import hashlib
import warnings

sys.dont_write_bytecode = True
warnings.filterwarnings("ignore", category=RuntimeWarning)
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import radial2 as R

ECS_JSON = "D:/PROJECTS/.cognition/audit/silice-origin-main/experimentos/glass006a_claude/resultados.json"
ECS_SRC = "D:/PROJECTS/.cognition/audit/silice-origin-main/experimentos/glass005_claude/radial_ecs.py"
CONTRACT = os.path.join(HERE, "CONTRATO-RADIAL2.md")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


H0 = 0.005e-6  # paso nominal (m), fijado en el contrato
T0 = time.time()
OUT = {
    "task": "TAREA C radial2 (disparo + biseccion)",
    "contract_sha256": sha(CONTRACT),
    "ecs_json_sha256": sha(ECS_JSON),
    "ecs_src_sha256": sha(ECS_SRC),
    "h0_m": H0,
    "r0_m": R.R0_DEFAULT,
    "constants": dict(lam_m=R.LAM, n0=R.N0, k0=R.K0, b0=R.B0),
}


def log(msg):
    print(f"[{time.time() - T0:7.1f}s] {msg}", flush=True)


# ---------------------------------------------------------------- C1
def c1_case(Delta, a=6e-6):
    n1, n2 = R.N0 + Delta, R.N0
    rec = {"Delta": Delta, "a_um": a * 1e6, "V": float(a * R.K0 * np.sqrt(n1 ** 2 - n2 ** 2)), "modes": {}}
    for l in (0, 1):
        closed = sorted(R.closed_roots(a, n1, n2, 0 if l == 0 else 1), reverse=True)
        xsE = np.linspace(R.N0 + 1e-9, n1 - 1e-9, 400)
        rE = sorted(R.real_roots(xsE, [(0.0, a, Delta)], l, "E", H0), reverse=True)
        gsP = np.linspace(1e-9, R.K0 * Delta * (1 - 1e-9), 400)
        rP = sorted([R.N0 + g / R.K0 for g in R.real_roots(gsP, [(0.0, a, Delta)], l, "P", H0)], reverse=True)
        entry = {"closed_neff": closed, "solver_E_neff": rE, "solver_P_neff": rP,
                 "n_closed": len(closed), "n_E": len(rE), "n_P": len(rP)}
        if closed:
            cE = [abs(x - y) for x, y in zip(rE, closed)] if len(rE) == len(closed) else None
            cP = [abs(x - y) for x, y in zip(rP, closed)] if len(rP) == len(closed) else None
            entry["abs_err_E"] = cE
            entry["abs_err_P"] = cP
            entry["abs_err_P_over_Delta"] = [x / Delta for x in cP] if cP else None
        rec["modes"][f"l{l}"] = entry
    log(f"C1 Delta={Delta}: " + str({k: (v['n_closed'], v['n_E'], v['n_P']) for k, v in rec['modes'].items()}))
    return rec


# ---------------------------------------------------------------- C2
def classify(root_list, layers, a, dn, h):
    res = []
    for o in root_list:
        g = o["g"]
        core = R.core_fraction(g, layers, 0, a, h)
        reasons = []
        if not (np.isfinite(o["rF"]) and o["rF"] < 1e-7):
            reasons.append("residuo_no_convergido")
        if not (g.imag >= 0):
            reasons.append("Im_g_negativa_crecimiento")
        if not (R.K0 * dn < g.real < 0):
            reasons.append("fuera_de_ventana_barrera")
        if not (core >= 0.3):
            reasons.append("fraccion_nucleo_menor_0.3")
        res.append(dict(g_re=float(g.real), g_im=float(g.imag),
                        neff=float(R.N0 + g.real / R.K0),
                        neff_im=float(g.imag / R.K0), rF=o["rF"], core_frac=core,
                        loss_dB_cm=R.loss_dB_cm(g), valid=(len(reasons) == 0), reasons=reasons))
    return res


def c2_case(a, t, dn, h=H0, r0=R.R0_DEFAULT):
    layers = [(0.0, a, 0.0), (a, a + t, dn)]
    out, info = R.quasibound_roots(layers, a, 0, h, dn, r0=r0)
    cl = classify(out, layers, a, dn, h)
    valid = [c for c in cl if c["valid"]]
    sel = max(valid, key=lambda c: c["g_re"]) if valid else None
    return dict(a_um=a * 1e6, t_um=t * 1e6, dn=dn, h_m=h, r0_m=r0, search=info, roots=cl, selected=sel)


def ecs_lookup(ecs, a, t, dn):
    for c in ecs["cases"]:
        if abs(c["a_um"] - a * 1e6) < 1e-9 and abs(c["t_um"] - t * 1e6) < 1e-9 and abs(c["dn"] - dn) < 1e-12:
            nom = c["configs"].get("nom", {})
            if "gamma_re" in nom:
                return dict(gamma_re=nom["gamma_re"], gamma_im=nom["gamma_im"], loss=nom["loss_dB_per_cm"],
                            core_frac_ecs_def=nom["core_frac"])
            return dict(note=nom.get("note", "sin dato"))
    return None


def compare(sel, ecs_nom):
    if sel is None or ecs_nom is None or "gamma_re" not in ecs_nom:
        return dict(status="sin_comparacion")
    gre_s, gim_s = sel["g_re"], sel["g_im"]
    gre_e, gim_e = ecs_nom["gamma_re"], ecs_nom["gamma_im"]
    d_re_rel = abs(gre_s - gre_e) / abs(gre_e)
    d_loss = abs(sel["loss_dB_cm"] - ecs_nom["loss"])
    loss_tol = max(0.10 * abs(ecs_nom["loss"]), 0.005)
    d_neff = (gre_s - gre_e) / R.K0
    return dict(
        dRe_rel=d_re_rel, dRe_g=gre_s - gre_e, dIm_g=gim_s - gim_e,
        dneff_abs=d_neff,
        loss_solver=sel["loss_dB_cm"], loss_ecs=ecs_nom["loss"],
        dloss_abs=d_loss, loss_tol=loss_tol,
        pass_C2_1=bool(d_re_rel <= 0.005), pass_C2_2=bool(d_loss <= loss_tol),
    )


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    which = sys.argv[1:] or ["C1", "C2", "C3"]
    ecs = json.load(open(ECS_JSON, encoding="utf-8"))

    if "C1" in which:
        log("C1 inicio")
        C1 = [c1_case(D) for D in (0.003, 0.005, 0.010)]
        OUT["C1"] = C1
        # criterios C1
        crit = {}
        ok11, ok12, ok13, ok14 = [], [], [], []
        for rec in C1:
            for l in ("l0", "l1"):
                m = rec["modes"][l]
                if m["n_closed"] == 0:
                    ok13.append(m["n_E"] == 0 and m["n_P"] == 0)
                    continue
                ok14.append(m["n_closed"] == m["n_E"] == m["n_P"])
                if m.get("abs_err_E"):
                    ok11.append(m["abs_err_E"][0] <= 1e-8)
                if m.get("abs_err_P_over_Delta"):
                    ok12.append(m["abs_err_P_over_Delta"][0] <= 0.01)
        crit["C1.1_E_maxroot_err_le_1e-8"] = dict(pass_all=bool(all(ok11)), n=len(ok11))
        crit["C1.2_P_maxroot_err_le_0.01_Delta"] = dict(pass_all=bool(all(ok12)), n=len(ok12))
        crit["C1.3_no_LP11_below_cutoff"] = dict(pass_all=bool(all(ok13)), n=len(ok13))
        crit["C1.4_root_count_matches_closed"] = dict(pass_all=bool(all(ok14)), n=len(ok14))
        OUT["C1_criteria"] = crit
        log("C1 criterios " + json.dumps({k: v["pass_all"] for k, v in crit.items()}))

    if "C2" in which:
        log("C2 inicio")
        C2_all = []
        for a in (6e-6, 10e-6):
            for dn in (-0.003, -0.005):
                for t in (3e-6, 6e-6, 9e-6, 12e-6, 18e-6):
                    rec = c2_case(a, t, dn)
                    ecs_nom = ecs_lookup(ecs, a, t, dn)
                    rec["ecs_nominal"] = ecs_nom
                    rec["compare"] = compare(rec["selected"], ecs_nom)
                    primary = (abs(a - 6e-6) < 1e-12) and (abs(t - 6e-6) < 1e-12 or abs(t - 12e-6) < 1e-12)
                    rec["primary"] = bool(primary)
                    C2_all.append(rec)
                    log(f"C2 a={a*1e6:.0f} t={t*1e6:.0f} dn={dn}: nroots={len(rec['roots'])} "
                        f"sel={None if rec['selected'] is None else (round(rec['selected']['g_re'],3), round(rec['selected']['g_im'],4))} "
                        f"ecs={None if ecs_nom is None else ecs_nom.get('gamma_re', ecs_nom)}")
        OUT["C2"] = C2_all
        prim = [r for r in C2_all if r["primary"]]
        OUT["C2_criteria"] = dict(
            C2_1_all_primary=bool(all(r["compare"].get("pass_C2_1", False) for r in prim)),
            C2_2_all_primary=bool(all(r["compare"].get("pass_C2_2", False) for r in prim)),
            C2_3_all_primary_valid=bool(all(r["selected"] is not None for r in prim)),
            n_primary=len(prim),
        )
        log("C2 criterios " + json.dumps(OUT["C2_criteria"]))

    if "C3" in which:
        log("C3 inicio")
        C3 = {}
        # C3.1/C3.2 paso: caso C2 primario a=6 t=6 dn=-0.003 y C1 Delta=0.010 (LP01, modelos P y E)
        def g_sel(h, r0=R.R0_DEFAULT):
            rec = c2_case(6e-6, 6e-6, -0.003, h=h, r0=r0)
            return rec["selected"]["g_re"], rec["selected"]["g_im"]

        hs = [H0, H0 / 2, H0 / 4]
        gvals = [g_sel(h) for h in hs]
        d1 = complex(gvals[0][0] - gvals[1][0], gvals[0][1] - gvals[1][1])
        d2 = complex(gvals[1][0] - gvals[2][0], gvals[1][1] - gvals[2][1])
        p_obs = float(np.log2(abs(d1) / abs(d2))) if abs(d2) > 0 else None
        rel_re_12 = abs(gvals[1][0] - gvals[2][0]) / abs(gvals[2][0])
        im_tol = 1e-3 * max(abs(gvals[2][1]), 1.0)
        rec_r0 = g_sel(H0, r0=0.01e-6)
        dr0 = abs(rec_r0[0] - gvals[0][0]) / abs(gvals[0][0])
        C3["C2_trench_a6_t6_dn-0.003"] = dict(
            h=hs, g_re=[v[0] for v in gvals], g_im=[v[1] for v in gvals],
            order_p=p_obs, rel_dRe_h2_h4=rel_re_12, dIm_h2_h4=abs(gvals[1][1] - gvals[2][1]), im_tol=im_tol,
            r0_test_rel_dRe=dr0,
            pass_C3_1=bool(rel_re_12 <= 1e-6 and (abs(gvals[1][1] - gvals[2][1]) <= im_tol or abs(gvals[2][1]) < 1.0)),
            pass_C3_2=bool((p_obs is not None and p_obs >= 3.5) or abs(d2) < 1e-9 * abs(gvals[2][0])),
            pass_C3_3=bool(dr0 <= 1e-9),
        )
        log("C3 trench " + json.dumps({k: C3["C2_trench_a6_t6_dn-0.003"][k] for k in ("order_p", "rel_dRe_h2_h4", "r0_test_rel_dRe")}))

        # C1 Delta=0.010 LP01 (modelo P y E), biseccion en h
        Delta, a = 0.010, 6e-6
        c1h = {}
        for model in ("E", "P"):
            vals = []
            for h in hs:
                gs = np.linspace(1e-9, R.K0 * Delta * (1 - 1e-9), 400) if model == "P" else np.linspace(R.N0 + 1e-9, R.N0 + Delta - 1e-9, 400)
                rts = R.real_roots(gs, [(0.0, a, Delta)], 0, model, h)
                vals.append(max(rts) if rts else None)
            if model == "P":
                vals = [None if v is None else R.N0 + v / R.K0 for v in vals]
            d1 = abs(vals[0] - vals[1]); d2 = abs(vals[1] - vals[2])
            p_obs = float(np.log2(d1 / d2)) if d2 > 0 else None
            c1h[model] = dict(h=hs, neff_LP01=vals, abs_d_h_h2=d1, abs_d_h2_h4=d2, order_p=p_obs,
                              pass_C3_1=bool(d2 <= 1e-6 * vals[2] or d2 < 1e-12), pass_C3_2=bool((p_obs or 0) >= 3.5 or d2 < 1e-12))
            log(f"C3 C1 Delta=0.010 modelo {model}: neff={vals} orden={p_obs}")
        C3["C1_step_Delta0.010_LP01"] = c1h
        OUT["C3"] = C3

    OUT["runtime_s"] = round(time.time() - T0, 1)
    dst = os.path.join(HERE, "resultados_radial2.json")
    json.dump(OUT, open(dst, "w", encoding="utf-8"), indent=1, default=lambda o: float(o) if isinstance(o, (np.floating,)) else (bool(o) if isinstance(o, np.bool_) else str(o)))
    log(f"escrito {dst}")
