"""Driver r2 de la Tarea C (ronda 2; ver CONTRATO-RADIAL2-r2.md).

C1: identico a ronda 1 (reutiliza run_radial2.c1_case y el mismo criterio).
C2 primario (a=6 um, t in {6,12}, dn in {-0,003;-0,005}):
    t=6 um por escaneo grueso de ronda 1; t=7..12 um por continuacion en t (semilla = raiz del paso anterior,
    solo resultados del propio solver). En cada paso se registra el escaneo grueso como comprobacion.
C3: convergencia en paso (h0, h0/2, h0/4) y en r0 sobre la rama de continuacion a t=12 (dn=-0,003),
    y C3 de ronda 1 para C1 Delta=0,010.
Solo CPU, OMP_NUM_THREADS=1. Ejecutar: python -B run_radial2_r2.py
Escribe resultados_radial2.json (r2). Los criterios pass se calculan aqui, no a mano.
Todo es modelo numerico; no se lee ni se copia codigo de src/silice/."""
import os
import sys
import json
import time
import hashlib
import warnings

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
warnings.filterwarnings("ignore", category=RuntimeWarning)
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import radial2 as R
import run_radial2 as R1

CONTRACT_R2 = os.path.join(HERE, "CONTRATO-RADIAL2-r2.md")
CONTRACT_R1 = os.path.join(HERE, "CONTRATO-RADIAL2.md")
DST = os.path.join(HERE, "resultados_radial2.json")
H0 = 0.005e-6
A = 6e-6
T0 = time.time()


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def log(msg):
    print(f"[{time.time() - T0:7.1f}s] {msg}", flush=True)


def _ser(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, (complex, np.complexfloating)):
        return {"re": float(np.real(o)), "im": float(np.imag(o))}
    return str(o)


OUT = {
    "task": "TAREA C radial2, ronda 2 (campana primaria con seguimiento en t)",
    "contract_r2_sha256": sha(CONTRACT_R2),
    "contract_r1_sha256": sha(CONTRACT_R1),
    "ecs_json_sha256": sha(R1.ECS_JSON),
    "ecs_src_sha256": sha(R1.ECS_SRC),
    "h0_m": H0,
    "r0_m": R.R0_DEFAULT,
    "constants": dict(lam_m=R.LAM, n0=R.N0, k0=R.K0, b0=R.B0),
    "method_note": ("Ronda 2: C2 primario usa escaneo grueso de ronda 1 solo en t=6 um y "
                    "continuacion en t (paso 1 um) para t=7..12 um. Umbrales identicos a ronda 1."),
    "not_run_r2": "casos secundarios a=6 (t=3,9,18) y a=10 um: no repetidos en r2; ver resultados_radial2_ronda1_smoke.json",
    "stage_status": {},
}


def save():
    OUT["runtime_s"] = round(time.time() - T0, 1)
    with open(DST, "w", encoding="utf-8") as fh:
        json.dump(OUT, fh, indent=1, default=_ser)


def layers_t(t, dn):
    return [(0.0, A, 0.0), (A, A + t, dn)]


def fval(g, L, h, r0):
    with np.errstate(all="ignore"):
        return R.Fc(np.array([g]), L, 0, h, r0=r0)[0]


def sec_root(g0, g1, L, h, r0, maxit=40):
    """Secante compleja sobre F(g) del modelo paraxial con salida radiante."""
    F0 = fval(g0, L, h, r0)
    F1 = fval(g1, L, h, r0)
    for _ in range(maxit):
        den = F1 - F0
        if (not np.isfinite(den)) or den == 0:
            return g1, False
        g2 = g1 - F1 * (g1 - g0) / den
        if not np.isfinite(g2):
            return g1, False
        g0, F0 = g1, F1
        g1 = g2
        F1 = fval(g1, L, h, r0)
        if abs(g1 - g0) < 1e-11 * abs(g1) + 1e-9:
            return g1, True
    return g1, False


def resid(g, L, h, r0):
    with np.errstate(all="ignore"):
        _, F, psi, dpsi, f, fp = R.mismatch(np.array([g]), L, 0, "P", h, r0=r0, real_bound=False)
        return float(abs(F[0]) / (abs(dpsi[0] / psi[0]) + abs(fp[0] / f[0])))


def track(dn, h=H0, r0=R.R0_DEFAULT, g_start=None, coarse_checks=True, t_max_um=12):
    """Rama de la raiz: t=6 por escaneo grueso (si g_start es None), luego continuacion en t (paso 1 um)."""
    steps = []
    L6 = layers_t(6e-6, dn)
    if g_start is None:
        out, info = R.quasibound_roots(L6, A, 0, h, dn, r0=r0)
        cl = R1.classify(out, L6, A, dn, h)
        val = [c for c in cl if c["valid"]]
        sel = max(val, key=lambda c: c["g_re"]) if val else None
        steps.append(dict(t_um=6.0, method="escaneo_grueso_ronda1", search=info, roots=cl,
                          selected=sel, rF_root=(sel["rF"] if sel else None)))
        if sel is None:
            return steps
        gs = [(6.0, complex(sel["g_re"], sel["g_im"]))]
    else:
        gs = [(6.0, complex(g_start))]
        steps.append(dict(t_um=6.0, method="semilla_del_solver_h0", seed=complex(g_start)))
    for tu in range(7, t_max_um + 1):
        t = tu * 1e-6
        L = layers_t(t, dn)
        if len(gs) >= 2:
            (t1, g1), (t2, g2) = gs[-2], gs[-1]
            gp = g2 + (g2 - g1) * (tu - t2) / (t2 - t1)
        else:
            gp = gs[-1][1]
        cands = []
        for off in (0.3, 0.3j):
            gr, conv = sec_root(gp, gp + off, L, h, r0)
            if conv and np.isfinite(gr):
                rF = resid(gr, L, h, r0)
                if np.isfinite(rF) and rF < 1e-7:
                    cands.append((abs(gr - gp), gr, rF))
        entry = dict(t_um=float(tu), method="continuacion_en_t", seed=complex(gp), n_conv=len(cands))
        if not cands:
            entry.update(root=None, selected=None, roots=[])
            steps.append(entry)
            log(f"  dn={dn} t={tu}: sin raiz por continuacion")
            break
        cands.sort(key=lambda c: c[0])
        _, gr, rF = cands[0]
        cl = R1.classify([dict(g=gr, rF=rF)], L, A, dn, h)
        c0 = cl[0]
        entry.update(root=dict(g_re=c0["g_re"], g_im=c0["g_im"], rF=rF, loss_dB_cm=c0["loss_dB_cm"],
                               core_frac=c0["core_frac"], valid=c0["valid"], reasons=c0["reasons"]),
                     selected=(c0 if c0["valid"] else None), roots=cl)
        if coarse_checks:
            out, info = R.quasibound_roots(L, A, 0, h, dn, r0=r0)
            cc = R1.classify(out, L, A, dn, h)
            same = [c for c in cc if abs(complex(c["g_re"], c["g_im"]) - gr) <= 0.02 * abs(gr) + 1.0]
            entry["coarse_check"] = dict(n_roots_coarse=len(cc), search=info,
                                         encontrado_por_malla_gruesa=bool(len(same) > 0))
        steps.append(entry)
        gs.append((float(tu), gr))
        log(f"  dn={dn} t={tu}: g={gr.real:.4f}{gr.imag:+.4f}j valid={c0['valid']} rF={rF:.2e} "
            f"loss={c0['loss_dB_cm']:.4f}")
    return steps


def c2_primary_case(steps, t_um, dn):
    """Caso primario (a=6, t, dn) a partir de la rama."""
    t = t_um * 1e-6
    st = [s for s in steps if abs(s["t_um"] - t_um) < 1e-9]
    if not st:
        return dict(a_um=6.0, t_um=t_um, dn=dn, selected=None, reason="no_alcanzado")
    s = st[0]
    sel = s.get("selected")
    ecs_nom = R1.ecs_lookup(R1.json.load(open(R1.ECS_JSON, encoding="utf-8")), A, t, dn)
    return dict(a_um=6.0, t_um=t_um, dn=dn, selected=sel, roots=s.get("roots", []),
                method=s.get("method"), ecs_nominal=ecs_nom,
                compare=R1.compare(sel, ecs_nom), primary=True)


if __name__ == "__main__":
    which = sys.argv[1:] or ["C1", "C2", "C3"]
    ecs_all = R1.json.load(open(R1.ECS_JSON, encoding="utf-8"))

    # ------------------------------------------------------------ C1 (identico a ronda 1)
    if "C1" in which:
        log("C1 inicio")
        C1 = [R1.c1_case(D) for D in (0.003, 0.005, 0.010)]
        OUT["C1"] = C1
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
        OUT["stage_status"]["C1"] = "done"
        save()
        log("C1 criterios " + json.dumps({k: v["pass_all"] for k, v in crit.items()}))

    # ------------------------------------------------------------ C2 primario
    if "C2" in which:
        log("C2 inicio (rama t=6..12, dn=-0,003 y -0,005)")
        OUT["C2_trace"] = {}
        C2 = []
        for dn in (-0.003, -0.005):
            steps = track(dn, h=H0, r0=R.R0_DEFAULT, coarse_checks=True)
            OUT["C2_trace"][f"dn={dn}"] = [
                {k: v for k, v in s.items() if k not in ("roots",)} | {"roots": s.get("roots", [])}
                for s in steps]
            for t_um in (6.0, 12.0):
                rec = c2_primary_case(steps, t_um, dn)
                C2.append(rec)
                sel = rec.get("selected")
                log(f"C2 t={t_um} dn={dn}: sel={'-' if sel is None else (round(sel['g_re'], 3), round(sel['g_im'], 4))}"
                    f" ecs={rec.get('ecs_nominal')}")
            save()
        OUT["C2"] = C2
        prim = C2
        crit2 = dict(
            C2_1_all_primary=bool(all(r.get("compare", {}).get("pass_C2_1", False) for r in prim)),
            C2_2_all_primary=bool(all(r.get("compare", {}).get("pass_C2_2", False) for r in prim)),
            C2_3_all_primary_valid=bool(all(r.get("selected") is not None for r in prim)),
            n_primary=len(prim),
            per_case=[dict(t_um=r["t_um"], dn=r["dn"],
                           pass_C2_1=bool(r.get("compare", {}).get("pass_C2_1", False)),
                           pass_C2_2=bool(r.get("compare", {}).get("pass_C2_2", False)),
                           pass_C2_3=bool(r.get("selected") is not None))
                      for r in prim],
        )
        OUT["C2_criteria"] = crit2
        OUT["stage_status"]["C2"] = "done"
        save()
        log("C2 criterios " + json.dumps({k: v for k, v in crit2.items() if k != "per_case"}))

    # ------------------------------------------------------------ C3
    if "C3" in which:
        log("C3 inicio")
        C3 = {}
        # C3.1-C3.4 en la rama de continuacion a t=12, dn=-0,003
        main = track(-0.003, h=H0, r0=R.R0_DEFAULT, coarse_checks=False)
        g6 = complex(main[0]["selected"]["g_re"], main[0]["selected"]["g_im"])
        hs = [H0, H0 / 2, H0 / 4]
        gv, rF_end = [], []
        for h in hs:
            st = track(-0.003, h=h, r0=R.R0_DEFAULT, g_start=g6, coarse_checks=False)
            last = [s for s in st if abs(s["t_um"] - 12.0) < 1e-9]
            if last and last[0].get("root") is not None:
                gv.append(complex(last[0]["root"]["g_re"], last[0]["root"]["g_im"]))
                rF_end.append(last[0]["root"]["rF"])
            else:
                gv.append(None)
                rF_end.append(None)
            log(f"  C3 h={h:.3e}: g12={gv[-1]}")
        if None in gv:
            C3["trench_t12_dn-0.003"] = dict(status="sin_raiz_en_algun_h", gv=[str(x) for x in gv])
        else:
            d1 = abs(gv[0] - gv[1])
            d2 = abs(gv[1] - gv[2])
            rel_re_12 = abs(gv[1].real - gv[2].real) / abs(gv[2].real)
            im_tol = 1e-3 * max(abs(gv[2].imag), 1.0)
            saturated = d2 < 1e-9 * abs(gv[2])
            p_obs = float(np.log2(d1 / d2)) if d2 > 0 else None
            # C3.3: radio de arranque 0,01 um frente a 0,02 um, misma rama
            st_r0 = track(-0.003, h=H0, r0=0.01e-6, g_start=g6, coarse_checks=False)
            last_r0 = [s for s in st_r0 if abs(s["t_um"] - 12.0) < 1e-9]
            dr0 = None
            if last_r0 and last_r0[0].get("root") is not None:
                gr0 = complex(last_r0[0]["root"]["g_re"], last_r0[0]["root"]["g_im"])
                dr0 = abs(gr0.real - gv[0].real) / abs(gv[0].real)
            C3["trench_t12_dn-0.003"] = dict(
                h_m=hs, g_t12=[{"re": x.real, "im": x.imag} for x in gv], rF_end=rF_end,
                d_h0_h2=float(d1), d_h2_h4=float(d2), rel_dRe_h2_h4=float(rel_re_12),
                dIm_h2_h4=float(abs(gv[1].imag - gv[2].imag)), im_tol=float(im_tol),
                saturated_h2_h4=bool(saturated), order_p=p_obs,
                r0_test_rel_dRe=dr0,
                pass_C3_1=bool(rel_re_12 <= 1e-6 and (abs(gv[1].imag - gv[2].imag) <= im_tol or abs(gv[2].imag) < 1.0)),
                pass_C3_2=bool(saturated or (p_obs is not None and p_obs >= 3.5)),
                pass_C3_3=bool(dr0 is not None and dr0 <= 1e-9),
                pass_C3_4=bool(all(r is not None and r < 1e-7 for r in rF_end)),
            )
        log("C3 trench " + json.dumps({k: v for k, v in C3["trench_t12_dn-0.003"].items()
                                        if k.startswith("pass") or k in ("order_p", "rel_dRe_h2_h4")}, default=str))
        OUT["C3"] = C3
        save()

        # C1 Delta=0,010, LP01: convergencia en paso (modelos E y P), como ronda 1
        Delta, a = 0.010, 6e-6
        c1h = {}
        for model in ("E", "P"):
            vals = []
            for h in [H0, H0 / 2, H0 / 4]:
                gs = (np.linspace(1e-9, R.K0 * Delta * (1 - 1e-9), 400) if model == "P"
                      else np.linspace(R.N0 + 1e-9, R.N0 + Delta - 1e-9, 400))
                rts = R.real_roots(gs, [(0.0, a, Delta)], 0, model, h)
                vals.append(max(rts) if rts else None)
            if model == "P":
                vals = [None if v is None else R.N0 + v / R.K0 for v in vals]
            d1 = abs(vals[0] - vals[1])
            d2 = abs(vals[1] - vals[2])
            p_obs = float(np.log2(d1 / d2)) if d2 > 0 else None
            c1h[model] = dict(h=[H0, H0 / 2, H0 / 4], neff_LP01=vals, abs_d_h_h2=float(d1), abs_d_h2_h4=float(d2),
                              order_p=p_obs,
                              pass_C3_1=bool(d2 <= 1e-6 * vals[2] or d2 < 1e-12),
                              pass_C3_2=bool((p_obs or 0) >= 3.5 or d2 < 1e-12))
            log(f"C3 C1 Delta=0.010 modelo {model}: neff={vals} orden={p_obs}")
        C3["C1_step_Delta0.010_LP01"] = c1h
        OUT["C3"] = C3
        OUT["stage_status"]["C3"] = "done"
        save()

    # ------------------------------------------------------------ resumen de criterios (calculado por el codigo)
    C1c = OUT.get("C1_criteria")
    C2c = OUT.get("C2_criteria")
    C3d = OUT.get("C3", {}).get("trench_t12_dn-0.003", {})
    C3c = OUT.get("C3", {}).get("C1_step_Delta0.010_LP01", {})
    evaluated = {
        "C1": C1c is not None,
        "C2": C2c is not None,
        "C3_trench": "pass_C3_1" in C3d,
        "C3_C1": bool(C3c),
    }
    OUT["criterios_r2"] = {
        "C1.1": (C1c or {}).get("C1.1_E_maxroot_err_le_1e-8", {}).get("pass_all"),
        "C1.2": (C1c or {}).get("C1.2_P_maxroot_err_le_0.01_Delta", {}).get("pass_all"),
        "C1.3": (C1c or {}).get("C1.3_no_LP11_below_cutoff", {}).get("pass_all"),
        "C1.4": (C1c or {}).get("C1.4_root_count_matches_closed", {}).get("pass_all"),
        "C2.1_primary_all": (C2c or {}).get("C2_1_all_primary"),
        "C2.2_primary_all": (C2c or {}).get("C2_2_all_primary"),
        "C2.3_primary_all_valid": (C2c or {}).get("C2_3_all_primary_valid"),
        "C3.1_trench_t12_dn-0.003": C3d.get("pass_C3_1"),
        "C3.2_trench_t12_dn-0.003": C3d.get("pass_C3_2"),
        "C3.3_trench_t12_dn-0.003": C3d.get("pass_C3_3"),
        "C3.4_trench_t12_dn-0.003": C3d.get("pass_C3_4"),
        "C3.1_C1_Delta0.010_E": C3c.get("E", {}).get("pass_C3_1"),
        "C3.1_C1_Delta0.010_P": C3c.get("P", {}).get("pass_C3_1"),
        "C3.2_C1_Delta0.010_E": C3c.get("E", {}).get("pass_C3_2"),
        "C3.2_C1_Delta0.010_P": C3c.get("P", {}).get("pass_C3_2"),
    }
    all_eval = all(v is not None for v in OUT["criterios_r2"].values())
    OUT["status"] = "done" if (all_eval and all(evaluated.values())) else "partial"
    OUT["evaluated_flags"] = evaluated
    OUT["limitations"] = [
        "C2 t=7..12: rama por continuacion en t; no garantiza exhaustividad de raices (la malla gruesa no resuelve Im g pequeno).",
        "El criterio 'mayor Re g' se aplica dentro de la rama seguida.",
        "Casos secundarios no repetidos en r2.",
        "Convencion de signo: perdida = 2 Im g * 4,343e-2, decaimiento <=> Im g >= 0 (igual que la salida numerica de glass006a).",
    ]
    save()
    log(f"escrito {DST} status={OUT['status']}")
