"""GLASS-009c-VACIO. Analisis de la validacion en vacio de la frontera absorbente (CONTRATO-VACIO.md).

Lee (solo lectura): out/, out2/ (resultados 009c, 009c-2) y vacio_out/, vacio_estados/ (corridas nuevas).
Escribe: resultados009c_vacio.json (nuevo). No modifica ningun resultado previo.
Uso: python -B validacion_vacio_analisis.py
"""
import os, sys, json, glob, math, hashlib
os.environ["OMP_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "glass009_claude"))
import numpy as np
import adi2d as S

W0 = 6e-6; RU = 40e-6; ZMM = 2e-3; SMAX = 4e4
K1_THR = 1e-4          # -40 dB de la potencia de entrada (CONTRATO-VACIO K1)
K2_SPREAD = 2.0        # factor de dependencia (K2)
K0A_TOL = 1e-9
K5_TOL = 1e-9
B1_THR = 1e-3          # gate B1 de 009c para el suelo de discretizacion

def P(p):  # carga JSON
    return json.load(open(p))

# ------------------------------------------------------------------ coleccion de configuraciones
configs = []

controls = []

def add(path, origin):
    d = P(path)
    smax_file = float(d.get("smax", SMAX))
    if abs(smax_file - SMAX) > 1e-9:  # controles (enmienda 1), no entran en la malla
        controls.append(dict(path=path, smax=smax_file, theta=round(d["theta_rad"], 6), dom=round(d["domain_um"], 3),
                             dx=round(d["dx_um"], 4), z_arr=d["z_arr_m"], rows=d["rows"], N=int(d["N"]),
                             P0=d["rows"][0]["P_total_num"], origin=origin, file=os.path.relpath(path, HERE)))
        return
    c = dict(
        origin=origin, file=os.path.relpath(path, HERE),
        theta=round(d["theta_rad"], 6), dom=round(d["domain_um"], 3), dx=round(d["dx_um"], 4),
        dz=round(d.get("dz_um", 2.5), 4), frac=round(d.get("frac", 0.2), 4), p=int(d.get("p", 4)),
        N=int(d["N"]), z_arr=d["z_arr_m"], rows=d["rows"],
    )
    c["P0"] = c["rows"][0]["P_total_num"]
    configs.append(c)

for f in sorted(glob.glob(os.path.join(HERE, "out", "th*_dom*_dx*.json"))):
    add(f, "009c out/ (dz 2,5)")
for f in sorted(glob.glob(os.path.join(HERE, "out2", "th*_dom*_dx5_dz*.json"))):
    add(f, "009c-2 out2/")
for f in sorted(glob.glob(os.path.join(HERE, "vacio_out", "th*_dom*_dx*_f*_p*.json"))):
    add(f, "vacio (nuevo)")

def find(theta, dom, dx, dz=2.5, frac=0.2, p=4, origin=None):
    for c in configs:
        if (abs(c["theta"] - theta) < 1e-9 and abs(c["dom"] - dom) < 1e-6 and abs(c["dx"] - dx) < 1e-6
                and abs(c["dz"] - dz) < 1e-6 and abs(c["frac"] - frac) < 1e-9 and c["p"] == p):
            if origin is None or origin in c["origin"]:
                return c
    return None

# ------------------------------------------------------------------ metricas por configuracion
def metrics(c):
    rows = c["rows"]; P0 = c["P0"]; za = c["z_arr"]
    W = [r for r in rows if za is not None and r["z_m"] >= za - 1e-12]
    pre = [r for r in rows if za is None or r["z_m"] < za - 1e-12]
    dP = [(r["Pu_num"] - r["Pu_an"]) / P0 for r in W]
    if dP:
        imax = int(np.argmax(np.abs(dP)))
        maxabs = float(abs(dP[imax])); zmax = W[imax]["z_m"] * 1e3
        rel_max = float(dP[imax] / (W[imax]["Pu_an"] / P0)) if W[imax]["Pu_an"] > 0 else None
    else:
        maxabs = None; zmax = None; rel_max = None
    Pt = [r["P_total_num"] for r in rows]
    mono_viol = max([(Pt[i + 1] - Pt[i]) / P0 for i in range(len(Pt) - 1)] + [0.0])
    return dict(
        theta_rad=c["theta"], dom_um=c["dom"], dx_um=c["dx"], dz_um=c["dz"], frac=c["frac"], p=c["p"],
        origin=c["origin"], file=c["file"], z_arr_mm=(None if za is None else round(za * 1e3, 4)),
        n_window=len(W),
        maxabs_dP=maxabs, z_at_maxabs_mm=(None if zmax is None else round(zmax, 4)), rel_dP_at_max=rel_max,
        rho_max=(None if not dP else float(max(max(v, 0.0) for v in dP))),
        lam_max=(None if not dP else float(max(max(-v, 0.0) for v in dP))),
        E_pre_arrival=(max(r["E"] for r in pre) if pre else None),
        E_max=max(r["E"] for r in rows),
        E_2mm=rows[-1]["E"],
        absorbed_frac_2mm=float(1 - rows[-1]["P_total_num"] / P0),
        K1_pass=(None if maxabs is None else bool(maxabs < K1_THR)),
        mono_violation_over_P0=float(mono_viol),
        K5_pass=bool(mono_viol <= K5_TOL),
    )

# ------------------------------------------------------------------ K0 verificacion
K0 = {}
# K0a reproduccion: runner nuevo (f=0,2 p=4 dx=0,5 dom 128 dz 2,5) frente a 009c.
rep = []
for th, ref in [(0.0, "out/th000_dom128_dx5.json"), (0.02, "out2/th020_dom128_dx5_dz250.json"),
                (0.05, "out2/th050_dom128_dx5_dz250.json"), (0.08, "out2/th080_dom128_dx5_dz250.json")]:
    new = find(th, 128, 0.5, 2.5, 0.2, 4, origin="vacio")
    old = P(os.path.join(HERE, "..", "glass009c_claude", ref))["rows"]
    if new is None:
        rep.append(dict(theta=th, missing=True)); continue
    nrows = new["rows"]
    dE = max(abs(a["E"] - b["E"]) for a, b in zip(nrows, old))
    dPu = max(max(abs(a["Pu_num"] - b["Pu_num"]), abs(a["Pu_an"] - b["Pu_an"])) for a, b in zip(nrows, old))
    rep.append(dict(theta=th, n=len(nrows), max_dE=float(dE), max_dPu=float(dPu), ref=ref))
K0["a_reproduccion_009c"] = dict(rows=rep,
    pass_=all((not r.get("missing")) and r["max_dE"] < K0A_TOL and r["max_dPu"] < K0A_TOL for r in rep))
# K0b sigma identico a adi2d.sigma_map (f=0,2, p=4)
Nq, dxq = 256, 0.5e-6
xq, yq = S.coords(Nq, dxq); eq = np.maximum(np.abs(xq), np.abs(yq)) / (Nq * dxq / 2)
sig_runner = SMAX * np.maximum((eq - 0.8) / 0.2, 0) ** 4
sig_009 = S.sigma_map(Nq, dxq)
rel_sig = float(np.abs(sig_runner - sig_009).max() / SMAX)
K0["b_sigma_vs_adi2d"] = dict(max_rel_diff=rel_sig, pass_=bool(rel_sig < 1e-12))
# K0c analitico en z=0 frente al gaussiano discreto
def analytic_field(N, dx, theta, z):
    kt = S.b0 * theta; x, y = S.coords(N, dx); zR = S.b0 * W0 ** 2 / 2
    A0 = S.gaussian(N, dx, W0, 0.0, kt); N0 = A0[N // 2, N // 2].real
    zeta = z / zR; xs = kt * z / S.b0
    Aa = N0 / (1 + 1j * zeta) * np.exp(-(((x - xs) ** 2 + y * y) / (W0 ** 2 * (1 + 1j * zeta)))) \
        * np.exp(1j * kt * x) * np.exp(-1j * kt ** 2 * z / (2 * S.b0))
    return A0, Aa
c0 = []
for th in [0.0, 0.02, 0.05, 0.08]:
    A0, Aa0 = analytic_field(256, 0.5e-6, th, 0.0)
    c0.append(float(np.abs(Aa0 - A0).max() / np.abs(A0).max()))
K0["c_analitico_z0"] = dict(max_rel=max(c0), pass_=bool(max(c0) < 1e-9))
# K0d/K5 monotonia en todas las corridas nuevas
new_cfg = [c for c in configs if c["origin"].startswith("vacio")]
mono = [(m["file"], m["mono_violation_over_P0"]) for m in (metrics(c) for c in new_cfg)]
K0["d_energia_monotona_nuevas"] = dict(n=len(new_cfg), max_violation=max(v for _, v in mono) if mono else None,
                                       pass_=all(v <= K5_TOL for _, v in mono))
# K0e consistencia de estados guardados con E(2 mm) de los JSON (009c-2)
state_checks = []
for th, dom, dx, fn, sfile in [
    (0.02, 128, 0.5, "out2/th020_dom128_dx5_dz250.json", "out2/state_th020_dom128_dx5_dz250.npy"),
    (0.05, 128, 0.5, "out2/th050_dom128_dx5_dz250.json", "out2/state_th050_dom128_dx5_dz250.npy"),
    (0.08, 128, 0.5, "out2/th080_dom128_dx5_dz250.json", "out2/state_th080_dom128_dx5_dz250.npy"),
    (0.0, 256, 0.5, "out2/th000_dom256_dx5_dz250.json", "out2/state_th000_dom256_dx5_dz250.npy"),
]:
    N = int(round(dom / dx)); An = np.load(os.path.join(HERE, "..", "glass009c_claude", sfile))
    A0, Aa = analytic_field(N, dx * 1e-6, th, ZMM)
    x, y = S.coords(N, dx * 1e-6); useful = np.hypot(x, y) < RU
    E = float(np.linalg.norm((An - Aa)[useful]) / np.linalg.norm(Aa[useful]))
    ref = P(os.path.join(HERE, "..", "glass009c_claude", fn))["rows"][-1]["E"]
    state_checks.append(dict(theta=th, dom=dom, E_from_state=E, E_json_2mm=ref, diff=abs(E - ref)))
K0["e_estado_vs_json_2mm"] = dict(rows=state_checks, pass_=all(s["diff"] < 1e-9 for s in state_checks))

# ------------------------------------------------------------------ D1: retorno en malla 009c
D1 = []
for th in [0.0, 0.02, 0.05, 0.08]:
    for dom, dx, origin in [(128, 1.0, "009c out/"), (128, 0.5, None), (256, 1.0, "009c out/"), (256, 0.5, None)]:
        c = find(th, dom, dx, 2.5, 0.2, 4, origin=origin)
        if c is None and origin is None:
            # prioriza el 009c original; si no existe, la corrida nueva
            c = find(th, dom, dx, 2.5, 0.2, 4, origin="009c") or find(th, dom, dx, 2.5, 0.2, 4, origin="vacio")
        if c is None:
            D1.append(dict(theta_rad=th, dom_um=dom, dx_um=dx, missing=True)); continue
        m = metrics(c); D1.append(m)
D1_dx05 = [m for m in D1 if m.get("dx_um") == 0.5 and not m.get("missing")]
D1_dx10 = [m for m in D1 if m.get("dx_um") == 1.0 and not m.get("missing")]
K1_all = bool(all(m["K1_pass"] for m in D1_dx05)) if D1_dx05 else False

# ------------------------------------------------------------------ D2: barrido del absorbente (dom 128, dx 0,5)
FP = [(0.2, 4), (0.2, 2), (0.2, 6), (0.1, 4), (0.3, 4)]
D2 = {}
for th in [0.0, 0.02, 0.05, 0.08]:
    lst = []
    for f, p in FP:
        c = find(th, 128, 0.5, 2.5, f, p, origin="vacio")
        if c is None:
            lst.append(dict(frac=f, p=p, missing=True)); continue
        m = metrics(c)
        Aint = SMAX * f * (c["N"] * c["dx"] * 1e-6 / 2) / (p + 1)
        m["A_int"] = float(Aint)
        lst.append(m)
    D2[str(th)] = lst
D2_summary = {}
for th, lst in D2.items():
    vals = [m["maxabs_dP"] for m in lst if not m.get("missing") and m["maxabs_dP"] is not None]
    if vals:
        lo = max(min(vals), 1e-12)
        D2_summary[th] = dict(max=max(vals), min=min(vals), spread=max(vals) / lo, depends=bool(max(vals) / lo > K2_SPREAD))
# existe configuracion que pase K1 para todo theta en {0,02; 0,05; 0,08}
passing = []
for f, p in FP:
    ok = True
    for th in ["0.02", "0.05", "0.08"]:
        m = [mm for mm in D2[th] if (not mm.get("missing")) and mm["frac"] == f and mm["p"] == p]
        if not m or not m[0]["K1_pass"]:
            ok = False; break
    if ok:
        passing.append(dict(frac=f, p=p))
K2_pass = bool(len(passing) > 0)
K2_depends = bool(any(v["depends"] for v in D2_summary.values())) if D2_summary else None

# ------------------------------------------------------------------ D4: malla fina dx=0,25 frente a dx=0,5 (dom 128, f 0,2, p 4)
D4 = []
for th in [0.0, 0.02, 0.05, 0.08]:
    c5 = find(th, 128, 0.5, 2.5, 0.2, 4, origin="009c") or find(th, 128, 0.5, 2.5, 0.2, 4, origin="vacio")
    c25 = find(th, 128, 0.25, 2.5, 0.2, 4, origin="vacio")
    if c5 is None or c25 is None:
        D4.append(dict(theta_rad=th, missing=True)); continue
    m5 = metrics(c5); m25 = metrics(c25)
    q = m5["maxabs_dP"] / m25["maxabs_dP"] if m25["maxabs_dP"] else None
    if q is None:
        cls = "indeterminado"
    elif 2.5 <= q <= 6:
        cls = "discretizacion (orden 2)"
    elif 0.67 <= q <= 1.5:
        cls = "retorno del absorbente, independiente de la malla"
    else:
        cls = "indeterminado"
    D4.append(dict(theta_rad=th, dx05=m5, dx025=m25, q=q, clasificacion=cls,
                   E_pre_dx05=m5["E_pre_arrival"], E_pre_dx025=m25["E_pre_arrival"],
                   K1_dx05=m5["K1_pass"], K1_dx025=m25["K1_pass"],
                   B1_floor_dx025_pass=(None if m25["E_pre_arrival"] is None else bool(m25["E_pre_arrival"] < B1_THR))))
K4_B1_theta0 = D4[0].get("B1_floor_dx025_pass") if D4 and not D4[0].get("missing") else None

# ------------------------------------------------------------------ D3: fase del campo final (z = 2 mm), dom 128/256
def phase_row(th, dom, dx, state_path, tag):
    N = int(round(dom / dx)); dxm = dx * 1e-6
    An = np.load(state_path)
    A0, Aa = analytic_field(N, dxm, th, ZMM)
    x, y = S.coords(N, dxm); useful = np.hypot(x, y) < RU; d2 = dxm * dxm
    ov = (np.conj(Aa[useful]) * An[useful]).sum() * d2
    Pa = (np.abs(Aa[useful]) ** 2).sum() * d2; Pn = (np.abs(An[useful]) ** 2).sum() * d2
    err = ov - Pa  # sum conj(Aa)*(An-Aa)
    return dict(tag=tag, theta_rad=th, dom_um=dom, dx_um=dx, N=N,
                psi_ov_rad=float(np.angle(ov)), coherencia=float(abs(ov) / math.sqrt(Pa * Pn)),
                psi_err_rad=float(np.angle(err)), Pu_an_2mm=float(Pa), Pu_num_2mm=float(Pn))
phase_states = []
for th, dom, dx, sp, tag in [
    (0.02, 128, 0.5, os.path.join(HERE, "..", "glass009c_claude", "out2", "state_th020_dom128_dx5_dz250.npy"), "009c-2 dz2,5"),
    (0.05, 128, 0.5, os.path.join(HERE, "..", "glass009c_claude", "out2", "state_th050_dom128_dx5_dz250.npy"), "009c-2 dz2,5"),
    (0.08, 128, 0.5, os.path.join(HERE, "..", "glass009c_claude", "out2", "state_th080_dom128_dx5_dz250.npy"), "009c-2 dz2,5"),
    (0.0, 256, 0.5, os.path.join(HERE, "..", "glass009c_claude", "out2", "state_th000_dom256_dx5_dz250.npy"), "009c-2 dz2,5"),
    (0.05, 256, 0.5, os.path.join(HERE, "..", "glass009c_claude", "out2", "state_th050_dom256_dx5_dz250.npy"), "009c-2 dz2,5"),
]:
    phase_states.append(phase_row(th, dom, dx, sp, tag))
for th in [0.0, 0.02, 0.05, 0.08]:
    for dom, dx in [(128, 0.5), (128, 0.25)]:
        f = os.path.join(HERE, "vacio_estados", f"state_th{int(round(th*1000)):03d}_dom{dom}_dx{int(round(dx*100)):03d}_f20_p4.npy")  # dx en um -> dxNNN = NNN x 0,01 um
        fj = os.path.join(HERE, "vacio_out", os.path.basename(f).replace("state_", "").replace(".npy", ".json"))
        if os.path.exists(f) and os.path.exists(fj):  # solo estados finales (JSON escrito al terminar)
            phase_states.append(phase_row(th, dom, dx, f, "vacio dz2,5 f0,2 p4"))
    if th in (0.02, 0.08):
        f = os.path.join(HERE, "vacio_estados", f"state_th{int(round(th*1000)):03d}_dom256_dx050_f20_p4.npy")
        fj = os.path.join(HERE, "vacio_out", os.path.basename(f).replace("state_", "").replace(".npy", ".json"))
        if os.path.exists(f) and os.path.exists(fj):
            phase_states.append(phase_row(th, 256, 0.5, f, "vacio dz2,5 f0,2 p4 (ampliado)"))
ph1d = {round(r["theta_rad"], 4): r["phase_rad"] for r in P(os.path.join(HERE, "..", "frontera_claude", "fase_resultados.json"))["rows"]}
for r in phase_states:
    ref = ph1d.get(round(r["theta_rad"], 4))
    r["arg_r_1D_mismo_theta"] = ref
    r["diff_wrapped_ov_vs_1D"] = (None if ref is None else float(np.angle(np.exp(1j * (r["psi_ov_rad"] - ref)))))
K3_comparable = False  # pre-declarado en CONTRATO-VACIO K3 (i) y (ii) no se cumplen

# ------------------------------------------------------------------ enmienda 1: controles (diagnostico, sin gate)
CTRL = dict(sin_esponja=[], ref_dom512=[], descomposicion=[])
for cc in controls:
    m = metrics(dict(origin="control", file=cc["file"], theta=cc["theta"], dom=cc["dom"], dx=cc["dx"], dz=2.5,
                     frac=0.2, p=4, N=cc["N"], z_arr=cc["z_arr"], rows=cc["rows"], P0=cc["P0"]))
    m["smax"] = cc["smax"]
    CTRL["sin_esponja"].append(m)
for th in [0.05, 0.08]:
    ref = find(th, 512, 0.5, 2.5, 0.2, 4, origin="vacio")
    base = find(th, 128, 0.5, 2.5, 0.2, 4, origin="vacio") or find(th, 128, 0.5, 2.5, 0.2, 4, origin="009c")
    if ref is None or base is None:
        CTRL["ref_dom512"].append(dict(theta_rad=th, missing=True)); continue
    mr = metrics(ref); mb = metrics(base)
    CTRL["ref_dom512"].append(dict(theta_rad=th, ref=mr, base128=mb))
    # descomposicion sample a sample (mismos pasos): delta_frontera = (Pu_128 - Pu_512)/P0
    rb = {r["step"]: r for r in base["rows"]}; rr = {r["step"]: r for r in ref["rows"]}
    common = sorted(set(rb) & set(rr))
    zarr = base["z_arr"]; P0b = base["P0"]; P0r = ref["P0"]
    dfront = []; dref = []
    for st_ in common:
        z = rb[st_]["z_m"]
        if zarr is None or z < zarr - 1e-12:
            continue
        dfront.append(dict(z_mm=round(z * 1e3, 3), delta_frontera=(rb[st_]["Pu_num"] - rr[st_]["Pu_num"]) / P0b,
                           dP_128=(rb[st_]["Pu_num"] - rb[st_]["Pu_an"]) / P0b,
                           dP_512=(rr[st_]["Pu_num"] - rr[st_]["Pu_an"]) / P0r))
    CTRL["descomposicion"].append(dict(theta_rad=th, serie=dfront,
        max_abs_delta_frontera=max(abs(v["delta_frontera"]) for v in dfront) if dfront else None,
        max_abs_dP_512=max(abs(v["dP_512"]) for v in dfront) if dfront else None,
        E_2mm_128=base["rows"][-1]["E"], E_2mm_512=ref["rows"][-1]["E"]))

# ------------------------------------------------------------------ resumen
crit = []
crit.append(dict(id="K0a", description="runner reproduce filas 009c (f 0,2 p 4 dx 0,5 dom 128): |dE|,|dPu| < 1e-9",
                 value=("max_dE/dPu=" + ", ".join(f"{r['max_dE']:.1e}/{r['max_dPu']:.1e}" for r in rep if not r.get("missing"))),
                 pass_=K0["a_reproduccion_009c"]["pass_"]))
crit.append(dict(id="K0b", description="sigma runner = adi2d.sigma_map (f 0,2 p 4) < 1e-12 relativo",
                 value=f"{rel_sig:.1e}", pass_=K0["b_sigma_vs_adi2d"]["pass_"]))
crit.append(dict(id="K0c", description="analitico(z=0) = gaussiano discreto < 1e-9 relativo",
                 value=f"{max(c0):.1e}", pass_=K0["c_analitico_z0"]["pass_"]))
crit.append(dict(id="K0d", description="energia total monotona no creciente en corridas nuevas (tol 1e-9 P0)",
                 value=f"max violacion {K0['d_energia_monotona_nuevas']['max_violation']:.1e} P0 en {K0['d_energia_monotona_nuevas']['n']} corridas",
                 pass_=K0["d_energia_monotona_nuevas"]["pass_"]))
crit.append(dict(id="K0e", description="estado guardado reproduce E(2 mm) del JSON 009c-2 (< 1e-9)",
                 value=", ".join(f"{s['diff']:.1e}" for s in state_checks), pass_=K0["e_estado_vs_json_2mm"]["pass_"]))
crit.append(dict(id="K1", description="retorno en vacio: max_W |dPu|/P0 < 1e-4 en todas las mallas dx 0,5 (dom 128 y 256)",
                 value="; ".join(f"dom{m['dom_um']:.0f} th{m['theta_rad']}: {m['maxabs_dP']:.2e}" for m in D1_dx05),
                 pass_=K1_all))
crit.append(dict(id="K1-diag", description="diagnostico dx 1,0 (no se reevalua el veredicto de 009c; K1 como referencia)",
                 value="; ".join(f"dom{m['dom_um']:.0f} th{m['theta_rad']}: {m['maxabs_dP']:.2e}" for m in D1_dx10),
                 pass_=bool(all(m["K1_pass"] for m in D1_dx10)) if D1_dx10 else None))
crit.append(dict(id="K2", description="existe configuracion (f,p) que pasa K1 para theta 0,02/0,05/0,08; y dependencia (spread>2)",
                 value=f"pasan: {passing}; dependencia: {K2_depends}; spreads: " + "; ".join(f"th{k}={v['spread']:.2f}" for k, v in D2_summary.items()),
                 pass_=K2_pass))
crit.append(dict(id="K3", description="fase comparable con la 1D (pre-declarado: no comparable)",
                 value="no comparable (magnitud y geometria distintas, ver texto)", pass_=False))
crit.append(dict(id="K4", description="malla: q = max|dPu|(0,5)/max|dPu|(0,25) clasifica; B1 suelo 0,25 en theta 0 < 1e-3",
                 value="; ".join(f"th{d['theta_rad']}: q={d['q']:.2f} {d['clasificacion']}" for d in D4 if not d.get("missing") and d["q"] is not None)
                       + f"; B1_0,25(th=0): {K4_B1_theta0}",
                 pass_=bool(K4_B1_theta0) if K4_B1_theta0 is not None else False))
crit.append(dict(id="K6", description="ley 1D R0^(sin th) aplicable al absorbente paraxial (pre-declarado: no)",
                 value="no aplicable: la cantidad 2D no es reflectancia de la pared y la dependencia en theta es opuesta (ver texto)",
                 pass_=False))

out = dict(
    task="GLASS-009c-VACIO", contrato="CONTRATO-VACIO.md",
    adi2d_sha256=hashlib.sha256(open(os.path.join(HERE, "..", "glass009_claude", "adi2d.py"), "rb").read()).hexdigest(),
    analisis_sha256=hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
    K1_thr=K1_THR, K2_spread=K2_SPREAD, K5_tol=K5_TOL, B1_thr=B1_THR,
    K0=K0, criteria=crit,
    D1_dx05=D1_dx05, D1_dx10=D1_dx10,
    D2=D2, D2_summary=D2_summary, D2_passing=passing,
    D4=D4, D3_phases=phase_states, CONTROLES_enmienda1=CTRL,
)
json.dump(out, open(os.path.join(HERE, "resultados009c_vacio.json"), "w"), indent=1, ensure_ascii=False, default=lambda o: float(o) if isinstance(o, (np.floating,)) else (bool(o) if isinstance(o, np.bool_) else str(o)))

print("== K0 ==")
for k, v in K0.items():
    print(k, v.get("pass_"), {kk: vv for kk, vv in v.items() if kk != "pass_" and kk != "rows"})
print("== D1 dx0.5 ==")
for m in D1_dx05:
    print(f"dom{m['dom_um']:>5.0f} th{m['theta_rad']:<5} z_arr={m['z_arr_mm']} nW={m['n_window']} max|dP|/P0={m['maxabs_dP']:.3e} @z={m['z_at_maxabs_mm']} rho={m['rho_max']:.3e} lam={m['lam_max']:.3e} E_pre={m['E_pre_arrival']:.3e} E_2mm={m['E_2mm']:.3e} K1={m['K1_pass']}")
print("== D1 dx1.0 (diag) ==")
for m in D1_dx10:
    print(f"dom{m['dom_um']:>5.0f} th{m['theta_rad']:<5} z_arr={m['z_arr_mm']} max|dP|/P0={m['maxabs_dP']:.3e} E_pre={m['E_pre_arrival']:.3e} K1={m['K1_pass']}")
print("== D2 ==")
for th, lst in D2.items():
    for m in lst:
        if m.get("missing"):
            print(th, m["frac"], m["p"], "MISSING"); continue
        print(f"th{th:<5} f{m['frac']} p{m['p']} A_int={m['A_int']:.3f} z_arr={m['z_arr_mm']} max|dP|={m['maxabs_dP']:.3e} rho={m['rho_max']:.3e} lam={m['lam_max']:.3e} E_pre={m['E_pre_arrival']:.3e} K1={m['K1_pass']}")
print("spread", D2_summary)
print("== D4 ==")
for d in D4:
    if d.get("missing"):
        print(d["theta_rad"], "MISSING"); continue
    print(f"th{d['theta_rad']} q={d['q']} {d['clasificacion']} K1_05={d['K1_dx05']} K1_025={d['K1_dx025']} E_pre05={d['E_pre_dx05']} E_pre025={d['E_pre_dx025']} max05={d['dx05']['maxabs_dP']:.3e} max025={d['dx025']['maxabs_dP']:.3e}")
print("== CONTROLES (enmienda 1) ==")
for m in CTRL["sin_esponja"]:
    print(f"SIN ESPONJA dom{m['dom_um']:.0f} th{m['theta_rad']} z_arr={m['z_arr_mm']} max|dP|/P0={m['maxabs_dP']:.3e} rho={m['rho_max']:.3e} lam={m['lam_max']:.3e} E_pre={m['E_pre_arrival']:.3e} E_2mm={m['E_2mm']:.3e} P_abs_2mm={m['absorbed_frac_2mm']:.3e}")
for d in CTRL["ref_dom512"]:
    if d.get("missing"):
        print("REF512 th", d["theta_rad"], "MISSING"); continue
    print(f"REF512 th{d['theta_rad']} max|dP_512|/P0={d['ref']['maxabs_dP']:.3e} E_pre={d['ref']['E_pre_arrival']:.3e} E_2mm={d['ref']['E_2mm']:.3e} | base128 max|dP|={d['base128']['maxabs_dP']:.3e} E_2mm={d['base128']['E_2mm']:.3e}")
for d in CTRL["descomposicion"]:
    print(f"DESCOMP th{d['theta_rad']} max|delta_frontera|/P0={d['max_abs_delta_frontera']:.3e} max|dP_512|/P0={d['max_abs_dP_512']:.3e} E2mm_128={d['E_2mm_128']:.3e} E2mm_512={d['E_2mm_512']:.3e}")
print("== D3 ==")
for r in phase_states:
    print(f"{r['tag']:<32} th{r['theta_rad']:<5} dom{r['dom_um']:>4.0f} dx{r['dx_um']} psi_ov={r['psi_ov_rad']:+.4f} coh={r['coherencia']:.6f} psi_err={r['psi_err_rad']:+.4f} 1D={r['arg_r_1D_mismo_theta']} diff={r['diff_wrapped_ov_vs_1D']}")
